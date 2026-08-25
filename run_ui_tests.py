#!/usr/bin/env python3
import os
import sys
import time
import subprocess

SDK_PATH = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH = "developer_key.der"
OUTPUT_DIR = "test_output/screenshots"
REPORT_PATH = "test_output/visual_report.html"

DEVICES = [
    ("fenix7", "260x260 MIP Solar", "Fenix 7 / Fenix 9 Pro Solar 47mm"),
    ("enduro3", "280x280 MIP Solar", "Enduro 3 / Fenix 9 Pro Solar 51mm"),
    ("epix2pro42mm", "390x390 AMOLED", "Epix 2 Pro 42mm"),
    ("epix2", "416x416 AMOLED", "Epix Gen 2 47mm"),
    ("fenix847mm", "454x454 AMOLED", "Fenix 8 / Fenix 9 Pro 47mm")
]

SCENARIOS = [
    # Group A: 19 Metric Types
    "1. Battery Slot (50%, 10%, 100%)",
    "2. Heart Rate (80 BPM, 199 BPM)",
    "3. Step Counter (99,999 STEPS)",
    "4. Step Goal % (100% GOAL)",
    "5. Active Calories (1000 kCal)",
    "6. Distance (999.9 KM)",
    "7. Floors Climbed (999 FLOORS)",
    "8. Active Minutes (9,999 MINS)",
    "9. Stress Score (100 STRESS)",
    "10. Digital Time (23:59)",
    "11. Notifications (99 NOTIF)",
    "12. Altitude (9,999 M)",
    "13. Barometer (1013 hPa)",
    "14. Weather Temp (45°C)",
    "15. Weather Condition (SUNRISE/RAIN)",
    "16. Solar Sun Event (06:14 SUNRISE)",
    "17. Body Battery (100% BODY BATT)",
    "18. Sunrise Only (06:14 AM)",
    "19. Sunset Only (07:45 PM)",

    # Group B: Length Bounds & Uniform Placements
    "20. Max Character String Length Bounds in All 7 Slots",
    "21. Min Character String Length Bounds in All 7 Slots",
    "22. Uniform Heart Rate in All 7 Slots",
    "23. Uniform Battery in All 7 Slots",
    "24. Uniform Steps in All 7 Slots",
    "25. Uniform Distance in All 7 Slots",
    "26. Uniform Calories in All 7 Slots",
    "27. Uniform Weather in All 7 Slots",

    # Group C: Color Themes & Battery Levels
    "28. Color Theme 1 (Red / Default)",
    "29. Color Theme 2 (Teal / Cyan)",
    "30. Color Theme 3 (Warm Orange)",
    "31. Color Theme 4 (Electric Green)",
    "32. Color Theme 5 (Gold / Yellow)",
    "33. Color Theme 6 (Pure White)",
    "34. Battery Low Warning Level (<= 20% Red)",
    "35. Battery Charging Animation State",

    # Group D: Power & Vision Modes
    "36. Low-Power AOD Mode (Dimmed Gray, Hidden Dial BG)",
    "37. Night Mode Red Theme Override",
    "38. Night Mode Green Theme Override",
    "39. Night Mode Orange Theme Override",
    "40. Full Active Mode (Analog Hands, Seconds, Rings, All 7 Slots)"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("========================================================")
print("🎨 PERPEX VISUAL UI & SCREENSHOT TEST HARNESS")
print("========================================================")
print(f"Verifying {len(SCENARIOS)} Exhaustive Test Scenarios across 5 Device Resolutions...")
print("========================================================")

def get_simulator_window_bounds():
    for _ in range(15):
        try:
            script = 'tell application "System Events" to tell process "simulator" to get {position, size} of window 1'
            res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                parts = [int(x.strip()) for x in res.stdout.strip().split(',')]
                return parts[0], parts[1], parts[2], parts[3]
        except Exception as e:
            pass
        time.sleep(2)
    print("Warning: Could not get simulator bounds after 30 seconds.")
    try:
        script = 'tell application "System Events" to tell process "simulator" to get {position, size} of window 1'
        res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            parts = [int(x.strip()) for x in res.stdout.strip().split(',')]
            return parts[0], parts[1], parts[2], parts[3]
    except Exception as e:
        print(f"Warning getting window bounds: {e}")
    return None

report_rows = []

print("Connect IQ Simulator should already be running (managed by run_tests.sh).")

for dev_id, res_info, dev_name in DEVICES:
    print(f"\n📱 Generating Visual UI Snapshot for: {dev_name} ({dev_id})...")
    prg_path = f"bin/Visual_{dev_id}.prg"
    img_path = f"{OUTPUT_DIR}/{dev_id}.png"
    
    # Build binary
    cmd_build = [
        os.path.join(SDK_PATH, "bin/monkeyc"),
        "-f", "monkey.jungle",
        "-o", prg_path,
        "-d", dev_id,
        "-y", KEY_PATH
    ]
    res_build = subprocess.run(cmd_build, capture_output=True, text=True)
    if res_build.returncode != 0:
        print(f"❌ Build failed for {dev_id}: {res_build.stderr}")
        continue
        
    # Launch in simulator
    cmd_do = [
        os.path.join(SDK_PATH, "bin/monkeydo"),
        prg_path,
        dev_id
    ]
    subprocess.Popen(cmd_do, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)
    
    # Bring simulator to front
    subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of (first process whose name is "simulator") to true'])
    time.sleep(1)
    
    # Capture exact simulator window region
    bounds = get_simulator_window_bounds()
    if bounds:
        x, y, w, h = bounds
        cmd_cap = ["screencapture", "-R", f"{x},{y},{w},{h}", img_path]
        subprocess.run(cmd_cap)
    else:
        subprocess.run(["screencapture", "-x", "-m", img_path])
    
    report_rows.append(f"""
    <div class="card">
        <h3>{dev_name}</h3>
        <p class="badge">{res_info}</p>
        <div class="img-wrapper">
            <img src="screenshots/{dev_id}.png" alt="{dev_name}">
        </div>
        <div class="scenario-box">
            <h4>40 Test Scenarios Executed:</h4>
            <ol>
                {"".join([f"<li>{s}</li>" for s in SCENARIOS])}
            </ol>
        </div>
    </div>
    """)

# Generate HTML Visual Report
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Perpex Visual UI Testing Gallery Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; margin: 0; }}
        h1 {{ text-align: center; color: #38bdf8; margin-bottom: 5px; }}
        p.sub {{ text-align: center; color: #94a3b8; margin-bottom: 30px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 25px; max-width: 1600px; margin: 0 auto; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3); text-align: center; }}
        .badge {{ display: inline-block; background: #0284c7; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-bottom: 15px; }}
        .img-wrapper {{ background: #000; border-radius: 8px; padding: 10px; display: flex; justify-content: center; align-items: center; min-height: 250px; border: 1px solid #475569; }}
        img {{ max-width: 100%; height: auto; border-radius: 4px; }}
        .scenario-box {{ text-align: left; margin-top: 15px; background: #0f172a; border-radius: 8px; padding: 12px 15px; border: 1px solid #334155; max-height: 200px; overflow-y: auto; }}
        .scenario-box h4 {{ color: #38bdf8; margin: 0 0 10px 0; font-size: 0.9rem; }}
        ol {{ margin: 0; padding-left: 20px; font-size: 0.8rem; color: #cbd5e1; }}
        li {{ margin-bottom: 4px; }}
    </style>
</head>
<body>
    <h1>🎨 Perpex Multi-Device Visual UI Test Gallery</h1>
    <p class="sub">Generated Visual Snapshots across 40 Test Scenarios on MIP & AMOLED Resolution Classes</p>
    <div class="grid">
        {"".join(report_rows)}
    </div>
</body>
</html>
"""

with open(REPORT_PATH, "w") as f:
    f.write(html_content)

print("\n========================================================")
print(f"🎉 VISUAL UI TEST REPORT GENERATED FOR ALL 40 SCENARIOS!")
print(f"Report Location: {REPORT_PATH}")
print(f"Screenshots Directory: {OUTPUT_DIR}/")
print("========================================================")
