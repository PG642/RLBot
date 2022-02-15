from pathlib import Path

import os
import argparse
import numpy as np
import rlbot
import rlbottraining.exercise_runner as er
from rlbot.training.training import Pass

from rlbot.matchconfig.conversions import read_match_config_from_file
from rlbot.matchconfig.match_config import Team, PlayerConfig
from rlbottraining.training_exercise import Playlist
from goalie_training import BallRollingToGoalie

current_checkpoint = None

def make_match_config():
    match_config = read_match_config_from_file(Path('goalie_match.cfg'))
    playerConfig = PlayerConfig.bot_config(
        Path(__file__).absolute().parent / 'goalie_bot.cfg', Team.BLUE)
    match_config.player_configs = [
        playerConfig
    ]
    return match_config


# match_config = make_match_config()


def make_default_playlist(shot_ids) -> Playlist:
    exercises = []
    for id in shot_ids:
        ex = BallRollingToGoalie("save shot: " + str(id), shot=id)
        ex.match_config = make_match_config()
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
        a[i] = os.path.join(dirpath, f)
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to the directory that contains checkpoints", default="./checkpoints/baseline_2/20220212-201235_50/")
    args = parser.parse_args()
    path = args.path

    checkpoints = get_sorted_checkpoints(path)

    with er.use_or_create(None, er.setup_manager_context) as setup_manager:
        er.apply_render_policy(er.RenderPolicy.DEFAULT, setup_manager)
        training_results = np.zeros((len(checkpoints), 3, 3)) # checkpoints, repetitions, seeds
        # Loop checkpoints
        for check, checkpoint in enumerate(checkpoints):
            current_checkpoint = checkpoint
            # Loop repetitions
            for rep in range(3):
                # Loop execercises
                training_shots = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                playlist = make_default_playlist(training_shots)
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
                        training_results[check, rep, id] = 1
                    else:
                        print("GOAL")

    print(training_results)
