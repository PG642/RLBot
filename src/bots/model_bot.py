from pathlib import Path

import numpy as np
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket

from src.utils.drive import steer_toward_target
from src.utils.vec import Vec3, Location, Velocity, Quaternion, AngularVelocity

from src.models.onnx_model import ONNXModel

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

        car_physics = packet.game_cars[self.index].physics
        ball_physics = packet.game_ball.physics

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

        # get input shape of model and set batch size to one
        input_shape = self.model.get_input_shape()
        input_shape[0] = 1

        data = np.zeros(shape=input_shape, dtype=np.float32)
        data[0, 0:3] = list(car_location)
        data[0, 3:7] = list(car_rotation)
        data[0, 7:10] = list(car_velocity)
        data[0, 10:13] = list(car_angular_velocity)
        data[0, 13:16] = list(ball_location)
        data[0, 16:19] = list(ball_velocity)
        data[0, 19] = boost

        output = self.model.run(data)
        output = output[0].tolist()[0]

        controls = SimpleControllerState()
        if self.model.is_multi_discrete:
            controls.throttle = DISCRETE_ACTIONS[output[0]]
            controls.steer = DISCRETE_ACTIONS[output[1]]
            controls.yaw = DISCRETE_ACTIONS[output[1]]
            controls.pitch = DISCRETE_ACTIONS[output[2]]
            if output[3] == 0:
                controls.roll = -1
            elif output[3] == 2:
                controls.roll = 1
            else:
                controls.roll = 0
            controls.boost = output[4] > 0
            controls.handbrake = output[5] > 0
            if output[6] > 1:
                controls.roll = output[1]
                controls.yaw = 0
            controls.jump = output[7] > 0
        elif self.model.is_continuous:
            controls.throttle = output[0]
            controls.steer = output[1]
            controls.yaw = output[1]
            controls.pitch = output[2]
            controls.roll = 0
            if output[3] > 0:
                controls.roll = -1
            elif output[3] < 0:
                controls.roll = 1
            if output[6] > 0:
                controls.roll = output[1]
                controls.yaw = 0
            controls.boost = output[4] > 0
            controls.handbrake = output[5] > 0
            if output[6] > 1:
                controls.roll = output[1]
                controls.yaw = 0
            controls.jump = output[7] > 0

        # controls.use_item = False

        return controls

    def load_config(self, config_object_header):
        model_path = config_object_header['model_path'].value
        if model_path is not None:
            absolute_model_path = Path(__file__).absolute().parent / model_path
            self.model = ONNXModel(absolute_model_path.__str__())

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('model_path', str, default=None,
                         description='Port to use for websocket communication')
