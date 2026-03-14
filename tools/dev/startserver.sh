#!/bin/bash
set -e


VENV_DIR=".venv"
APP="main:app"
HOST="127.0.0.1"
PORT="8000"

cd "$PROJECT_DIR/$SERVER_DIR"

if [ ! -d "$VENV_DIR" ]; then
	pwd
	echo "Creating virtual environment..."
	python3 -m venv "$VENV_DIR"
else
	echo "Virtual environment already created."
fi
source "$VENV_DIR/bin/activate"

echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "Starting server at http://$HOST:$PORT"

uvicorn "$APP" --host "$HOST" --port "$PORT" --reload

trap deactivate EXIT
