from PIL import Image
img = Image.open('test_dial_jul.png').convert('L')
w, h = img.size
# Find bounding box of all non-white pixels
min_y = h
max_y = 0
for y in range(h):
    for x in range(w):
        if img.getpixel((x, y)) < 128:
            min_y = min(min_y, y)
            max_y = max(max_y, y)

print(f"Bounding box Y: {min_y} to {max_y}")

# Let's see the distribution of pixels in the top 5 rows vs bottom 5 rows of the bounding box
top_pixels = 0
for y in range(min_y, min_y + 5):
    for x in range(w):
        if img.getpixel((x, y)) < 128:
            top_pixels += 1

bottom_pixels = 0
for y in range(max_y - 4, max_y + 1):
    for x in range(w):
        if img.getpixel((x, y)) < 128:
            bottom_pixels += 1

print(f"Top 5 rows dark pixels: {top_pixels}")
print(f"Bottom 5 rows dark pixels: {bottom_pixels}")
