brown = (130, 82, 1)
dark_brown = (100, 52, 0)
black = (0,0,0)
white = (255,255,255)

grey = (188,188,188)
dark_grey = (108,108,108)
darkmed_grey = (120,120,120)
very_dark_grey = (80,80,80)

red = (255, 10, 10)
dark_red = (205, 10, 10)

yellow = (255, 255, 10)
dark_yellow = (205, 205, 100)

green = (10, 255, 20)
dark_green = (100, 205, 100)

blue = (10, 10, 195)
medium_blue = (50, 50, 255)
light_blue = (100, 100, 255)

def lighten(c):
    (r,g,b) = c
    return (r+15, g+15, b+15)
def extreme_lighten(c):
    (r,g,b) = c
    return (r+60, g+60, b+60)

def darken(c):
    (r,g,b) = c
    return (r-15, g-15, b-15)
def extreme_darken(c):
    (r,g,b) = c
    return (r-60, g-60, b-60)

def tint(a, b):
    return max(0, a[0]+b[0]), max(0, a[1]+b[1]), max(0, a[2]+b[2])
