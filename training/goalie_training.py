from math import pi, pow, sqrt
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader
from base_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from utility.math import Vec3


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
        target = Vec3(rng.uniform(-800, 800), -5800, 0)
        ball_location = Vec3(rng.uniform(-800, 800), 0, 100)
        ball_velocity = (target - ball_location).normalize() * \
            rng.uniform(1500, 1800)
        return GameState(
            ball=BallState(physics=Physics(
                location=ball_location.toRLVec(),
                velocity=ball_velocity.toRLVec(),
                angular_velocity=Vector3(0, 0, 0)
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, -5800, 0),
                        rotation=Rotator(0, pi/2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    ),
                    boost_amount=0
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        BallRollingToGoalie('BallRollingToGoalie'),
    ]
