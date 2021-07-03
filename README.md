# RLBot
This repository contains all RLBot related content (bots, exercises, test scenario framework) needed.

# Basic structure
Bot scripts are located in [src](src/bots/). Currently there are three different bots: 
* an example bot created from the [RLBot Python Example](https://github.com/RLBot/RLBotPythonExample)
* a [model bot](src/bots/model_bot.py) that loads a ONNX model and supplies all game inputs to the runtime to enable transfer learning
* a [test bot](src/bots/test_bot.py) which loads a specified scenario.json, runs a predefined action sequence and logs all game packets to a file - this is used for scenario testing

## Prerequisites
Create a virtual environment / conda environment and install `pip`. Run `pip install -r requirements.txt`. After that
a training runner can be executed by running e.g. `python src\scenarios\goalie\goalie_runner.py` from the root directory.

### Common Errors
We found a common error with the flatbuffer library that rlbot is dependant on. It might helpt to uninstall and reinstall rlbot / rlbottraining manually via `pip`.


# Training Exercises
The folder [scenarios](src/scenarios) contains exercise scenarios and training runners. Exercises are typically composed of a bot config, a match config, a exercise / training class and a runner script. 
All configuration related to the bot (path to the actual bot scrip, accessory config like settings paths etc.) are located in the <exercise>_bot.cfg. Same goes for the <exercise>_match.cfg containing all match related configuration.
Logic on how an exercise is created, the initial game state, how the exercise is to be graded etc. can be found in the <exercise>_training.py containing the specified Exercise dataclass and needed graders. The runner script can be run simply executing the main of the script.

## Test exercise
The test exercise is used to run predefined scenarios to log relevant game state information. Therefore a JSON file is needed that describes the scenario. Needed values / the file format of a such a scenario is as follows:
```json
  "time": 10.0,
  "name": "example",
  "startValues": [
    {
      "gameObject": "car",
      "position": {
        "x": 0.0,
        "y": 0.1852,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "angularVelocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "rotation": {
        "x": 0.0,
        "y": 90.0,
        "z": 0.0
      }
    },
    {
      "gameObject": "ball",
      "position": {
        "x": 5.0,
        "y": 0.9275,
        "z": 0.0
      },
      "velocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "angularVelocity": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      },
      "rotation": {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0
      }
    }
  ],
  "actions": [
    {
      "duration": 0.1,
      "inputs": [
        {
          "name": "jump",
          "value": 1.0
        }
      ]
    }]
}
```
This scenario file is loaded from a `settings.json` (referred to as **scenario_settings**) specifying all path information. This itself is loaded from the path specified in the `settings.json` in [exercise directory](src/scenarios/Test/settings.json).
By running the `test_runner.py` the currently specified scenario in the **scenario_settings** is loaded and run by the exercise / bot. All game packets received during runtime are then logged to a file created in the RLBot output directory specified in **scenario_settings** and named after the scenario name.

## Goalie Exercise
A basic exercise to test out transfer learning from Roboleague to RLBot was created in [goalie](src/scenarios/goalie). It contains all the needed configs and runners.

# Copyright notices
Based on the [RLBot Python Example](https://github.com/RLBot/RLBotPythonExample)
