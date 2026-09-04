from PIL import Image
img = Image.open('resources/fonts/Raleway_Large_16_0.png')
img = img.convert('RGBA')
pixels = img.load()
print(pixels[0,0])
