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

    if w == 260:
        dx = {1: 0, 2: -36, 3: 36, 4: 0, 5: -36, 6: 36, 7: 0}
        dy = {1: -42, 2: -22, 3: -22, 4: 10, 5: 24, 6: 24, 7: 48}
    elif w == 280:
        dx = {1: 0, 2: -39, 3: 39, 4: 0, 5: -39, 6: 39, 7: 0}
        dy = {1: -45, 2: -24, 3: -24, 4: 11, 5: 26, 6: 26, 7: 52}
    else:
        dx = {1: 0, 2: int(-36*s), 3: int(36*s), 4: 0,
              5: int(-36*s), 6: int(36*s), 7: 0}
        dy = {1: int(-42*s), 2: int(-22*s), 3: int(-22*s),
              4: int(10*s),  5: int(24*s),  6: int(24*s),  7: int(48*s)}

    return cx + dx.get(slot_id, 0), cy + dy.get(slot_id, 0)


def _slot_zone(slot_id, w, h):
    """
    Returns (x1, y1, x2, y2) bounding box for a slot.
    """
    sx, sy = _slot_center(slot_id, w, h)
    s = w / 260.0
    hw = int(18 * s)
    hh = int(18 * s)
    return (
        max(0, int(sx - hw)),
        max(0, int(sy - hh)),
        min(w,  int(sx + hw)),
        min(h,  int(sy + hh)),
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
    """Return count of bright pixels in the zone that are outside the bezel ellipse."""
    rx, ry = w / 2.0, h / 2.0
    cx, cy = w / 2.0, h / 2.0
    count = 0
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

    # 3. OVERLAP check (only directly adjacent slot pairs)
    adjacent_pairs = [(1,2),(1,3),(2,4),(3,4),(4,5),(4,6),(5,7),(6,7)]
    for (a, b) in adjacent_pairs:
        if a in active_slots and b in active_slots:
            shared = _zones_overlap_count(pixels, zones[a], zones[b], w, h)
            if shared > 8:
                issues.append(f"Slots {a}+{b}: OVERLAP — {shared} shared pixels")

    # 4. Annotated debug image
    annotated = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(annotated, "RGBA")

    # Draw bezel boundary
    draw.ellipse([(2, 2), (w-2, h-2)], outline=(80, 80, 80, 200), width=2)

    # Draw safe inner dial ring (concentric ring boundary)
    s = w / 260.0
    r_inner = int(72.0 * s)
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
