import json

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState, BOT_CONFIG_AGENT_HEADER
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.parsing.custom_config import ConfigObject
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics
from rlbot.utils.structures.game_data_struct import GameTickPacket

from src.utils.sequence import Sequence, ControlStep
from src.utils.scenario_test_object import ScenarioTestObject
from src.utils.logger import Logger
from src.utils.vec import Location, Velocity, AngularVelocity, EulerAngles, UnitSystem


class TestBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence = None
        self.scenario = None
        self.logger = None

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        """
        This function will be called by the framework many times per second. This is where you can
        see the motion of the ball, etc. and return controls to drive your car.
        """

        if self.active_sequence is None:
            self.setup()
            return SimpleControllerState()

        if self.active_sequence is not None and not self.active_sequence.done:
            self.logger.log(packet)
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls

        if not self.logger.was_dumped:
            self.logger.dump()
        return SimpleControllerState()

    def setup(self):
        self.setup_game_state()
        self.setup_action_sequence()

    def setup_action_sequence(self):
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)
        self.logger = Logger(self.scenario.name)

        control_step_list = []
        for action in self.scenario.actions:
            control_step_list.append(
                ControlStep(duration=action.duration, controls=self.get_action_controls(action.inputs)))

        self.active_sequence = Sequence(control_step_list)

    @staticmethod
    def get_physics(values) -> 'Physics':
        position = Location(values.position.x, values.position.y, values.position.z, UnitSystem.UNITY)
        velocity = Velocity(values.velocity.x, values.velocity.y, values.velocity.z, UnitSystem.UNITY)
        angular_velocity = AngularVelocity(values.angularVelocity.x, values.angularVelocity.y, values.angularVelocity.z,
                                           UnitSystem.UNITY)
        rotation = EulerAngles(values.rotation.x, values.rotation.y, -values.rotation.z, UnitSystem.UNITY)
        return Physics(
            location=position.to_unreal_units().to_game_state_vector(),
            rotation=rotation.to_unreal_units().to_game_state_vector(),
            velocity=velocity.to_unreal_units().to_game_state_vector(),
            angular_velocity=angular_velocity.to_unreal_units().to_game_state_vector()
        )

    def setup_game_state(self):
        start_values = self.scenario.startValues
        gs = GameState()
        gs.cars = dict()
        for values in start_values:
            if values.gameObject == 'car':
                gs.cars[len(gs.cars)] = CarState(physics=self.get_physics(values))
            elif values.gameObject == 'ball':
                gs.ball = BallState(physics=self.get_physics(values))

        self.set_game_state(gs)

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

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('scenarios', str, default=None,
                         description='Scenario file.')
