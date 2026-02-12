#!/bin/sh
# Start realtime_consumer.py if not running. Requires venv_mq (Python 3.8+) with MQ deps.
DIR="/home/idesig02/helgamade.com/svitlobot"
PYTHON="$DIR/venv_mq/bin/python"
LOG="$DIR/svitlobot-mq.log"
if [ ! -x "$PYTHON" ]; then
  exit 0
fi
if /usr/bin/pgrep -f "python realtime_consumer.py" > /dev/null 2>&1; then
  exit 0
fi
cd "$DIR" || exit 1
nohup "$PYTHON" realtime_consumer.py >> "$LOG" 2>&1 &
