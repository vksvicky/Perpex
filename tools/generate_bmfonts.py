import os
from PIL import Image, ImageDraw, ImageFont
import re

font_path = "resources/fonts/Raleway.ttf"
out_dir = "resources/fonts"

sizes = {
    "Raleway_Tiny_6": 12,
    "Raleway_XSmall_8": 16,
    "Raleway_XXSmall_10": 20,
    "Raleway_Small_12": 24,
    "Raleway_Medium_14": 28,
    "Raleway_Large_16": 32,
    "Raleway_XLarge_18": 36,
    "Raleway_Native_20": 40
}

def generate_pngs():
    for name, size in sizes.items():
        fnt_file = f"{out_dir}/{name}.fnt"
        png_file = f"{out_dir}/{name}_0.png"
        
        if not os.path.exists(fnt_file):
            print(f"Skipping {name}, fnt not found")
            continue
            
        print(f"Generating PNG for {name} from existing .fnt...")
        
        with open(fnt_file, 'r') as f:
            fnt_data = f.read()
            
        # Parse scaleW and scaleH from common line
        common_match = re.search(r'common .*scaleW=(\d+)\s+scaleH=(\d+)', fnt_data)
        if not common_match:
            print("Could not find scaleW/H")
            continue
            
        atlas_w = int(common_match.group(1))
        atlas_h = int(common_match.group(2))
        
        # We need a font size that approximately matches the bounding boxes
        # The '.fnt' sizes were 6, 8, 10 but that was likely 'points' and rendered at a higher DPI
        # Let's try to infer a good Pillow size by finding the max height
        chars = []
        for line in fnt_data.split('\n'):
            if line.startswith('char '):
                # parse attributes
                attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
                if attrs:
                    chars.append(attrs)
                    
        if not chars:
            continue
            
        # Try to find a font size that fits. size = max_height * 1.2
        max_h = max(int(c['height']) for c in chars)
        
        # Load font
        try:
            # size is points, usually pixels is slightly larger. Trial and error approximation based on max_h
            font = ImageFont.truetype(font_path, int(max_h * 1.3)) 
        except Exception as e:
            print(f"Failed to load font: {e}")
            continue
            
        img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for char_info in chars:
            c_id = int(char_info['id'])
            x = int(char_info['x'])
            y = int(char_info['y'])
            w = int(char_info['width'])
            h = int(char_info['height'])
            xoff = int(char_info['xoffset'])
            yoff = int(char_info['yoffset'])
            
            c = chr(c_id)
            
            # Draw character exactly within the bounds
            # Pillow anchor lt means left ascender. 
            draw.text((x - (xoff/2), y - (yoff/2)), c, font=font, fill=(255,255,255,255), anchor="lt")
            
        img.save(png_file)
        
if __name__ == "__main__":
    generate_pngs()
