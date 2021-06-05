from dataclasses import dataclass
from typing import Mapping, Optional, Union

from rlbot.training.training import Pass, Fail, Grade
from rlbottraining.grading.grader import Grader, TrainingTickPacket
from rlbottraining.history.metric import Metric


class WrongGoalFail(Fail):
    def __repr__(self):
        return f'{super().__repr__()}: Ball went into the wrong goal.'


@dataclass
class PassOnGoalForAllyTeam(Grader):
    """
    Terminates the Exercise when any goal is scored.
    Returns a Pass iff the goal was for ally_team,
    otherwise returns a Fail.
    """

    ally_team: int  # The team ID, as in game_datastruct.PlayerInfo.team
    init_score: Optional[Mapping[int, int]] = None  # team_id -> score

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Union[Pass, WrongGoalFail]]:
        score = {
            team.team_index: team.score
            for team in tick.game_tick_packet.teams
        }

        # Initialize or re-initialize due to some major change in the tick packet.
        if (
            self.init_score is None
            or score.keys() != self.init_score.keys()
            or any(score[t] < self.init_score[t] for t in self.init_score)
        ):
            self.init_score = score
            return

        scoring_team_id = None
        for team_id in self.init_score:
            # team score value has increased
            if self.init_score[team_id] < score[team_id]:
                assert scoring_team_id is None, "Only one team should score per tick."
                scoring_team_id = team_id

        if scoring_team_id is not None:
            return Pass() if scoring_team_id == self.ally_team else WrongGoalFail()


class PassOnBallGoingAwayFromGoal(Grader):
    """
    Returns Pass() iff a player on the ally team prevents a goal
    and triggers the in-game "save" event.
    Never returns a Fail().
    """

    # Prevent false positives which might be caused by two bots touching the ball at basically the same time.
    REQUIRED_CONSECUTIVE_TICKS = 20

    def __init__(self, ally_team: int):
        """
        :param ally_team: number equal to game_datastruct.PlayerInfo.team.
        """
        self.ally_team = ally_team
        self.consequtive_good_ticks = 0

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Union[Pass, WrongGoalFail]]:
        to_own_goal = 1 if self.ally_team == 0 else -1
        if tick.game_tick_packet.game_ball.physics.velocity.y * to_own_goal > 0:
            self.consequtive_good_ticks += 1
        else:
            self.consequtive_good_ticks = 0

        if self.consequtive_good_ticks >= self.REQUIRED_CONSECUTIVE_TICKS:
            return Pass()


class FailOnTimeout(Grader):
    """Fails the exercise if we take too long."""

    class FailDueToTimeout(Fail):
        def __init__(self, max_duration_seconds):
            self.max_duration_seconds = max_duration_seconds

        def __repr__(self):
            return f'{super().__repr__()}: Timeout: Took longer than {self.max_duration_seconds} seconds.'

    def __init__(self, max_duration_seconds: float):
        self.max_duration_seconds = max_duration_seconds
        self.initial_seconds_elapsed: float = None
        self.measured_duration_seconds: float = None

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Grade]:
        seconds_elapsed = tick.game_tick_packet.game_info.seconds_elapsed
        if self.initial_seconds_elapsed is None:
            self.initial_seconds_elapsed = seconds_elapsed
        self.measured_duration_seconds = seconds_elapsed - self.initial_seconds_elapsed
        if self.measured_duration_seconds > self.max_duration_seconds:
            return self.FailDueToTimeout(self.max_duration_seconds)

    @dataclass(frozen=True)
    class TimeoutMetric(Metric):
        max_duration_seconds: float
        initial_seconds_elapsed: float
        measured_duration_seconds: float

    def get_metric(self) -> Optional[Metric]:
        return FailOnTimeout.TimeoutMetric(
            self.max_duration_seconds,
            self.initial_seconds_elapsed,
            self.measured_duration_seconds,
        )


class PassOnTimeout(FailOnTimeout):
    """Passes the exercise if we manage not to fail until here."""

    class PassDueToTimeout(Pass):
        def __init__(self, max_duration_seconds):
            self.max_duration_seconds = max_duration_seconds

        def __repr__(self):
            return f'{super().__repr__()}: Timeout: Survived {self.max_duration_seconds} seconds.'

    def on_tick(self, tick: TrainingTickPacket) -> Optional[Grade]:
        grade_maybe = super().on_tick(tick)
        if isinstance(grade_maybe, FailOnTimeout.FailDueToTimeout):
            grade_maybe = self.PassDueToTimeout(self.max_duration_seconds)
        return grade_maybe
