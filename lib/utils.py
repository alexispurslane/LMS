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
        self.radius = math.floor(w/2)
        self.center = Point(math.floor((self.x1 + self.x2) / 2),
                            math.floor((self.y1 + self.y2) / 2));
        
        self.room_type = random.choice([
            'Square', 'Square',
            'Square', 'Square',
            'Square', 'Square',
            'Square', 'Round',
        ])

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
        def putpixel(x, y, wall=False):
            pos = max(0, x), max(0, y)
            tmap.remembered_terrain.transparent[pos] = not wall
            tmap.remembered_terrain.walkable[pos] = not wall
            tmap.lighted_terrain.transparent[pos] = not wall
            tmap.lighted_terrain.walkable[pos] = not wall
            
        if self.room_type == 'Square':
            n = random.randint(1, 100)
            rand_walls = n < 25 and math.floor(n/5) != 0
            for x in range(0, self.w):
                for y in range(0, self.h):
                    wall = False
                    if rand_walls and x+y % math.floor(n/5) == 0:
                        wall = True

                    putpixel(x+self.x1, y+self.y1, wall=wall)

                    if not wall:
                        pos = x+self.x1, y+self.y1
                        if tmap.hell_level:
                            tmap.dungeon_decor[pos] = random.choice(['FR', 'FL', None, None, None, None])
                        else:
                            tmap.dungeon_decor[pos] = random.choice(['FM', None, None, None, None])
                        
        elif self.room_type == 'Round':
            for x in range(-self.radius, self.radius):
                for y in range(-self.radius, self.radius):
                        if x*x + y*y <= pow(self.radius, 2):
                            putpixel(self.x1 + x, self.y1 + y);

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

def streight_line(a, b):
    As = [
        (a[0]-1, a[1]),
        (a[0]+1, a[1]),
        (a[0], a[1]-1),
        (a[0], a[1]+1),
    ]

    return b in As
