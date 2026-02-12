#!/bin/sh
# Start displayboard_http.py (HTTP on 8080) for Arduino clones without SSL. Optional.
DIR="/home/idesig02/helgamade.com/svitlobot"
VENV="$DIR/venv"
LOG="$DIR/displayboard_http.log"
PORT="${DISPLAYBOARD_HTTP_PORT:-8080}"

if [ ! -f "$DIR/displayboard_http.py" ]; then
  exit 0
fi
if /usr/bin/pgrep -f "displayboard_http.py" > /dev/null 2>&1; then
  exit 0
fi
if [ ! -x "$VENV/bin/python" ]; then
  exit 0
fi
cd "$DIR" || exit 1
export DISPLAYBOARD_HTTP_PORT="$PORT"
nohup "$VENV/bin/python" displayboard_http.py >> "$LOG" 2>&1 &
