#!/bin/bash
set -e

SDK_PATH="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2"
KEY_PATH="developer_key.der"
OUTPUT_PRG="bin/GarminWatchFaceTest.prg"

DEVICES=("fenix7" "enduro3" "epix2pro42mm" "epix2" "fenix847mm")

MODE="${1:-unit}"

if [ "$MODE" = "ui" ]; then
    echo "========================================================"
    echo "📸 STARTING VISUAL UI SNAPSHOT TESTS"
    echo "========================================================"
    python3 run_ui_tests.py
    exit 0
elif [ "$MODE" = "sim" ]; then
    TARGET_DEV="${2:-fenix7}"
    echo "========================================================"
    echo "⌚ LAUNCHING NORMAL WATCHFACE IN SIMULATOR ($TARGET_DEV)"
    echo "========================================================"
    mkdir -p bin
    echo "Starting Connect IQ Simulator..."
    killall simulator 2>/dev/null || true
    sleep 1
    "$SDK_PATH/bin/connectiq" &
    sleep 5
    
    echo "Compiling for $TARGET_DEV..."
    "$SDK_PATH/bin/monkeyc" -f monkey.jungle -o "bin/GarminWatchFace.prg" -d "$TARGET_DEV" -y "$KEY_PATH"
    
    echo "Launching in Simulator..."
    "$SDK_PATH/bin/monkeydo" "bin/GarminWatchFace.prg" "$TARGET_DEV"
    exit 0
elif [ "$MODE" != "unit" ]; then
    echo "Usage: ./run_tests.sh [unit | ui | sim <device>]"
    echo "  unit : Run headless logic unit tests (default)"
    echo "  ui   : Run visual UI snapshot tests"
    echo "  sim  : Compile and launch normal watchface in simulator"
    exit 1
fi

echo "========================================================"
echo "🧪 PERPEX COMPREHENSIVE UNIT & LOGIC TEST RUNNER"
echo "========================================================"
echo "Compiling & Executing Unit Assertions via monkeydo -t..."
echo "========================================================"

mkdir -p bin

FAILURES=0
# Ensure Simulator is running
echo "Starting Connect IQ Simulator..."
killall simulator 2>/dev/null || true
sleep 1
"$SDK_PATH/bin/connectiq" &
sleep 5

for dev in "${DEVICES[@]}"; do
    echo ""
    echo "--------------------------------------------------------"
    echo "📱 Compiling & Running Unit Tests on Target Device: $dev"
    echo "--------------------------------------------------------"
    
    # 1. Compile unit test binary with -t flag
    if "$SDK_PATH/bin/monkeyc" -f monkey.jungle -o "$OUTPUT_PRG" -d "$dev" -y "$KEY_PATH" -t; then
        echo "✅ Compilation with Unit Tests SUCCESSFUL for $dev"
        echo "🚀 Executing test assertions in Connect IQ runtime environment..."
        
        # 2. Run test assertions via monkeydo -t
        # monkeydo often returns 1 on macOS even on success, so we parse the output
        TEST_OUT=$("$SDK_PATH/bin/monkeydo" "$OUTPUT_PRG" "$dev" -t 2>&1) || true
        echo "$TEST_OUT"
        
        if echo "$TEST_OUT" | grep -q "PASSED ("; then
            echo "✅ All assertions PASSED for $dev"
        else
            echo "❌ Test Assertions FAILED for $dev"
            FAILURES=$((FAILURES + 1))
        fi
    else
        echo "❌ Compilation FAILED for $dev"
        FAILURES=$((FAILURES + 1))
    fi
done

echo ""
echo "========================================================"
if [ $FAILURES -eq 0 ]; then
    echo "🎉 ALL COMPLIANCE & UNIT TEST SUITES PASSED CLEANLY!"
else
    echo "⚠️ $FAILURES DEVICE SUITES DETECTED ISSUES FOR REVIEW"
fi
echo "========================================================"
