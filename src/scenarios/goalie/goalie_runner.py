from pathlib import Path

import os
import argparse
import numpy as np
import rlbot
import rlbottraining.exercise_runner as er
from rlbot.training.training import Pass
import pickle

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

# create default match config
match_config = make_match_config()

def make_default_playlist(checkpoints, repetitions, shot_ids) -> Playlist:
    exercises = []
    for checkpoint in checkpoints:
        for repetition in range(repetitions):
            for id in shot_ids:
                ex = BallRollingToGoalie("save shot: " + str(id), path=checkpoint, repetition=repetition, shot=id)
                # ex.match_config = make_match_config()
                ex.match_config = match_config
                exercises.append(ex)
    return exercises

def get_sorted_checkpoints(dirpath):
    """Generates the full file paths to each checkpoint and sorts them alphabetically.

    Arguments:
        dirpath {string} -- Path to the directory containing the checkpoints

    Returns:
        {list} -- List that containts the full file path to each checkpoint
    """
    a = [s for s in os.listdir(dirpath)
         if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=lambda s: os.path.getmtime(os.path.join(dirpath, s)))
    for i, f in enumerate(a):
        a[i] = os.path.abspath(os.path.join(dirpath, f))
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the directory that contains checkpoints", default="./checkpoints/baseline_2/20220212-201235_50/")
    args = parser.parse_args()
    path = args.path
    repetitions = 3
    training_shots = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    checkpoints = get_sorted_checkpoints(path)
    num_experiments = len(checkpoints) * len(training_shots) * repetitions

    with er.use_or_create(None, er.setup_manager_context) as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        training_results = np.zeros((len(checkpoints), repetitions, len(training_shots))) # checkpoints, repetitions, seeds
        flat_results = np.zeros(num_experiments)
        # Loop execercises
        playlist = make_default_playlist(checkpoints, repetitions, training_shots)
        wrapped_exercises = [er.TrainingExerciseAdapter(ex) for ex in playlist]
        for id, rlbot_result in enumerate(er.rlbot_run_exercises(setup_manager, wrapped_exercises, seed=0, reload_agent=False)):
            result = er.ExerciseResult(
                grade=rlbot_result.grade,
                exercise=rlbot_result.exercise.exercise,  # unwrap the TrainingExerciseAdapter.
                reproduction_info=er.ReproductionInfo(
                    seed=0,
                    playlist_index=id,
                )
            )
            # Store grade
            if isinstance(result.grade, Pass):
                print("SAVE")
                flat_results = 1
            else:
                print("GOAL")

    training_results = flat_results.reshape(len(checkpoints), repetitions, len(training_shots))
    pickle.dump( training_results, open( "training_results.p", "wb" ) )
