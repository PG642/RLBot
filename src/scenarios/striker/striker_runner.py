from pathlib import Path

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
from striker_training import GoalStrikingExercise


def make_match_config():
    match_config_local = read_match_config_from_file(Path('striker_match.cfg'))
    player_config = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'striker_bot.cfg', Team.BLUE)
    match_config_local.player_configs = [
        player_config
    ]
    return match_config_local


match_config = make_match_config()


def make_default_playlist() -> Playlist:
    exercises = [
        GoalStrikingExercise('GoalStriking')
    ]
    for exercise in exercises:
        exercise.match_config = match_config
    return exercises


if __name__ == "__main__":
    er.run_module(Path(__file__).absolute(), reload_policy=er.ReloadPolicy.EACH_EXERCISE)
