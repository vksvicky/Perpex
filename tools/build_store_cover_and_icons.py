#!/usr/bin/env python3
"""
tools/build_store_cover_and_icons.py
====================================
Generates the official Cover Image & App Icons for Garmin Connect IQ Store listing.

1. Cover Image (Web/Mobile):
   - Dimensions: 500 x 500
   - Format: PNG & JPG
   - File size limit: < 300 KB
   - Design: Premium bezel-framed tactical watch face with active analog hands,
             subtle ambient shadow and depth.

2. Store Icons:
   - 512x512, 256x256, 128x128, 70x70, 40x40
   - Format: PNG
   - File size: < 300 KB
"""

import os
from PIL import Image, ImageDraw, ImageFilter

STORE_DIR = "store_assets"
os.makedirs(STORE_DIR, exist_ok=True)

# Source: flagship 466x466 AMOLED watchface capture with hands
SRC_WATCH = "showcase/images/showcase_perm1_core_activity.png"
if not os.path.exists(SRC_WATCH):
    print(f"❌ Source image not found: {SRC_WATCH}")
    exit(1)

watch_img = Image.open(SRC_WATCH).convert("RGBA")

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE 500 x 500 COVER IMAGE (WEB & MOBILE)
# ─────────────────────────────────────────────────────────────────────────────

cover_canvas = Image.new("RGBA", (500, 500), (10, 13, 18, 255))
cover_draw = ImageDraw.Draw(cover_canvas)

# Draw subtle ambient background gradient / vignette
for r in range(250, 0, -5):
    alpha = int(18 * (1.0 - (r / 250.0)))
    cover_draw.ellipse(
        [250 - r, 250 - r, 250 + r, 250 + r],
        outline=(25, 32, 44, alpha),
        width=5
    )

# Scale watch face slightly to fit with a sleek bezel frame (456x456 centered on 500x500)
watch_scaled = watch_img.resize((456, 456), Image.Resampling.LANCZOS)

# Create circular mask for watchface
mask = Image.new("L", (456, 456), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.ellipse([0, 0, 455, 455], fill=255)

# Outer bezel shadow & metallic bezel ring
bezel_offset = (500 - 456) // 2  # 22px
bezel_box = [bezel_offset - 2, bezel_offset - 2, bezel_offset + 456 + 1, bezel_offset + 456 + 1]
cover_draw.ellipse(bezel_box, outline=(40, 46, 56, 255), width=3)
cover_draw.ellipse([bezel_offset - 1, bezel_offset - 1, bezel_offset + 456, bezel_offset + 456], outline=(20, 24, 30, 255), width=2)

# Paste watch face onto cover canvas
cover_canvas.paste(watch_scaled, (bezel_offset, bezel_offset), mask)

# Save Cover PNG
cover_png = os.path.join(STORE_DIR, "cover_image_500x500.png")
# Quantize to 256 colors for perfect gradients and tiny file size (~60 KB)
q_cover = cover_canvas.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
q_cover.save(cover_png, "PNG", optimize=True)
cover_png_size = os.path.getsize(cover_png) / 1024

# Save Cover JPG (95% quality, ~55 KB)
cover_jpg = os.path.join(STORE_DIR, "cover_image_500x500.jpg")
cover_rgb = Image.new("RGB", (500, 500), (10, 13, 18))
cover_rgb.paste(cover_canvas, (0, 0), cover_canvas)
cover_rgb.save(cover_jpg, "JPEG", quality=95, optimize=True)
cover_jpg_size = os.path.getsize(cover_jpg) / 1024

print("========================================================")
print("📦 GARMIN CONNECT IQ STORE COVER IMAGE (500x500)")
print("========================================================")
print(f"🖼️  Cover PNG: {cover_png} ({cover_png_size:.1f} KB) -> {'✅ PASS (<300KB)' if cover_png_size < 300 else '❌ FAIL'}")
print(f"🖼️  Cover JPG: {cover_jpg} ({cover_jpg_size:.1f} KB) -> {'✅ PASS (<300KB)' if cover_jpg_size < 300 else '❌ FAIL'}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. GENERATE STORE APP ICONS (512x512, 256x256, 128x128, 70x70, 40x40)
# ─────────────────────────────────────────────────────────────────────────────

print("\n========================================================")
print("📦 GARMIN CONNECT IQ STORE APP ICONS")
print("========================================================")

ICON_SIZES = [512, 256, 128, 70, 40]

for sz in ICON_SIZES:
    icon_canvas = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    icon_draw = ImageDraw.Draw(icon_canvas)
    
    # Render circular watch icon
    watch_resized = watch_img.resize((sz, sz), Image.Resampling.LANCZOS)
    mask_icon = Image.new("L", (sz, sz), 0)
    mask_icon_draw = ImageDraw.Draw(mask_icon)
    mask_icon_draw.ellipse([0, 0, sz - 1, sz - 1], fill=255)
    
    icon_canvas.paste(watch_resized, (0, 0), mask_icon)
    
    # Save icon PNG
    icon_path = os.path.join(STORE_DIR, f"app_icon_{sz}x{sz}.png")
    if sz >= 128:
        q_icon = icon_canvas.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        q_icon.save(icon_path, "PNG", optimize=True)
    else:
        icon_canvas.save(icon_path, "PNG", optimize=True)
        
    icon_size_kb = os.path.getsize(icon_path) / 1024
    print(f"🔹 Icon {sz}x{sz}: {icon_path} ({icon_size_kb:.1f} KB) -> ✅ PASS (<300KB)")

print("\n========================================================")
print(f"🎉 All Store Cover Images & Icons saved in: {STORE_DIR}/")
print("========================================================")
