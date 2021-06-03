from pathlib import Path

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
import goalie_training as gt



def make_match_config():
    match_config = read_match_config_from_file(Path('goalie_match.cfg'))
    playerConfig = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'goalie_bot.cfg', Team.BLUE)
    # This is needed to only reset the gamestate instead of resetting the game
    # Else the spawn_id will be random and each new spawn ID provokes a new gamestate
    # playerConfig.spawn_id = 1
    match_config.player_configs = [
        playerConfig
    ]
    return match_config

match_config = make_match_config()

def make_default_playlist() -> Playlist:
    exercises = [
        gt.BallRollingToGoalie('BallRollingToGoalie')
    ]
    for exercise in exercises:
        exercise.match_config = match_config
    return exercises


if __name__ == "__main__":
    er.run_module(Path(__file__).absolute(), reload_policy=er.ReloadPolicy.EACH_EXERCISE)
