from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.text((10, 10), "A", fill=(255,255,255,255))
img.save("test_rgba.png")
img2 = Image.open("test_rgba.png")
print("Mode:", img2.mode, "Extrema:", img2.getextrema())
