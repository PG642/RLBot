from os import stat
from pathlib import Path

import numpy as np
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket

from src.utils.drive import steer_toward_target
from src.utils.vec import Vec3, Location, Velocity, Quaternion, AngularVelocity

from src.models.onnx_model import ONNXModel

import torch
from src.neroRL.nn.actor_critic import create_actor_critic_model
from gym import spaces

from math import sin, cos

DISCRETE_ACTIONS = [-1, -0.5, 0, 0.5, 1]

class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """
        # Prepare vector observations and apply normalization
        car_physics = packet.game_cars[self.index].physics
        ball_physics = packet.game_ball.physics

        relativeLocation = Location(ball_physics.location) - Location(car_physics.location)
        relativeLocation = Location(relativeLocation)
        relativeLocation.to_unity_units()
        relativeLocation = relativeLocation.obs_normalized()

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
        policy, value, _, _ = self.model(None, torch.tensor(vec_obs, dtype=torch.float32, device=self.device), None)

        print(list(relativeLocation))

        # Samplem actions
        actions = []
        # Sample action
        for action_dimension in policy:
            actions.append(action_dimension.sample())

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
        if actions[6] > 1:
            controls.roll = actions[1]
            controls.yaw = 0
        controls.jump = actions[7] > 0
        # controls.use_item = False
        return controls

    def load_config(self, config_object_header):
        model_path = config_object_header['model_path'].value
        if model_path is not None:
            absolute_model_path = Path(__file__).absolute().parent / model_path
            # self.model = ONNXModel(absolute_model_path.__str__())
            self.create_and_load_model(absolute_model_path.__str__())

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('model_path', str, default=None,
                         description='Port to use for websocket communication')

    def create_and_load_model(self, path:str):
        # Determine the model's device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.is_available():
            torch.set_default_tensor_type("torch.cuda.FloatTensor")
        else:
            torch.set_default_tensor_type("torch.FloatTensor")
        # Load checkpoint
        checkpoint = torch.load(path)
        # Setup spaces
        self.vis_obs_space = None
        self.vec_obs_space = (23, )
        self.action_space_shape = (5, 5, 5, 3, 2, 2, 2, 2)
        # Create model
        self.model = create_actor_critic_model(checkpoint["config"]["model"], True, self.vis_obs_space,
                            self.vec_obs_space, self.action_space_shape,
                            checkpoint["config"]["model"]["recurrence"] if "recurrence" in checkpoint["config"]["model"] else None,
                            self.device)
        # Load model parameters
        self.model.load_state_dict(checkpoint["model"])
        # Run inference
        self.model.eval()
