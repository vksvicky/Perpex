import os
import re
import subprocess
import time
from PIL import Image

SDK_PATH = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH = "developer_key.der"

def ensure_simulator_running():
    app_path = os.path.join(SDK_PATH, "bin/ConnectIQ.app")
    subprocess.run(["open", app_path])
    time.sleep(2)

def get_simulator_window_bounds():
    for _ in range(5):
        try:
            script = '''
            tell application "System Events"
                set procs to (every process whose name is "simulator" or name is "ConnectIQ")
                if (count of procs) > 0 then
                    set simProc to item 1 of procs
                    set frontmost of simProc to true
                    get {position, size} of window 1 of simProc
                else
                    return ""
                end if
            end tell
            '''
            res = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                parts = [int(x.strip()) for x in res.stdout.strip().split(',')]
                if len(parts) == 4:
                    return parts[0], parts[1], parts[2], parts[3]
        except Exception:
            pass
        time.sleep(1.5)
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

def launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info=None):
    ensure_simulator_running()
    cmd_do = [
        os.path.join(SDK_PATH, "bin/monkeydo"),
        prg_path,
        dev_id
    ]
    proc = subprocess.Popen(cmd_do, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(6)
    
    os.makedirs(os.path.dirname(img_path) or ".", exist_ok=True)
    bounds = get_simulator_window_bounds()
    if bounds:
        x, y, w, h = bounds
        subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", img_path])
    else:
        subprocess.run(["screencapture", "-x", "-m", img_path])
    if os.path.exists(img_path):
        _crop_to_watch_face(img_path, res_info, img_path)
    return True

def _crop_to_watch_face(src_path, res_info, dst_path):
    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    dev_w, dev_h = None, None
    if res_info:
        m = re.search(r"(\d+)[x×](\d+)", res_info)
        if m:
            dev_w, dev_h = int(m.group(1)), int(m.group(2))
    if dev_w is None or (w <= dev_w and h <= dev_h):
        if src_path != dst_path:
            img.save(dst_path)
        return

    pixels = img.load()
    min_x, max_x = w, 0
    min_y, max_y = h, 0
    margin_x = int(w * 0.1)
    margin_y = int(h * 0.15)
    for y in range(margin_y, h - margin_y):
        for x in range(margin_x, w - margin_x):
            r, g, b = pixels[x, y]
            if max(r, g, b) < 15:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

    scale = round(w / dev_w) if w > dev_w else 1
    scale = max(1, min(scale, 3))
    phy_w = dev_w * scale
    phy_h = dev_h * scale

    if min_x < max_x and min_y < max_y:
        cx = (min_x + max_x) // 2
        cy = (min_y + max_y) // 2
        bbox_w = max_x - min_x + 1
        scale = round(bbox_w / dev_w)
        scale = max(1, min(scale, 3))
        phy_w = dev_w * scale
        phy_h = dev_h * scale
        l = max(0, cx - (phy_w // 2))
        t = max(0, cy - (phy_h // 2))
        cropped = img.crop((l, t, l + phy_w, t + phy_h))
    else:
        cl = max(0, (w - phy_w) // 2)
        ct = max(0, (h - phy_h) // 2)
        cropped = img.crop((cl, ct, cl + phy_w, ct + phy_h))

    if cropped.size != (dev_w, dev_h):
        cropped = cropped.resize((dev_w, dev_h), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)
    cropped.save(dst_path)
