import math
for a_deg in [-90, -45, 0, 45, 90, 135, 180]:
    rot = -(a_deg + 90.0)
    # PIL rotate by `rot` counter-clockwise.
    # original top is -90.
    new_top = -90 - rot
    new_top = new_top % 360
    inwards = (a_deg - 180) % 360
    outwards = a_deg % 360
    print(f"a={a_deg}: rot={rot}, new_top={new_top}, inwards={inwards}, outwards={outwards}")
