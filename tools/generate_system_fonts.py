import os
from PIL import Image, ImageDraw, ImageFont

font_path = "/Library/Fonts/Arial.ttf"
out_dir = "resources/fonts"

sizes = {
    "SystemLike_14": 18, # Adjusting to achieve an internal size of around 14
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
            
        atlas_w = 512
        x, y = 0, 0
        max_h = 0
        line_h = 0
        char_metrics = {}
        
        dummy_img = Image.new("RGBA", (100, 100))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        for c in chars_to_render:
            bbox = dummy_draw.textbbox((0, 0), c, font=font, anchor="lt")
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
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
        
        img = Image.new("P", (atlas_w, atlas_h), 0)
        palette = []
        for i in range(256):
            palette.extend([i, i, i])
        img.putpalette(palette)
        
        l_img = Image.new("L", (atlas_w, atlas_h), 0)
        l_draw = ImageDraw.Draw(l_img)
        
        for c, m in char_metrics.items():
            cx = m['x'] - m['xoff']
            cy = m['y'] - m['yoff']
            l_draw.text((cx, cy), c, font=font, fill=255, anchor="lt")
            
        img.paste(l_img)
        
        fnt_lines = [
            'info face="Arial" size=14 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=1,1 outline=0',
            f'common lineHeight={size} base={int(size * 0.8)} scaleW={atlas_w} scaleH={atlas_h} pages=1 packed=0 alphaChnl=0 redChnl=0 greenChnl=0 blueChnl=0',
            f'page id=0 file="{name}_0.png"',
            f'chars count={len(char_metrics)}'
        ]
        
        for c, m in char_metrics.items():
            fnt_lines.append(f"char id={m['id']:<5} x={m['x']:<5} y={m['y']:<5} width={m['w']:<5} height={m['h']:<5} xoffset={m['xoff']:<5} yoffset={m['yoff']:<5} xadvance={m['adv']:<5} page=0  chnl=15")
            
        img.save(f"{out_dir}/{name}_0.png", transparency=0)
        with open(f"{out_dir}/{name}.fnt", "w") as f:
            f.write("\n".join(fnt_lines))

if __name__ == "__main__":
    generate()
