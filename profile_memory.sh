#!/bin/bash
set -e

SDK_PATH="$HOME/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2"
KEY_PATH="developer_key.der"

# Devices to profile and their known memory limits for watchfaces (in bytes)
DEVICES=(
    "fenix7:117162"       # 260x260 MIP
    "epix2:117162"        # 416x416 AMOLED
    "enduro3:117162"      # 280x280 MIP
    "fenix847mm:131072"   # 454x454 AMOLED
    "fr255:117162"        # 260x260 MIP
    "venu3s:117162"       # 390x390 AMOLED
)

echo "========================================================"
echo "📊 GARMIN WATCHFACE MEMORY PROFILER"
echo "========================================================"
echo "Compiling and analyzing runtime memory requirements..."
echo ""

mkdir -p bin

for ENTRY in "${DEVICES[@]}"; do
    DEV="${ENTRY%%:*}"
    LIMIT="${ENTRY##*:}"
    
    echo "--------------------------------------------------------"
    echo "📱 Profiling Device: $DEV (Hardware Limit: $((LIMIT/1024)) KB)"
    echo "--------------------------------------------------------"
    
    # Run the compiler with basic build stats, extract the output, and silence standard build logs
    STATS=$("$SDK_PATH/bin/monkeyc" -f monkey.jungle -o "bin/profile_$DEV.prg" -y "$KEY_PATH" -d "$DEV" --build-stats 0 2>&1)
    
    # Extract Data and Code sizes (Foreground)
    DATA_BYTES=$(echo "$STATS" | awk '/Data:/ {in_data=1} in_data && /Foreground:/ {print $2; in_data=0}')
    CODE_BYTES=$(echo "$STATS" | awk '/Code:/ {in_code=1} in_code && /Foreground:/ {print $2; in_code=0}')
    
    if [ -z "$DATA_BYTES" ] || [ -z "$CODE_BYTES" ]; then
        echo "❌ Failed to extract memory stats. Compiler output:"
        echo "$STATS"
        continue
    fi
    
    TOTAL_MEM=$((DATA_BYTES + CODE_BYTES))
    PERCENT_USED=$(awk "BEGIN {printf \"%.1f\", ($TOTAL_MEM / $LIMIT) * 100}")
    
    echo "🔹 Foreground Data:  $DATA_BYTES bytes"
    echo "🔹 Foreground Code:  $CODE_BYTES bytes"
    echo "========================================="
    echo "📈 Total Mem Used:   $TOTAL_MEM bytes ($PERCENT_USED% of Limit)"
    
    if (( TOTAL_MEM > LIMIT )); then
        echo "⚠️  WARNING: OUT OF MEMORY (Exceeds $LIMIT bytes)!"
    elif (( TOTAL_MEM > LIMIT - 10240 )); then
        echo "⚠️  WARNING: VERY CLOSE TO LIMIT (Less than 10KB free)!"
    else
        echo "✅ PASS (Safe Memory Footprint)"
    fi
    echo ""
done

# Cleanup temporary profile binaries
rm -f bin/profile_*.prg

echo "========================================================"
echo "🎉 Memory Profiling Complete!"
echo "========================================================"
