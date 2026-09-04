import os
from PIL import Image, ImageDraw, ImageFont

font_path = "resources/fonts/Raleway.ttf"
out_dir = "resources/fonts"

sizes = {
    "Raleway_Large_16": 24, # Tweaked to approximate the desired pixel size
    "Raleway_Native_20": 28 # Tweaked to approximate the desired pixel size
}

chars_to_render = [chr(i) for i in range(32, 127)] + [chr(176)] # ASCII + degree symbol

def generate():
    for name, size in sizes.items():
        print(f"Generating {name}...")
        
        try:
            font = ImageFont.truetype(font_path, size)
        except Exception as e:
            print(f"Failed to load font: {e}")
            continue
            
        # First pass: calculate total atlas width and max height
        atlas_w = 1024
        x, y = 0, 0
        max_h = 0
        line_h = 0
        
        char_metrics = {}
        
        # We need a dummy image just to get getbbox
        dummy_img = Image.new("RGBA", (100, 100))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        for c in chars_to_render:
            # get bounding box
            # getbbox returns (left, top, right, bottom)
            bbox = dummy_draw.textbbox((0, 0), c, font=font, anchor="lt")
            
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            
            # advance
            adv = dummy_draw.textlength(c, font=font)
            
            if x + w > atlas_w:
                x = 0
                y += line_h + 2
                line_h = 0
                
            char_metrics[c] = {
                'id': ord(c),
                'x': x,
                'y': y,
                'w': w,
                'h': h,
                'xoff': bbox[0],
                'yoff': bbox[1],
                'adv': int(adv + 0.5)
            }
            
            x += w + 2
            line_h = max(line_h, h)
            
        atlas_h = y + line_h + 2
        
        # Second pass: Draw the atlas
        # MUST BE 8-BIT PALETTED WITH INDEX 0 AS TRANSPARENT
        # Image.new("P") initializes all pixels to index 0.
        img = Image.new("P", (atlas_w, atlas_h), 0)
        
        # Create a 256-color palette.
        # Index 0: Transparent (RGB 0,0,0, but we specify transparency=0 in save)
        # Index 255: White (255,255,255)
        # To anti-alias, we use grayscale colors from index 0 to 255
        palette = []
        for i in range(256):
            palette.extend([i, i, i])
        img.putpalette(palette)
        
        # We can't directly draw anti-aliased text on a 'P' image with ImageDraw.
        # So we draw on an 'L' image, then copy it to the 'P' image.
        l_img = Image.new("L", (atlas_w, atlas_h), 0)
        l_draw = ImageDraw.Draw(l_img)
        
        for c, m in char_metrics.items():
            # Draw on L image. White text.
            # We offset by -bbox[0] and -bbox[1] so the top-left of the bounding box is at m['x'], m['y']
            cx = m['x'] - m['xoff']
            cy = m['y'] - m['yoff']
            l_draw.text((cx, cy), c, font=font, fill=255, anchor="lt")
            
        # Copy L to P. In Pillow, L pixels (0-255) directly map to P indices (0-255).
        # Since our palette has index i = color (i,i,i), this works perfectly!
        img.paste(l_img)
        
        # Third pass: generate .fnt file
        fnt_lines = [
            'info face="Raleway" size=20 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
            f'common lineHeight={size} base={int(size * 0.8)} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0 alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0',
            f'page id=0 file="{name}_0.png"',
            f'chars count={len(char_metrics)}'
        ]
        
        for c, m in char_metrics.items():
            fnt_lines.append(f"char id={m['id']:<5} x={m['x']:<5} y={m['y']:<5} width={m['w']:<5} height={m['h']:<5} xoffset={m['xoff']:<5} yoffset={m['yoff']:<5} xadvance={m['adv']:<5} page=0  chnl=15")
            
        # Save files
        img.save(f"{out_dir}/{name}_0.png", transparency=0)
        with open(f"{out_dir}/{name}.fnt", "w") as f:
            f.write("\n".join(fnt_lines))

if __name__ == "__main__":
    generate()
