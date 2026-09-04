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
5. Dynamic card data (showcase/cards_data.js) and interactive web showcase.
"""

import os
import sys
import json
import argparse
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from test_ui.simulator_driver import build_app, launch_simulator_and_screenshot
from test_ui.config_manager import set_properties, backup_properties, restore_properties
from test_ui.layout_validator import _slot_center
from tools.showcase_data import SHOWCASE_PASSES

SHOWCASE_DIR = os.path.join(PROJECT_ROOT, "showcase")
IMAGES_DIR = os.path.join(SHOWCASE_DIR, "images")
ANNOTATED_DIR = os.path.join(SHOWCASE_DIR, "annotated")

DEV_ID = "fenix9pro51mm"
DEV_NAME = "Fenix 9 Pro 51mm"
RES_INFO = "466x466 AMOLED"
DW, DH = 466, 466


def annotate_screenshot(raw_path, pass_def, out_path):
    """Draws blueprint-style technical callout lines and label tags pointing to each slot."""
    try:
        raw_img = Image.open(raw_path).convert("RGBA")
    except Exception as e:
        print(f"    ❌ Failed to open raw image {raw_path}: {e}")
        return False

    canvas_w = DW + 560
    canvas_h = DH + 80
    bg = Image.new("RGBA", (canvas_w, canvas_h), (11, 14, 20, 255))
    draw = ImageDraw.Draw(bg)

    ox = 280
    oy = 40
    bg.paste(raw_img, (ox, oy))
    draw.ellipse([ox - 1, oy - 1, ox + DW, oy + DH], outline=(40, 50, 65, 255), width=2)

    try:
        font_bold = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 15)
        font_main = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 13)
        font_sub = ImageFont.truetype("/System/Library/Fonts/SFNSMono.ttf", 11)
        font_head = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 16)
    except Exception:
        font_bold = ImageFont.load_default()
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_head = ImageFont.load_default()

    draw.text((20, 14), pass_def["title"].upper(), fill=(88, 166, 255, 255), font=font_head)
    draw.text((20, 32), f"{DEV_NAME} ({RES_INFO}) — All Hands Active", fill=(139, 148, 158, 255), font=font_sub)

    slots_info = pass_def.get("slots", {})
    card_colors = {
        1: (88, 166, 255), 2: (0, 204, 204), 3: (0, 255, 102),
        4: (255, 136, 0), 5: (255, 204, 0), 6: (255, 51, 51),
    }

    left_slots = [s for s in [2, 4, 1] if s in slots_info]
    right_slots = [s for s in [3, 5, 6] if s in slots_info]

    def place_callouts(slots_list, is_left):
        count = len(slots_list)
        if count == 0:
            return
        box_h = 48
        total_h = count * box_h + (count - 1) * 20
        start_y = oy + (DH - total_h) // 2

        for i, s_num in enumerate(slots_list):
            info = slots_info[s_num]
            col = card_colors.get(s_num, (200, 200, 200))
            tag_y = start_y + i * (box_h + 20)

            cx, cy = _slot_center(s_num, DW, DH)
            scx = ox + cx
            scy = oy + cy

            draw.ellipse([scx - 4, scy - 4, scx + 4, scy + 4], fill=col + (255,), outline=(255, 255, 255, 255), width=1)

            if is_left:
                box_x = 20
                box_w = 230
                elbow_x = ox - 20
                draw.line([(scx, scy), (elbow_x, tag_y + 24), (box_x + box_w, tag_y + 24)], fill=col + (180,), width=1)
                draw.rectangle([box_x, tag_y, box_x + box_w, tag_y + box_h], fill=(20, 25, 35, 240), outline=col + (200,), width=1)
                draw.text((box_x + 8, tag_y + 6), f"SLOT {s_num}: {info['name']}", fill=col + (255,), font=font_bold)
                draw.text((box_x + 8, tag_y + 26), f"{info['val']}  ({info['desc'][:26]})", fill=(230, 237, 243, 255), font=font_main)
            else:
                box_x = ox + DW + 30
                box_w = 230
                elbow_x = ox + DW + 20
                draw.line([(scx, scy), (elbow_x, tag_y + 24), (box_x, tag_y + 24)], fill=col + (180,), width=1)
                draw.rectangle([box_x, tag_y, box_x + box_w, tag_y + box_h], fill=(20, 25, 35, 240), outline=col + (200,), width=1)
                draw.text((box_x + 8, tag_y + 6), f"SLOT {s_num}: {info['name']}", fill=col + (255,), font=font_bold)
                draw.text((box_x + 8, tag_y + 26), f"{info['val']}  ({info['desc'][:26]})", fill=(230, 237, 243, 255), font=font_main)

    place_callouts(left_slots, is_left=True)
    place_callouts(right_slots, is_left=False)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bg.save(out_path, "PNG")
    return True


def export_showcase_data(passes):
    """Generates the clean compact cards_data.js for dynamic web presentation."""
    cards_data = []
    for p in passes:
        card = {
            "id": p["id"],
            "category": p["category"],
            "title": p["title"],
            "subtitle": p["subtitle"],
            "image": f"images/{p['id']}.png",
            "annotated": f"annotated/{p['id']}.png",
            "slots": []
        }
        for s_num in range(1, 7):
            if s_num in p["slots"]:
                info = p["slots"][s_num]
                cx, cy = _slot_center(s_num, DW, DH)
                card["slots"].append({
                    "slot": s_num,
                    "name": info["name"],
                    "val": info["val"],
                    "desc": info["desc"],
                    "setting": info["setting"],
                    "left": round((cx / float(DW)) * 100, 2),
                    "top": round((cy / float(DH)) * 100, 2)
                })
        cards_data.append(card)

    lines = ["const SHOWCASE_CARDS = ["]
    for c in cards_data:
        lines.append("  {")
        lines.append(f'    "id": "{c["id"]}", "category": "{c["category"]}", "title": "{c["title"]}",')
        lines.append(f'    "subtitle": "{c["subtitle"]}", "image": "{c["image"]}", "annotated": "{c["annotated"]}",')
        lines.append('    "slots": [')
        for s in c["slots"]:
            lines.append("      " + json.dumps(s) + ",")
        lines.append("    ]")
        lines.append("  },")
    lines.append("];\n")

    data_path = os.path.join(SHOWCASE_DIR, "cards_data.js")
    with open(data_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  📄 Showcase Data: {data_path} ({len(lines)} lines)")


def run_showcase(target_id=None, skip_sim=False):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(ANNOTATED_DIR, exist_ok=True)

    print("=================================================================")
    print(f"🎨 PERPEX FEATURE & METRIC SHOWCASE GENERATOR ({DEV_NAME})")
    print(f"   Resolution: {RES_INFO} | Analog Hands: RENDERED (TestHideHands = 0)")
    print("=================================================================")

    passes_to_run = [p for p in SHOWCASE_PASSES if target_id is None or p["id"] == target_id]

    if not skip_sim:
        backup_properties()
        try:
            for idx, p in enumerate(passes_to_run, 1):
                pid = p["id"]
                raw_path = os.path.join(IMAGES_DIR, f"{pid}.png")
                ann_path = os.path.join(ANNOTATED_DIR, f"{pid}.png")

                print(f"\n[{idx}/{len(passes_to_run)}] {p['title']}")
                print(f"   Subtitle: {p['subtitle']}")

                set_properties(p["props"])
                prg_path = f"bin/Showcase_{DEV_ID}_{pid}.prg"

                if build_app(DEV_ID, prg_path):
                    captured = launch_simulator_and_screenshot(DEV_ID, prg_path, raw_path, RES_INFO)
                    if captured:
                        print(f"   📸 Raw capture saved: {raw_path}")
                        if annotate_screenshot(raw_path, p, ann_path):
                            print(f"   📋 Annotated blueprint saved: {ann_path}")
                    else:
                        print(f"   ❌ Simulator capture failed for {pid}")
                else:
                    print(f"   ❌ Compilation failed for {pid}")
        finally:
            restore_properties()
    else:
        print("⏩ Skipping simulator compilation — generating annotated blueprints and data only...")
        for p in passes_to_run:
            raw_path = os.path.join(IMAGES_DIR, f"{p['id']}.png")
            ann_path = os.path.join(ANNOTATED_DIR, f"{p['id']}.png")
            if os.path.exists(raw_path):
                annotate_screenshot(raw_path, p, ann_path)

    export_showcase_data(passes_to_run)
    print("\n=================================================================")
    print("🎉 SHOWCASE GENERATION COMPLETE")
    print(f"   Interactive Web Showcase: file://{os.path.join(SHOWCASE_DIR, 'index.html')}")
    print("=================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate visual showcase with analog hands.")
    parser.add_argument("--pass-id", help="Run a specific pass by ID")
    parser.add_argument("--skip-sim", action="store_true", help="Skip simulator execution and rebuild blueprints from existing captures")
    args = parser.parse_args()

    run_showcase(target_id=args.pass_id, skip_sim=args.skip_sim)
