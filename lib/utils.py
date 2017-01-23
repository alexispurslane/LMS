import math, random, consts, items

# Calculate distance.
def dist(p1, p2):
    return math.ceil(math.sqrt(math.pow(p2[0] - p1[0], 2) +
                               math.pow(p2[1] - p1[1], 2)))

def flip(t, do_it=True):
    if do_it:
        return t[1], t[0]
    else:
        return t

def clamp(x, a=1, b=2):
    return max(a, min(x, b-1))

def clamp_point(p, mins=(1, 1), maxs=(1, 1)):
    return (clamp(p[0], a=mins[0], b=maxs[0]),
            clamp(p[1], a=mins[1], b=maxs[1]))

def tuple_add(a, b):
    return tuple(map(sum, zip(a, b)))

# TODO: Allow for animation by waiting to move, but remember moves.
def monster_turn(GS):
    for m in GS['terrain_map'].dungeon['monsters']:
        speed = math.ceil(m.speed/10)
        if speed == 1:
            m.move(GS)
        elif speed > 1 and GS['turns'] % speed == 0:
            m.move(GS)
            
def f7(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

# Checks if b is adjacent to (in a streight line of) a.
def streight_line(a, b):
    return b in [
        (a[0]-1, a[1]),
        (a[0]+1, a[1]),
        (a[0], a[1]-1),
        (a[0], a[1]+1)
    ]
