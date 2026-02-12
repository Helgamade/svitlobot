#!/bin/bash
# Запускает svitlobot, если он ещё не запущен. Для крона (каждые 5–10 мин).
DIR="/home/idesig02/helgamade.com/svitlobot"
LOG="$DIR/svitlobot.log"
cd "$DIR" || exit 1
if pgrep -f "python main.py" > /dev/null 2>&1; then
  exit 0
fi
source venv/bin/activate
nohup python main.py >> "$LOG" 2>&1 &
