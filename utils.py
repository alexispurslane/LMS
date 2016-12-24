import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False
    def __ne__(self, other):
        """Define a non-equality test"""
        return not self.__eq__(other)

def dist(p1, p2):
    return math.ceil(math.sqrt(math.pow(p2.x - p1.x, 2) +
                                math.pow(p2.y - p1.y, 2)))

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def monster_turn(GS):
    for m in GS['terrain_map'].proweling_monsters:
        m.move(GS)
