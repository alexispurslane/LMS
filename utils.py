import math, random

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

class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.x2 = x + w
        self.y1 = y
        self.y2 = y + h
        self.w = w
        self.h = h
        self.center = Point(math.floor((self.x1 + self.x2) / 2),
                            math.floor((self.y1 + self.y2) / 2));

    def intersects(self, room):
        return self.x1 <= room.x2 and self.x2 >= room.x1 and\
               self.y1 <= room.y2 and self.y2 >= room.y1

    def draw_into_map(self, tmap):
        waters = 0
        for x in range(0, self.w):
            for y in range(0, self.h):
                pos = x+self.x1, y+self.y1
                tmap.terrain_map.transparent[pos] = True
                tmap.terrain_map.walkable[pos] = True
                tmap.dungeon_decor[pos] = random.choice(['FM', 'RB', None, None, None])
                
                if random.randint(0, 100) > 90 and waters < 1:
                    tmap.water[pos] = True
                    waters += 1
                if tmap.adjacent_water(x, y):
                    tmap.water[pos] = True
