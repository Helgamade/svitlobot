#!/bin/sh
# Start web_send (gunicorn) for https://svitlobot.helgamade.com/ if not running.
DIR="/home/idesig02/helgamade.com/svitlobot"
VENV="$DIR/venv"
LOG="$DIR/web_send.log"
PORT=5000

if [ ! -f "$DIR/web_send.py" ]; then
  exit 0
fi
if /usr/bin/pgrep -f "gunicorn.*web_send" > /dev/null 2>&1; then
  exit 0
fi
if [ ! -x "$VENV/bin/python" ]; then
  exit 0
fi
cd "$DIR" || exit 1
if [ ! -x "$VENV/bin/gunicorn" ]; then
  "$VENV/bin/pip" install -q -r requirements.txt 2>/dev/null || exit 0
fi
nohup "$VENV/bin/gunicorn" -w 1 -b 127.0.0.1:$PORT web_send:app >> "$LOG" 2>&1 &
