import os
import sys
cwd = os.getcwd()
sys.path.append(cwd + '/../../..')

from math import pi
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader

from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, UnitSystem, Velocity


class GoalieGrader(CompoundGrader):
    def __init__(self, timeout_seconds=10.0, ally_team=0):
        super().__init__([
            PassOnBallGoingAwayFromGoal(ally_team),
            PassOnGoalForAllyTeam(ally_team),
            PassOnTimeout(timeout_seconds),
        ])


@dataclass
class BallRollingToGoalie(TrainingExercise):
    grader: Grader = field(default_factory=GoalieGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_location = Location(rng.uniform(-10, 0), rng.uniform(1, 12), rng.uniform(-30, 30), UnitSystem.UNITY)\
            .to_unreal_units()
        target = Location(-51, rng.uniform(3, 3), rng.uniform(-7, 7), UnitSystem.UNITY).to_unreal_units()
        ball_velocity = (target - ball_location).normalized() * rng.uniform(2000, 4000)
        return GameState(
            ball=BallState(physics=Physics(
                location=ball_location.to_game_state_vector(),
                velocity=ball_velocity.to_game_state_vector(),
                angular_velocity=Vector3(0, 0, 0)
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, -5300, 0),
                        rotation=Rotator(0, pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    ),
                    boost_amount=32
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        BallRollingToGoalie('BallRollingToGoalie'),
    ]
