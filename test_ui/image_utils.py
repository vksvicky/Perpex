import os
from PIL import Image, ImageChops, ImageStat

def calculate_pixel_diff(img1_path, img2_path, diff_output_path):
    if not os.path.exists(img1_path) or not os.path.exists(img2_path):
        return 0.0

    try:
        im1 = Image.open(img1_path).convert('RGB')
        im2 = Image.open(img2_path).convert('RGB')

        diff = ImageChops.difference(im1, im2)
        
        # Create visual diff mask (threshold > 5)
        mask = diff.convert('L').point(lambda x: 255 if x > 5 else 0)
        
        # Calculate percentage of pixels that are different
        stat_mask = ImageStat.Stat(mask)
        diff_pixels = stat_mask.sum[0] / 255.0
        total_pixels = mask.width * mask.height
        diff_pct = (diff_pixels / total_pixels) * 100
        im_mask = Image.new('RGB', im1.size, (255, 0, 0))
        result = Image.composite(im_mask, im2, mask)
        result.save(diff_output_path)

        return diff_pct
    except Exception as e:
        print(f"Error calculating diff: {e}")
        return 100.0
