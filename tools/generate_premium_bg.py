from PIL import Image, ImageDraw, ImageFont
import math

W, H = 260, 260
CENTER = (W / 2, H / 2)

OUTER_R = 120
MID_R   = 100
INNER_R = 83

COLOR_DIM_OUTER = (220, 220, 220, 255)
COLOR_DIM_MID   = (180, 180, 180, 255)
COLOR_DIM_INNER = (150, 150, 150, 255)
COLOR_TRANSPARENT = (0, 0, 0, 0)

TWO_PI = math.pi * 2.0
HALF_PI = math.pi / 2.0

font_path = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"

font_days = ImageFont.truetype(font_path, 13)
font_months = ImageFont.truetype(font_path, 16)
font_weeks = ImageFont.truetype(font_path, 16)

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

bg_img = Image.new('RGBA', (W, H), (0, 0, 0, 255))
draw = ImageDraw.Draw(bg_img)

# Radial gradient
for r in range(W//2, 0, -1):
    c = int(40 * (r / (W/2)))
    draw.ellipse((CENTER[0]-r, CENTER[1]-r, CENTER[0]+r, CENTER[1]+r), fill=(c,c,c,255))

draw.ellipse((CENTER[0]-128, CENTER[1]-128, CENTER[0]+128, CENTER[1]+128), outline=(100,100,100,255), width=1)
draw.ellipse((CENTER[0]-110, CENTER[1]-110, CENTER[0]+110, CENTER[1]+110), outline=(60,60,60,255), width=1)
draw.ellipse((CENTER[0]-90,  CENTER[1]-90,  CENTER[0]+90,  CENTER[1]+90),  outline=(60,60,60,255), width=1)
draw.ellipse((CENTER[0]-73,  CENTER[1]-73,  CENTER[0]+73,  CENTER[1]+73),  outline=(60,60,60,255), width=1)

day_step = TWO_PI / 31.0
for d in range(1, 32):
    angle = -HALF_PI + ((d - 1) * day_step)
    draw_rotated_text(bg_img, str(d), angle, OUTER_R, font_days, COLOR_DIM_OUTER)

months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
mon_step = TWO_PI / 12.0
for m in range(12):
    angle = -HALF_PI + (m * mon_step)
    draw_rotated_text(bg_img, months[m], angle, MID_R, font_months, COLOR_DIM_MID)

days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
wk_step = TWO_PI / 7.0
for w in range(7):
    angle = -HALF_PI + (w * wk_step)
    draw_rotated_text(bg_img, days[w], angle, INNER_R, font_weeks, COLOR_DIM_INNER)

# Convert to 256-color palette (optimized) to force Garmin compiler to use 8bpp
bg_img = bg_img.convert('P', palette=Image.ADAPTIVE, colors=256)
bg_img.save("resources/drawables/dial_bg.png")
