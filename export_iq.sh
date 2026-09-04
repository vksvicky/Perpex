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

notes = f'''Perpex v{version} Release Notes

What's New in v{version}
• Added full support for 466x466 AMOLED resolution (Fenix 9 Pro 51mm)
• Expanded device support across Fenix 8 Pro, Fenix 9, Enduro 3, and Venu series
• Refined 6-slot grid spacing with increased vertical breathing room between rows
• Calibrated Venu Sq 2 (320x360) inner ring track clearance for pixel-perfect alignment
• Enhanced offline solar calculations (Sunrise/Sunset) using weather station position fallbacks

Supported Icons and Metrics in Resources
• icon_battery: Dynamic battery gauge with color thresholds (Green above 40%, Yellow under 40%, Red 20% or below)
• icon_heart: Real-time pulse monitoring with live animated pulsing heart indicator (BPM)
• icon_steps: Daily cumulative step count with active progress tracking
• icon_step_goal: Target icon showing percentage completion toward your daily step goal
• icon_flame: Active metabolic calorie burn expenditure (kCal)
• icon_distance: Total daily walking and running distance displayed in kilometers (KM)
• icon_floors: Total vertical flights of stairs climbed today
• icon_active_mins: Stopwatch icon for weekly moderate and vigorous intensity activity minutes
• icon_stress: Real-time all-day physiological stress score (0–100)
• icon_bluetooth: Phone connectivity indicator and unread notification counter
• icon_altitude: Mountain icon tracking real-time elevation in meters above sea level
• icon_barometer: Gauge icon monitoring ambient atmospheric pressure in hectopascals (hPa)
• icon_weather_temp: Thermometer icon with configurable Celsius (°C) and Fahrenheit (°F)
• icon_weather_cond: Dynamic weather icon mapping automatically to current outdoor conditions
• icon_raindrop: Precipitation probability percentage (0–100%)
• icon_weather_sunny: Clear and sunny skies
• icon_weather_partly_cloudy: Sun and cloud cover indicator for fair weather
• icon_weather_cloudy: Overcast conditions with dense cloud cover
• icon_weather_rain: Rain and showers indicator
• icon_weather_thunderstorm: Severe weather and thunderstorm warning
• icon_weather_snow: Snowflake icon for freezing temperatures and snowfall
• icon_weather_wind: Wind velocity converted to nautical knots (kt) for outdoor navigation
• icon_sunrise: Civil dawn time calculation with automatic GPS and weather fallback
• icon_sunset: Civil dusk time calculation with automatic GPS and weather fallback
• icon_body_battery: Lightning bolt battery icon for Body Battery energy reserve (0–100%)
• icon_recovery_time: Recommended recovery hours remaining before your next workout
• icon_vo2max: Cardiovascular aerobic fitness score for running and cycling

Themes and Display Features
• 6 Color Themes: Red (Default), Teal, Warm Orange, Electric Green, Gold, and Pure White
• Night Mode (Tactical Red, Night Amber, Stealth Green) with automatic solar schedule dimming
• AMOLED Burn-In Protection: Always-On Display (AOD) compliant with Garmin's under 10% active pixel threshold
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
