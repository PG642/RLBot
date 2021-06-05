# RLBot
RLBot repository used for transfer learning of a Unity ml-agents learned model on RoboLeague.

# Training
The folder [scenarios](src/scenarios) contains exercise scenarios and training runners.
## Exercises
Following exercise scenarios are currently implemented:
- Goalie Exercise (ball rolling to goal)
## Usage
Create a virtual environment / conda environment and install `pip`. Run `pip install -r requirements.txt` or `pip install rlbottraining`. After that
a training runner can be executed by running e.g. `rlbottraining run_module src\scenarios\goalie\goalie_runner.py` or `python src\scenarios\goalie\goalie_runner.py` from the root directory.

# Copyright notices
Based on the [RLBot Python Example](https://github.com/RLBot/RLBotPythonExample)
