#!/bin/sh
# Run DB test using venv (avoid alias python). From project root: ./deploy/run_test_db.sh
DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DIR" || exit 1
"$DIR/venv/bin/python" "$DIR/deploy/test_db_write_read.py"
