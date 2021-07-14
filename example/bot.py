import time
from pathlib import Path

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket

from src.utils.ball_prediction_analysis import find_slice_at_time
from src.utils.boost_pad_tracker import BoostPadTracker
from src.utils.drive import steer_toward_target
from src.utils.sequence import Sequence, ControlStep
from src.utils.vec import Vec3

class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence: Sequence = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        if self.active_sequence is not None and not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls

        return self.sequence(packet)

    def sequence(self, packet):
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_InPosition)

        self.active_sequence = Sequence([
            ControlStep(duration=1.0, controls=SimpleControllerState(throttle=1.0, steer=1.0)),
            ControlStep(duration=1.0, controls=SimpleControllerState(throttle=1.0, steer=-1.0)),
        ])

        return self.active_sequence.tick(packet)

    def load_config(self, config_object_header):
        """the parameter from the bot config files can be used here"""
        self.value = config_object_header['name'].value

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        """the config header [Bot Parameters] has to be initilaized to allow its usage"""
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('model_path', str, default=None,
                         description='Port to use for websocket communication')