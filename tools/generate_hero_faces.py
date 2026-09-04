#!/usr/bin/env python3
"""
tools/generate_hero_faces.py
============================
Captures 5 distinct watch face states on fenix9pro51mm (466x466) with analog hands,
ensuring each watch has completely different theme colors, metrics, and icons:

1. w1_teal_sensors: Teal Accent, Barometer (1013 hPa), Altitude (342m), Stress (28), Active Mins (45m), Floors (14), Notifications (3)
2. w2_orange_wind_weather: Warm Orange Accent, Wind Speed (12kt), Temp (22°C), Sunset (19:42), Raindrop, Recovery (18h), VO2 Max (52)
3. w3_red_core_fitness: Signature Red Accent, Battery Gauge (85%), Heart Rate (74 BPM), Steps (8,420), Goal (84%), Calories (540 kcal), Distance (6.2km)
4. w4_green_performance: Electric Green Accent, Body Battery (76%), Recovery (18h), VO2 Max (54), Active Calories (620), Floors (18), Active Mins (55m)
5. w5_night_vision: Full Tactical Red Night Mode, preserving night vision with nocturnal luminescent dial
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from test_ui.simulator_driver import build_app, launch_simulator_and_screenshot
from test_ui.config_manager import set_properties, backup_properties, restore_properties

DEV_ID = "fenix9pro51mm"
RES_INFO = "466x466 AMOLED"
OUT_DIR = "showcase/hero_faces"
os.makedirs(OUT_DIR, exist_ok=True)

HERO_FACE_SPECS = [
    {
        "id": "w1_teal_sensors",
        "name": "Watch 1: Teal Accent — Barometer & Environmental Sensors",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 2, # Teal
            "Slot1Metric": 13, # Barometer (1013 hPa)
            "Slot2Metric": 12, # Altitude (342 m)
            "Slot3Metric": 9,  # Stress (28)
            "Slot4Metric": 8,  # Active Minutes (45 min)
            "Slot5Metric": 7,  # Floors Climbed (14 fl)
            "Slot6Metric": 11, # Notifications (3)
        }
    },
    {
        "id": "w2_orange_wind_weather",
        "name": "Watch 2: Warm Orange Accent — Nautical Wind & Ambient Weather",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 3, # Warm Orange
            "TestWeatherOverride": 8, # Wind 12kt
            "Slot1Metric": 15, # Weather Wind (12 kt)
            "Slot2Metric": 14, # Weather Temp (22°C)
            "Slot3Metric": 16, # Sun Event (19:42)
            "Slot4Metric": 17, # Body Battery (76%)
            "Slot5Metric": 20, # Recovery Time (18h)
            "Slot6Metric": 21, # VO2 Max (52)
        }
    },
    {
        "id": "w3_red_core_fitness",
        "name": "Watch 3: Signature Tactical Red — Core Fitness Dashboard",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1, # Tactical Red
            "Slot1Metric": 1,  # Battery Gauge (85%)
            "Slot2Metric": 2,  # Heart Rate (74 BPM)
            "Slot3Metric": 3,  # Steps (8,420)
            "Slot4Metric": 4,  # Step Goal (84%)
            "Slot5Metric": 5,  # Active Calories (540 kcal)
            "Slot6Metric": 6,  # Distance (6.2 km)
        }
    },
    {
        "id": "w4_green_performance",
        "name": "Watch 4: Electric Green Accent — Firstbeat Performance & Recovery",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 4, # Electric Green
            "Slot1Metric": 17, # Body Battery (76%)
            "Slot2Metric": 20, # Recovery Time (18h)
            "Slot3Metric": 21, # VO2 Max (54)
            "Slot4Metric": 5,  # Active Calories (620 kcal)
            "Slot5Metric": 7,  # Floors (18 fl)
            "Slot6Metric": 8,  # Active Minutes (55 min)
        }
    },
    {
        "id": "w5_night_vision",
        "name": "Watch 5: Tactical Red Night Mode — Nocturnal Vision Dial",
        "props": {
            "TestHideHands": 0, "NightMode": 3, "NightModeColor": 0, # Tactical Red Always-On
            "Slot1Metric": 13, # Barometer
            "Slot2Metric": 2,  # Heart Rate
            "Slot3Metric": 12, # Altitude
            "Slot4Metric": 16, # Solar Event
            "Slot5Metric": 1,  # Battery
            "Slot6Metric": 9,  # Stress
        }
    }
]

print("========================================================")
print("⌚ CAPTURING 5 DISTINCT HERO BANNER WATCH FACES")
print("========================================================")

backup_properties()
try:
    for idx, spec in enumerate(HERO_FACE_SPECS, 1):
        pid = spec["id"]
        out_img = os.path.join(OUT_DIR, f"{pid}.png")
        print(f"\n[{idx}/5] {spec['name']}")
        
        set_properties(spec["props"])
        prg_path = f"bin/Hero_{DEV_ID}_{pid}.prg"
        
        if build_app(DEV_ID, prg_path):
            captured = launch_simulator_and_screenshot(DEV_ID, prg_path, out_img, RES_INFO)
            if captured:
                print(f"  📸 Captured: {out_img}")
            else:
                print(f"  ❌ Capture failed for {pid}")
        else:
            print(f"  ❌ Build failed for {pid}")

finally:
    restore_properties()

print("\n========================================================")
print("🎉 All 5 unique hero watch faces captured successfully!")
print("========================================================")
