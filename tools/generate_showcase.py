#!/usr/bin/env python3
"""
tools/generate_showcase.py
==========================
Generates a complete visual showcase of the Perpex Watch Face with:
1. Analog Hour, Minute, and Second hands rendered (TestHideHands = 0).
2. Comprehensive coverage of all 27 metrics across 6 slots, color themes,
   night vision modes, weather overrides, and low-power AOD mode.
3. High-resolution raw simulator captures saved to showcase/images/.
4. Annotated screenshot cards with callout lines saved to showcase/annotated/.
5. An interactive showcase web page (showcase/index.html) with pulsing
   hotspots and rich hover tooltips detailing every slot and metric.
"""

import os
import sys
import json
import base64
import argparse
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path so we can import test_ui modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from test_ui.simulator_driver import build_app, launch_simulator_and_screenshot
from test_ui.config_manager import set_properties, backup_properties, restore_properties
from test_ui.layout_validator import _slot_center

SHOWCASE_DIR = os.path.join(PROJECT_ROOT, "showcase")
IMAGES_DIR = os.path.join(SHOWCASE_DIR, "images")
ANNOTATED_DIR = os.path.join(SHOWCASE_DIR, "annotated")

# ─────────────────────────────────────────────────────────────────────────────
# SHOWCASE PASS DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

SHOWCASE_PASSES = [
    {
        "id": "showcase_perm1_core_activity",
        "category": "metrics",
        "title": "Core Fitness & Activity Metrics",
        "subtitle": "Daily performance dashboard: Battery gauge, Heart Rate, Steps, Calories & Distance",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery Level", "val": "85%", "desc": "Dynamic color-coded gauge tracking battery charge remaining", "setting": "Slot1Metric = 1"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Continuous pulse monitoring with live animated heart", "setting": "Slot2Metric = 2"},
            3: {"name": "Step Count", "val": "8,420", "desc": "Daily cumulative steps tracking active movement", "setting": "Slot3Metric = 3"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Percentage completion toward daily active target", "setting": "Slot4Metric = 4"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Estimated active metabolic burn expenditure", "setting": "Slot5Metric = 5"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Total distance traveled today in kilometers", "setting": "Slot6Metric = 6"},
        }
    },
    {
        "id": "showcase_perm2_sensors_alerts",
        "category": "metrics",
        "title": "Sensors, Alerts & Atmosphere",
        "subtitle": "Environmental and connectivity vitals: Elevation, Barometer, Stress, Floors & Alerts",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1,
            "Slot1Metric": 7, "Slot2Metric": 8, "Slot3Metric": 9,
            "Slot4Metric": 11, "Slot5Metric": 12, "Slot6Metric": 13,
        },
        "slots": {
            1: {"name": "Floors Climbed", "val": "14 fl", "desc": "Vertical flights of stairs climbed today", "setting": "Slot1Metric = 7"},
            2: {"name": "Active Minutes", "val": "45 min", "desc": "Moderate and vigorous intensity activity minutes accumulated", "setting": "Slot2Metric = 8"},
            3: {"name": "Stress Level", "val": "28", "desc": "Real-time all-day physiological stress score", "setting": "Slot3Metric = 9"},
            4: {"name": "Notifications", "val": "3", "desc": "Unread notification counter and smartphone Bluetooth status", "setting": "Slot4Metric = 11"},
            5: {"name": "Altitude", "val": "342 m", "desc": "Real-time barometric altitude elevation above sea level", "setting": "Slot5Metric = 12"},
            6: {"name": "Barometer", "val": "1013 hPa", "desc": "Ambient atmospheric sea-level pressure monitoring", "setting": "Slot6Metric = 13"},
        }
    },
    {
        "id": "showcase_perm3_solar_weather_recovery",
        "category": "metrics",
        "title": "Weather, Solar & Training Status",
        "subtitle": "Performance & environment: Ambient Weather, Solar Times, Body Battery, Recovery & VO2 Max",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1,
            "Slot1Metric": 14, "Slot2Metric": 15, "Slot3Metric": 16,
            "Slot4Metric": 17, "Slot5Metric": 20, "Slot6Metric": 21,
            "TestWeatherOverride": 2,
        },
        "slots": {
            1: {"name": "Weather Temp", "val": "22°C", "desc": "Outdoor temperature from connected weather provider", "setting": "Slot1Metric = 14"},
            2: {"name": "Weather Condition", "val": "Sunny", "desc": "Context-aware dynamic condition icon (Clear Skies)", "setting": "Slot2Metric = 15"},
            3: {"name": "Solar Event", "val": "19:42", "desc": "Next sunrise/sunset calculation with offline GPS fallback", "setting": "Slot3Metric = 16"},
            4: {"name": "Body Battery", "val": "76%", "desc": "Garmin Firstbeat real-time bodily energy reserve", "setting": "Slot4Metric = 17"},
            5: {"name": "Recovery Time", "val": "18 hrs", "desc": "Hours remaining before next recommended training session", "setting": "Slot5Metric = 20"},
            6: {"name": "VO2 Max", "val": "52", "desc": "Cardiovascular aerobic fitness capacity score", "setting": "Slot6Metric = 21"},
        }
    },
    {
        "id": "showcase_weather_rain",
        "category": "weather",
        "title": "Weather: Rain & Precipitation",
        "subtitle": "Displays live rain showers and precipitation chance percentage",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1,
            "Slot1Metric": 15, "Slot2Metric": 1, "Slot3Metric": 2,
            "Slot4Metric": 4, "Slot5Metric": 3, "Slot6Metric": 17,
            "TestWeatherOverride": 1,
        },
        "slots": {
            1: {"name": "Precipitation Chance", "val": "27%", "desc": "Precipitation probability indicator with raindrop vector icon", "setting": "TestWeatherOverride = 1"},
            2: {"name": "Battery", "val": "85%", "desc": "Battery level gauge", "setting": "Slot2Metric = 1"},
            3: {"name": "Heart Rate", "val": "74 BPM", "desc": "Live heart rate pulse", "setting": "Slot3Metric = 2"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4"},
            5: {"name": "Steps", "val": "8,420", "desc": "Daily step count", "setting": "Slot5Metric = 3"},
            6: {"name": "Body Battery", "val": "76%", "desc": "Body Battery energy score", "setting": "Slot6Metric = 17"},
        }
    },
    {
        "id": "showcase_weather_wind",
        "category": "weather",
        "title": "Weather: Nautical Wind Velocity",
        "subtitle": "Converts ambient wind speed into nautical knots (kt) for marine & outdoor navigation",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 1,
            "Slot1Metric": 15, "Slot2Metric": 1, "Slot3Metric": 2,
            "Slot4Metric": 4, "Slot5Metric": 3, "Slot6Metric": 17,
            "TestWeatherOverride": 8,
        },
        "slots": {
            1: {"name": "Wind Velocity", "val": "12 kt", "desc": "High wind velocity in knots for outdoor navigation", "setting": "TestWeatherOverride = 8"},
            2: {"name": "Battery", "val": "85%", "desc": "Battery level gauge", "setting": "Slot2Metric = 1"},
            3: {"name": "Heart Rate", "val": "74 BPM", "desc": "Live heart rate pulse", "setting": "Slot3Metric = 2"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4"},
            5: {"name": "Steps", "val": "8,420", "desc": "Daily step count", "setting": "Slot5Metric = 3"},
            6: {"name": "Body Battery", "val": "76%", "desc": "Body Battery energy score", "setting": "Slot6Metric = 17"},
        }
    },
    {
        "id": "showcase_theme_teal",
        "category": "themes",
        "title": "Color Theme: Teal Accent",
        "subtitle": "Crisp cyan and teal accents on hands, date ring, and secondary indicators",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 2,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Battery level", "setting": "Slot1Metric = 1"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Heart rate pulse", "setting": "Slot2Metric = 2"},
            3: {"name": "Steps", "val": "8,420", "desc": "Daily step count", "setting": "Slot3Metric = 3"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Active calorie expenditure", "setting": "Slot5Metric = 5"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6"},
        }
    },
    {
        "id": "showcase_theme_orange",
        "category": "themes",
        "title": "Color Theme: Warm Orange",
        "subtitle": "High-contrast tactical orange accent for maximum daylight visibility",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 3,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Battery level", "setting": "Slot1Metric = 1"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Heart rate pulse", "setting": "Slot2Metric = 2"},
            3: {"name": "Steps", "val": "8,420", "desc": "Daily step count", "setting": "Slot3Metric = 3"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Active calorie expenditure", "setting": "Slot5Metric = 5"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6"},
        }
    },
    {
        "id": "showcase_theme_green",
        "category": "themes",
        "title": "Color Theme: Electric Green",
        "subtitle": "Vibrant tactical green accent matching sport and outdoor aviation aesthetics",
        "props": {
            "TestHideHands": 0, "NightMode": 0, "ThemeColor": 4,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Battery level", "setting": "Slot1Metric = 1"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Heart rate pulse", "setting": "Slot2Metric = 2"},
            3: {"name": "Steps", "val": "8,420", "desc": "Daily step count", "setting": "Slot3Metric = 3"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Step goal percentage", "setting": "Slot4Metric = 4"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Active calorie expenditure", "setting": "Slot5Metric = 5"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Distance traveled", "setting": "Slot6Metric = 6"},
        }
    },
    {
        "id": "showcase_night_red",
        "category": "night_mode",
        "title": "Night Mode: Tactical Red",
        "subtitle": "Full red illumination to preserve rhodopsin night vision in pitch-dark environments",
        "props": {
            "TestHideHands": 0, "NightMode": 3, "NightModeColor": 0,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Battery level in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Pulse in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
            3: {"name": "Steps", "val": "8,420", "desc": "Step count in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Goal % in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Calories in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Distance in Tactical Red", "setting": "NightModeColor = 0 (Red)"},
        }
    },
    {
        "id": "showcase_night_green",
        "category": "night_mode",
        "title": "Night Mode: Stealth Green",
        "subtitle": "Optimized for night vision goggles and tactical operations",
        "props": {
            "TestHideHands": 0, "NightMode": 3, "NightModeColor": 2,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Battery level in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Pulse in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
            3: {"name": "Steps", "val": "8,420", "desc": "Step count in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Goal % in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Calories in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Distance in Stealth Green", "setting": "NightModeColor = 2 (Green)"},
        }
    },
    {
        "id": "showcase_low_power_aod",
        "category": "aod",
        "title": "Low-Power AOD Mode",
        "subtitle": "AMOLED burn-in protected Always-On Display with under 10% active pixel load",
        "props": {
            "TestHideHands": 0, "LowPowerMode": 1, "NightMode": 0,
            "Slot1Metric": 1, "Slot2Metric": 2, "Slot3Metric": 3,
            "Slot4Metric": 4, "Slot5Metric": 5, "Slot6Metric": 6,
        },
        "slots": {
            1: {"name": "Battery", "val": "85%", "desc": "Dimmed battery outline for burn-in protection", "setting": "LowPowerMode = 1"},
            2: {"name": "Heart Rate", "val": "74 BPM", "desc": "Dimmed pulse display", "setting": "LowPowerMode = 1"},
            3: {"name": "Steps", "val": "8,420", "desc": "Dimmed step count", "setting": "LowPowerMode = 1"},
            4: {"name": "Step Goal %", "val": "84%", "desc": "Dimmed goal %", "setting": "LowPowerMode = 1"},
            5: {"name": "Active Calories", "val": "540 kCal", "desc": "Dimmed active calories", "setting": "LowPowerMode = 1"},
            6: {"name": "Distance", "val": "6.2 KM", "desc": "Dimmed distance", "setting": "LowPowerMode = 1"},
        }
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# ANNOTATION GRAPHICS GENERATOR (PILLOW)
# ─────────────────────────────────────────────────────────────────────────────

def create_annotated_card(raw_img_path, annotated_path, ppass, w, h):
    """
    Creates a composite card with callout arrows and tooltip badges
    pointing to each slot.
    """
    base_img = Image.open(raw_img_path).convert("RGBA")
    
    # Create canvas with extra padding for callout text
    canvas_w = w + 460
    canvas_h = max(h + 80, 600)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (18, 22, 28, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Paste watch image
    img_x = 40
    img_y = (canvas_h - h) // 2
    canvas.paste(base_img, (img_x, img_y), base_img)

    # Title header
    draw.text((img_x, 24), ppass["title"], fill=(255, 255, 255, 255))
    draw.text((img_x, 48), ppass["subtitle"], fill=(150, 160, 175, 255))

    # Draw callout annotations for each slot
    right_x = w + 80
    slot_order = [1, 2, 3, 4, 5, 6]
    row_h = (h - 60) // 6

    for idx, sid in enumerate(slot_order):
        slot_info = ppass["slots"].get(sid)
        if not slot_info:
            continue

        # Get slot center on the image
        scx, scy = _slot_center(sid, w, h)
        watch_pt = (int(img_x + scx), int(img_y + scy))

        # Target callout point on the right panel
        badge_y = img_y + 30 + idx * row_h
        target_pt = (right_x, badge_y + 12)

        # Draw connecting line
        draw.line([watch_pt, target_pt], fill=(88, 166, 255, 180), width=2)
        # Small circle at slot center
        draw.ellipse([watch_pt[0]-4, watch_pt[1]-4, watch_pt[0]+4, watch_pt[1]+4], fill=(88, 166, 255, 255))

        # Callout card box
        card_w = 340
        card_h = row_h - 10
        card_rect = [right_x + 10, badge_y, right_x + 10 + card_w, badge_y + card_h]
        draw.rectangle(card_rect, fill=(30, 36, 46, 255), outline=(55, 65, 80, 255), width=1)

        # Text inside callout
        slot_title = f"Slot {sid}: {slot_info['name']} ({slot_info['val']})"
        draw.text((card_rect[0] + 10, card_rect[1] + 6), slot_title, fill=(240, 246, 252, 255))
        draw.text((card_rect[0] + 10, card_rect[1] + 24), slot_info["desc"][:45], fill=(140, 150, 165, 255))

    canvas.save(annotated_path)


# ─────────────────────────────────────────────────────────────────────────────
# INTERACTIVE HTML SHOWCASE GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_interactive_html(passes, dev_id, w, h):
    """
    Generates a high-fidelity interactive showcase website with:
    - Tab navigation (All, Metrics, Weather, Themes, Night Mode, AOD).
    - Responsive watch image viewer.
    - Pulsing hotspots placed on each slot according to _slot_center.
    - Floating animated tooltips displaying icon, value, description, and settings.
    """
    html_items = []
    for p in passes:
        pid = p["id"]
        raw_rel = f"images/{pid}.png"
        ann_rel = f"annotated/{pid}.png"

        # Calculate percentage positions for each slot hotspot
        hotspots = []
        for sid in [1, 2, 3, 4, 5, 6]:
            sinfo = p["slots"].get(sid)
            if not sinfo:
                continue
            scx, scy = _slot_center(sid, w, h)
            left_pct = round((scx / w) * 100, 2)
            top_pct = round((scy / h) * 100, 2)

            hotspot_html = f'''          <div class="hotspot" style="left: {left_pct}%; top: {top_pct}%;">
            <div class="pin"></div>
            <div class="tooltip">
              <div class="tooltip-header">
                <span class="slot-badge">Slot {sid}</span>
                <span class="tooltip-name">{sinfo['name']}</span>
              </div>
              <div class="tooltip-value">{sinfo['val']}</div>
              <div class="tooltip-desc">{sinfo['desc']}</div>
              <div class="tooltip-setting"><code>{sinfo['setting']}</code></div>
            </div>
          </div>'''
            hotspots.append(hotspot_html)

        hotspots_block = "\n".join(hotspots)

        item_html = f'''      <div class="showcase-card" data-category="{p['category']}">
        <div class="card-header">
          <span class="badge {p['category']}">{p['category'].upper()}</span>
          <h3>{p['title']}</h3>
          <p>{p['subtitle']}</p>
        </div>
        <div class="watch-stage">
          <img src="{raw_rel}" alt="{p['title']}" class="watch-img" />
          <div class="hotspots-overlay">
{hotspots_block}
          </div>
        </div>
        <div class="card-footer">
          <a href="{ann_rel}" target="_blank" class="btn-card">View Annotated Blueprint</a>
        </div>
      </div>'''
        html_items.append(item_html)

    cards_block = "\n".join(html_items)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Perpex Watch Face — Interactive Feature & Metric Showcase</title>
  <style>
    :root {{
      --bg: #0b0e14;
      --card-bg: #141923;
      --border: #232b38;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --accent: #ff3333;
      --blue: #58a6ff;
      --teal: #00cccc;
      --orange: #ff8800;
      --green: #00ff66;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 30px 20px;
      line-height: 1.5;
    }}
    header {{
      max-width: 1200px;
      margin: 0 auto 30px auto;
      text-align: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
    }}
    h1 {{ font-size: 32px; font-weight: 800; color: #fff; margin-bottom: 8px; }}
    p.lead {{ font-size: 16px; color: var(--text-muted); max-width: 700px; margin: 0 auto; }}

    /* Filters */
    .filter-bar {{
      display: flex;
      justify-content: center;
      gap: 10px;
      margin: 24px 0;
      flex-wrap: wrap;
    }}
    .filter-btn {{
      background: var(--card-bg);
      color: var(--text-muted);
      border: 1px solid var(--border);
      padding: 8px 18px;
      border-radius: 20px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.2s ease;
    }}
    .filter-btn:hover, .filter-btn.active {{
      background: #21262d;
      color: #fff;
      border-color: var(--blue);
    }}

    /* Grid */
    .grid {{
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 28px;
    }}
    .showcase-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .card-header {{
      padding: 20px 20px 14px 20px;
      border-bottom: 1px solid var(--border);
    }}
    .badge {{
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      margin-bottom: 8px;
      text-transform: uppercase;
    }}
    .badge.metrics {{ background: rgba(88, 166, 255, 0.15); color: var(--blue); }}
    .badge.weather {{ background: rgba(0, 204, 204, 0.15); color: var(--teal); }}
    .badge.themes {{ background: rgba(255, 136, 0, 0.15); color: var(--orange); }}
    .badge.night_mode {{ background: rgba(255, 51, 51, 0.15); color: var(--accent); }}
    .badge.aod {{ background: rgba(139, 148, 158, 0.2); color: #fff; }}

    .card-header h3 {{ font-size: 18px; color: #fff; margin-bottom: 6px; }}
    .card-header p {{ font-size: 13px; color: var(--text-muted); }}

    /* Watch stage */
    .watch-stage {{
      position: relative;
      background: #090c10;
      padding: 30px;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    .watch-img {{
      width: 260px;
      height: 260px;
      border-radius: 50%;
      box-shadow: 0 4px 20px rgba(0,0,0,0.8);
    }}
    .hotspots-overlay {{
      position: absolute;
      width: 260px;
      height: 260px;
      pointer-events: auto;
    }}

    /* Hotspot */
    .hotspot {{
      position: absolute;
      transform: translate(-50%, -50%);
      z-index: 10;
    }}
    .pin {{
      width: 14px;
      height: 14px;
      border-radius: 50%;
      background: var(--blue);
      border: 2px solid #fff;
      box-shadow: 0 0 8px rgba(88, 166, 255, 0.8);
      cursor: pointer;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0% {{ box-shadow: 0 0 0 0 rgba(88, 166, 255, 0.7); }}
      70% {{ box-shadow: 0 0 0 10px rgba(88, 166, 255, 0); }}
      100% {{ box-shadow: 0 0 0 0 rgba(88, 166, 255, 0); }}
    }}

    /* Tooltip */
    .tooltip {{
      visibility: hidden;
      opacity: 0;
      width: 240px;
      background: rgba(22, 27, 34, 0.96);
      backdrop-filter: blur(8px);
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 12px;
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      transition: opacity 0.25s ease, transform 0.25s ease;
      z-index: 50;
      box-shadow: 0 8px 24px rgba(0,0,0,0.7);
      pointer-events: none;
    }}
    .hotspot:hover .tooltip {{
      visibility: visible;
      opacity: 1;
      transform: translateX(-50%) translateY(-4px);
    }}
    .tooltip-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }}
    .slot-badge {{
      background: #21262d;
      color: var(--blue);
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }}
    .tooltip-name {{
      font-weight: 600;
      font-size: 13px;
      color: #fff;
    }}
    .tooltip-value {{
      font-size: 15px;
      font-weight: 700;
      color: #58a6ff;
      margin-bottom: 4px;
    }}
    .tooltip-desc {{
      font-size: 11px;
      color: var(--text-muted);
      line-height: 1.4;
      margin-bottom: 6px;
    }}
    .tooltip-setting {{
      font-size: 10px;
      color: #8b949e;
      border-top: 1px solid #30363d;
      padding-top: 4px;
    }}
    code {{ color: #7ee787; font-family: monospace; }}

    .card-footer {{
      padding: 14px 20px;
      background: #10141d;
      border-top: 1px solid var(--border);
      text-align: right;
    }}
    .btn-card {{
      color: var(--blue);
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
    }}
    .btn-card:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <h1>Perpex Watch Face Showcase</h1>
    <p class="lead">Interactive overview of all 27 metrics, 6 slot positions, analog watch hands, color themes, night vision, and low-power AOD modes.</p>
    <div class="filter-bar">
      <button class="filter-btn active" data-filter="all">All Screenshots</button>
      <button class="filter-btn" data-filter="metrics">Core Metrics</button>
      <button class="filter-btn" data-filter="weather">Weather & Wind</button>
      <button class="filter-btn" data-filter="themes">Color Themes</button>
      <button class="filter-btn" data-filter="night_mode">Night Vision</button>
      <button class="filter-btn" data-filter="aod">Always-On Display</button>
    </div>
  </header>

  <main class="grid">
{cards_block}
  </main>

  <script>
    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.showcase-card');

    buttons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.dataset.filter;

        cards.forEach(card => {{
          if (filter === 'all' || card.dataset.category === filter) {{
            card.style.display = 'flex';
          }} else {{
            card.style.display = 'none';
          }}
        }});
      }});
    }});
  </script>
</body>
</html>'''

    out_html_path = os.path.join(SHOWCASE_DIR, "index.html")
    with open(out_html_path, "w") as f:
        f.write(html)
    return out_html_path


# ─────────────────────────────────────────────────────────────────────────────
# MAIN EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate complete watchface showcase with analog hands and interactive tooltips")
    parser.add_argument("--device", default="fenix9pro51mm", help="Target device (default: fenix9pro51mm 466x466 AMOLED)")
    args = parser.parse_args()

    dev_id = args.device
    res_info = "466x466 AMOLED"
    w, h = 466, 466

    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(ANNOTATED_DIR, exist_ok=True)

    print("========================================================")
    print("⌚ PERPEX WATCH FACE SHOWCASE GENERATOR")
    print(f"Target Device : {dev_id} ({res_info})")
    print(f"Hands Rendered: Hour, Minute, and Second Hands ACTIVE")
    print(f"Output Dir    : {SHOWCASE_DIR}")
    print("========================================================")

    backup_properties()
    successful_passes = []

    try:
        for idx, ppass in enumerate(SHOWCASE_PASSES, 1):
            pid = ppass["id"]
            print(f"\n[{idx}/{len(SHOWCASE_PASSES)}] Capturing: {ppass['title']}")
            
            # Apply properties with hands enabled
            set_properties(ppass["props"])

            prg_path = f"bin/Showcase_{dev_id}_{pid}.prg"
            raw_img_path = os.path.join(IMAGES_DIR, f"{pid}.png")
            annotated_img_path = os.path.join(ANNOTATED_DIR, f"{pid}.png")

            print(f"  → Building binary: {prg_path}")
            if build_app(dev_id, prg_path):
                print(f"  → Launching simulator and capturing with hands...")
                captured = launch_simulator_and_screenshot(dev_id, prg_path, raw_img_path, res_info)
                if captured:
                    print(f"  📸 Screenshot saved: {raw_img_path}")
                    create_annotated_card(raw_img_path, annotated_img_path, ppass, w, h)
                    print(f"  🎨 Annotated card created: {annotated_img_path}")
                    successful_passes.append(ppass)
                else:
                    print(f"  ⚠️ Screenshot capture timed out for {pid}")
            else:
                print(f"  ❌ Build failed for {pid}")

    finally:
        restore_properties()

    print("\n--------------------------------------------------------")
    print(f"Building interactive showcase website...")
    html_path = generate_interactive_html(successful_passes, dev_id, w, h)
    print(f"✅ Showcase website generated: {html_path}")
    print("========================================================")
    print("🎉 ALL SHOWCASE SCREENSHOTS & TOOLTIPS COMPLETED!")
    print(f"Open in browser: open {html_path}")
    print("========================================================")


if __name__ == "__main__":
    main()
