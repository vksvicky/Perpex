# Kill existing simulator instances to prevent connection issues
pkill -f connectiq || true
sleep 1

# Clean bin directory
rm -rf "/Users/vivek/Development/GarminWatchFace/bin"

# Create bin directory
mkdir -p "/Users/vivek/Development/GarminWatchFace/bin"

# Compile the watch face
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/monkeyc" \
    -d fenix6 \
    -f monkey.jungle \
    -o bin/GarminWatchFace.prg \
    -y developer_key.der

# Start the simulator with the watch face
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/connectiq" \
    &
sleep 5
"/Users/vivek/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-8.0.0_Beta-2025-01-07-276916717/bin/monkeydo" \
    "/Users/vivek/Development/GarminWatchFace/bin/GarminWatchFace.prg" \
    fenix6