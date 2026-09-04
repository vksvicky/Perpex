from PIL import Image
img = Image.open('resources/fonts/Raleway_Large_16_0.png')
img = img.convert('RGBA')
pixels = img.load()
width, height = img.size
found = False
for y in range(height):
    for x in range(width):
        if pixels[x,y][0] > 0:
            print(f"Found non-zero red at {x},{y}: {pixels[x,y]}")
            found = True
            break
    if found: break
