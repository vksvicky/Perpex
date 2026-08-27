from PIL import Image
img = Image.open('resources/fonts/Raleway_Large_16_0.png')
img = img.convert('RGBA')
pixels = img.load()
width, height = img.size
found_alpha = False
for y in range(height):
    for x in range(width):
        r,g,b,a = pixels[x,y]
        if a > 0 or r > 0 or g > 0 or b > 0:
            found_alpha = True
            break
print(f"Size: {width}x{height}, Found non-zero pixels: {found_alpha}")
