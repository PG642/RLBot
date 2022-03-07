from os import stat
from pathlib import Path

import numpy as np
from queue import Empty

from multi_sample_factory.algorithms.appo.actor_worker import transform_dict_observations
from multi_sample_factory.algorithms.appo.model_utils import get_hidden_size
from multi_sample_factory.algorithms.utils.action_distributions import transform_action_space
from multi_sample_factory.utils.utils import AttrDict
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket
from rlbot.matchcomms.common_uses.set_attributes_message import handle_set_attributes_message
from rlbot.matchcomms.common_uses.reply import reply_to
from multi_sample_factory.algorithms.appo.enjoy_appo import create_model
from multi_sample_factory.algorithms.utils.arguments import parse_args, load_from_checkpoint
from gym.spaces import MultiDiscrete, Box
from src.utils.drive import steer_toward_target
from src.utils.vec import Vec3, Location, Velocity, Quaternion, AngularVelocity

import torch
from src.neroRL.nn.actor_critic import create_actor_critic_model

from math import sin, cos

DISCRETE_ACTIONS = [-1, -0.5, 0, 0.5, 1]


class MSFBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.absolute_model_path = ""
        self.vis_obs_space = None
        self.vec_obs_space = (23,)
        self.action_space_shape = [5, 5, 5, 3, 2, 2, 2, 2]
        self.rnn_states = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """
        # Read messages from the exercise to change the model parameters on demand
        for i in range(100):  # process at most 100 messages per tick.
            try:
                msg = self.matchcomms.incoming_broadcast.get_nowait()
            except Empty:
                break

            if handle_set_attributes_message(msg, self, allowed_keys=['path']):
                reply_to(self.matchcomms, msg)  # Let the sender know we've set the attribute.
                print("--------------------------------------------")
                print("message received")
                print(msg["setattrs"]["path"])
                abs_path = Path(__file__).absolute().parent.parent / msg["setattrs"]["path"]
                if self.absolute_model_path != abs_path:
                    print("Load new checkpoint: " + str(abs_path))
                    self.absolute_model_path = abs_path
                    self.create_and_load_model(abs_path)
            else:
                # Ignore messages that are not for us.
                self.logger.debug(f'Unhandled message: {msg}')
            print("--------------------------------------------")

        # Prepare vector observations and apply normalization
        car_physics = packet.game_cars[self.index].physics
        ball_physics = packet.game_ball.physics

        ball_location = Location(ball_physics.location).to_unity_units()
        car_location = Location(car_physics.location).to_unity_units()
        relativeX = ((ball_location.x + 60.0) - (car_location.x + 60.0)) / 120.0
        relativeY = (ball_location.y - car_location.y) / 20.0
        relativeZ = ((ball_location.z + 41.0) - (car_location.z + 41.0)) / 82.0
        relativeLocation = Location(relativeX, relativeY, relativeZ)

        car_location = Location(car_physics.location)
        car_location.to_unity_units()
        car_location = car_location.obs_normalized()

        car_velocity = Velocity(car_physics.velocity)
        car_velocity.to_unity_units()
        car_velocity = car_velocity.obs_normalized()

        car_rotation = Quaternion(car_physics.rotation)
        car_rotation.to_unity_units()
        car_rotation = car_rotation.obs_normalized()

        car_angular_velocity = AngularVelocity(car_physics.angular_velocity)
        car_angular_velocity.to_unity_units()
        car_angular_velocity = car_angular_velocity.obs_normalized()

        ball_location = Location(ball_physics.location)
        ball_location.to_unity_units()
        ball_location = ball_location.obs_normalized()

        ball_velocity = Velocity(ball_physics.velocity)
        ball_velocity.to_unity_units()
        ball_velocity = ball_velocity.obs_normalized(is_ball=True)

        boost = packet.game_cars[self.index].boost / 100

        # Concatenate vector observations
        vec_obs = np.zeros(shape=(1, self.vec_obs_space[0]), dtype=np.float32)
        vec_obs[0, 0:3] = list(car_location)
        vec_obs[0, 3:7] = list(car_rotation)
        vec_obs[0, 7:10] = list(car_velocity)
        vec_obs[0, 10:13] = list(car_angular_velocity)
        vec_obs[0, 13:16] = list(ball_location)
        vec_obs[0, 16:19] = list(ball_velocity)
        vec_obs[0, 19] = boost
        vec_obs[0, 20:] = list(relativeLocation)

        obs_torch = AttrDict(transform_dict_observations(vec_obs))
        for key, x in obs_torch.items():
            obs_torch[key] = torch.from_numpy(x).to(self.device).float()

        # Set rnn states, if first package
        if self.rnn_states is None:
            self.rnn_states = torch.zeros([len(packet.game_cars), get_hidden_size(self.cfg)], dtype=torch.float32,
                                          device=self.device)

        policy_outputs = self.model(obs_torch, self.rnn_states, with_action_distribution=True)

        # Sample actions
        # sample actions from the distribution by default
        actions = policy_outputs[2].actions
        actions = actions.cpu().numpy()
        self.rnn_states = policy_outputs[2].rnn_states

        # Put actions to live
        controls = SimpleControllerState()
        controls.throttle = DISCRETE_ACTIONS[actions[0]]
        controls.steer = DISCRETE_ACTIONS[actions[1]]
        controls.yaw = DISCRETE_ACTIONS[actions[1]]
        controls.pitch = DISCRETE_ACTIONS[actions[2]]
        if actions[3] == 0:
            controls.roll = -1
        elif actions[3] == 2:
            controls.roll = 1
        else:
            controls.roll = 0
        controls.boost = actions[4] > 0
        controls.handbrake = actions[5] > 0
        if actions[6] > 0:
            controls.roll = DISCRETE_ACTIONS[actions[1]]
            controls.yaw = 0
        controls.jump = actions[7] > 0
        # controls.use_item = False
        return controls

    def load_config(self, config_object_header):
        model_path = config_object_header['model_path'].value
        if model_path is not None:
            absolute_model_path = Path(__file__).absolute().parent / model_path
            self.create_and_load_model(absolute_model_path)

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('model_path', str, default=None,
                         description='Port to use for websocket communication')

    def create_and_load_model(self, path: Path):
        #D:\PG\Run_Ergebnisse\reward_func_test_frederik_higher_pen_0\checkpoint_p0\model.pth
        experiment = path.parents[1].name
        train_dir = str(path.parents[2])
        self.cfg = parse_args(argv=["--algo=APPO", "--experiment={0}".format(experiment), "--train_dir={0}".format(train_dir)], evaluation=True)
        self.cfg = load_from_checkpoint(self.cfg)
        self.cfg.env_frameskip = 1  # for evaluation
        self.cfg.num_envs = 1
        self.device = torch.device('cpu' if self.cfg.device == 'cpu' else 'cuda')
        action_space = transform_action_space(MultiDiscrete(self.action_space_shape))
        observation_space = Box(self.vec_obs_space)
        self.model = create_model(self.cfg, self.device, action_space, observation_space)

        # Run inference
        self.model.eval()

    def is_hot_reload_enabled(self):
        return False