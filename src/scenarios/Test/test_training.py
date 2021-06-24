from math import pi
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader

from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, Velocity, AngularVelocity, Quaternion
from src.utils.ScenarioTestObject import ScenarioTestObject


class TestGrader(CompoundGrader):
    def __init__(self, timeout_seconds=10.0):
        super().__init__([
            PassOnTimeout(timeout_seconds),
        ])


@dataclass
class TestExercise(TrainingExercise):
    scenario: ScenarioTestObject = field(default_factory=ScenarioTestObject)
    grader: Grader = field(default_factory=TestGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        start_values = self.scenario.startValues
        for values in start_values:
            if values.gameObject == 'car':
                car_position = Location(values.position.x, values.position.y, values.position.z)
                car_velocity = Velocity(values.velocity.x, values.velocity.y, values.velocity.z)
                car_angular_velocity = AngularVelocity(values.angularVelocity.x, values.angularVelocity.y,
                                                       values.angularVelocity.z)
                # TODO this does not rotate for 90 degree if we set it to 90 degree
                car_rotation = Rotator(values.rotation.x, values.rotation.y, -values.rotation.z)
            elif values.gameObject == 'ball':
                ball_position = Location(values.position.x, values.position.y, values.position.z)
                ball_velocity = Velocity(values.velocity.x, values.velocity.y, values.velocity.z)
                ball_angular_velocity = AngularVelocity(values.angularVelocity.x, values.angularVelocity.y,
                                                        values.angularVelocity.z)
                ball_rotation = Rotator(values.rotation.x, values.rotation.y, -values.rotation.z)

        return GameState(
            ball=BallState(
                physics=Physics(
                    location=ball_position.convert(to_unity_units=False).to_game_state_vector(),
                    rotation=ball_rotation,
                    velocity=ball_velocity.convert(to_unity_units=False).to_game_state_vector(),
                    angular_velocity=ball_angular_velocity.convert(to_unity_units=False).to_game_state_vector()
                )
            ),
            cars={
                0: CarState(
                    physics=Physics(
                        location=car_position.convert(to_unity_units=False).to_game_state_vector(),
                        rotation=car_rotation,
                        velocity=car_velocity.convert(to_unity_units=False).to_game_state_vector(),
                        angular_velocity=car_angular_velocity.convert(to_unity_units=False).to_game_state_vector()
                    )
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        TestExercise('TestExercise'),
    ]
