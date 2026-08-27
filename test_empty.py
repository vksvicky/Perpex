import glob
from PIL import Image

for png_file in glob.glob("resources/fonts/*_0.png"):
    img = Image.open(png_file)
    extrema = img.getextrema()
    print(f"{png_file}: {extrema}")

