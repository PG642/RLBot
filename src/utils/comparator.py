import json
import os
import pandas as pd


'''
specifies a path to the test result json files and saves the loaded data
'''
class Comparator:
    def __init__(self):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, '../scenarios/')
        self.rlbot_results = self.load_test_results(path, 'Neuer_Test0.json')
        self.roboleague_results = self.load_test_results(path, 'Neuer_Test0.json')

'''
return true for every frame where the difference between the rlbot and roboleague data is within rounding error
'''
def compare(rlbot_dataframe, roboleague_dataframe):
    return (rlbot_dataframe - roboleague_dataframe).abs() < 0.0001

'''
returns the difference between the rlbot and the roboleague data for each frame
'''
def difference(rlbot_dataframe, roboleague_dataframe):
    return rlbot_dataframe - roboleague_dataframe

'''
returns true if rlbot and roboleague dataframe are equal in all recorded frames
'''
def equal(rlbot_dataframe, roboleague_dataframe):
    return compare(rlbot_dataframe, roboleague_dataframe).all()

'''
loads the test_results from a json at the specified path into pandas dataframes structured in dictionaries
'''
def load_test_results(path, filename):
    data = path + filename
    with open(data, 'rb') as fb:
        results_json = json.load(fb)

    frames = results_json['frames']

    car_location = pd.DataFrame([])
    car_location['x'] = [frame['game_cars'][0]['physics']['location']['x'] for frame in frames]
    car_location['y'] = [frame['game_cars'][0]['physics']['location']['y'] for frame in frames]
    car_location['z'] = [frame['game_cars'][0]['physics']['location']['z'] for frame in frames]

    car_rotation = pd.DataFrame([])
    car_rotation['pitch'] = [frame['game_cars'][0]['physics']['rotation']['pitch'] for frame in frames]
    car_rotation['yaw'] = [frame['game_cars'][0]['physics']['rotation']['yaw'] for frame in frames]
    car_rotation['roll'] = [frame['game_cars'][0]['physics']['rotation']['roll'] for frame in frames]

    car_velocity = pd.DataFrame([])
    car_velocity['x'] = [frame['game_cars'][0]['physics']['velocity']['x'] for frame in frames]
    car_velocity['y'] = [frame['game_cars'][0]['physics']['velocity']['y'] for frame in frames]
    car_velocity['z'] = [frame['game_cars'][0]['physics']['velocity']['z'] for frame in frames]

    car_angular_velocity = pd.DataFrame([])
    car_angular_velocity['x'] = [frame['game_cars'][0]['physics']['angular_velocity']['x'] for frame in frames]
    car_angular_velocity['y'] = [frame['game_cars'][0]['physics']['angular_velocity']['y'] for frame in frames]
    car_angular_velocity['z'] = [frame['game_cars'][0]['physics']['angular_velocity']['z'] for frame in frames]

    ball_location = pd.DataFrame([])
    ball_location['x'] = [frame['game_ball']['physics']['location']['x'] for frame in frames]
    ball_location['y'] = [frame['game_ball']['physics']['location']['y'] for frame in frames]
    ball_location['z'] = [frame['game_ball']['physics']['location']['z'] for frame in frames]

    ball_rotation = pd.DataFrame([])
    ball_rotation['pitch'] = [frame['game_ball']['physics']['rotation']['pitch'] for frame in frames]
    ball_rotation['yaw'] = [frame['game_ball']['physics']['rotation']['yaw'] for frame in frames]
    ball_rotation['roll'] = [frame['game_ball']['physics']['rotation']['roll'] for frame in frames]

    ball_velocity = pd.DataFrame([])
    ball_velocity['x'] = [frame['game_ball']['physics']['velocity']['x'] for frame in frames]
    ball_velocity['y'] = [frame['game_ball']['physics']['velocity']['y'] for frame in frames]
    ball_velocity['z'] = [frame['game_ball']['physics']['velocity']['z'] for frame in frames]

    ball_angular_velocity = pd.DataFrame([])
    ball_angular_velocity['x'] = [frame['game_ball']['physics']['angular_velocity']['x'] for frame in frames]
    ball_angular_velocity['y'] = [frame['game_ball']['physics']['angular_velocity']['y'] for frame in frames]
    ball_angular_velocity['z'] = [frame['game_ball']['physics']['angular_velocity']['z'] for frame in frames]

    car_extra = pd.DataFrame([])
    car_extra['jumped'] = [frame['game_cars'][0]['jumped'] for frame in frames]
    car_extra['boost'] = [frame['game_cars'][0]['boost'] for frame in frames]

    car_physics = dict([("location", car_location), ("rotation", car_rotation), ("velocity", car_velocity),
                        ("angular_velocity", car_angular_velocity)])
    ball_physics = dict([("location", ball_location), ("rotation", ball_rotation), ("velocity", ball_velocity),
                         ("angular_velocity", ball_angular_velocity)])
    ball_data = dict([("physics", ball_physics)])
    car_data = dict([("physics", car_physics), ("jumped", car_extra["jumped"]), ("boost", car_extra["boost"])])
    test_results = dict([("car", car_data), ("ball", ball_data)])
    return test_results