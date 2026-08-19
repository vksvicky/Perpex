from PIL import Image, ImageDraw, ImageFont
import math

W = 280
H = 280
R = 125
img = Image.new('RGB', (W, H), 'white')
font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)

a = 90
rot = -(math.degrees(math.radians(a)) + 90.0)

text = "JUL"
tracking = 1.0
char_widths = [font.getlength(c) + tracking for c in text]
total_arc = sum(char_widths) / R

start_angle = math.radians(a) - (total_arc / 2.0)
current_angle = start_angle

for i, c in enumerate(text):
    c_arc = char_widths[i] / R
    char_a = current_angle + c_arc / 2.0
    
    char_rot = -(math.degrees(char_a) + 90.0)
    
    # create temp img
    temp = Image.new('RGBA', (40, 40), (0,0,0,0))
    td = ImageDraw.Draw(temp)
    td.text((20, 20), c, font=font, fill='black', anchor="mm")
    
    temp = temp.rotate(char_rot, expand=True)
    
    cx = W/2 + R * math.cos(char_a)
    cy = H/2 + R * math.sin(char_a)
    
    img.paste(temp, (int(cx - temp.width/2), int(cy - temp.height/2)), temp)
    
    current_angle += c_arc

img.save("test_dial_jul.png")
