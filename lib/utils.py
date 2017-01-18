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

# Represents a dungeon room.
class Room:
    def __init__(self, x, y, w, h):
        # Diagnostic: is this room connected according to the DGA?
        self.connected = False
        self.item_attempts = 0
        
        # Starting point position
        self.pos1 = (x, y)
        
        # Ending point position
        self.pos2 = (x + w, y + h)

        # Dimentions
        self.w = w
        self.h = h

        # Circle dimentions
        self.radius = math.floor(w/2)

        # Room type:
        # 3/5 chance to be square,
        # 1/5 chance to be round,
        # 1/5 chance to be a sanctuary.
        self.room_type = random.choice([
            'Square', 'Square',
            'Square', 'Round',
            'Sanctuary'
        ])

        # Room center.
        if self.room_type == 'Square':
            self.center = (math.floor((self.pos1[0] + self.pos2[0]) / 2),
                           math.floor((self.pos1[1] + self.pos2[1]) / 2))
        elif self.room_type == 'Sanctuary':
            if w < 6:
                self.room_type = 'Square'
                
            self.center = tuple_add(self.pos1, (math.ceil(w/2),
                                                math.ceil(h/2)))
        else:
            self.center = tuple_add(self.pos1, (math.ceil(w/2),
                                                math.ceil(h/2)))

    def edge_points(self):
        pnts = [(0,0)]
        for x in range(1, self.pos2[0]):
            pnts.append((x, self.pos1[1]))
            pnts.append((x, self.pos2[1]-1))
            
        for y in range(1, self.pos2[1]):
            pnts.append((self.pos1[0], y))
            pnts.append((self.pos2[0]-1, y))

        return pnts
    
    # Checks if a room intersects the other.
    def intersects(self, room):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        return x1 <= room.pos2[0] and x2 >= room.pos1[0] and\
            y1 <= room.pos2[1] and y2 >= room.pos1[1]

    def create_block(self, tmap, spacing, raw_pos):
        pos = tuple_add(self.pos1, raw_pos)
        wall = raw_pos[0] % spacing == 0 and raw_pos[1] % spacing == 0
        tmap.place_cell(pos, is_wall=wall)

        # Add decoration/fire and items.
        if not wall:
            decor = ['FM', None, None, None, None]
            if tmap.is_hell_level():
                decor = ['FR', 'FL', None, None, None, None]
            tmap.dungeon['decor'][pos] = random.choice(decor)

            if self.item_attempts < consts.ITEMS_PER_ROOM:
                if random.randint(1, 2) == 1:
                    n = random.randint(1, 100)
                    pitems = list(filter(lambda x: n < x.probability,
                                         sorted(items.DUNGEON_ITEMS,
                                                key=lambda x: x.probability)))
                    if len(pitems) > 0:
                        tmap.dungeon['items'][pos] = [pitems[0]]
                        
                    self.item_attempts += 1
            else:
                tmap.dungeon['items'][pos] = []

    # Draws the room into the supplied terrain map.
    def draw_into_map(self, i, tmap):
        spacing = random.randint(4, 31)
        
        if self.room_type == 'Square':
            for x in range(0, self.w):
                for y in range(0, self.h):
                    self.create_block(tmap, spacing, (x, y))
        elif self.room_type == 'Round':
            for x in range(-self.radius, self.radius):
                for y in range(-self.radius, self.radius):
                    if x*x + y*y <= pow(self.radius, 2):
                        self.create_block(tmap, spacing, (x, y))
        elif self.room_type == 'Sanctuary':
            for x in range(0, self.w):
                for y in range(0, self.h):
                    self.create_block(tmap, spacing, (x, y))
                    
            gap = random.randint(1, math.floor(self.w/2)-3)
            for x in range(gap, self.w-gap):
                for y in range(gap, self.h-gap):
                    pos = tuple_add(self.pos1, (x, y))
                    if x != gap+1: 
                        tmap.place_cell(pos, is_wall=True)

            for x in range(gap+1, self.w-gap-1):
                for y in range(gap+1, self.h-gap-1):
                    pos = tuple_add(self.pos1, (x, y))
                    tmap.place_cell(pos)
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
