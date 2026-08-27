import os
import glob
from PIL import Image

for png_file in glob.glob("resources/fonts/*_0.png"):
    img = Image.open(png_file)
    if img.mode == 'L':
        pass # we will process it
    elif img.mode == 'RGBA':
        img = img.split()[-1] # extract alpha back to L
    
    # img is now L mode, representing the alpha mask.
    # We want to create a P mode image where the palette is all white,
    # but the transparency is mapped to the L channel.
    # Pillow allows saving an L mode image as P by simply doing:
    # img.convert("P") ? No, we need transparency.
    # Actually, if we just save RGBA with a specific tool it might work.
    pass

