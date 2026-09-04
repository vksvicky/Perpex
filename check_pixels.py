from PIL import Image
import re

fnt_file = "resources/fonts/Raleway_Large_16.fnt"
png_file = "resources/fonts/Raleway_Large_16_0.png"

img = Image.open(png_file)
# if img is RGBA, we can check alpha.
if img.mode == 'RGBA':
    data = img.split()[3]
elif img.mode == 'LA':
    data = img.split()[1]
else:
    data = img

total_box_area = 0
opaque_pixels_in_boxes = 0

with open(fnt_file, 'r') as f:
    for line in f:
        if line.startswith('char '):
            attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
            x, y, w, h = int(attrs['x']), int(attrs['y']), int(attrs['width']), int(attrs['height'])
            total_box_area += w * h
            for iy in range(y, y+h):
                for ix in range(x, x+w):
                    if ix < data.width and iy < data.height:
                        if data.getpixel((ix, iy)) > 0:
                            opaque_pixels_in_boxes += 1

print(f"Total box area: {total_box_area}")
print(f"Opaque pixels inside boxes: {opaque_pixels_in_boxes}")

# Total opaque pixels in the entire image
total_opaque = sum(1 for p in data.getdata() if p > 0)
print(f"Total opaque pixels in image: {total_opaque}")

