from pathlib import Path

from rlbot.matchconfig.match_config import Team, PlayerConfig, MatchConfig
from rlbottraining.training_exercise import Playlist
from goalie_training import BallRollingToGoalie


def make_default_playlist() -> Playlist:
    exercises = [
        BallRollingToGoalie('BallRollingToGoalie')
    ]
    for exercise in exercises:
        exercise.match_config.player_configs = [
            PlayerConfig.bot_config(
                Path(__file__).absolute().parent.parent / 'src' / 'bot.cfg', Team.BLUE)
        ]
    return exercises
