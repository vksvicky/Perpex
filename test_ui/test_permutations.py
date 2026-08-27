import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot
from .image_utils import make_3panel_diff

# ---------------------------------------------------------------------------
# 3 Permutation passes covering all 19 metrics across 7 slots
# ---------------------------------------------------------------------------
PERMUTATION_PASSES = [
    {
        "id": "perm1",
        "name": "Permutation 1: Core Activity (Metrics 1–7)",
        "description": "Standard fitness & activity metrics layout.",
        "slots": [
            "Slot 1: Battery (1)",
            "Slot 2: Heart Rate (2)",
            "Slot 3: Steps (3)",
            "Slot 4: Step Goal % (4)",
            "Slot 5: Active Calories (5)",
            "Slot 6: Distance (6)",
            "Slot 7: Floors Climbed (7)",
        ],
        "expected": "Battery gauge, HR, steps, goal %, calories, distance and floors with icons and values centred.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
            "Slot7Metric": 7,
        },
    },
    {
        "id": "perm2",
        "name": "Permutation 2: Sensors & Environment (Metrics 8–14)",
        "description": "Stress, atmospheric sensors, digital clock, and weather metrics.",
        "slots": [
            "Slot 1: Active Minutes (8)",
            "Slot 2: Stress Score (9)",
            "Slot 3: Digital Time (10)",
            "Slot 4: Notifications (11)",
            "Slot 5: Altitude (12)",
            "Slot 6: Barometer (13)",
            "Slot 7: Weather Temp (14)",
        ],
        "expected": "Atmospheric/sensor icons and formatted data (hPa, metres, °C, active mins) render without overlap.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 8,  "Slot2Metric": 9,  "Slot3Metric": 10,
            "Slot4Metric": 11, "Slot5Metric": 12, "Slot6Metric": 13,
            "Slot7Metric": 14,
        },
    },
    {
        "id": "perm3",
        "name": "Permutation 3: Solar, Weather & Body Battery (Metrics 15–19)",
        "description": "Weather conditions, dynamic solar times (sunrise/sunset), and Body Battery.",
        "slots": [
            "Slot 1: Weather Condition (15)",
            "Slot 2: Sun Times / Solar Gauge (16)",
            "Slot 3: Body Battery (17)",
            "Slot 4: Next Sunrise (18)",
            "Slot 5: Next Sunset (19)",
            "Slot 6: Battery Backup (1)",
            "Slot 7: Heart Rate Backup (2)",
        ],
        "expected": "Dynamic solar calculations, precipitation text, and body battery render correctly.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 15, "Slot2Metric": 16, "Slot3Metric": 17,
            "Slot4Metric": 18, "Slot5Metric": 19, "Slot6Metric": 1,
            "Slot7Metric": 2,
        },
    },
]


def run_permutation_tests(dev_id, dev_name, output_dir, baselines_dir, diffs_dir):
    """
    Runs all 3 metric permutation passes for *dev_id*.

    Args:
        dev_id:       Garmin device identifier (e.g. "fenix7")
        dev_name:     Human-readable name for reporting
        output_dir:   Directory for current-branch screenshots
        baselines_dir: Directory containing baseline images from main
        diffs_dir:    Directory to write 3-panel diff composites

    Returns:
        list[dict] – one result entry per pass
    """
    print(f"\n  📊 Metric Permutations ({dev_name})")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(diffs_dir, exist_ok=True)
    results = []

    for ppass in PERMUTATION_PASSES:
        pid = ppass["id"]
        print(f"    → {ppass['name']}")
        set_properties(ppass["props"])

        prg_path  = f"bin/Visual_{dev_id}_{pid}.prg"
        img_path  = os.path.join(output_dir,   f"{dev_id}_{pid}.png")
        base_path = os.path.join(baselines_dir, f"{dev_id}_{pid}.png")
        diff_path = os.path.join(diffs_dir,     f"{dev_id}_{pid}.png")

        if build_app(dev_id, prg_path):
            launch_simulator_and_screenshot(dev_id, prg_path, img_path)

        diff_result = make_3panel_diff(base_path, img_path, diff_path)
        results.append({
            "pass_name":    ppass["name"],
            "description":  ppass["description"],
            "slots":        ppass["slots"],
            "expected":     ppass["expected"],
            "baseline_img": base_path,
            "current_img":  img_path,
            "diff_img":     diff_result["composite_path"],
            "diff_pct":     diff_result["diff_pct"],
            "has_baseline": diff_result["has_baseline"],
        })

    return results
