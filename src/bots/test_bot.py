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
import os


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
        """
        Setup for the action sequence with given actions in the scenario file.
        If the actions don't fill the whole scenario time an idle action is appended so log more packets
        """
        self.send_quick_chat(team_only=False, quick_chat=QuickChatSelection.Information_IGotIt)
        self.logger = Logger(self.scenario.name)

        acc_durations = 0.0

        control_step_list = []
        for action in self.scenario.actions:
            control_step_list.append(
                ControlStep(duration=action.duration, controls=self.get_action_controls(action.inputs)))
            acc_durations += action.duration

        if self.scenario.time > acc_durations:
            control_step_list.append(ControlStep(duration=self.scenario.time - acc_durations,
                                                 controls=SimpleControllerState()))

        self.active_sequence = Sequence(control_step_list)

    @staticmethod
    def get_physics(values) -> 'Physics':
        """
        Returns a physics object with location, rotation, velocity and angular_velocity parses from a corresponding
        object that has all the needed attributes. (Supplied by the json config)
        """
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
        """
        Setup of the initial game state. This is made in the bot because setting the initial game state in the training
        exercise lead to certain time offsets in logging.
        """
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
        """
        Returns a SimpleControllerState with the given inputs set to given values of the inputs object.
        The object should have a name attribute corresponding to the input name in the ControllerState and a specified
        value.
        """
        control = SimpleControllerState()
        for i in inputs:
            setattr(control, i.name, i.value)

        return control

    def load_config(self, config_object_header):
        settings_path = config_object_header['settings'].value
        with open(settings_path) as settings_file:
            settings = json.load(settings_file, object_hook=ScenarioTestObject)
            with open(settings.path_to_settings) as scenario_settings_file:
                scenario_settings = json.load(scenario_settings_file, object_hook=ScenarioTestObject)
                with open(os.path.join(scenario_settings.szenario_path, scenario_settings.file_name)) as scenario_file:
                    self.scenario = json.load(scenario_file, object_hook=ScenarioTestObject)

    @staticmethod
    def create_agent_configurations(config: ConfigObject):
        params = config.get_header(BOT_CONFIG_AGENT_HEADER)
        params.add_value('settings', str, default=None, description='Settings file that points to scenario settings')
