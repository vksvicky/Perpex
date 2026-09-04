from PIL import Image
import re
import sys

fnt_file = "resources/fonts/Raleway_Native_20.fnt"
png_file = "resources/fonts/Raleway_Native_20_0.png"

img = Image.open(png_file)
data = img.split()[-1] if img.mode in ('RGBA', 'LA') else img

total_box = 0
opaque_in_box = 0
with open(fnt_file, 'r') as f:
    for line in f:
        if line.startswith('char '):
            attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
            x, y, w, h = int(attrs['x']), int(attrs['y']), int(attrs['width']), int(attrs['height'])
            total_box += w * h
            for iy in range(y, y+h):
                for ix in range(x, x+w):
                    if ix < data.width and iy < data.height:
                        if data.getpixel((ix, iy)) > 0:
                            opaque_in_box += 1

print(f"Opaque in box: {opaque_in_box} / {total_box}")
