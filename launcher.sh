#!/bin/bash

# launcher: starts netatmo.py in a new tmux session.
# To launch at startup as pi, add this to /etc/rc.local:
#   su -c /home/pi/netatmo/launcher.sh -l pi

SESSION="NETATMO"

echo "Launching tmux"
# allow re-launch
tmux has-session -t $SESSION 2>/dev/null && tmux kill-session -t $SESSION
tmux new-session -d -s $SESSION

echo "Pause"
sleep 5

echo "Launching netatmo.py"
tmux send-keys -t $SESSION.0 "cd ~/netatmo" C-m
echo "Pause"
sleep 1
tmux send-keys -t $SESSION.0 "./netatmo.py" C-m