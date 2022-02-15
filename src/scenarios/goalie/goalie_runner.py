from pathlib import Path

import rlbottraining.exercise_runner as er

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
from goalie_training import BallRollingToGoalie


def make_match_config():
    match_config = read_match_config_from_file(Path('goalie_match.cfg'))
    playerConfig = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'goalie_bot.cfg', Team.BLUE)
    match_config.player_configs = [
        playerConfig
    ]
    return match_config


match_config = make_match_config()


def make_default_playlist() -> Playlist:
    shot_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009]

    exercises = []
    for id in shot_ids:
        for repetition in range(3):
            exercises.append(BallRollingToGoalie("save shot: " + str(id) + " rep: " + str(repetition) , shot=id))

    for exercise in exercises:
        exercise.match_config = match_config
    return exercises


if __name__ == "__main__":
    playlist_factory = make_default_playlist()
    playlist: Playlist = None

    with er.use_or_create(None, er.setup_manager_context) as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        playlist = make_default_playlist()
        wrapped_exercises = [er.TrainingExerciseAdapter(ex) for ex in playlist]
        seed = er.infinite_seed_generator()
        for i, rlbot_result in enumerate(
                er.rlbot_run_exercises(setup_manager, wrapped_exercises, seed=seed, reload_agent=True)):
            print(er.ExerciseResult(
                grade=rlbot_result.grade,
                exercise=rlbot_result.exercise.exercise,  # unwrap the TrainingExerciseAdapter.
                reproduction_info=er.ReproductionInfo(
                    seed=seed,
                    playlist_index=i,
                )
            ))
