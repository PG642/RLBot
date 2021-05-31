from pathlib import Path

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.match_config import Team, PlayerConfig, MatchConfig
from rlbottraining.training_exercise import Playlist
import goalie_training as gt


def make_default_playlist() -> Playlist:
    exercises = [
        gt.BallRollingToGoalie('BallRollingToGoalie')
    ]
    for exercise in exercises:
        playerConfig = PlayerConfig.bot_config(
            Path(__file__).absolute().parent.parent / 'src' / 'bot.cfg', Team.BLUE)
        # This is needed to only reset the gamestate instead of resetting the game
        # Else the spawn_id will be random and each new spawn ID provokes a new gamestate
        playerConfig.spawn_id = 1
        exercise.match_config.player_configs = [
            playerConfig
        ]
    return exercises


if __name__ == "__main__":
    er.run_module(Path(__file__).absolute())
