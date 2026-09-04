# Perpex Watch Face - Asset Generation Tools

This directory contains utility Python scripts used to pre-render graphical assets (backgrounds, complex UI elements, and fonts) for the Perpex watch face. 

Pre-rendering these assets into static bitmaps (PNGs) is crucial for Garmin Connect IQ development, as drawing complex shapes (like 60 individual tick marks or anti-aliased custom fonts) dynamically on the watch consumes too much CPU and battery life, especially on Always-On AMOLED displays.

## Setup & Dependencies

All scripts are written in Python 3 and utilize the `Pillow` (PIL) library for image processing. 
A virtual environment (`.venv`) is set up in this directory.

To run these scripts, ensure you have your virtual environment activated and dependencies installed:
```bash
cd tools
source .venv/bin/activate
pip install Pillow
```

## Available Scripts

### 1. `generate_bmfonts.py`
**Purpose:** Generates standard Garmin BMFont files (`.fnt` + `.png` pairs) from a TrueType font (`.ttf`).
**Details:** The Garmin SDK does not natively support scaling custom TTF fonts. This script uses `Pillow` to rasterize a TTF (like `Raleway.ttf`) into a sprite sheet of characters along with an `.fnt` metadata file that maps the character coordinates, widths, and offsets. It ensures critical UI characters (numbers, letters, punctuation, spaces, `%`, `°`) are properly mapped and cleanly anti-aliased using the grayscale alpha channel.

### 2. `generate_dial_bg.py`
**Purpose:** Generates the static analog dial background image.
**Details:** Renders the complex watch face background, including:
- The 60 minute/second tick marks around the outer edge.
- The inner concentric rings that map to data slots.
- Any baked-in text or static dial graphics.
By rendering this as a single static image, the watch simply calls `dc.drawBitmap()` instead of performing expensive trigonometry inside `onUpdate()`.

### 3. `generate_premium_bg.py`
**Purpose:** Generates alternative/premium dial background assets.
**Details:** Similar to `generate_dial_bg.py`, but tailored for different themes or premium aesthetic variations of the watch face.

### 4. `generate_curved_fonts.py`
**Purpose:** Pre-processes fonts for circular/curved rendering.
**Details:** Connect IQ does not have a native `drawTextOnPath` function. To draw text along the circular edge of the screen (e.g. month names or calendar data), this script calculates the necessary rotation and spacing to bake curved text rendering into usable sprite assets.
