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

# Clean bin directory
rm -rf "/Users/vivek/Development/GarminWatchFace/bin"
mkdir -p "/Users/vivek/Development/GarminWatchFace/bin"

echo "Building watch face for $DEVICE..."

# Compile the watch face
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/monkeyc" \
    -d "$DEVICE" \
    -f monkey.jungle \
    -o bin/GarminWatchFace.prg \
    -y developer_key.der

# Start the simulator with the watch face
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/connectiq" \
    &
sleep 5
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/monkeydo" \
    "/Users/vivek/Development/GarminWatchFace/bin/GarminWatchFace.prg" \
    "$DEVICE"