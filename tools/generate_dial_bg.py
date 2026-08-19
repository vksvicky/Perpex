from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 390, 390
CENTER = (W / 2, H / 2)

# Matching the original GarminBasicWatchFaceView.mc math:
# radius = 195
# r1 = radius - 15 = 180
# r2 = radius - 45 = 150
# r3 = radius - 70 = 125
OUTER_R = 180
MID_R   = 150
INNER_R = 125

COLOR_DIM_OUTER = (170, 170, 170, 255)
COLOR_DIM_MID   = (100, 100, 100, 255)
COLOR_HIGHLIGHT = (255, 0, 0, 255)
COLOR_TRANSPARENT = (0, 0, 0, 0)
COLOR_BG = (255, 255, 255, 255)

TWO_PI = math.pi * 2.0
HALF_PI = math.pi / 2.0

font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
if not os.path.exists(font_path):
    font_path = "/Library/Fonts/Arial.ttf"

font_days = ImageFont.truetype(font_path, 20)
font_months = ImageFont.truetype(font_path, 24, index=1)
font_weeks = ImageFont.truetype(font_path, 24, index=1)

def draw_rotated_text(img, text, angle_rad, radius, font, color):
    text_w = int(font.getlength(text))
    text_h = int(font.size * 1.2)
    txt_img = Image.new('RGBA', (text_w * 2, text_h * 2), COLOR_TRANSPARENT)
    txt_draw = ImageDraw.Draw(txt_img)
    txt_draw.text((text_w, text_h), text, font=font, fill=color, anchor="mm")
    
    rot_deg = -(math.degrees(angle_rad) + 90.0)
    txt_rotated = txt_img.rotate(rot_deg, resample=Image.BICUBIC, expand=True)
    
    cx = CENTER[0] + radius * math.cos(angle_rad)
    cy = CENTER[1] + radius * math.sin(angle_rad)
    
    paste_x = int(cx - txt_rotated.width / 2)
    paste_y = int(cy - txt_rotated.height / 2)
    
    img.alpha_composite(txt_rotated, (paste_x, paste_y))

bg_img = Image.new('RGBA', (W, H), COLOR_BG)

# ── Outer ring: Days 1–31 ──────────────────────────────────────
day_step = TWO_PI / 31.0
for d in range(1, 32):
    angle = -HALF_PI + ((d - 1) * day_step)
    draw_rotated_text(bg_img, str(d), angle, OUTER_R, font_days, COLOR_DIM_OUTER)
    
    # Generate Sprite
    sprite = Image.new('RGBA', (W, H), COLOR_TRANSPARENT)
    draw_rotated_text(sprite, str(d), angle, OUTER_R, font_days, COLOR_HIGHLIGHT)
    sprite.save(f"resources/drawables/day_{d}_v7.png")

# ── Middle ring: Months JAN-DEC ────────────────────────────────────────
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
mon_step = TWO_PI / 12.0
for m in range(12):
    angle = -HALF_PI + (m * mon_step)
    draw_rotated_text(bg_img, months[m], angle, MID_R, font_months, COLOR_DIM_MID)
    
    # Generate Sprite (mon_1 to mon_12)
    sprite = Image.new('RGBA', (W, H), COLOR_TRANSPARENT)
    draw_rotated_text(sprite, months[m], angle, MID_R, font_months, COLOR_HIGHLIGHT)
    sprite.save(f"resources/drawables/mon_{m+1}_v7.png")

# ── Inner ring: Weekdays SUN-SAT ───────────────────────────────────────
days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
wk_step = TWO_PI / 7.0
for w in range(7):
    angle = -HALF_PI + (w * wk_step)
    draw_rotated_text(bg_img, days[w], angle, INNER_R, font_weeks, COLOR_DIM_MID)
    
    # Generate Sprite (wk_1 to wk_7)
    sprite = Image.new('RGBA', (W, H), COLOR_TRANSPARENT)
    draw_rotated_text(sprite, days[w], angle, INNER_R, font_weeks, COLOR_HIGHLIGHT)
    sprite.save(f"resources/drawables/wk_{w+1}_v7.png")

bg_img.save("resources/drawables/dial_bg_v7.png")
print("Finished generating all 51 images (1 bg, 31 days, 12 months, 7 weekdays)")
