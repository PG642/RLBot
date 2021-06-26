from math import pi
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader

from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, Velocity, AngularVelocity, EulerAngles
from src.utils.scenario_test_object import ScenarioTestObject


class TestGrader(CompoundGrader):
    def __init__(self, timeout_seconds=100.0):
        super().__init__([
            PassOnTimeout(timeout_seconds),
        ])


@dataclass
class TestExercise(TrainingExercise):
    scenario: ScenarioTestObject = field(default_factory=ScenarioTestObject)
    grader: Grader = field(default_factory=TestGrader)

    def __post_init__(self):
        self.grader = TestGrader(self.scenario.time + 1)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState()


def make_default_playlist() -> Playlist:
    return [
        TestExercise('TestExercise'),
    ]
