#!/bin/sh
DIR="/home/idesig02/helgamade.com/svitlobot"
PYTHON="$DIR/venv/bin/python"
LOG="$DIR/svitlobot.log"
if /usr/bin/pgrep -f "python main.py" > /dev/null 2>&1; then
  exit 0
fi
cd "$DIR" || exit 1
nohup "$PYTHON" main.py >> "$LOG" 2>&1 &
