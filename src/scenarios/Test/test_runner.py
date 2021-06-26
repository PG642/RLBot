import configparser
import time
from pathlib import Path
import json

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
from rlbot.training.training import _setup_exercise, _grade_exercise
from test_training import TestExercise
from src.utils.scenario_test_object import ScenarioTestObject


def make_match_config():
    match_config = read_match_config_from_file(Path('test_match.cfg'))
    playerConfig = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'test_bot.cfg', Team.BLUE)
    match_config.player_configs = [
        playerConfig
    ]
    return match_config

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
    for exercise in exercises:
        exercise.match_config = match_config
    return exercises


if __name__ == "__main__":
    with er.setup_manager_context() as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        seed = er.infinite_seed_generator()
        playlist = make_default_playlist()

        exercise = [er.TrainingExerciseAdapter(ex) for ex in playlist]
        result_iter = er.rlbot_run_exercises(setup_manager, exercise, seed)

        #_setup_exercise(setup_manager.game_interface, exercise[0], seed)
        #setup_manager.reload_all_agents()
        #_grade_exercise(setup_manager.game_interface, exercise[0], seed)

        # time.sleep(10)

        for _ in result_iter:
            pass
    """python_file_with_playlist = Path(__file__).absolute()
    history_dir = None
    reload_policy = er.ReloadPolicy.NEVER
    render_policy = er.RenderPolicy.DEFAULT

    # load the playlist initially, keep trying if we fail
    playlist_factory = None
    playlist: Playlist = None
    while playlist is None:
        try:
            playlist_factory = er.load_default_playlist(python_file_with_playlist)
            playlist = playlist_factory()
        except Exception:
            er.traceback.print_exc()
            er.time.sleep(1.0)

    log = er.get_logger(er.LOGGER_ID)
    with er.setup_manager_context() as setup_manager:
        er.apply_render_policy(render_policy, setup_manager)

        playlist = playlist_factory()
        wrapped_exercises = [er.TrainingExerciseAdapter(ex) for ex in playlist]
        reload_agent = reload_policy != er.ReloadPolicy.NEVER
        seed = er.infinite_seed_generator()
        result_iter = er.rlbot_run_exercises(setup_manager, wrapped_exercises, seed, reload_agent=reload_agent)

        for i, rlbot_result in enumerate(result_iter):
            result = er.ExerciseResult(
                grade=rlbot_result.grade,
                exercise=rlbot_result.exercise.exercise,  # unwrap the TrainingExerciseAdapter.
                reproduction_info=er.ReproductionInfo(
                    seed=seed,
                    python_file_with_playlist=str(python_file_with_playlist.absolute()),
                    playlist_index=i,
                )
            )

            er.log_result(result, log)
            """
