from math import pi
from dataclasses import dataclass

from rlbottraining.common_exercises.common_base_exercises import GoalieExercise
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator


@dataclass
class BallRollingToGoalie(GoalieExercise):
    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(rng.uniform(-30, 30), -1500, 100),
                velocity=Vector3(0, rng.uniform(-500, -1000), 0),
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
                    jumped=False,
                    double_jumped=False,
                    boost_amount=0
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        BallRollingToGoalie('BallRollingToGoalie'),
    ]
