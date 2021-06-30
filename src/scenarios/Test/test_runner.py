import configparser
import json
from pathlib import Path

import rlbottraining.exercise_runner as er
from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist

from src.utils.scenario_test_object import ScenarioTestObject
from test_training import TestExercise


def make_match_config():
    result_match_config = read_match_config_from_file(Path('test_match.cfg'))
    player_config = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'test_bot.cfg', Team.BLUE)
    result_match_config.player_configs = [
        player_config
    ]
    return result_match_config


match_config = make_match_config()


def make_default_playlist() -> Playlist:
    config = configparser.ConfigParser()
    config.read('./test_bot.cfg')
    # scenarios = config["Bot Parameters"]["scenarios"]

    with open('./example.json') as file:
        scenario = json.load(file, object_hook=ScenarioTestObject)

    exercises = [
        TestExercise(name='TestExercise1', scenario=scenario)
    ]
    for e in exercises:
        e.match_config = match_config
    return exercises


if __name__ == "__main__":
    with er.setup_manager_context() as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        seed = er.infinite_seed_generator()
        playlist = make_default_playlist()

        exercise = [er.TrainingExerciseAdapter(ex) for ex in playlist]
        result_iter = er.rlbot_run_exercises(setup_manager, exercise, seed)

        for _ in result_iter:
            pass
