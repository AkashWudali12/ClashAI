#!/bin/bash
adb forward tcp:27183 localabstract:scrcpy 
source ./venv/bin/activate
python ./play_game.py