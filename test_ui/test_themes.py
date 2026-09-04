import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot
from .layout_validator import validate_layout

# ---------------------------------------------------------------------------
# Colour theme passes
# ---------------------------------------------------------------------------
THEME_PASSES = [
    {
        "id": "theme1",
        "name": "Theme: Vibrant Red (Default)",
        "description": "Standard Tactical Red theme accent on hands, date arcs, and status icons.",
        "expected": "Accent elements render in vibrant red (#FF3333).",
        "props": {"ThemeColor": 1, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "theme2",
        "name": "Theme: Teal / Cyan Accent",
        "description": "High-contrast Teal / Cyan theme accent.",
        "expected": "Accent elements render in vibrant cyan/teal (#00CCCC).",
        "props": {"ThemeColor": 2, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "theme3",
        "name": "Theme: Warm Orange Accent",
        "description": "High-visibility Warm Orange theme accent.",
        "expected": "Accent elements render in warm orange (#FF8800).",
        "props": {"ThemeColor": 3, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "theme4",
        "name": "Theme: Electric Green Accent",
        "description": "High-visibility Electric Green theme accent.",
        "expected": "Accent elements render in electric green (#00FF66).",
        "props": {"ThemeColor": 4, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "theme5",
        "name": "Theme: Gold / Yellow Accent",
        "description": "High-visibility Gold/Yellow theme accent.",
        "expected": "Accent elements render in bright gold (#FFFF00).",
        "props": {"ThemeColor": 5, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "theme6",
        "name": "Theme: Pure White Accent",
        "description": "Monochrome crisp Pure White theme accent.",
        "expected": "Accent elements render in pure white (#FFFFFF).",
        "props": {"ThemeColor": 6, "NightMode": 0, "TestHideHands": 1},
    },
    {
        "id": "night_red",
        "name": "Night Mode: Tactical Red",
        "description": "Tactical Red Night Mode for preserved night vision.",
        "expected": "All active elements shift to Tactical Red (#FF0000).",
        "props": {"NightMode": 3, "NightModeColor": 0, "TestHideHands": 1},
    },
    {
        "id": "night_amber",
        "name": "Night Mode: Night Amber",
        "description": "Night Amber mode for low-light legibility.",
        "expected": "All active elements shift to Amber (#FF8800).",
        "props": {"NightMode": 3, "NightModeColor": 1, "TestHideHands": 1},
    },
    {
        "id": "night_green",
        "name": "Night Mode: Stealth Green",
        "description": "Stealth Green mode for tactical night use.",
        "expected": "All active elements shift to Stealth Green (#00FF00).",
        "props": {"NightMode": 3, "NightModeColor": 2, "TestHideHands": 1},
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
    "props": {"NightMode": 0, "TestHideHands": 1, "LowPowerMode": 1},
}


def run_theme_tests(dev_id, dev_name, res_info, output_dir):
    """
    Runs all colour-theme passes + the low-power AOD pass for *dev_id*.

    Returns list[dict] – one entry per pass.
    """
    print(f"\n  🎨 Theme & Power Passes ({dev_name})")
    os.makedirs(output_dir, exist_ok=True)
    results = []

    all_passes = THEME_PASSES + [LOW_POWER_PASS]

    for tpass in all_passes:
        pid = tpass["id"]
        print(f"    → {tpass['name']}")
        set_properties(tpass["props"])

        prg_path  = f"bin/Visual_{dev_id}_{pid}.prg"
        img_path  = os.path.join(output_dir, f"{dev_id}_{pid}.png")

        if build_app(dev_id, prg_path):
            launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info)

        # By default all themes use the 7 standard slots
        val = validate_layout(img_path, [1, 2, 3, 4, 5, 6, 7])

        results.append({
            "pass_name":    tpass["name"],
            "description":  tpass["description"],
            "slots":        [f"Theme: {tpass['name']}", "NightMode: 0"],
            "expected":     tpass["expected"],
            "current_img":  img_path,
            "zones_img":    val["annotated_path"],
            "passed":       val["pass"],
            "issues":       val["issues"],
        })

    return results
