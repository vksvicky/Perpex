import os
import math
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "tools/Roboto-Bold.ttf"
FONT_SIZE = 18
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ .-"
OUTPUT_DIR = "resources/fonts/curved"
os.makedirs(OUTPUT_DIR, exist_ok=True)

angles = range(0, 360, 3)
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

max_w, max_h = 0, 0
for c in CHARS:
    bbox = font.getbbox(c)
    if bbox:
        max_w = max(max_w, bbox[2] - bbox[0])
        max_h = max(max_h, bbox[3] - bbox[1])

DIM = int(math.sqrt(max_w**2 + max_h**2)) + 6

fonts_xml_content = "<resources>\n"
monkey_c_content = "using Toybox.WatchUi;\nclass CurvedFonts {\n    static function getFont(idx) {\n"

for i, angle in enumerate(angles):
    fnt_filename = f"curved_{i}"
    images = []
    
    for c in CHARS:
        # Solid black background
        img = Image.new('RGB', (DIM, DIM), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bbox = font.getbbox(c)
        if bbox:
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((DIM/2 - w/2 - bbox[0], DIM/2 - h/2 - bbox[1]), c, font=font, fill=(255, 255, 255))
        
        # Rotate using NEAREST to prevent any antialiased grey pixels, forcing crisp 1-bit output
        rotated = img.rotate(angle, resample=Image.NEAREST, expand=False, fillcolor=(0, 0, 0))
        images.append((c, rotated))
    
    sheet_w = sum(img.width for _, img in images) + len(images)
    sheet_h = DIM
    
    sheet = Image.new('RGB', (sheet_w, sheet_h), (0, 0, 0))
    
    # Set aa=0 in the fnt file to match tomfogg's exact output
    fnt_content = f"""info face="Roboto" size="{FONT_SIZE}" bold=1 italic=0 charset=ascii unicode=0 stretchH=100 smooth=1 aa=0 padding=0,0,0,0 spacing=0,0 outline=0
common lineHeight={sheet_h} base={sheet_h} scaleW={sheet_w} scaleH={sheet_h} pages=1 packed=0
page id=0 file="{fnt_filename}.png"
chars count={len(CHARS)}\n"""
    
    cur_x = 0
    for c, img in images:
        sheet.paste(img, (cur_x, 0))
        char_id = ord(c)
        fnt_content += f"char id={char_id} x={cur_x} y=0 width={DIM} height={DIM} xoffset=0 yoffset=0 xadvance={DIM} page=0 chnl=0\n"
        cur_x += DIM + 1
        
    sheet.save(os.path.join(OUTPUT_DIR, f"{fnt_filename}.png"))
    with open(os.path.join(OUTPUT_DIR, f"{fnt_filename}.fnt"), 'w') as f:
        f.write(fnt_content)
        
    # Set antialias="false" in XML to prevent Garmin from trying to smooth it
    fonts_xml_content += f'    <font id="curved_{i}" filename="fonts/curved/{fnt_filename}.fnt" antialias="false" />\n'
    
    if i == 0:
        monkey_c_content += f"        if (idx == 0) {{ return WatchUi.loadResource(Rez.Fonts.curved_0); }}\n"
    else:
        monkey_c_content += f"        else if (idx == {i}) {{ return WatchUi.loadResource(Rez.Fonts.curved_{i}); }}\n"

fonts_xml_content += "</resources>\n"
monkey_c_content += "        return null;\n    }\n}\n"

with open("resources/curved_fonts.xml", "w") as f:
    f.write(fonts_xml_content)
    
with open("source/CurvedFonts.mc", "w") as f:
    f.write(monkey_c_content)
    
print("Successfully generated curved fonts.")
