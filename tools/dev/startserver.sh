#!/bin/bash
set -e
source "$HELPERS"

VENV_DIR=".venv"
APP="server:app"
HOST="127.0.0.1"
PORT="8000"

if [ ! -d "$OPT_DIR" ]; then
	cerr "Your system is missing the required setup. Read the README.md file for more information on how to get started."
	exit 1
fi

if [ ! -d "$DUMP1090_DIR" ]; then
	cerr "dump1090 not installed. Make sure to run setup"
	exit 1
fi

cd "$PROJECT_DIR/$SERVER_DIR"

if [ ! -d "$VENV_DIR" ]; then
	pwd
	clog "Creating virtual environment..."
	python3 -m venv "$VENV_DIR"
else
	clog "Virtual environment already created."
fi
source "$VENV_DIR/bin/activate"

clog "Installing dependencies..."
pip install --upgrade pip -q
pip install -r dev-requirements.txt -q

clog "Starting server at http://$HOST:$PORT"

cd "$PROJECT_DIR/$DUMP1090_DIR"
./dump1090 --net >/dev/null &
DUMP1090_PID=$!

cd "$PROJECT_DIR/$SERVER_DIR"
uvicorn "$APP" --host "$HOST" --port "$PORT" --reload &
UVICORN_PID=$!

trap "kill $DUMPS1090_PID $UVICORN_PID 2>/dev/null; wait $DUMPS1090_PID $UVICORN_PID 2>/dev/null; deactivate" EXIT INT TERM
wait $DUMPS1090_PID $UVICORN_PID
