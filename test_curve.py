import math

def test_curve(text, center_angle):
    is_bottom = math.sin(center_angle) > 0
    print(f"Text: {text}, Center Angle: {math.degrees(center_angle)}, is_bottom: {is_bottom}")
    
    chars = list(text)
    # fake widths
    char_widths = [10 for _ in chars]
    
    total_arc = sum(char_widths) / 100.0
    start_angle = center_angle - (total_arc / 2.0)
    
    if is_bottom:
        # Bottom text reads left-to-right (from larger angle to smaller angle)
        # So we reverse the characters if we want to iterate increasing angles?
        # Or we just iterate decreasing angles!
        start_angle = center_angle + (total_arc / 2.0)
        current_angle = start_angle
        for i, c in enumerate(chars):
            c_arc = char_widths[i] / 100.0
            a = current_angle - c_arc / 2.0
            rot = -(math.degrees(a) - 90.0)
            print(f"Char {c} at angle {math.degrees(a)}, rot {rot}")
            current_angle -= c_arc
    else:
        start_angle = center_angle - (total_arc / 2.0)
        current_angle = start_angle
        for i, c in enumerate(chars):
            c_arc = char_widths[i] / 100.0
            a = current_angle + c_arc / 2.0
            rot = -(math.degrees(a) + 90.0)
            print(f"Char {c} at angle {math.degrees(a)}, rot {rot}")
            current_angle += c_arc

test_curve("JAN", -math.pi/2) # Top
print("---")
test_curve("JUL", math.pi/2) # Bottom
