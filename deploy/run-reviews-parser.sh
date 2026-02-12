#!/bin/sh
DIR="/home/idesig02/helgamade.com/svitlobot"
cd "$DIR" || exit 0
"$DIR/venv/bin/python" reviews_parser.py
