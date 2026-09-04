#!/bin/bash
set -e

SDK_PATH="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2"
KEY_PATH="developer_key.der"
OUTPUT_IQ="bin/PerpexTacticalWatchFace.iq"
MANIFEST_PATH="manifest.xml"
RELEASE_NOTES_PATH="bin/RELEASE_NOTES.txt"

BUMP_TYPE="$1"
CUSTOM_VERSION=""

# ─────────────────────────────────────────────────────────────────────────────
# DETECT DIRECT VERSION NUMBERS (e.g. ./export_iq.sh 1.2.3)
# ─────────────────────────────────────────────────────────────────────────────
if [[ "$BUMP_TYPE" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    CUSTOM_VERSION="$BUMP_TYPE"
    BUMP_TYPE="custom"
fi

if [ -z "$BUMP_TYPE" ]; then
    if [ -t 0 ]; then
        echo "Select version bump option for this store release:"
        select opt in "patch (1.0.0 -> 1.0.1)" "minor (1.0.0 -> 1.1.0)" "major (1.0.0 -> 2.0.0)" "custom (specify exact version)" "skip (keep current version)"; do
            case $opt in
                "patch (1.0.0 -> 1.0.1)") BUMP_TYPE="patch"; break ;;
                "minor (1.0.0 -> 1.1.0)") BUMP_TYPE="minor"; break ;;
                "major (1.0.0 -> 2.0.0)") BUMP_TYPE="major"; break ;;
                "custom (specify exact version)")
                    BUMP_TYPE="custom"
                    read -p "Enter exact version number (e.g. 1.0.1): " CUSTOM_VERSION
                    break
                    ;;
                "skip (keep current version)") BUMP_TYPE="skip"; break ;;
                *) echo "Invalid option." ;;
            esac
        done
    else
        BUMP_TYPE="patch"
    fi
fi

CURRENT_VERSION="1.0.0"

if [ "$BUMP_TYPE" != "skip" ]; then
    CURRENT_VERSION=$(python3 -c "
import re

manifest_path = '$MANIFEST_PATH'
bump_type = '$BUMP_TYPE'
custom_ver = '$CUSTOM_VERSION'

with open(manifest_path, 'r') as f:
    content = f.read()

match = re.search(r'version=\"(\d+)\.(\d+)\.(\d+)\"', content)
if match:
    major, minor, patch = map(int, match.groups())
    old_version = f'{major}.{minor}.{patch}'
    
    if bump_type == 'custom' and custom_ver:
        new_version = custom_ver
    elif bump_type == 'major':
        new_version = f'{major + 1}.0.0'
    elif bump_type == 'minor':
        new_version = f'{major}.{minor + 1}.0'
    else: # patch
        new_version = f'{major}.{minor}.{patch + 1}'
        
    new_content = re.sub(r'version=\"\d+\.\d+\.\d+\"', f'version=\"{new_version}\"', content, count=1)
    
    with open(manifest_path, 'w') as f:
        f.write(new_content)
        
    print(new_version)
else:
    print('1.0.0')
")
else
    CURRENT_VERSION=$(python3 -c "
import re
with open('$MANIFEST_PATH', 'r') as f:
    match = re.search(r'version=\"(\d+\.\d+\.\d+)\"', f.read())
    print(match.group(1) if match else '1.0.0')
")
fi

echo "========================================================"
echo "📦 EXPORTING GARMIN CONNECT IQ STORE PACKAGE (v$CURRENT_VERSION)"
echo "========================================================"

if [ ! -f "$KEY_PATH" ]; then
    echo "🔑 Generating new RSA developer key..."
    openssl genrsa -out developer_key.pem 4096
    openssl pkcs8 -topk8 -inform PEM -outform DER -in developer_key.pem -out developer_key.der -nocrypt
fi

mkdir -p bin

echo "🚀 Compiling multi-device store package with monkeyc..."
"$SDK_PATH/bin/monkeyc" -e -y "$KEY_PATH" -o "$OUTPUT_IQ" -f monkey.jungle -r

# ─────────────────────────────────────────────────────────────────────────────
# GENERATE COPY-PASTE GARMIN STORE RELEASE NOTES
# ─────────────────────────────────────────────────────────────────────────────
python3 -c "
import subprocess

version = '$CURRENT_VERSION'
out_path = '$RELEASE_NOTES_PATH'

try:
    git_logs = subprocess.check_output(['git', 'log', '-n', '5', '--pretty=format:- %s'], text=True).strip()
except Exception:
    git_logs = '- Performance and stability improvements.'

notes = f'''Perpex v{version} Release Notes:
========================================================
✨ WHAT'S NEW IN v{version}:
========================================================
- Added full support for 466x466 AMOLED resolution (Fenix 9 Pro 51mm).
- Expanded official device coverage across Fenix 8 Pro, Fenix 9, Enduro 3, and Venu series.
- Refined 6-slot grid spacing with increased vertical breathing room between rows.
- Calibrated Venu Sq 2 (320x360) inner ring track clearance for pixel-perfect alignment.
- Enhanced offline solar calculations (Sunrise/Sunset) using weather station position fallbacks.

========================================================
📊 SUPPORTED ICONS & DATA METRICS:
========================================================
🔋 Battery Level        : Dynamic gauge with smart color thresholds (Green above 40%, Yellow under 40%, Red 20% or below).
❤️ Heart Rate           : Real-time pulse monitoring with live animated pulsing heart indicator (BPM).
👟 Steps Counter        : Daily cumulative step count with active progress tracking.
🎯 Step Goal %          : Percentage completion toward your daily step goal.
🔥 Active Calories      : Daily active metabolic calorie burn expenditure (kCal).
📏 Distance             : Total daily walking and running distance displayed in kilometers (KM).
🪜 Floors Climbed       : Total vertical flights of stairs climbed today.
⏱️ Active Minutes       : Total moderate and vigorous intensity activity minutes accumulated this week.
🧘 Stress Score         : Real-time all-day physiological stress score (0–100).
💬 Notifications        : Unread smartphone notification counter and connectivity indicator.
🏔️ Altitude            : Real-time elevation tracking in meters above sea level.
🧭 Barometer            : Ambient atmospheric pressure monitoring in hectopascals (hPa).
🌡️ Weather Temp        : Ambient outdoor temperature with configurable Celsius (°C) and Fahrenheit (°F).
🌦️ Weather Condition   : Context-sensitive vector icon with auto-switching precipitation %, humidity, or wind speed.
☀️ Clear / Sunny        : Solar condition vector icon for sunny and clear skies.
⛅ Partly Cloudy        : Dual-tone cloud and sun indicator for fair weather.
☁️ Overcast / Cloudy    : Dense cloud cover indicator for overcast conditions.
💧 Rain / Precipitation : Raindrop icon displaying live precipitation probability percentage.
⛈️ Thunderstorms        : Severe weather alert icon for lightning and thunderstorms.
❄️ Snow & Wintry Mix    : Crisp snowflake icon for freezing temperatures and snowfall.
💨 Wind Velocity        : Wind speed converted to nautical knots (kt) for outdoor/marine navigation.
🌅 Sunrise Time         : Civil dawn time calculation with automatic GPS and weather station fallback.
🌇 Sunset Time          : Civil dusk time calculation with automatic GPS and weather station fallback.
☀️ Dynamic Solar Event  : Smart single-slot display that automatically toggles between next sunrise and sunset.
⚡ Body Battery         : Real-time bodily energy reserve percentage (0–100%).
🛌 Recovery Time        : Recommended recovery hours remaining before your next hard workout.
🏃 VO2 Max              : Cardiovascular aerobic fitness score for running and cycling.

========================================================
🎨 THEMES & DISPLAY FEATURES:
========================================================
- 6 Handcrafted Color Themes: Red (Default), Teal, Warm Orange, Electric Green, Gold, and Pure White.
- Night Mode (Tactical Red, Night Amber, Stealth Green) with automatic solar schedule dimming.
- AMOLED Burn-In Protection: Always-On Display (AOD) compliant with Garmin's under 10% active pixel threshold.
'''

with open(out_path, 'w') as f:
    f.write(notes)
"

echo ""
echo "========================================================"
echo "SUCCESS! Production Store Package Created:"
echo "Location: $OUTPUT_IQ"
echo "Size: $(du -h "$OUTPUT_IQ" | cut -f1)"
echo "========================================================"
echo ""
echo "📋 GARMIN CONNECT IQ STORE RELEASE NOTES (COPY & PASTE):"
echo "--------------------------------------------------------"
cat "$RELEASE_NOTES_PATH"
echo "--------------------------------------------------------"
echo "Saved to: $RELEASE_NOTES_PATH"
