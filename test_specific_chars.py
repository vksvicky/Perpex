from PIL import Image
import re

fnt_file = "resources/fonts/Raleway_Large_16.fnt"
png_file = "resources/fonts/Raleway_Large_16_0.png"
img = Image.open(png_file)
data = img.split()[-1] if img.mode in ('RGBA', 'LA') else img

chars_to_check = ['5', '0', '%']
char_ids = [ord(c) for c in chars_to_check]

with open(fnt_file, 'r') as f:
    for line in f:
        if line.startswith('char '):
            attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
            cid = int(attrs['id'])
            if cid in char_ids:
                x, y, w, h = int(attrs['x']), int(attrs['y']), int(attrs['width']), int(attrs['height'])
                opaque = 0
                for iy in range(y, y+h):
                    for ix in range(x, x+w):
                        if ix < data.width and iy < data.height:
                            if data.getpixel((ix, iy)) > 0:
                                opaque += 1
                print(f"Char '{chr(cid)}' (id {cid}): w={w}, h={h}. Opaque pixels: {opaque}")
