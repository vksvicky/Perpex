from PIL import Image
img = Image.open('test_output/screenshots/fenix7.png').convert('RGB')
# Look at the battery area (top, around x=130, y=50)
found_white = False
for y in range(40, 90):
    for x in range(100, 160):
        r, g, b = img.getpixel((x, y))
        if r > 200 and g > 200 and b > 200:
            found_white = True
            break
print("Found white text:", found_white)
