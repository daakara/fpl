#!/bin/bash

# Configuration
APP_NAME="FPL_Analytics"
RELEASES_DIR="./releases"
DATE=$(date +%Y%m%d_%H%M%S)

# 1. Automatic Version Incrementing
# Reads version: 1.0.0+1 and increments the build number (the +1 part)
if [ -f "pubspec.yaml" ]; then
    echo "Updating build number in pubspec.yaml..."
    sed -i '' -E 's/(version: [0-9]+\.[0-9]+\.[0-9]+\+)([0-9]+)/echo "\1$((\2+1))"/e' pubspec.yaml
    NEW_VERSION=$(grep "version: " pubspec.yaml | sed 's/version: //')
    echo "New Version: $NEW_VERSION"
else
    echo "pubspec.yaml not found. Skipping auto-versioning."
    NEW_VERSION="1.0.0+1"
fi

# 2. Build the APK
echo "Starting Flet Android Build..."
flet build apk \
    --project "$APP_NAME" \
    --build-version "${NEW_VERSION%+*}" \
    --build-number "${NEW_VERSION#*+}" \
    --arch arm64-v8a

# 3. Archive the Release
mkdir -p "$RELEASES_DIR"
APK_SOURCE="build/apk/release.apk" # Path may vary slightly based on Flet version

if [ -f "$APK_SOURCE" ]; then
    FINAL_APK="$RELEASES_DIR/${APP_NAME}_v${NEW_VERSION//+/_}_$DATE.apk"
    mv "$APK_SOURCE" "$FINAL_APK"
    echo "------------------------------------------------"
    echo "BUILD SUCCESSFUL!"
    echo "Release archived to: $FINAL_APK"
    echo "------------------------------------------------"
else
    echo "Error: APK not found at $APK_SOURCE"
    exit 1
fi