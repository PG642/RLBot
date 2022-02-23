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
from rlbot.matchcomms.common_uses.set_attributes_message import make_set_attributes_message
from rlbot.matchcomms.common_uses.reply import send_and_wait_for_replies

from src.graders.pass_graders import PassOnBallGoingAwayFromGoal, PassOnGoalForAllyTeam, PassOnTimeout
from src.utils.vec import Vec3, Location, UnitSystem, Velocity

shots = {
    "0": {"speed": 7.084905, "agent_pos": (25.000000, 0.170000, -2.524189), "ball_pos": (45.000000, 2.979179, -6.533014)},
    "1": {"speed": 6.216718, "agent_pos": (25.000000, 0.170000, -14.990540), "ball_pos": (45.000000, 2.957048, -5.920912)},
    "2": {"speed": 7.013624, "agent_pos": (25.000000, 0.170000, 2.553644), "ball_pos": (45.000000, 2.446143, 6.429302)},
    "3": {"speed": 6.234258, "agent_pos": (25.000000, 0.170000, -9.858517), "ball_pos": (45.000000, 3.628427, 5.974151)},
    "4": {"speed": 6.314954, "agent_pos": (25.000000, 0.170000, 7.710499), "ball_pos": (45.000000, 2.843827, 5.304496)},
    "5": {"speed": 7.741034, "agent_pos": (25.000000, 0.170000, -4.787891), "ball_pos": (45.000000, 3.188043, -5.374331)},
    "6": {"speed": 7.301214, "agent_pos": (25.000000, 0.170000, 12.803730), "ball_pos": (45.000000, 2.453931, 5.613322)},
    "7": {"speed": 6.393831, "agent_pos": (25.000000, 0.170000, 0.293704), "ball_pos": (45.000000, 2.914342, -5.663524)},
    "8": {"speed": 7.047027, "agent_pos": (25.000000, 0.170000, -12.173490), "ball_pos": (45.000000, 2.408874, 6.879426)},
    "9": {"speed": 5.631223, "agent_pos": (25.000000, 0.170000, 5.495281), "ball_pos": (45.000000, 4.519328, 5.658399)},
    "2000": {"speed": 5.955235, "agent_pos": (25.000000, 0.170000, 12.129260), "ball_pos": (45.000000, 3.149744, 5.530918)},
    "2001": {"speed": 6.910624, "agent_pos": (25.000000, 0.170000, -5.859770), "ball_pos": (45.000000, 2.423821, 6.017602)},
    "2002": {"speed": 7.118073, "agent_pos": (25.000000, 0.170000, 7.022098), "ball_pos": (45.000000, 3.283388, -5.839446)},
    "2003": {"speed": 6.137679, "agent_pos": (25.000000, 0.170000, -11.120800), "ball_pos": (45.000000, 2.970313, 6.673732)},
    "2004": {"speed": 7.084312, "agent_pos": (25.000000, 0.170000, 1.767595), "ball_pos": (45.000000, 2.629859, 6.165126)},
    "2005": {"speed": 6.075547, "agent_pos": (25.000000, 0.170000, 14.389180), "ball_pos": (45.000000, 3.537929, 6.239063)},
    "2006": {"speed": 7.570527, "agent_pos": (25.000000, 0.170000, -3.677740), "ball_pos": (45.000000, 4.733460, -5.759993)},
    "2007": {"speed": 5.347713, "agent_pos": (25.000000, 0.170000, 9.193646), "ball_pos": (45.000000, 3.781638, 6.554876)},
    "2008": {"speed": 7.264133, "agent_pos": (25.000000, 0.170000, -8.809277), "ball_pos": (45.000000, 2.299183, 6.825105)},
    "2009": {"speed": 6.888661, "agent_pos": (25.000000, 0.170000, 4.082965), "ball_pos": (45.000000, 3.716304, 6.757848)},
    "3000": {"speed": 5.955235, "agent_pos": (20.000000, 0.170000, -2), "ball_pos": (45.000000, 3.149744, 5.530918)},
    "3001": {"speed": 6.910624, "agent_pos": (21.000000, 0.170000, -1), "ball_pos": (45.000000, 2.423821, 6.017602)},
    "3002": {"speed": 7.118073, "agent_pos": (22.000000, 0.170000, 0), "ball_pos": (45.000000, 3.283388, -5.839446)},
    "3003": {"speed": 6.910624, "agent_pos": (23.000000, 0.170000, 1), "ball_pos": (45.000000, 2.970313, 6.673732)},
    "3004": {"speed": 5.955235, "agent_pos": (24.000000, 0.170000, 2), "ball_pos": (45.000000, 2.629859, 6.165126)},
    "3005": {"speed": 6.137679, "agent_pos": (20.000000, 0.170000, -16), "ball_pos": (45.000000, 3.537929, 6.239063)},
    "3006": {"speed": 7.084312, "agent_pos": (21.000000, 0.170000, 16), "ball_pos": (45.000000, 4.733460, -5.759993)},
    "3007": {"speed": 7.570527, "agent_pos": (22.000000, 0.170000, -17), "ball_pos": (45.000000, 3.781638, 6.554876)},
    "3008": {"speed": 6.075547, "agent_pos": (23.000000, 0.170000, 17), "ball_pos": (45.000000, 2.299183, 6.825105)},
    "3009": {"speed": 6.888661, "agent_pos": (24.000000, 0.170000, 18), "ball_pos": (45.000000, 3.716304, 6.757848)},
}

class GoalieGrader(CompoundGrader):
    def __init__(self, timeout_seconds=5.0, ally_team=1):
        super().__init__([
            PassOnGoalForAllyTeam(ally_team),
            PassOnTimeout(timeout_seconds),
        ])

@dataclass
class StrikerEasy(TrainingExercise):
    grader: Grader = field(default_factory=GoalieGrader)
    shot:int = 0
    repetition:int = 0
    path:str = "blank"

    def on_briefing(self):
        send_and_wait_for_replies(self.get_matchcomms(), [make_set_attributes_message(0, {'path': self.path}),])

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        agent_location = Location(shots[str(self.shot)]["agent_pos"][0], shots[str(self.shot)]["agent_pos"][1], shots[str(self.shot)]["agent_pos"][2], UnitSystem.UNITY)
        agent_location = agent_location.to_unreal_units()
        ball_location = Location(shots[str(self.shot)]["ball_pos"][0], shots[str(self.shot)]["ball_pos"][1], shots[str(self.shot)]["ball_pos"][2], UnitSystem.UNITY)
        ball_location = ball_location.to_unreal_units()
        target = Location(shots[str(self.shot)]["ball_pos"][0], 0.0, 0.0, UnitSystem.UNITY).to_unreal_units()
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
                        location=agent_location.to_game_state_vector(),
                        rotation=Rotator(0, pi / 2, 0),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)
                    ),
                    boost_amount=100
                )
            },
        )