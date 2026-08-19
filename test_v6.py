from PIL import Image
img = Image.open('resources/drawables/mon_8_v6.png')
# save it as ascii art to see what it looks like
def to_ascii(image):
    image = image.convert('L')
    pixels = image.getdata()
    chars = ["B","S","#","&","@","$","%","*","!",":","."]
    new_pixels = [chars[pixel//25] for pixel in pixels]
    new_pixels = ''.join(new_pixels)
    new_pixels_count = len(new_pixels)
    ascii_image = [new_pixels[index:index + image.width] for index in range(0, new_pixels_count, image.width)]
    return "\n".join(ascii_image)

print(to_ascii(img))
