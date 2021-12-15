from math import pi
from dataclasses import dataclass, field

from rlbot.matchconfig.match_config import Team
from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader

from src.graders.fail_graders import FailOnTimeout, FailOnBallPassingStriker
from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, UnitSystem


class StrikerGrader(CompoundGrader):
    def __init__(self, timeout_seconds=10.0, ally_team=0):
        super().__init__([
            PassOnGoalForAllyTeam(ally_team),
            FailOnTimeout(timeout_seconds),
            FailOnBallPassingStriker()
        ])


@dataclass
class GoalStrikingExercise(TrainingExercise):
    grader: Grader = field(default_factory=StrikerGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_location = Location(rng.uniform(30, 50), rng.uniform(0.17, 10), rng.uniform(-20, 20), UnitSystem.UNITY)\
            .to_unreal_units()
        car_start_position = Location(0, 0.17, rng.uniform(-15, 15), UnitSystem.UNITY).to_unreal_units()
        car_start_rotation = Rotator(0, pi / 2 + rng.uniform(-0.2, 0.2), 0)
        target = Location(rng.uniform(10, 30), rng.uniform(0, 7), car_start_position.z, UnitSystem.UNITY)\
            .to_unreal_units()
        ball_velocity = (target - ball_location).normalized() * rng.uniform(500, 1000)
        return GameState(
            ball=BallState(physics=Physics(
                location=ball_location.to_game_state_vector(),
                velocity=ball_velocity.to_game_state_vector(),
                angular_velocity=Vector3(0, 0, 0)
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=car_start_position.to_game_state_vector(),
                        rotation=car_start_rotation,
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    ),
                    boost_amount=32
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        GoalStrikingExercise('GoalStrikingExercise'),
    ]
