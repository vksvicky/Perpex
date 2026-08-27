import os
from .config_manager import set_properties
from .simulator_driver import build_app, launch_simulator_and_screenshot, OUTPUT_DIR
from .image_utils import calculate_pixel_diff

# 3 Configurations to test all 19 metrics across the 7 slots
PERMUTATION_PASSES = [
    {
        "name": "Permutation 1: Baseline (Metrics 1 to 7)",
        "description": "Standard fitness & activity metrics layout. Used as the baseline reference.",
        "slots": [
            "Slot 1: Battery (1)",
            "Slot 2: Heart Rate (2)",
            "Slot 3: Steps (3)",
            "Slot 4: Step Goal % (4)",
            "Slot 5: Calories (5)",
            "Slot 6: Distance (6)",
            "Slot 7: Floors Climbed (7)"
        ],
        "expected": "Displays battery gauge, HR, steps, goal %, calories, distance, and floors with icons and values centered.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
            "Slot7Metric": 7
        }
    },
    {
        "name": "Permutation 2: Sensor & Environmental (Metrics 8 to 14)",
        "description": "Stress, atmospheric sensors, digital clock, and weather metrics.",
        "slots": [
            "Slot 1: Active Minutes (8)",
            "Slot 2: Stress Score (9)",
            "Slot 3: Digital Time (10)",
            "Slot 4: Notifications (11)",
            "Slot 5: Altitude (12)",
            "Slot 6: Barometer Pressure (13)",
            "Slot 7: Weather Temperature (14)"
        ],
        "expected": "Verifies atmospheric/sensor icons and formatted data (e.g. hPa, meters, °C, active mins) render clearly without overlapping.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 8, "Slot2Metric": 9, "Slot3Metric": 10,
            "Slot4Metric": 11, "Slot5Metric": 12, "Slot6Metric": 13,
            "Slot7Metric": 14
        }
    },
    {
        "name": "Permutation 3: Solar, Weather & Battery (Metrics 15 to 19)",
        "description": "Weather conditions, dynamic solar times (sunrise/sunset), and Body Battery.",
        "slots": [
            "Slot 1: Weather Condition (15)",
            "Slot 2: Sun Times Solar Gauge (16)",
            "Slot 3: Body Battery (17)",
            "Slot 4: Next Sunrise (18)",
            "Slot 5: Next Sunset (19)",
            "Slot 6: Battery Backup (1)",
            "Slot 7: Heart Rate Backup (2)"
        ],
        "expected": "Verifies dynamic solar calculations (SunCalc sunrise/sunset times), precipitation text, and body battery render correctly.",
        "props": {
            "NightMode": 0,
            "Slot1Metric": 15, "Slot2Metric": 16, "Slot3Metric": 17,
            "Slot4Metric": 18, "Slot5Metric": 19, "Slot6Metric": 1,
            "Slot7Metric": 2
        }
    }
]

def run_permutation_tests(dev_id, dev_name):
    print(f"\n--- Running Dynamic Metric Permutations for {dev_name} ---")
    results = []
    
    for i, ppass in enumerate(PERMUTATION_PASSES):
        print(f"  Testing Pass {i+1}/3: {ppass['name']}")
        set_properties(ppass['props'])
        
        prg_path = f"bin/Visual_{dev_id}_perm{i+1}.prg"
        img_path = f"{OUTPUT_DIR}/{dev_id}_perm{i+1}.png"
        diff_path = f"{OUTPUT_DIR}/{dev_id}_perm{i+1}_diff.png"
        golden_path = f"test_baselines/{dev_id}_perm{i+1}.png"
        
        if build_app(dev_id, prg_path):
            if launch_simulator_and_screenshot(dev_id, prg_path, img_path):
                diff_pct = calculate_pixel_diff(golden_path, img_path, diff_path)
                results.append({
                    "pass_name": ppass['name'],
                    "description": ppass['description'],
                    "slots": ppass['slots'],
                    "expected": ppass['expected'],
                    "image": f"screenshots/{dev_id}_perm{i+1}.png",
                    "diff_image": f"screenshots/{dev_id}_perm{i+1}_diff.png" if diff_pct > 0 else None,
                    "diff_pct": diff_pct,
                    "has_baseline": os.path.exists(golden_path)
                })
    return results
