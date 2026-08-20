#!/bin/bash
set -e

SDK_PATH="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2"
KEY_PATH="developer_key.der"
OUTPUT_IQ="bin/PerpexTacticalWatchFace.iq"
MANIFEST_PATH="manifest.xml"

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

if [ "$BUMP_TYPE" != "skip" ]; then
    python3 -c "
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
        
    print(f'🏷️  Version updated in manifest.xml: {old_version} -> {new_version}')
else:
    print('⚠️ Could not parse version in manifest.xml')
"
fi

echo "========================================================"
echo "📦 EXPORTING GARMIN CONNECT IQ STORE PACKAGE (.iq)"
echo "========================================================"

if [ ! -f "$KEY_PATH" ]; then
    echo "🔑 Generating new RSA developer key..."
    openssl genrsa -out developer_key.pem 4096
    openssl pkcs8 -topk8 -inform PEM -outform DER -in developer_key.pem -out developer_key.der -nocrypt
fi

mkdir -p bin

echo "🚀 Compiling multi-device store package with monkeyc..."
"$SDK_PATH/bin/monkeyc" -e -y "$KEY_PATH" -o "$OUTPUT_IQ" -f monkey.jungle -r

echo ""
echo "========================================================"
echo "SUCCESS! Production Store Package Created:"
echo "Location: $OUTPUT_IQ"
echo "Size: $(du -h "$OUTPUT_IQ" | cut -f1)"
echo "========================================================"
