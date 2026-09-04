import os
import re
import subprocess
import time
from PIL import Image

SDK_PATH = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks/connectiq-sdk-mac-9.2.0-2026-06-09-92a1605b2")
KEY_PATH = "developer_key.der"

_CURRENT_DEVICE = None
DEVICES_DIR = os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Devices")

def ensure_simulator_running(target_dev_id=None):
    global _CURRENT_DEVICE
    # If switching to a different device, kill the existing simulator so it loads the new device window
    if target_dev_id and _CURRENT_DEVICE is not None and _CURRENT_DEVICE != target_dev_id:
        subprocess.run(["killall", "-9", "simulator", "ConnectIQ"], capture_output=True)
        time.sleep(1.5)
        _CURRENT_DEVICE = None

    app_path = os.path.join(SDK_PATH, "bin/ConnectIQ.app")
    subprocess.run(["open", app_path])
    time.sleep(4)
    if target_dev_id:
        _CURRENT_DEVICE = target_dev_id

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

def kill_running_simulator_app():
    """Tells Garmin simulator to 'Kill App' cleanly so the next app loads immediately without hanging."""
    script = '''
    tell application "System Events"
        set procs to (every process whose name is "simulator" or name is "ConnectIQ")
        if (count of procs) > 0 then
            try
                click menu item "Kill App" of menu 1 of menu bar item "File" of menu bar 1 of item 1 of procs
            end try
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script], capture_output=True)

def launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info=None):
    # Clean any previous monkeydo/MonkeyDoDeux instances and tell simulator to kill active app
    subprocess.run(["killall", "-9", "monkeydo"], capture_output=True)
    subprocess.run(["pkill", "-9", "-f", "MonkeyDoDeux"], capture_output=True)
    kill_running_simulator_app()
    ensure_simulator_running(target_dev_id=dev_id)
    time.sleep(0.5)
    cmd_do = [
        os.path.join(SDK_PATH, "bin/monkeydo"),
        prg_path,
        dev_id
    ]
    proc = subprocess.Popen(cmd_do, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5)
    
    os.makedirs(os.path.dirname(img_path) or ".", exist_ok=True)
    raw_tmp = img_path + ".raw.png"
    
    captured = False
    for attempt in range(6):
        bounds = get_simulator_window_bounds()
        if bounds:
            x, y, w, h = bounds
            subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", raw_tmp])
        else:
            subprocess.run(["screencapture", "-x", "-m", raw_tmp])
        
        if os.path.exists(raw_tmp):
            success = _crop_to_watch_face(raw_tmp, res_info, img_path, dev_id=dev_id, window_bounds=bounds)
            if success:
                captured = True
                try:
                    os.remove(raw_tmp)
                except Exception:
                    pass
                break
        time.sleep(2.0)

    if os.path.exists(raw_tmp):
        try:
            os.remove(raw_tmp)
        except Exception:
            pass

    if not captured and os.path.exists(img_path):
        try:
            os.remove(img_path)
        except Exception:
            pass

    try:
        proc.terminate()
        proc.wait(timeout=1)
    except Exception:
        pass

    return captured

def _crop_to_watch_face(src_path, res_info, dst_path, dev_id=None, window_bounds=None):
    img = Image.open(src_path).convert("RGB")
    img_w, img_h = img.size

    # Check SDK display location metadata first
    dev_h = None
    if dev_id:
        sim_json = os.path.join(DEVICES_DIR, dev_id, "simulator.json")
        if os.path.exists(sim_json):
            try:
                import json
                with open(sim_json) as f:
                    d = json.load(f)
                    sdk_loc = d.get("display", {}).get("location")
                    img_name = d.get("image")
                    if img_name:
                        skin_path = os.path.join(DEVICES_DIR, dev_id, img_name)
                        if os.path.exists(skin_path):
                            with Image.open(skin_path) as skin_img:
                                _, dev_h = skin_img.size
            except Exception:
                sdk_loc = None

    if sdk_loc and window_bounds:
        _, _, win_w, win_h = window_bounds
        scale = img_w / float(win_w)
        titlebar_px = 56
        crop_x1 = max(0, int(sdk_loc["x"] * scale))
        crop_y1 = max(0, int(sdk_loc["y"] * scale) + titlebar_px)
        crop_x2 = min(img_w, crop_x1 + int(sdk_loc["width"] * scale))
        crop_y2 = min(img_h, crop_y1 + int(sdk_loc["height"] * scale))
        cropped = img.crop((crop_x1, crop_y1, crop_x2, crop_y2))
        target_w, target_h = sdk_loc["width"], sdk_loc["height"]
    else:
        # Fallback to resolution string
        target_w, target_h = None, None
        if res_info:
            m = re.search(r"(\d+)[x×](\d+)", res_info)
            if m:
                target_w, target_h = int(m.group(1)), int(m.group(2))
        if target_w is None or (img_w <= target_w and img_h <= target_h):
            if src_path != dst_path:
                img.save(dst_path)
            return True
        cropped = img

    # Check for blue triangle boot screen or blank screen
    c_w, c_h = cropped.size
    pixels = cropped.load()
    dark_count = 0
    blue_triangle_count = 0
    step = 2
    for y in range(0, c_h, step):
        for x in range(0, c_w, step):
            r, g, b = pixels[x, y]
            if max(r, g, b) < 40:
                dark_count += 1
            if 30 < r < 95 and 100 < g < 175 and 165 < b < 245:
                blue_triangle_count += 1

    total_samples = (c_w // step) * (c_h // step)
    # Real Garmin boot triangle covers > 2-5% of screen; icons/dials have < 0.2%
    is_boot_triangle = (blue_triangle_count > 1500) or (blue_triangle_count / total_samples > 0.015)
    if is_boot_triangle or (dark_count / total_samples) < 0.2:
        return False

    if target_w and target_h and cropped.size != (target_w, target_h):
        cropped = cropped.resize((target_w, target_h), Image.LANCZOS)

    os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)
    cropped.save(dst_path)
    return True
