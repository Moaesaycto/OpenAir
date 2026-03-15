#!/bin/bash
source "$HELPERS"

clog "Attempting to build $APP_NAME version $VERSION"
clog

TMPDIR=$(mktemp -d)
trap "deactivate 2>/dev/null; rm -rf $TMPDIR" EXIT

# Setting variables
APP_FILE_NAME="$APP_NAME-v$VERSION"

clog "Building client..."

cd "$PROJECT_DIR/$CLIENT_DIR"
clog "Loading dependencies via npm install..."
q npm install

clog "Building client..."
q npm run build

cd "$PROJECT_DIR"
cdone "Successfully built client"
clog

# Installing dump1090
DUMP1090_ZIP="$TMPDIR/sources/dump1090.zip"
DUMP1090_BUILD="$TMPDIR/opt"
DUMP1090_LOCAL_DIR="$DUMP1090_BUILD/dump1090-master"
mkdir -p "$TMPDIR/sources"

clog "Fetching latest version of dump1090"
q wget -q "https://github.com/flightaware/dump1090/archive/refs/heads/master.zip" -O "$DUMP1090_ZIP"
q unzip -o "$DUMP1090_ZIP" -d "$DUMP1090_BUILD"
cd "$DUMP1090_LOCAL_DIR"
clog "Building dump1090"
q make
cdone "Successfully compiled dump1090"
clog

cd "$PROJECT_DIR"

# Create prod environment
clog "Entering production build virtual environment"
python3 -m venv prod-venv
source prod-venv/bin/activate
q pip install pip-tools pyinstaller pyinstaller-hooks-contrib

clog "Compiling production requirements"
q pip install -r "$PROJECT_DIR/$SERVER_DIR/prod-requirements.txt"

# PyInstaller stuff
q pyi-makespec "$PROJECT_DIR/$SERVER_DIR/App.py" \
	--onefile --windowed --name "$APP_FILE_NAME" \
	--specpath "$TMPDIR" \
	--add-data "$CLIENT_BUILD:static" \
	--hidden-import="server" \
	--add-binary "$DUMP1090_LOCAL_DIR/dump1090:."

clog "Building executable file"

DIST_PATH="$PROJECT_DIR/dist"
BUILD_PATH="$TMPDIR/build"

pyinstaller "$TMPDIR/$APP_FILE_NAME.spec" \
	--distpath "$DIST_PATH" -y \
	--workpath "$BUILD_PATH" \
	--log-level ERROR

# It worked!
cdone "Successfully built executable file"
clog
clog "Check $DIST_PATH/$APP_FILE_NAME for the runnable file"
echo