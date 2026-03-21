#!/bin/bash
set -e
source "$HELPERS"

clog "Installing node modules"
cd "$PROJECT_DIR/$CLIENT_DIR"
q npm install

clog "Starting client server"
npm run dev