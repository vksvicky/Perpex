"""
layout_validator.py
===================
Zone-based layout validation for Perpex watch face screenshots.

Derives slot bounding boxes directly from the same formulae used in
UIDrawer.mc (getSlotX / getSlotY), then checks each screenshot for:

  1. RENDERED  - each active slot has non-black content in its zone
  2. NO OVERFLOW - no content extends outside the circular bezel
  3. NO OVERLAP  - adjacent slot zones share content pixels outside
                   the central hands area

The central hands area (a circle of ~35% of the face radius) is excluded
from all checks, since the clock hands always pass through it.

No baseline needed. Each screenshot is validated on its own.
"""

import math
import os
from PIL import Image, ImageDraw


# ── Slot geometry (mirrors UIDrawer.mc getSlotX / getSlotY) ──────────────────

def _slot_center(slot_id, w, h):
    """Returns the (x, y) anchor of a slot as used by UIDrawer."""
    cx, cy = w / 2.0, h / 2.0
    s = w / 260.0

    if w == 320 and h == 360:
        dx = {1: 0, 2: -52, 3: 52, 4: -52, 5: 52, 6: 0}
        dy = {1: -64, 2: -25, 3: -25, 4: 28, 5: 28, 6: 64}
    elif w == 240:
        dx = {1: 0, 2: -42, 3: 42, 4: -42, 5: 42, 6: 0}
        dy = {1: -48, 2: -24, 3: -24, 4: 26, 5: 26, 6: 48}
    elif w == 260:
        dx = {1: 0, 2: -44, 3: 44, 4: -44, 5: 44, 6: 0}
        dy = {1: -52, 2: -25, 3: -25, 4: 27, 5: 27, 6: 52}
    elif w == 280:
        dx = {1: 0, 2: -47, 3: 47, 4: -47, 5: 47, 6: 0}
        dy = {1: -56, 2: -27, 3: -27, 4: 29, 5: 29, 6: 56}
    else:
        dx = {1: 0, 2: int(-44*s), 3: int(44*s), 4: int(-44*s), 5: int(44*s), 6: 0}
        dy = {1: int(-52*s), 2: int(-25*s), 3: int(-25*s),
              4: int(27*s),  5: int(27*s),  6: int(52*s)}

    return cx + dx.get(slot_id, 0), cy + dy.get(slot_id, 0)


def _slot_zone(slot_id, w, h):
    """
    Returns (x1, y1, x2, y2) bounding box for a slot.
    """
    sx, sy = _slot_center(slot_id, w, h)
    s = w / 260.0
    hw = int(18 * s)
    hh = int(18 * s)
    center_y_box = sy - int(2 * s)
    return (
        max(0, int(sx - hw)),
        max(0, int(center_y_box - hh)),
        min(w,  int(sx + hw)),
        min(h,  int(center_y_box + hh)),
    )


# ── Hands mask: central circle to exclude from overlap checks ────────────────

def _in_hands_area(x, y, w, h):
    """Returns True if the pixel is inside the central pivot area."""
    cx, cy = w / 2.0, h / 2.0
    r = min(w, h) * 0.15
    return (x - cx)**2 + (y - cy)**2 <= r * r


# ── Image helpers ─────────────────────────────────────────────────────────────

_DARK_THRESHOLD = 30
_CONTENT_MIN_PX = 8


def _is_bright(pixel):
    return max(pixel[:3]) > _DARK_THRESHOLD


def _zone_content_pixels(pixels, x1, y1, x2, y2, w, h, exclude_hands=False):
    """Count bright pixels in a zone."""
    count = 0
    for y in range(y1, y2):
        for x in range(x1, x2):
            if exclude_hands and _in_hands_area(x, y, w, h):
                continue
            if _is_bright(pixels[x, y]):
                count += 1
    return count


def _zone_overflows_bezel(pixels, x1, y1, x2, y2, w, h):
    """Return count of bright pixels in the zone that are outside the screen bezel."""
    count = 0
    if w != h:
        for y in range(y1, y2):
            for x in range(x1, x2):
                if _is_bright(pixels[x, y]):
                    if x < 4 or x >= w - 4 or y < 4 or y >= h - 4:
                        count += 1
        return count

    rx, ry = w / 2.0, h / 2.0
    cx, cy = w / 2.0, h / 2.0
    for y in range(y1, y2):
        for x in range(x1, x2):
            if _is_bright(pixels[x, y]):
                ddx = (x - cx) / rx
                ddy = (y - cy) / ry
                if ddx*ddx + ddy*ddy > 0.98:
                    count += 1
    return count


def _zone_overflows_inner_ring(pixels, x1, y1, x2, y2, w, h):
    """Return count of bright pixels in the zone that cross outside the safe inner dial (into concentric rings)."""
    s = w / 260.0
    max_safe_r = 72.0 * s
    if w == 320 and h == 360:
        max_safe_r = 88.0
    cx, cy = w / 2.0, h / 2.0
    count = 0
    for y in range(y1, y2):
        for x in range(x1, x2):
            if _is_bright(pixels[x, y]):
                dist = math.hypot(x - cx, y - cy)
                if dist > max_safe_r:
                    count += 1
    return count


def _zones_overlap_count(pixels, zone_a, zone_b, w, h):
    """
    Count bright pixels in the intersection of two zones.
    If the zones do not geometrically intersect, returns 0.
    """
    ax1, ay1, ax2, ay2 = zone_a
    bx1, by1, bx2, by2 = zone_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix1 >= ix2 or iy1 >= iy2:
        return 0
    return _zone_content_pixels(pixels, ix1, iy1, ix2, iy2, w, h, exclude_hands=True)


# ── Public API ────────────────────────────────────────────────────────────────

def validate_layout(img_path, active_slots):
    """
    Validates a single watch face screenshot.

    Args:
        img_path:     Path to screenshot PNG.
        active_slots: List of slot IDs (1-7) that are expected to have content.

    Returns:
        {
          "pass": bool,
          "issues": list[str],
          "slot_results": dict,
          "annotated_path": str,
        }
    """
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    pixels = img.load()

    issues = []
    slot_results = {}
    zones = {sid: _slot_zone(sid, w, h) for sid in active_slots}

    # 0. DIAL SANITY check: Ensure screenshot is actually a rendered dark watch face
    dark_pixels = 0
    total_samples = 0
    step = 4
    for y in range(0, h, step):
        for x in range(0, w, step):
            total_samples += 1
            if max(pixels[x, y]) < 40:
                dark_pixels += 1
    dark_ratio = dark_pixels / total_samples
    if dark_ratio < 0.35:
        issues.append(f"SCREENSHOT INVALID / BLANK: Only {dark_ratio*100:.1f}% dark pixels (expected watch dial background >= 35%). Simulator failed to render.")

    # 1. RENDERED check
    for sid in active_slots:
        x1, y1, x2, y2 = zones[sid]
        content = _zone_content_pixels(pixels, x1, y1, x2, y2, w, h)
        rendered = content >= _CONTENT_MIN_PX
        slot_results[sid] = {
            "rendered": rendered,
            "content_px": content,
            "overflow_px": 0,
            "zone": zones[sid],
        }
        if not rendered:
            issues.append(
                f"Slot {sid}: NO CONTENT — only {content} bright pixels in zone "
                f"({x1},{y1})-({x2},{y2})"
            )

    # 2. OVERFLOW check (bezel & inner ring)
    for sid in active_slots:
        x1, y1, x2, y2 = zones[sid]
        overflow = _zone_overflows_bezel(pixels, x1, y1, x2, y2, w, h)
        ring_overflow = _zone_overflows_inner_ring(pixels, x1, y1, x2, y2, w, h)
        slot_results[sid]["overflow_px"] = overflow + ring_overflow
        if overflow > 5:
            issues.append(f"Slot {sid}: OVERFLOW — {overflow} pixels outside bezel")
        if ring_overflow > 15:
            issues.append(f"Slot {sid}: RING COLLISION — {ring_overflow} pixels crossed into concentric date/month rings")

    # 3. OVERLAP & HORIZONTAL CLEARANCE check
    # Check if Slot 1 content bleeds into Slot 2 (left) or Slot 3 (right)
    s = w / 260.0
    center_x = w // 2
    
    if 1 in active_slots:
        z1 = zones[1]
        z2 = zones.get(2)
        z3 = zones.get(3)
        # Scan Slot 1 text row region (from y1 to y2)
        # For each y, measure contiguous text span starting from center_x
        text_min_x, text_max_x = center_x, center_x
        found_text = False
        for y in range(z1[1], z1[3]):
            # Scan left from center_x while pixels are bright and not concentric rings
            lx = center_x
            while lx >= 0 and _is_bright(pixels[lx, y]) and math.hypot(lx - center_x, y - (h // 2)) <= 68 * s:
                lx -= 1
            # Scan right from center_x while pixels are bright and not concentric rings
            rx = center_x
            while rx < w and _is_bright(pixels[rx, y]) and math.hypot(rx - center_x, y - (h // 2)) <= 68 * s:
                rx += 1
            if rx - lx - 1 > 3:
                found_text = True
                if lx + 1 < text_min_x: text_min_x = lx + 1
                if rx - 1 > text_max_x: text_max_x = rx - 1
        
        if found_text:
            text_width = text_max_x - text_min_x + 1
            # Slot 1 text should not extend past the inner boundary of Slot 2 or Slot 3
            if z2 and text_min_x <= z2[2] - int(2 * s):
                issues.append(f"Slot 1: HORIZONTAL OVERLAP with Slot 2 (text width {text_width}px extends into Slot 2 boundary)")
            if z3 and text_max_x >= z3[0] + int(2 * s):
                issues.append(f"Slot 1: HORIZONTAL OVERLAP with Slot 3 (text width {text_width}px extends into Slot 3 boundary)")

    adjacent_pairs = [(1,2), (1,3), (2,4), (3,5), (4,6), (5,6)]
    for (a, b) in adjacent_pairs:
        if a in active_slots and b in active_slots:
            shared = _zones_overlap_count(pixels, zones[a], zones[b], w, h)
            if shared > 8:
                issues.append(f"Slots {a}+{b}: OVERLAP — {shared} shared pixels")

    # 3b. DIAL COVERAGE check: Ensure dial background spans full display radius
    if w == h and w > 260:
        outer_dial_r = int(w * 0.44)
        outer_content = 0
        for deg in range(0, 360, 5):
            rad = math.radians(deg)
            for r_offset in range(-8, 8):
                qx = int(center_x + (outer_dial_r + r_offset) * math.cos(rad))
                qy = int(center_x + (outer_dial_r + r_offset) * math.sin(rad))
                if 0 <= qx < w and 0 <= qy < h and _is_bright(pixels[qx, qy]):
                    outer_content += 1
                    break
        if outer_content < 5:
            issues.append(f"DIAL UNDERSIZED / MISALIGNED: Outer dial perimeter has only {outer_content} markings at radius {outer_dial_r}px (expected full-diameter dial background).")

    # 4. Annotated debug image
    annotated = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(annotated, "RGBA")

    # Draw bezel boundary
    if w != h:
        draw.rounded_rectangle([(2, 2), (w-2, h-2)], radius=24, outline=(80, 80, 80, 200), width=2)
    else:
        draw.ellipse([(2, 2), (w-2, h-2)], outline=(80, 80, 80, 200), width=2)

    # Draw safe inner dial ring (concentric ring boundary)
    s = w / 260.0
    r_inner = 88 if (w == 320 and h == 360) else int(72.0 * s)
    cx, cy = w // 2, h // 2
    draw.ellipse([(cx - r_inner, cy - r_inner), (cx + r_inner, cy + r_inner)], outline=(200, 140, 40, 160), width=1)

    # Draw hands exclusion circle
    r = int(min(w, h) * 0.15)
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], outline=(80, 80, 200, 150), width=1)

    # Draw slot zones
    for sid in active_slots:
        x1, y1, x2, y2 = zones[sid]
        sr = slot_results[sid]
        ok = sr["rendered"] and sr["overflow_px"] <= 15
        color = (0, 220, 80, 200) if ok else (220, 40, 40, 200)
        draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=2)
        draw.text((x1 + 2, y1 + 1), str(sid), fill=color)

    base, _ = os.path.splitext(img_path)
    annotated_path = base + "_zones.png"
    annotated.save(annotated_path)

    return {
        "pass": len(issues) == 0,
        "issues": issues,
        "slot_results": slot_results,
        "annotated_path": annotated_path,
    }
