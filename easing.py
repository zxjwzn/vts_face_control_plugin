import math

PI = 3.1415926545

def ease_in_sine(t):
    return math.sin(1.5707963 * t)

def ease_out_sine(t):
    return 1 + math.sin(1.5707963 * (t - 1))

def ease_in_out_sine(t):
    return 0.5 * (1 + math.sin(3.1415926 * (t - 0.5)))

def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return t * (2 - t)

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else t * (4 - 2 * t) - 1

def ease_in_cubic(t):
    return t * t * t

def ease_out_cubic(t):
    t -= 1
    return 1 + t * t * t

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        t -= 1
        return 1 + t * (2 * t) * (2 * t)

def ease_in_quart(t):
    t *= t
    return t * t

def ease_out_quart(t):
    t = (t - 1) * t
    return 1 - t * t

def ease_in_out_quart(t):
    if t < 0.5:
        t *= t
        return 8 * t * t
    else:
        t = (t - 1) * t
        return 1 - 8 * t * t

def ease_in_quint(t):
    t2 = t * t
    return t * t2 * t2

def ease_out_quint(t):
    t -= 1
    t2 = t * t
    return 1 + t * t2 * t2

def ease_in_out_quint(t):
    if t < 0.5:
        t2 = t * t
        return 16 * t * t2 * t2
    else:
        t -= 1
        t2 = t * t
        return 1 + 16 * t * t2 * t2

def ease_in_expo(t):
    return (pow(2, 8 * t) - 1) / 255

def ease_out_expo(t):
    return 1 - pow(2, -8 * t)

def ease_in_out_expo(t):
    if t < 0.5:
        return (pow(2, 16 * t) - 1) / 510
    else:
        return 1 - 0.5 * pow(2, -16 * (t - 0.5))

def ease_in_circ(t):
    return 1 - math.sqrt(1 - t)

def ease_out_circ(t):
    return math.sqrt(t)

def ease_in_out_circ(t):
    if t < 0.5:
        return (1 - math.sqrt(1 - 2 * t)) * 0.5
    else:
        return (1 + math.sqrt(2 * t - 1)) * 0.5

def ease_in_back(t):
    return t * t * (2.70158 * t - 1.70158)

def ease_out_back(t):
    t -= 1
    return 1 + t * t * (2.70158 * t + 1.70158)

def ease_in_out_back(t):
    if t < 0.5:
        return t * t * (7 * t - 2.5) * 2
    else:
        t -= 1
        return 1 + t * t * 2 * (7 * t + 2.5)

def ease_in_elastic(t):
    t2 = t * t
    return t2 * t2 * math.sin(t * PI * 4.5)

def ease_out_elastic(t):
    t2 = (t - 1) * (t - 1)
    return 1 - t2 * t2 * math.cos(t * PI * 4.5)

def ease_in_out_elastic(t):
    if t < 0.45:
        t2 = t * t
        return 8 * t2 * t2 * math.sin(t * PI * 9)
    elif t < 0.55:
        return 0.5 + 0.75 * math.sin(t * PI * 4)
    else:
        t2 = (t - 1) * (t - 1)
        return 1 - 8 * t2 * t2 * math.sin(t * PI * 9)

def ease_in_bounce(t):
    return pow(2, 6 * (t - 1)) * abs(math.sin(t * PI * 3.5))

def ease_out_bounce(t):
    return 1 - pow(2, -6 * t) * abs(math.cos(t * PI * 3.5))

def ease_in_out_bounce(t):
    if t < 0.5:
        return 8 * pow(2, 8 * (t - 1)) * abs(math.sin(t * PI * 7))
    else:
        return 1 - 8 * pow(2, -8 * t) * abs(math.sin(t * PI * 7))