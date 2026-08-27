import os
import glob
from PIL import Image

for png_file in glob.glob("resources/fonts/*_0.png"):
    img = Image.open(png_file)
    print(f"Checking {png_file}: mode={img.mode}")
    if img.mode == 'L':
        # Create an image where RGB is all white (255), and Alpha is the gray value
        rgba = Image.new("RGBA", img.size, (255, 255, 255, 255))
        rgba.putalpha(img)
        rgba.save(png_file, format="PNG")
        print(f"Fixed {png_file} -> converted L to RGBA with alpha masking")
    elif img.mode == 'P':
        rgba = img.convert("RGBA")
        rgba.save(png_file, format="PNG")
        print(f"Fixed {png_file} -> converted P to RGBA")

