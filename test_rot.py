import math
import sys

TWO_PI = math.pi * 2.0
HALF_PI = math.pi / 2.0

def test(angle_deg):
    a = math.radians(angle_deg)
    is_bottom = math.sin(a) > 0.001
    
    if is_bottom:
        rot = -(math.degrees(a) - 90.0)
        print(f"Angle {angle_deg}: BOTTOM -> rot = {rot}")
    else:
        rot = -(math.degrees(a) + 90.0)
        print(f"Angle {angle_deg}: TOP -> rot = {rot}")

test(-90)
test(90)
test(120)
