import os
import sys
cwd = os.getcwd()
sys.path.append(cwd + '/../../../..')

from math import pi
from dataclasses import dataclass, field

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.grading.grader import Grader
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.common_graders.compound_grader import CompoundGrader
from rlbot.matchcomms.common_uses.set_attributes_message import make_set_attributes_message
from rlbot.matchcomms.common_uses.reply import send_and_wait_for_replies

from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, UnitSystem, Velocity

shots = {
    "0": {"speed": 27.002470, "ball_pos": (-5.841396, 5.575093, -10.416420), "shoot_at": (3, 2.729553)},
    "1": {"speed": 24.304210, "ball_pos": (-9.996847, 3.483109, -10.859030), "shoot_at": (3, -1.321984)},
    "2": {"speed": 33.576840, "ball_pos": (-4.148786, 10.903650, -21.07715), "shoot_at": (3, 2.396912)},
    "3": {"speed": 24.745290, "ball_pos": (-8.286172, 2.553209, 2.56854300), "shoot_at": (3, -1.240129)},
    "4": {"speed": 33.840110, "ball_pos": (-2.429834, 2.662836, -13.123460), "shoot_at": (3, -0.863549)},
    "5": {"speed": 30.197650, "ball_pos": (-6.595964, 7.245919, -6.2391360), "shoot_at": (3, 5.791491)},
    "6": {"speed": 28.216090, "ball_pos": (-0.732091, 11.361090, -20.92138), "shoot_at": (3, 3.738999)},
    "7": {"speed": 26.982800, "ball_pos": (-4.902099, 4.571924, -11.713150), "shoot_at": (3, -0.495453)},
    "8": {"speed": 32.742650, "ball_pos": (-9.057829, 10.233490, -21.82253), "shoot_at": (3, 2.552792)},
    "9": {"speed": 32.429900, "ball_pos": (-3.168240, 9.440445, 20.3865500), "shoot_at": (3, -4.054292)},
    "2000": {"speed": 23.475070, "ball_pos": (-0.956915, 7.523063, -7.0051260), "shoot_at": (3, -2.542238)},
    "2001": {"speed": 26.165200, "ball_pos": (-6.953257, 3.420645, -21.523570), "shoot_at": (3, 1.916244)},
    "2002": {"speed": 24.587460, "ball_pos": (-2.659301, 6.675485, -4.3322500), "shoot_at": (3, 2.884336)},
    "2003": {"speed": 29.421850, "ball_pos": (-8.706933, 3.445635, -10.593730), "shoot_at": (3, -1.690832)},
    "2004": {"speed": 20.623810, "ball_pos": (-4.410801, 6.122281, -17.402820), "shoot_at": (3, 2.726788)},
    "2005": {"speed": 23.887970, "ball_pos": (-0.203606, 11.098390, 0.7585680), "shoot_at": (3, -1.980781)},
    "2006": {"speed": 26.057990, "ball_pos": (-6.225913, 3.953239, 24.6691900), "shoot_at": (3, 4.995790)},
    "2007": {"speed": 21.246770, "ball_pos": (-1.935451, 3.202096, 5.63275600), "shoot_at": (3, -5.377339)},
    "2008": {"speed": 37.599100, "ball_pos": (-7.936425, 5.167992, -24.016330), "shoot_at": (3, 3.565954)},
    "2009": {"speed": 39.123190, "ball_pos": (-3.639012, 8.417792, 4.32608400), "shoot_at": (3, 1.813753)},
    "3000": {"speed": 50, "ball_pos": (-0.956915, 7.523063, -7.0051260), "shoot_at": (3, -2.542238)},
    "3001": {"speed": 49, "ball_pos": (-6.953257, 3.420645, -21.523570), "shoot_at": (3, 1.916244)},
    "3002": {"speed": 48, "ball_pos": (-2.659301, 6.675485, -4.3322500), "shoot_at": (3, 2.884336)},
    "3003": {"speed": 47, "ball_pos": (-8.706933, 3.445635, -10.593730), "shoot_at": (3, -1.690832)},
    "3004": {"speed": 46, "ball_pos": (-4.410801, 6.122281, -17.402820), "shoot_at": (3, 2.726788)},
    "3005": {"speed": 45, "ball_pos": (-0.203606, 11.098390, 0.7585680), "shoot_at": (3, -1.980781)},
    "3006": {"speed": 44, "ball_pos": (-6.225913, 3.953239, 24.6691900), "shoot_at": (3, 4.995790)},
    "3007": {"speed": 43, "ball_pos": (-1.935451, 3.202096, 5.63275600), "shoot_at": (3, -5.377339)},
    "3008": {"speed": 42, "ball_pos": (-7.936425, 5.167992, -24.016330), "shoot_at": (3, 3.565954)},
    "3009": {"speed": 41, "ball_pos": (-3.639012, 8.417792, 4.32608400), "shoot_at": (3, 1.813753)},
}

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
    shot:int = 0
    repetition:int = 0
    path:str = "blank"

    def on_briefing(self):
        send_and_wait_for_replies(self.get_matchcomms(), [make_set_attributes_message(0, {'path': self.path}),])

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        ball_location = Location(shots[str(self.shot)]["ball_pos"][0], shots[str(self.shot)]["ball_pos"][1], shots[str(self.shot)]["ball_pos"][2], UnitSystem.UNITY)
        ball_location = ball_location.to_unreal_units()
        target = Location(-51, rng.uniform(3, 3), shots[str(self.shot)]["shoot_at"][1], UnitSystem.UNITY).to_unreal_units()
        ball_velocity = (target - ball_location).normalized() * shots[str(self.shot)]["speed"] * 100.0
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