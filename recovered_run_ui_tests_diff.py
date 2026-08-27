import os
import subprocess
import time
import argparse
from PIL import Image, ImageChops, ImageStat

SDK_PATH = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH = "developer_key.der"
OUTPUT_DIR = "test_output/screenshots"
BASELINE_DIR = "test_baselines"
REPORT_PATH = "test_output/visual_report.html"

DEVICES = [
    ("fenix7", "260x260 MIP Solar", "Fenix 7 / Fenix 9 Pro Solar 47mm"),
    ("enduro3", "280x280 MIP Solar", "Enduro 3 / Fenix 9 Pro Solar 51mm"),
    ("epix2pro42mm", "390x390 AMOLED", "Epix 2 Pro 42mm"),
    ("epix2", "416x416 AMOLED", "Epix Gen 2 47mm"),
    ("fenix847mm", "454x454 AMOLED", "Fenix 8 / Fenix 9 Pro 47mm"),
    ("venusq2", "320x360 AMOLED", "Venu Sq 2")
]

SCENARIOS = [
    "1. Battery Slot (50%, 10%, 100%)",
    "2. Heart Rate (80 BPM, 199 BPM)",
    "3. Step Counter (99,999 STEPS)",
    "4. Step Goal % (100% GOAL)",
    "5. Active Calories (1000 kCal)",
    "6. Distance (999.9 KM)",
    "7. Floors Climbed (999 FLOORS)",
    "8. Active Minutes (9,999 MINS)",
    "9. Stress Score (100 STRESS)",
    "10. Digital Time (23:59)"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(BASELINE_DIR, exist_ok=True)

def calculate_pixel_diff(img1_path, img2_path, diff_output_path):
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        return 0.0

    try:
        im1 = Image.open(img1_path).convert('RGB')
        im2 = Image.open(img2_path).convert('RGB')

        diff = ImageChops.difference(im1, im2)
        mask = diff.convert('L').point(lambda x: 255 if x > 5 else 0)
        
        stat_mask = ImageStat.Stat(mask)
        diff_pixels = stat_mask.sum[0] / 255.0
        total_pixels = mask.width * mask.height
        diff_pct = (diff_pixels / total_pixels) * 100
        
        im_mask = Image.new('RGB', im1.size, (255, 0, 0))
        result = Image.composite(im_mask, im2, mask)
        result.save(diff_output_path)

        return diff_pct
    except Exception as e:
        print(f"Error calculating diff: {e}")
        return 100.0

def get_simulator_window_bounds():
    for _ in range(15):
        try:
            script = 'tell application "System Events" to tell process "simulator" to get {position, size} of window 1'
            res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                parts = [int(x.strip()) for x in res.stdout.strip().split(',')]
                return parts[0], parts[1], parts[2], parts[3]
        except Exception:
            pass
        time.sleep(2)
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run UI visual tests")
    parser.add_argument("targets", nargs="*", help="Specific device IDs to run (e.g. fenix7). Runs all if empty.")
    parser.add_argument("--update-baselines", action="store_true", help="Update the baseline images with the new screenshots.")
    args = parser.parse_args()

    targets = args.targets if args.targets else [d[0] for d in DEVICES]
    devices_to_run = [d for d in DEVICES if d[0] in targets]

    print("========================================================")
    print("🎨 PERPEX VISUAL UI & SCREENSHOT TEST HARNESS")
    print("========================================================")
    
    report_rows = []

    for dev_id, res_info, dev_name in devices_to_run:
        print(f"\n📱 Generating Visual UI Snapshot for: {dev_name} ({dev_id})...")
        prg_path = f"bin/Visual_{dev_id}.prg"
        img_path = f"{OUTPUT_DIR}/{dev_id}.png"
        baseline_path = f"{BASELINE_DIR}/{dev_id}.png"
        diff_path = f"{OUTPUT_DIR}/{dev_id}_diff.png"
        
        cmd_build = [os.path.join(SDK_PATH, "bin/monkeyc"), "-f", "monkey.jungle", "-o", prg_path, "-d", dev_id, "-y", KEY_PATH]
        res_build = subprocess.run(cmd_build, capture_output=True, text=True)
        if res_build.returncode != 0:
            print(f"❌ Build failed for {dev_id}: {res_build.stderr}")
            continue
            
        cmd_do = [os.path.join(SDK_PATH, "bin/monkeydo"), prg_path, dev_id]
        subprocess.Popen(cmd_do, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(8)
        
        subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of (first process whose name is "simulator") to true'])
        time.sleep(1)
        
        bounds = get_simulator_window_bounds()
        if bounds:
            x, y, w, h = bounds
            subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", img_path])
        else:
            subprocess.run(["screencapture", "-x", "-m", img_path])
            
        if args.update_baselines:
            import shutil
            shutil.copy2(img_path, baseline_path)
            print(f"✅ Updated baseline for {dev_id}")
            
        diff_pct = 0.0
        diff_html = ""
        baseline_html = ""
        
        if os.path.exists(baseline_path):
            diff_pct = calculate_pixel_diff(baseline_path, img_path, diff_path)
            diff_html = f'<img src="{dev_id}_diff.png" alt="Diff">'
            baseline_html = f'<img src="../{BASELINE_DIR}/{dev_id}.png" alt="Baseline">'
            status = "✅ PASS" if diff_pct < 0.5 else "❌ FAIL"
        else:
            status = "⚠️ NO BASELINE"
            
        report_rows.append(f"""
        <div class="card">
            <h3>{dev_name}</h3>
            <p class="badge">{res_info}</p>
            <p><strong>Status:</strong> {status} (Diff: {diff_pct:.2f}%)</p>
            <div class="grid" style="grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                <div class="img-wrapper"><p>Baseline</p>{baseline_html}</div>
                <div class="img-wrapper"><p>Current</p><img src="{dev_id}.png" alt="Current"></div>
                <div class="img-wrapper"><p>Diff</p>{diff_html}</div>
            </div>
        </div>
        """)

    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Perpex Visual UI Testing Report</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; margin: 0; }}
            h1 {{ text-align: center; color: #38bdf8; margin-bottom: 5px; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; margin-bottom: 20px; }}
            .badge {{ display: inline-block; background: #0284c7; color: white; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; margin-bottom: 15px; }}
            .img-wrapper {{ background: #000; border-radius: 8px; padding: 10px; text-align: center; border: 1px solid #475569; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>🎨 Perpex Multi-Device Visual UI Test Report</h1>
        {"".join(report_rows)}
    </body>
    </html>
    """

    with open(REPORT_PATH, "w") as f:
        f.write(html_content)
    print(f"\n🎉 Report Location: {REPORT_PATH}")
