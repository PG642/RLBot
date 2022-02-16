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

def eval_shots(checkpoints, repetitions, shots):
    with er.use_or_create(None, er.setup_manager_context) as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        num_experiments = len(checkpoints) * len(shots) * repetitions
        flat_results = np.zeros(num_experiments)
        # Loop execercises
        playlist = make_default_playlist(checkpoints, repetitions, shots)
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
                flat_results[id] = 1
            else:
                print("GOAL")
    return flat_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the directory that contains checkpoints", default="./checkpoints/baseline_2/20220212-201235_50/")
    parser.add_argument("out", help="Name of the output file", default="results.res")
    args = parser.parse_args()
    path = args.path
    out = args.out
    repetitions = 3
    checkpoints = get_sorted_checkpoints(path)

    # Eval training
    training_shots = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    training_results = eval_shots(checkpoints, repetitions, training_shots)
    training_results = training_results.reshape(len(checkpoints), repetitions, len(training_shots))
    
    # Eval unknown
    unknown_shots = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009]
    unknown_results = eval_shots(checkpoints, repetitions, unknown_shots)
    unknown_results = training_results.reshape(len(checkpoints), repetitions, len(unknown_shots))

    # Eval out of dist
    # out_of_dist_shots = [3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009]
    # out_of_dist_results = eval_shots(checkpoints, repetitions, out_of_dist_shots)
    # out_of_dist_results = training_results.reshape(len(checkpoints), repetitions, len(out_of_dist_shots))

    # Output result file
    data_dict = {
        "train": training_results,
        "eval": unknown_results,
        # "out_of_dist": out_of_dist_results
    }
    pickle.dump(data_dict, open(out, "wb"))
