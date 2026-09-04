import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot
from .layout_validator import validate_layout

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
        ],
        "active_slot_ids": [1, 2, 3, 4, 5, 6],
        "expected": "Battery gauge, HR, steps, goal %, calories and distance with icons and values centred.",
        "props": {
            "NightMode": 0, "TestHideHands": 1,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
    },
    {
        "id": "perm2",
        "name": "Permutation 2: Sensors, Alerts & Atmosphere (Metrics 7–13)",
        "description": "Floors climbed, active minutes, stress score, notifications, altitude, and barometer.",
        "slots": [
            "Slot 1: Floors Climbed (7)",
            "Slot 2: Active Minutes (8)",
            "Slot 3: Stress Score (9)",
            "Slot 4: Notifications (11)",
            "Slot 5: Altitude (12)",
            "Slot 6: Barometer (13)",
        ],
        "active_slot_ids": [1, 2, 3, 4, 5, 6],
        "expected": "Atmospheric, sensor and alert icons and formatted data (hPa, metres, active mins) render cleanly without overlap.",
        "props": {
            "NightMode": 0, "TestHideHands": 1,
            "Slot1Metric": 7,  "Slot2Metric": 8,  "Slot3Metric": 9,
            "Slot4Metric": 11, "Slot5Metric": 12, "Slot6Metric": 13,
        },
    },
    {
        "id": "perm3",
        "name": "Permutation 3: Solar, Weather & Performance (Metrics 14–21)",
        "description": "Weather temp, weather conditions, dynamic solar times, Body Battery, Recovery Time, and VO2 Max.",
        "slots": [
            "Slot 1: Weather Temp (14)",
            "Slot 2: Weather Condition (15)",
            "Slot 3: Sun Times Dynamic (16)",
            "Slot 4: Body Battery (17)",
            "Slot 5: Recovery Time (20)",
            "Slot 6: VO2 Max (21)",
        ],
        "active_slot_ids": [1, 2, 3, 4, 5, 6],
        "expected": "Weather temp, condition, dynamic solar, Body Battery, Recovery Time, and VO2 Max render with crisp icons and values.",
        "props": {
            "NightMode": 0, "TestHideHands": 1,
            "Slot1Metric": 14, "Slot2Metric": 15, "Slot3Metric": 16,
            "Slot4Metric": 17, "Slot5Metric": 20, "Slot6Metric": 21,
        },
    },
]


def run_permutation_tests(dev_id, dev_name, res_info, output_dir):
    """
    Runs all 3 metric permutation passes for *dev_id*.

    Args:
        dev_id:       Garmin device identifier (e.g. "fenix7")
        dev_name:     Human-readable name for reporting
        res_info:     Resolution string (e.g. "454×454 AMOLED")
        output_dir:   Directory for current-branch screenshots

    Returns:
        list[dict] – one result entry per pass
    """
    print(f"\n  📊 Metric Permutations ({dev_name})")
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for ppass in PERMUTATION_PASSES:
        pid = ppass["id"]
        print(f"    → {ppass['name']}")
        set_properties(ppass["props"])

        prg_path  = f"bin/Visual_{dev_id}_{pid}.prg"
        img_path  = os.path.join(output_dir, f"{dev_id}_{pid}.png")

        captured = False
        val = {"pass": False, "issues": ["Build failed"], "annotated_path": None}
        if build_app(dev_id, prg_path):
            captured = launch_simulator_and_screenshot(dev_id, prg_path, img_path, res_info)
            if captured:
                val = validate_layout(img_path, ppass["active_slot_ids"])
            else:
                val = {"pass": False, "issues": ["Simulator capture timed out / failed"], "annotated_path": None}

        results.append({
            "id":           pid,
            "pass_name":    ppass["name"],
            "description":  ppass["description"],
            "slots":        ppass["slots"],
            "expected":     ppass["expected"],
            "current_img":  img_path if captured else None,
            "zones_img":    val.get("annotated_path") if captured else None,
            "passed":       val.get("pass", False),
            "issues":       list(val.get("issues", [])),
        })

    return results
