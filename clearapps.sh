#!/bin/bash

# Replace with the path to your text file
APPS_FILE="applist.txt"

# Function to close an app using adb
close_app() {
    echo "adb shell am force-stop $1"
    adb shell am force-stop $1
}

# Connect to the Android TV (replace with your IP)
ANDROID_TV_IP="192.168.4.10"
adb connect $ANDROID_TV_IP

# Read app package names from the file
while IFS= read -r app; do
  # Check if line is empty or a comment (starting with #)
  if [[ -z "$app" || "$app" =~ ^# ]]; then
    continue
  fi
  close_app "$app"
done < "$APPS_FILE"

# Disconnect from the Android TV
adb disconnect $ANDROID_TV_IP

# Exit the script
exit 0