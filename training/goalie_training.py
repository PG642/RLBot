from math import pi, pow, sqrt
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader
from base_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout

from src.util.vec import Vec3


class GoalieGrader(CompoundGrader):
    def __init__(self, timeout_seconds=10.0, ally_team=0):
        super().__init__([
            PassOnBallGoingAwayFromGoal(ally_team),
            PassOnGoalForAllyTeam(ally_team),
            PassOnTimeout(timeout_seconds),
        ])


def norm(vec):
    norm = sqrt(pow(vec.x, 2)+pow(vec.y, 2) + pow(vec.z, 2))
    return Vector3(vec.x / norm, vec.y/norm, vec.z/norm)


def minus(vec1, vec2):
    return Vector3(vec1.x - vec2.x, vec1.y - vec2.y, vec1.z - vec2.z)


def times(vec, scalar):
    return Vector3(vec.x * scalar, vec.y * scalar, vec.z * scalar)


@dataclass
class BallRollingToGoalie(TrainingExercise):
    grader: Grader = field(default_factory=GoalieGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        target = Vec3(rng.uniform(-800, 800), -5800, 0)
        ball_location = Vec3(rng.uniform(-800, 800), 0, 100)
        ball_velocity = (target - ball_location).normalized() * rng.uniform(3000, 3000)
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(ball_location.x, ball_location.y, ball_location.z),
                velocity=Vector3(ball_velocity.x, ball_velocity.y, ball_velocity.z),
                angular_velocity=Vector3(0, 0, 0)
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, -5800, 0),
                        rotation=Rotator(0, pi/2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    )
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        BallRollingToGoalie('BallRollingToGoalie'),
    ]
