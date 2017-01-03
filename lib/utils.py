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
        speed = math.ceil(m.speed/10)
        if speed == 1:
            m.move(GS)
        elif speed > 1 and GS['turns'] % speed == 0:
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

    def edge_points(self):
        pnts = [(0,0)]
        for x in range(1, self.x2):
            pnts.append((x, self.y1))
            pnts.append((x, self.y2-1))

        for y in range(1, self.y2):
            pnts.append((self.x1, y))
            pnts.append((self.x2-1, y))

        return pnts

    def draw_into_map(self, tmap):
        waters = 0
        for x in range(0, self.w):
            for y in range(0, self.h):
                pos = x+self.x1, y+self.y1
                tmap.terrain_map.transparent[pos] = True
                tmap.terrain_map.walkable[pos] = True
                
                tmap.alt_terrain_map.transparent[pos] = True
                tmap.alt_terrain_map.walkable[pos] = True
                
                tmap.dungeon_decor[pos] = random.choice(['FM', None, None, None, None])

def dir_of(pos1, pos2):
    if pos1[0] < pos2[0]:
        return 'LEFT'
    elif pos1[0] > pos2[0]:
        return 'RIGHT'
    elif pos1[1] > pos2[1]:
        return 'DOWN'
    elif pos1[1] < pos2[1]:
        return 'UP'
    else:
        return 'SAME'
