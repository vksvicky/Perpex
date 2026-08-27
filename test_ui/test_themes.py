import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot
from .image_utils import make_3panel_diff

# ---------------------------------------------------------------------------
# Colour theme passes
# ---------------------------------------------------------------------------
THEME_PASSES = [
    {
        "id": "theme1",
        "name": "Theme: Vibrant Red (Default)",
        "description": "Standard Tactical Red theme accent on hands, date arcs, and status icons.",
        "expected": "Accent elements render in vibrant red (#FF3333).",
        "props": {"ThemeColor": 1, "NightMode": 0},
    },
    {
        "id": "theme2",
        "name": "Theme: Teal / Cyan Accent",
        "description": "High-contrast Teal / Cyan theme accent.",
        "expected": "Accent elements render in vibrant cyan/teal (#00CCCC).",
        "props": {"ThemeColor": 2, "NightMode": 0},
    },
    {
        "id": "theme3",
        "name": "Theme: Warm Orange Accent",
        "description": "High-visibility Warm Orange theme accent.",
        "expected": "Accent elements render in warm orange (#FF8800).",
        "props": {"ThemeColor": 3, "NightMode": 0},
    },
]

# ---------------------------------------------------------------------------
# Power / AOD pass
# ---------------------------------------------------------------------------
LOW_POWER_PASS = {
    "id": "low_power",
    "name": "Low-Power AOD Mode",
    "description": "Always-on display: dimmed grey face, hidden dial background, minimal hands.",
    "expected": "All accent elements dimmed to grey. Dial background hidden. Seconds hidden.",
    "props": {"NightMode": 0, "LowPowerMode": 1},
}


def run_theme_tests(dev_id, dev_name, output_dir, baselines_dir, diffs_dir):
    """
    Runs all colour-theme passes + the low-power AOD pass for *dev_id*.

    Returns list[dict] – one entry per pass.
    """
    print(f"\n  🎨 Theme & Power Passes ({dev_name})")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(diffs_dir, exist_ok=True)
    results = []

    all_passes = THEME_PASSES + [LOW_POWER_PASS]

    for tpass in all_passes:
        pid = tpass["id"]
        print(f"    → {tpass['name']}")
        set_properties(tpass["props"])

        prg_path  = f"bin/Visual_{dev_id}_{pid}.prg"
        img_path  = os.path.join(output_dir,    f"{dev_id}_{pid}.png")
        base_path = os.path.join(baselines_dir,  f"{dev_id}_{pid}.png")
        diff_path = os.path.join(diffs_dir,      f"{dev_id}_{pid}.png")

        if build_app(dev_id, prg_path):
            launch_simulator_and_screenshot(dev_id, prg_path, img_path)

        diff_result = make_3panel_diff(base_path, img_path, diff_path)
        results.append({
            "pass_name":    tpass["name"],
            "description":  tpass["description"],
            "slots":        [f"Theme: {tpass['name']}", "NightMode: 0"],
            "expected":     tpass["expected"],
            "baseline_img": base_path,
            "current_img":  img_path,
            "diff_img":     diff_result["composite_path"],
            "diff_pct":     diff_result["diff_pct"],
            "has_baseline": diff_result["has_baseline"],
        })

    return results
