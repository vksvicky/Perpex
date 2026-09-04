#!/usr/bin/env python3
"""
tools/build_hero_banner.py
==========================
Generates the updated official Garmin Connect IQ Hero Banner:
- Resolution: exactly 1440 x 720 pixels (2:1 aspect ratio)
- File size: strictly < 2048 KB
- Features: 5 Garmin smartwatches grouped closely in a premium layered echelon lineup,
  showcasing analog hands, real metrics, vibrant themes, and night vision mode.
"""

import os
from PIL import Image, ImageDraw, ImageFilter

HERO_DIR = "store_assets"
os.makedirs(HERO_DIR, exist_ok=True)

def clean_screenshot(p):
    img = Image.open(p).convert('RGBA')
    w, h = img.size
    img = img.crop((8, 8, w - 8, h - 8))
    datas = list(img.getdata())
    newData = []
    for item in datas:
        r, g, b, a = item
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum > 215:
            newData.append((0, 0, 0, 0))
        else:
            newData.append(item)
    img.putdata(newData)
    return img

def put_screen(watch, face_path, cx, cy, radius):
    face = Image.open(face_path).convert('RGBA')
    dia = radius * 2
    face_scaled = face.resize((dia, dia), Image.Resampling.LANCZOS)
    mask = Image.new('L', (dia, dia), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([0, 0, dia - 1, dia - 1], fill=255)
    watch.paste(face_scaled, (cx - radius, cy - radius), mask)
    return watch

def add_drop_shadow(img, offset=(0, 8), blur_radius=16, shadow_alpha=120):
    """Creates an expanded RGBA image with a soft drop shadow beneath."""
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    # Extract alpha mask
    alpha_mask = img.split()[3]
    # Draw black shadow with mask
    shadow_fill = Image.new('RGBA', img.size, (0, 0, 0, shadow_alpha))
    shadow.paste(shadow_fill, (0, 0), alpha_mask)
    
    # Expand canvas to allow blur
    pad = blur_radius * 2
    expanded = Image.new('RGBA', (img.width + pad * 2, img.height + pad * 2), (0, 0, 0, 0))
    expanded.paste(shadow, (pad + offset[0], pad + offset[1]), shadow)
    blurred_shadow = expanded.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Paste actual image on top
    blurred_shadow.paste(img, (pad, pad), img)
    return blurred_shadow, pad

print("========================================================")
print("⌚ BUILDING UPDATED 1440x720 HERO BANNER (5 WATCHES)")
print("========================================================")

# 1. Prepare 5 watch models with our real watch faces
print("  → Compositing watch face screens onto 5 watch cases...")

# Watch 1: Fenix Silver Bezel - Teal Theme (Barometer, Altitude, Stress, Active Mins, Floors, Alerts)
w1 = clean_screenshot('docs/images/store/04_fenix_high_teal_cyan.png')
put_screen(w1, 'showcase/hero_faces/w1_teal_sensors.png', 209, 292, 149)

# Watch 2: Enduro Black with Orange Button - Warm Orange Theme (Wind Speed 12kt, Temp 22°C, Sunset 19:42)
w2 = clean_screenshot('docs/images/store/06_enduro3_warm_orange.png')
put_screen(w2, 'showcase/hero_faces/w2_orange_wind_weather.png', 209, 292, 149)

# Watch 3: Centerpiece Epix 2 Titanium - Signature Tactical Red (Battery 85%, Heart Rate 74, Steps 8,420, Goal 84%, 540 kcal, 6.2 km)
w3 = clean_screenshot('docs/images/store/02_epix2_high_vibrant_red.png')
put_screen(w3, 'showcase/hero_faces/w3_red_core_fitness.png', 198, 292, 149)

# Watch 4: Fenix 8 Dark Titanium - Electric Green Theme (Body Battery 76%, Recovery 18h, VO2 Max 54)
w4 = clean_screenshot('docs/images/store/07_fenix8_green_fahrenheit.png')
put_screen(w4, 'showcase/hero_faces/w4_green_performance.png', 224, 292, 138)

# Watch 5: Tactical Stealth Watch - Tactical Red Night Vision Mode
w5 = clean_screenshot('docs/images/store/08_fenxi8_always_on.png')
put_screen(w5, 'showcase/hero_faces/w5_night_vision.png', 224, 292, 138)

# 2. Canvas 1440x720 with tactical dark studio gradient
width, height = 1440, 720
canvas = Image.new('RGBA', (width, height), (10, 13, 19, 255))
draw = ImageDraw.Draw(canvas)

# Radial / vertical ambient lighting in center
for y in range(height):
    grad = y / float(height)
    r = int(10 + grad * 8)
    g = int(14 + grad * 10)
    b = int(20 + grad * 14)
    draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

# Subtle spotlight glow in center
center_glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(center_glow)
glow_draw.ellipse([420, 100, 1020, 620], fill=(35, 48, 68, 60))
center_glow = center_glow.filter(ImageFilter.GaussianBlur(60))
canvas = Image.alpha_composite(canvas, center_glow)

# 3. Resize and position watches in layered echelon
# Height scaling: Center = 600px, Mid = 560px, Outer = 525px
print("  → Arranging 5 watches with close grouping and depth layering...")

def resize_watch(w_img, target_h):
    scale = target_h / float(w_img.height)
    new_w = int(w_img.width * scale)
    return w_img.resize((new_w, target_h), Image.Resampling.LANCZOS)

rw1 = resize_watch(w1, 520)
rw2 = resize_watch(w2, 560)
rw3 = resize_watch(w3, 615)  # Centerpiece stands proud
rw4 = resize_watch(w4, 560)
rw5 = resize_watch(w5, 520)

# Echelon X positions across 1440px with closer grouping (centers: ~170, 435, 720, 1005, 1270)
c1 = 170
c2 = 445
c3 = 720
c4 = 995
c5 = 1270

pos1 = (c1 - rw1.width // 2, (height - rw1.height) // 2 + 10)
pos2 = (c2 - rw2.width // 2, (height - rw2.height) // 2 + 6)
pos3 = (c3 - rw3.width // 2, (height - rw3.height) // 2 - 2) # Center slightly elevated
pos4 = (c4 - rw4.width // 2, (height - rw4.height) // 2 + 6)
pos5 = (c5 - rw5.width // 2, (height - rw5.height) // 2 + 10)

# Apply drop shadows and paste in Z-order: Outer (1, 5) -> Mid (2, 4) -> Center (3)
layers = [
    (rw1, pos1),
    (rw5, pos5),
    (rw2, pos2),
    (rw4, pos4),
    (rw3, pos3),
]

for w_item, (wx, wy) in layers:
    w_shadow, pad = add_drop_shadow(w_item, offset=(0, 10), blur_radius=20, shadow_alpha=140)
    canvas.paste(w_shadow, (wx - pad, wy - pad), w_shadow)

# 4. Save outputs
png_path = os.path.join(HERO_DIR, "hero_banner_1440x720.png")
jpg_path = os.path.join(HERO_DIR, "hero_banner_1440x720.jpg")

# Convert canvas to RGB for saving
canvas_rgb = canvas.convert('RGB')
canvas_rgb.save(png_path, "PNG", optimize=True)
canvas_rgb.save(jpg_path, "JPEG", quality=95, optimize=True)

png_kb = os.path.getsize(png_path) / 1024
jpg_kb = os.path.getsize(jpg_path) / 1024

print("\n========================================================")
print("HERO BANNER GENERATION COMPLETE")
print("========================================================")
print(f"🖼️  PNG Version: {png_path} ({png_kb:.1f} KB) -> {'✅ PASS (<2048KB)' if png_kb < 2048 else '❌ FAIL'}")
print(f"🖼️  JPG Version: {jpg_path} ({jpg_kb:.1f} KB) -> {'✅ PASS (<2048KB)' if jpg_kb < 2048 else '❌ FAIL'}")
print(f"Dimensions : {canvas.size[0]} x {canvas.size[1]} pixels (Exact 2:1)")
print("========================================================")
