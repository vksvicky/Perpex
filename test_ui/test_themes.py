import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot, OUTPUT_DIR
from .image_utils import calculate_pixel_diff

THEME_PASSES = [
    {
        "name": "Theme: Vibrant Red (Default Baseline)",
        "description": "Standard Tactical Red theme color accent on hands, date arcs, and status icons.",
        "expected": "Accent elements (arcs, indicators, hand highlights) render in vibrant red (#FF3333).",
        "props": { "ThemeColor": 1, "NightMode": 0 }
    },
    {
        "name": "Theme: Teal / Cyan Accent",
        "description": "High-contrast Teal / Cyan theme color accent.",
        "expected": "Accent elements (arcs, indicators, hand highlights) render in vibrant cyan / teal (#00CCCC).",
        "props": { "ThemeColor": 2, "NightMode": 0 }
    },
    {
        "name": "Theme: Warm Orange Accent",
        "description": "High-visibility Warm Orange theme color accent.",
        "expected": "Accent elements (arcs, indicators, hand highlights) render in pure warm orange (#FF8800).",
        "props": { "ThemeColor": 3, "NightMode": 0 }
    }
]

def run_theme_tests(dev_id, dev_name):
    print(f"\n--- Running Theme Permutations for {dev_name} ---")
    results = []
    
    for i, tpass in enumerate(THEME_PASSES):
        print(f"  Testing Theme Pass {i+1}/{len(THEME_PASSES)}: {tpass['name']}")
        set_properties(tpass['props'])
        
        prg_path = f"bin/Visual_{dev_id}_theme{i+1}.prg"
        img_path = f"{OUTPUT_DIR}/{dev_id}_theme{i+1}.png"
        diff_path = f"{OUTPUT_DIR}/{dev_id}_theme{i+1}_diff.png"
        golden_path = f"test_baselines/{dev_id}_theme{i+1}.png"
        
        if build_app(dev_id, prg_path):
            if launch_simulator_and_screenshot(dev_id, prg_path, img_path):
                diff_pct = calculate_pixel_diff(golden_path, img_path, diff_path)
                results.append({
                    "pass_name": tpass['name'],
                    "description": tpass['description'],
                    "slots": [f"Theme Color: {tpass['name']}", "Night Mode: Disabled (0)"],
                    "expected": tpass['expected'],
                    "image": f"screenshots/{dev_id}_theme{i+1}.png",
                    "diff_image": f"screenshots/{dev_id}_theme{i+1}_diff.png" if diff_pct > 0 else None,
                    "diff_pct": diff_pct,
                    "has_baseline": os.path.exists(golden_path)
                })
    return results
