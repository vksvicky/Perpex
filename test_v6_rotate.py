from PIL import Image
img = Image.open('resources/drawables/mon_8_v6.png')
# mon_8 is at 120 degrees (7 o'clock). Let's rotate by -120 to make it upright.
# Wait, if its bottom points to center, rotating by -120 should make it read A U G perfectly upright.
rotated = img.rotate(120, expand=True)

def to_ascii(image):
    image = image.convert('L')
    pixels = image.getdata()
    chars = ["B","S","#","&","@","$","%","*","!",":","."]
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + image.width] for index in range(0, new_pixels_count, image.width)]
    return "\n".join(ascii_image)

print(to_ascii(rotated))
