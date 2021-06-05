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

        car_location = Location(car_physics.location).convert(to_unity_units=True)
        car_velocity = Velocity(car_physics.velocity).convert(to_unity_units=True)
        car_rotation = Quaternion(car_physics.rotation).convert(to_unity_units=True)
        car_angular_velocity = AngularVelocity(car_physics.angular_velocity).convert(to_unity_units=True)
        ball_location = Location(ball_physics.location).convert(to_unity_units=True)
        ball_velocity = Velocity(ball_physics.velocity).convert(to_unity_units=True)

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

        output = self.model.run(data)
        output = output[0].tolist()[0]

        controls = SimpleControllerState()
        controls.throttle = output[0]
        controls.steer = max(min(20 * output[1], 1), -1)
        controls.yaw = output[1]
        controls.pitch = output[2]
        if output[3] > 0:
            controls.roll = 1
        elif output[3] < 0:
            controls.roll = -1
        else:
            controls.roll = 0
        controls.boost = True if output[4] > 0 else False
        controls.handbrake = True if output[5] > 0 else False
        # controls.jump = True if output[7] > 0 else False
        controls.use_item = False

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
