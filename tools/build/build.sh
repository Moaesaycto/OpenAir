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

cd ..
clog "${ASCII_GREEN}Successfully built client${ASCII_RESET}"
clog

# Create prod environment
clog "Entering production build virtual environment"
python3 -m venv prod-venv
source prod-venv/bin/activate
q pip install pip-tools pyinstaller pyinstaller-hooks-contrib

clog "Compiling production requirements"
q pip install -r "$SERVER_DIR/prod-requirements.txt"

# PyInstaller stuff
q pyi-makespec "$PROJECT_DIR/$SERVER_DIR/App.py" \
	--onefile --windowed --name "$APP_FILE_NAME" \
	--specpath "$TMPDIR" \
	--add-data "$CLIENT_BUILD:static" \
	--hidden-import="server"

clog "Building executable file"

DIST_PATH="$PROJECT_DIR/dist"
BUILD_PATH="$TMPDIR/build"

pyinstaller "$TMPDIR/$APP_FILE_NAME.spec" \
	--distpath "$DIST_PATH" -y \
	--workpath "$BUILD_PATH" \
	--log-level ERROR

# It worked!
clog "${ASCII_GREEN}Successfully built executable file${ASCII_RESET}"
clog
clog "Check $DIST_PATH/$APP_FILE_NAME for the runnable file"
echo