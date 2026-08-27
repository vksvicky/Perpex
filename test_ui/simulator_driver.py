import os
import time
import subprocess
from PIL import Image, ImageChops

SDK_PATH = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH = "developer_key.der"
OUTPUT_DIR = "test_output/screenshots"

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
    return None

def build_app(dev_id, output_path):
    cmd_build = [
        os.path.join(SDK_PATH, "bin/monkeyc"),
        "-f", "monkey.jungle",
        "-o", output_path,
        "-d", dev_id,
        "-y", KEY_PATH
    ]
    res_build = subprocess.run(cmd_build, capture_output=True, text=True)
    if res_build.returncode != 0:
        print(f"❌ Build failed for {dev_id}: {res_build.stderr}")
        return False
    return True

def launch_simulator_and_screenshot(dev_id, prg_path, img_path):
    cmd_do = [
        os.path.join(SDK_PATH, "bin/monkeydo"),
        prg_path,
        dev_id
    ]
    
    # Launch in simulator
    proc = subprocess.Popen(cmd_do, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8) # Wait for simulator to render
    
    # Bring simulator to front
    subprocess.run(['osascript', '-e', 'tell application "System Events" to set frontmost of (first process whose name is "simulator") to true'])
    time.sleep(1)
    
    # Capture screen
    bounds = get_simulator_window_bounds()
    if bounds:
        x, y, w, h = bounds
        cmd_cap = ["screencapture", "-R", f"{x},{y},{w},{h}", img_path]
        subprocess.run(cmd_cap)
    else:
        subprocess.run(["screencapture", "-x", "-m", img_path])
        
    return True

def calculate_pixel_diff(baseline_path, current_path, diff_output_path):
    """
    Compares two screenshots. If they differ, generates a diff mask highlighting the differences in red.
    Returns the percentage of pixels that differ.
    """
    if not os.path.exists(baseline_path) or not os.path.exists(current_path):
        return 0.0

    img1 = Image.open(baseline_path).convert("RGB")
    img2 = Image.open(current_path).convert("RGB")
    
    # Ensure same size
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)

    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    
    if bbox:
        # Convert difference to a grayscale mask
        mask = diff.convert("L")
        # Apply threshold so any small difference becomes white
        mask = mask.point(lambda p: 255 if p > 5 else 0)
        
        # Calculate percentage of pixels that differ
        diff_pixels = sum(mask.getdata()) / 255.0
        total_pixels = img1.size[0] * img1.size[1]
        pct = (diff_pixels / total_pixels) * 100.0
        
        # Create a red overlay
        red_layer = Image.new("RGB", img2.size, (255, 0, 0))
        # Composite the red layer over the current image using the diff mask
        highlighted = Image.composite(red_layer, img2, mask)
        highlighted.save(diff_output_path)
        
        return pct
        
    return 0.0
