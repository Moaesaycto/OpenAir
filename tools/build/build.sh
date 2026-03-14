#!/bin/bash

echo "Building client..."

cd "$PROJECT_DIR/$CLIENT_DIR"
echo "Loading dependencies via npm install..."
npm install 2>/dev/null >/dev/null

echo "Building client..."
if ! OUTPUT=$(npm run build 2>&1); then
	echo -e "${ASCII_RED}Failed to build client${ASCII_RESET}"
	echo "Reasoning:"
	echo "$OUTPUT"
	exit 1
fi
echo -e "${ASCII_GREEN}Successfully built client${ASCII_RESET}"

if [ -z "$PROJECT_DIR" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Error: PROJECT_DIR or OUTPUT_DIR is not set"
    exit 1
fi

BUILD_PATH="$PROJECT_DIR/$OUTPUT_DIR"
if [ -d "$BUILD_PATH" ]; then
	rm -rf "$BUILD_PATH"
fi
mkdir "$BUILD_PATH"
cp "$PROJECT_DIR/$CLIENT_DIR/$INDEX_OUTPUT" "$BUILD_PATH/index.html"