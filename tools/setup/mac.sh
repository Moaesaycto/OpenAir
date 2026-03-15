#!/bin/bash
source "$HELPERS"

TMPDIR=$(mktemp -d)
trap "deactivate 2>/dev/null; rm -rf $TMPDIR" EXIT

clog "Beginning MacOS development setup"
if ! command -v brew &>/dev/null; then
	cerr "Homebrew not found. Please install it from https://brew.sh"
	exit 1
fi

# Installing the necessary dependencies for the server
clog "Installing the necessary builds view brew"
q brew install python@3.14 pkg-config librtlsdr wget
cdone "Successfulled installed necessary packages"
clog

# Installing necessary dependencies for the client
clog "Preparing client for development"
cd "$PROJECT_DIR/$CLIENT_DIR"
q npm install
cdone "Successfully installed client dependencies"
clog

# dump1090 setup [https://github.com/antirez/dump1090]
cd "$PROJECT_DIR"
clog "Fetching latest version of dump1090..."
DUMP1090_ZIP="$TMPDIR/source.zip"
q wget -q "https://github.com/flightaware/dump1090/archive/refs/heads/master.zip" -O "$DUMP1090_ZIP"
q unzip -o "$DUMP1090_ZIP" -d "$OPT_DIR"
clog "Building dump1090..."
cd "$PROJECT_DIR/$DUMP1090_DIR"
q make
cdone "Successfully built dump1090"
