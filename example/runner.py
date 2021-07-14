from pathlib import Path

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
from training import PlaygroundExercise


def make_match_config():
    match_config = read_match_config_from_file(Path('match.cfg'))
    playerConfig = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'bot.cfg', Team.BLUE)
    match_config.player_configs = [
        playerConfig
    ]
    return match_config


match_config = make_match_config()


def make_default_playlist() -> Playlist:
    exercises = [
        PlaygroundExercise('PlaygroundExercise')
    ]
    for exercise in exercises:
        exercise.match_config = match_config
    return exercises


if __name__ == "__main__":
    er.run_module(Path(__file__).absolute(), reload_policy=er.ReloadPolicy.NEVER)
