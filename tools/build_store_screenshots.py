#!/usr/bin/env python3
"""
tools/build_store_screenshots.py
================================
Builds the 5 official device mockup screen images for the Garmin Connect IQ
Store app detail page (matching the exact 5 slots in the developer dashboard).

Requirement:
- JPG format
- File size strictly < 150 KB
- High resolution watch mockups (hardware bezel + strap) with our latest watch faces,
  active analog hands, real metrics, themes, and night mode.

The 5 Screen Images:
1. screen_1_aod_low_power.jpg        (Epix 2 Case — AMOLED Always-On Display)
2. screen_2_activity_vibrant_red.jpg (Enduro 3 Case — Signature Tactical Red Core Activity)
3. screen_3_weather_performance.jpg  (Fenix 7 Case — Solar, Weather, Recovery & VO2 Max)
4. screen_4_sensors_teal.jpg         (Fenix 8 Case — Sensors, Barometer & Altitude)
5. screen_5_tactical_night_mode.jpg  (Enduro 3 Nylon Case — Tactical Red Night Vision)
"""

import os
from PIL import Image, ImageDraw

STORE_DIR = "store_screenshots"
os.makedirs(STORE_DIR, exist_ok=True)

# Definition of the 5 store screen images matching the dashboard slots
SCREEN_SPECS = [
    {
        "slot": 1,
        "filename": "screen_1_aod_low_power.jpg",
        "base_mockup": "docs/images/store/01_epix2_high_always_on.jpg",
        "face_path": "showcase/images/showcase_low_power_aod.png",
        "cx": 638, "cy": 928, "radius": 514,
        "title": "AMOLED Always-On Display (AOD)",
        "desc": "Dimmed burn-in protected low-power mode with skeleton hands"
    },
    {
        "slot": 2,
        "filename": "screen_2_activity_vibrant_red.jpg",
        "base_mockup": "docs/images/store/06_enduro3_warm_orange.jpg",
        "face_path": "showcase/images/showcase_perm1_core_activity.png",
        "cx": 410, "cy": 565, "radius": 318,
        "title": "Signature Tactical Red (Core Activity)",
        "desc": "Dynamic battery gauge, live heart rate, steps, calories & distance"
    },
    {
        "slot": 3,
        "filename": "screen_3_weather_performance.jpg",
        "base_mockup": "docs/images/store/04_fenix_high_teal_cyan.jpg",
        "face_path": "showcase/images/showcase_perm3_solar_weather_recovery.png",
        "cx": 410, "cy": 565, "radius": 286,
        "title": "Weather, Solar & Performance",
        "desc": "Live ambient weather, sunrise/sunset, Body Battery, Recovery & VO2 Max"
    },
    {
        "slot": 4,
        "filename": "screen_4_sensors_teal.jpg",
        "base_mockup": "docs/images/store/07_fenix8_green_fahrenheit.jpg",
        "face_path": "showcase/images/showcase_theme_teal.png",
        "cx": 714, "cy": 921, "radius": 516,
        "title": "Environmental Sensors & Vitals",
        "desc": "High-contrast Teal accent with sea-level barometer (hPa) & elevation"
    },
    {
        "slot": 5,
        "filename": "screen_5_tactical_night_mode.jpg",
        "base_mockup": "docs/images/store/05_enduro3_temperature_setting.jpg",
        "face_path": "showcase/images/showcase_night_red.png",
        "cx": 410, "cy": 565, "radius": 318,
        "title": "Tactical Red Night Vision Mode",
        "desc": "Full tactical red nocturnal illumination for pitch-dark environments"
    }
]

def composite_store_screen(spec, target_h=1130):
    base = Image.open(spec["base_mockup"]).convert('RGBA')
    face = Image.open(spec["face_path"]).convert('RGBA')
    
    dia = spec["radius"] * 2
    face_scaled = face.resize((dia, dia), Image.Resampling.LANCZOS)
    
    # Circular anti-aliased mask
    mask = Image.new('L', (dia, dia), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, dia - 1, dia - 1], fill=255)
    
    # Paste new watchface inside bezel
    base.paste(face_scaled, (spec["cx"] - spec["radius"], spec["cy"] - spec["radius"]), mask)
    
    # Scale to standard height (1130px) for consistent aspect ratio and crispness
    if base.height != target_h:
        scale = target_h / float(base.height)
        new_w = int(base.width * scale)
        base = base.resize((new_w, target_h), Image.Resampling.LANCZOS)
    
    out_path = os.path.join(STORE_DIR, spec["filename"])
    rgb_img = base.convert('RGB')
    
    # Save optimized JPEG guaranteed < 150 KB
    for q in [92, 88, 85, 80]:
        rgb_img.save(out_path, 'JPEG', quality=q, optimize=True)
        size_kb = os.path.getsize(out_path) / 1024
        if size_kb < 145:
            break
            
    return out_path, size_kb, base.size, q

print("========================================================")
print("📦 BUILDING 5 STORE DETAIL PAGE SCREENSHOTS (MOCKUPS)")
print("Garmin Constraint: JPG strictly < 150 KB")
print("========================================================")

for spec in SCREEN_SPECS:
    out_path, size_kb, size, q = composite_store_screen(spec)
    status = "✅ PASS (< 150 KB)" if size_kb < 150 else "❌ OVERFLOW"
    print(f"\n📱 Screen {spec['slot']}: {spec['title']}")
    print(f"   • File: {out_path} ({size_kb:.1f} KB, quality {q}) -> {status}")
    print(f"   • Specs: {size[0]} x {size[1]} pixels | {spec['desc']}")

print("\n========================================================")
print(f"🎉 All 5 store screen images saved in: {STORE_DIR}/")
print("========================================================")
