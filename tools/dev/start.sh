#!/bin/bash
set -e
source "$HELPERS"

PREFIX_SERVER=$'\e[46m\e[1mSR\e[0m '
PREFIX_CLIENT=$'\e[45m\e[1mCL\e[0m '

./tools/dev/startserver.sh > >(sed "s/^/$PREFIX_SERVER/") 2> >(sed "s/^/$PREFIX_SERVER/" >&2) &
SERVER_PID=$!

./tools/dev/startclient.sh > >(sed "s/^/$PREFIX_CLIENT/") 2> >(sed "s/^/$PREFIX_CLIENT/" >&2) &
CLIENT_PID=$!

trap "kill $SERVER_PID $CLIENT_PID 2>/dev/null; wait $SERVER_PID $CLIENT_PID 2>/dev/null" EXIT INT TERM

wait $SERVER_PID $CLIENT_PID
