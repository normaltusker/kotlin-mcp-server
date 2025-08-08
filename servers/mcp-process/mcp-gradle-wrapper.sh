#!/bin/bash
# Simple wrapper script to run gradle commands via mcp-process

PROJECT_PATH="${1:-.}"
CMD="${2:-./gradlew tasks}"

echo "Running Gradle command in: $PROJECT_PATH"
cd "$PROJECT_PATH" || exit 1
eval "$CMD"
