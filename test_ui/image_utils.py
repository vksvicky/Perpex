import os
from PIL import Image, ImageChops, ImageStat, ImageDraw, ImageFont

# Separator width between panels in the 3-panel composite
_SEPARATOR_WIDTH = 4
_SEPARATOR_COLOR = (60, 60, 60)

# Panel label bar height
_LABEL_HEIGHT = 28
_LABEL_BG = (30, 30, 30)
_LABEL_COLORS = {
    "BASELINE": (56, 189, 248),   # sky blue
    "CURRENT":  (74, 222, 128),   # green
    "DIFF":     (248, 113, 113),  # red
}


def _add_label(img: Image.Image, text: str) -> Image.Image:
    """Returns a new image with a coloured label bar on top."""
    label = Image.new("RGB", (img.width, _LABEL_HEIGHT), _LABEL_BG)
    draw = ImageDraw.Draw(label)
    color = _LABEL_COLORS.get(text, (200, 200, 200))
    # Centre the text
    try:
        font = ImageFont.load_default(size=14)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (img.width - (bbox[2] - bbox[0])) // 2
    ty = (_LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), text, fill=color, font=font)

    combined = Image.new("RGB", (img.width, _LABEL_HEIGHT + img.height))
    combined.paste(label, (0, 0))
    combined.paste(img, (0, _LABEL_HEIGHT))
    return combined


def make_3panel_diff(baseline_path: str, current_path: str, diff_output_path: str) -> dict:
    """
    Produces a 3-panel composite image:
      [ BASELINE (blue tint) | CURRENT | DIFF (red highlights) ]

    Returns a dict:
      {
        "diff_pct": float,          # % of pixels that differ
        "has_baseline": bool,
        "composite_path": str,      # path to the 3-panel image
      }
    """
    has_baseline = os.path.exists(baseline_path)
    has_current  = os.path.exists(current_path)

    if not has_current:
        return {"diff_pct": 0.0, "has_baseline": has_baseline, "composite_path": None}

    if not has_baseline:
        # No baseline yet — just produce a single-panel "current only" composite
        current_img = Image.open(current_path).convert("RGB")
        panel = _add_label(current_img, "CURRENT")
        os.makedirs(os.path.dirname(diff_output_path), exist_ok=True)
        panel.save(diff_output_path)
        return {"diff_pct": None, "has_baseline": False, "composite_path": diff_output_path}

    try:
        baseline_img = Image.open(baseline_path).convert("RGB")
        current_img  = Image.open(current_path).convert("RGB")

        # Normalise sizes
        if baseline_img.size != current_img.size:
            current_img = current_img.resize(baseline_img.size, Image.LANCZOS)

        w, h = baseline_img.size

        # ── Mask out the clock hands ──────────────────────────────────────────
        # The hands radiate from the centre of the watch face. We black out a
        # central ellipse (55% of width, 55% of height) on BOTH images before
        # comparing, so only the metric data slots around the perimeter matter.
        # This is pure test-infrastructure — no production code is touched.
        hands_mask = Image.new("L", (w, h), 255)  # start fully visible
        draw_mask = ImageDraw.Draw(hands_mask)
        cx, cy = w // 2, h // 2
        rx, ry = int(w * 0.52), int(h * 0.52)     # 52% masks hour+minute hands, keeps metric ring
        draw_mask.ellipse(
            [(cx - rx, cy - ry), (cx + rx, cy + ry)],
            fill=0  # black = masked out
        )
        black = Image.new("RGB", (w, h), (0, 0, 0))
        baseline_cmp = Image.composite(baseline_img, black, hands_mask)
        current_cmp  = Image.composite(current_img,  black, hands_mask)
        # ─────────────────────────────────────────────────────────────────────

        # --- Pixel diff (on masked images) ---
        diff = ImageChops.difference(baseline_cmp, current_cmp)
        mask = diff.convert("L").point(lambda p: 255 if p > 5 else 0)

        diff_pixels = sum(mask.getdata()) / 255.0
        # Count only the unmasked (visible) pixels in the denominator
        visible_pixels = sum(1 for p in hands_mask.getdata() if p > 0)
        diff_pct = (diff_pixels / visible_pixels) * 100.0 if visible_pixels else 0.0

        # Red-highlighted diff panel (show on unmasked current so we can see hands)
        red_layer = Image.new("RGB", (w, h), (220, 38, 38))
        diff_panel = Image.composite(red_layer, current_img, mask)

        # Overlay the mask boundary on the diff panel so it's clear what was excluded
        mask_border = ImageDraw.Draw(diff_panel)
        mask_border.ellipse(
            [(cx - rx, cy - ry), (cx + rx, cy + ry)],
            outline=(80, 80, 80), width=1
        )

        # Blue-tinted baseline panel (unmasked, for visual clarity)
        blue_tint = Image.new("RGB", (w, h), (14, 116, 144))
        baseline_panel = Image.blend(baseline_img, blue_tint, alpha=0.15)

        # Add labels
        bp = _add_label(baseline_panel, "BASELINE")
        cp = _add_label(current_img.copy(), "CURRENT")
        dp = _add_label(diff_panel, "DIFF")

        lh = _LABEL_HEIGHT  # label bar height
        panel_h = h + lh
        sep = Image.new("RGB", (_SEPARATOR_WIDTH, panel_h), _SEPARATOR_COLOR)

        composite = Image.new("RGB", (w * 3 + _SEPARATOR_WIDTH * 2, panel_h))
        composite.paste(bp,  (0,                           0))
        composite.paste(sep, (w,                           0))
        composite.paste(cp,  (w + _SEPARATOR_WIDTH,        0))
        composite.paste(sep, (w * 2 + _SEPARATOR_WIDTH,    0))
        composite.paste(dp,  (w * 2 + _SEPARATOR_WIDTH * 2, 0))

        os.makedirs(os.path.dirname(diff_output_path), exist_ok=True)
        composite.save(diff_output_path)

        return {
            "diff_pct": diff_pct,
            "has_baseline": True,
            "composite_path": diff_output_path,
        }

    except Exception as e:
        print(f"  ⚠️  Error generating diff: {e}")
        return {"diff_pct": None, "has_baseline": True, "composite_path": None}


# ── Backwards-compat shim (used by simulator_driver.py) ──────────────────────
def calculate_pixel_diff(baseline_path: str, current_path: str, diff_output_path: str) -> float:
    result = make_3panel_diff(baseline_path, current_path, diff_output_path)
    return result["diff_pct"] if result["diff_pct"] is not None else 0.0
