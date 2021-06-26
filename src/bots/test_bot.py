import json
import time
from pathlib import Path

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.structures.game_data_struct import GameTickPacket

from src.utils.sequence import Sequence, ControlStep
from src.utils.scenario_test_object import ScenarioTestObject
from src.utils.logger import Logger

class TestBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence: Sequence = None
        self.scenario = None
        self.logger = None
        print('Init')

    def __del__(self):
        self.logger.dump()

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        self.logger.log(packet)

        if self.active_sequence is None:
            return self.start_action_sequence(packet)

        # This is good to keep at the beginning of get_output. It will allow you to continue
        # any sequences that you may have started during a previous call to get_output.
        if not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls

        self.logger.dump()

    def start_action_sequence(self, packet):
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)

        control_step_list = []
        for action in self.scenario.actions:
            control_step_list.append(
                ControlStep(duration=action.duration, controls=self.get_action_controls(action.inputs)))

        self.active_sequence = Sequence(control_step_list)

        return self.active_sequence.tick(packet)

    @staticmethod
    def get_action_controls(inputs):
        control = SimpleControllerState()
        for i in inputs:
            setattr(control, i.name, i.value)

        return control

    def load_config(self, config_object_header):
        scenario = config_object_header['scenarios'].value
        with open(scenario) as file:
            self.scenario = json.load(file, object_hook=ScenarioTestObject)

        self.logger = Logger(self.scenario.name)

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('scenarios', str, default=None,
                         description='Scenario file.')
