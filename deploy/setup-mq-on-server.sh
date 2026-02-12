#!/bin/sh
# One-time: create venv_mq (Python 3.8+) and install deps for realtime_consumer.py.
# Run from project root: cd /home/idesig02/helgamade.com/svitlobot && sh deploy/setup-mq-on-server.sh
set -e
DIR="${1:-/home/idesig02/helgamade.com/svitlobot}"
cd "$DIR" || exit 1

for py in python3.11 python3.10 python3.9 python3.8 python3; do
  if command -v "$py" >/dev/null 2>&1; then
    VER=$("$py" -c "import sys; print(sys.version_info.major, sys.version_info.minor)" 2>/dev/null) || continue
    MAJOR=$(echo "$VER" | cut -d' ' -f1)
    MINOR=$(echo "$VER" | cut -d' ' -f2)
    if [ "$MAJOR" = "3" ] && [ "$MINOR" -ge 8 ]; then
      PYTHON_CMD="$py"
      break
    fi
  fi
done

if [ -z "$PYTHON_CMD" ]; then
  echo "Need Python 3.8+ (python3.10, python3.9, ...). Install it and run this script again."
  exit 1
fi

echo "Using: $PYTHON_CMD"
# Try normal venv first; on some hostings ensurepip is missing, then use --without-pip + get-pip
if ! "$PYTHON_CMD" -m venv venv_mq 2>/dev/null; then
  echo "venv with pip failed, trying --without-pip + get-pip..."
  "$PYTHON_CMD" -m venv venv_mq --without-pip
  curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  ./venv_mq/bin/python /tmp/get-pip.py -q
  rm -f /tmp/get-pip.py
fi
./venv_mq/bin/pip install -q -r requirements.txt -r requirements-mq.txt
echo "venv_mq ready. Enable MQ consumer (run as root):"
echo "  sudo cp $DIR/deploy/svitlobot-mq.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload && sudo systemctl enable --now svitlobot-mq"
