from math import pi
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader

from src.graders.pass_graders import PassOnTimeout


class PlaygroundGrader(CompoundGrader):
    def __init__(self, timeout_seconds=10.0):
        super().__init__([
            PassOnTimeout(timeout_seconds),
        ])


@dataclass
class PlaygroundExercise(TrainingExercise):
    grader: Grader = field(default_factory=PlaygroundGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(0, 0, 100),
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0)
            )),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, -5800, 0),
                        rotation=Rotator(0, pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    )
                )
            },
        )


def make_default_playlist() -> Playlist:
    return [
        PlaygroundExercise('PlaygroundExercise'),
    ]
