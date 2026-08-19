#!/bin/bash
# Kill existing simulator instances to prevent connection issues
pkill -f connectiq || true
sleep 1

DEVICE="$1"

if [ -z "$DEVICE" ]; then
    echo "Select a target device to build for:"
    devices=("fenix7" "epix2" "venu3" "enduro3" "fenix847mm" "Quit")
    select sel in "${devices[@]}"; do
        if [ "$sel" = "Quit" ]; then
            echo "Exiting."
            exit 0
        elif [ -n "$sel" ]; then
            DEVICE="$sel"
            break
        else
            echo "Invalid selection. Please enter a number from the menu."
        fi
    done
fi

SDK_DIR="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks"
SDK_PATH=$(ls -td "$SDK_DIR"/connectiq-sdk-mac-* 2>/dev/null | head -n 1)

if [ -z "$SDK_PATH" ]; then
    echo "Error: No Garmin Connect IQ SDK found in $SDK_DIR"
    exit 1
fi

echo "Using Connect IQ SDK at: $SDK_PATH"

# Clean bin directory
rm -rf "/Users/vivek/Development/GarminWatchFace/bin"
mkdir -p "/Users/vivek/Development/GarminWatchFace/bin"

echo "Building watch face for $DEVICE..."

# Compile the watch face
"$SDK_PATH/bin/monkeyc" \
    -d "$DEVICE" \
    -f monkey.jungle \
    -o bin/GarminWatchFace.prg \
    -y developer_key.der

# Generate simulator settings XML definition
python3 /Users/vivek/.gemini/antigravity-ide/brain/71d42b51-5e25-4db8-94a7-530ece43b1ab/scratch/generate_settings_xml.py

# Start the simulator with the watch face
"$SDK_PATH/bin/connectiq" &
sleep 5
"$SDK_PATH/bin/monkeydo" \
    "/Users/vivek/Development/GarminWatchFace/bin/GarminWatchFace.prg" \
    "$DEVICE"