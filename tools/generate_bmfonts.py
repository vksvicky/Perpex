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
            continue
            
        with open(fnt_file, 'r') as f:
            fnt_data = f.read()
            
        common_match = re.search(r'common .*scaleW=(\d+)\s+scaleH=(\d+)', fnt_data)
        if not common_match:
            continue
            
        atlas_w = int(common_match.group(1))
        atlas_h = int(common_match.group(2))
        
        chars = []
        for line in fnt_data.split('\n'):
            if line.startswith('char '):
                attrs = dict(re.findall(r'(\w+)=(-?\d+)', line))
                if attrs:
                    chars.append(attrs)
                    
        if not chars:
            continue
            
        try:
            font = ImageFont.truetype(font_path, 100) 
        except Exception as e:
            print(f"Failed to load font: {e}")
            continue
            
        img_l = Image.new("L", (atlas_w, atlas_h), 0)
        
        for char_info in chars:
            c_id = int(char_info['id'])
            x = int(char_info['x'])
            y = int(char_info['y'])
            w = int(char_info['width'])
            h = int(char_info['height'])
            
            if w == 0 or h == 0:
                continue
                
            c = chr(c_id)
            
            temp_img = Image.new("L", (200, 200), 0)
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((50, 50), c, font=font, fill=255)
            
            bbox = temp_img.getbbox()
            if bbox:
                char_img = temp_img.crop(bbox)
                char_img = char_img.resize((w, h), Image.Resampling.LANCZOS)
                img_l.paste(char_img, (x, y))
            
        # Create an 8-bit paletted PNG with anti-aliasing transparency
        img_p = Image.new("P", (atlas_w, atlas_h), 0)
        
        # All colors in the palette are White (255, 255, 255)
        palette = [255, 255, 255] * 256
        img_p.putpalette(palette)
        
        # We need to tell PIL that each palette index has a specific transparency (alpha)
        # So index i has alpha=i
        transparency = bytes(range(256))
        
        img_p.paste(img_l, (0, 0))
        img_p.save(png_file, format="PNG", transparency=transparency)
        print(f"Generated {png_file} (Paletted with full alpha)")
        
if __name__ == "__main__":
    generate_pngs()
