from PIL import Image, ImageDraw
import re

fnt_file = "resources/fonts/Raleway_Large_16.fnt"
png_file = "resources/fonts/Raleway_Large_16_0.png"

img = Image.open(png_file).convert("RGBA")
draw = ImageDraw.Draw(img)

with open(fnt_file, 'r') as f:
    for line in f:
        if line.startswith('char '):
            attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
            x, y, w, h = int(attrs['x']), int(attrs['y']), int(attrs['width']), int(attrs['height'])
            # Draw a red rectangle showing the bounding box
            draw.rectangle([x, y, x+w, y+h], outline=(255, 0, 0, 255))

img.save("debug_bounds.png")
print("Saved debug_bounds.png")
