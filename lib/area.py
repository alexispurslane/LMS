import math, random, consts, items, utils

# Represents a stylistic area of the dungeon.
class Area:
    def __init__(self, x, y, w, h, at=None):
        self.pos1 = (x, y)
        self.pos2 = (x+w, y+h)
        self.w = w
        self.h = h

        self.area_type = random.choice(['Marble',
                                        'Cave', 'Cave',
                                        'Planted', 'Planted', 'Planted'])
        if at: self.area_type = at
        
    # Check equality
    def __eq__(self, other):
        return other != None and self.__dict__ == other.__dict__
    
    def inside(self, pos):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        return x1 <= pos[0] and x2 >= pos[0] and y1 <= pos[1] and y2 >= pos[1]
    
    def edge_points(self):
        pnts = [(0,0)]
        for x in range(1, self.pos2[0]):
            pnts.append((x, self.pos1[1]))
            pnts.append((x, self.pos2[1]-1))
            
        for y in range(1, self.pos2[1]):
            pnts.append((self.pos1[0], y))
            pnts.append((self.pos2[0]-1, y))

        return pnts
    
# Represents a dungeon room.
class Room(Area):
    def __init__(self, x, y, w, h):
        super(Room, self).__init__(x, y, w, h)
        # Diagnostic: is this room connected according to the DGA?
        self.connected = False
        self.item_attempts = 0
        
        # Circle dimentions
        self.radius = math.floor(w/2)

        # Room type:
        self.room_type = random.choice([
            'Square', 'Square',
            'Square', 'Round',
            'Round', 'Sanctuary',
            'Square', 'Sancutary',
            'Pool'
        ])

        # Room center.
        if self.room_type == 'Square':
            self.center = (math.floor((self.pos1[0] + self.pos2[0]) / 2),
                           math.floor((self.pos1[1] + self.pos2[1]) / 2))
        elif self.room_type == 'Sanctuary':
            if w < 9:
                self.room_type = 'Square'
                
            self.center = utils.tuple_add(self.pos1, (math.ceil(w/2),
                                                      math.ceil(h/2)))
        else:
            self.center = utils.tuple_add(self.pos1, (math.ceil(w/2),
                                                math.ceil(h/2)))

    # Checks if a room intersects the other.
    def intersects(self, room):
        x1, y1 = self.pos1
        x2, y2 = self.pos2
        return x1 <= room.pos2[0] and x2 >= room.pos1[0] and\
            y1 <= room.pos2[1] and y2 >= room.pos1[1]

    def create_block(self, tmap, spacing, raw_pos):
        pos = utils.tuple_add(self.pos1, raw_pos)
        wall = raw_pos[0] % spacing == 0 and raw_pos[1] % spacing == 0
        tmap.place_cell(pos, is_wall=wall)

        # Add decoration/fire and items.
        if not wall:
            decor = ['FM', None, None, None]
            if tmap.is_hell_level():
                decor = ['FR', 'FL', None, None, None, None]
            if random.randint(1, 1000) < 5:
                decor = ['TTRAP', 'TTRAP', 'DTRAP', 'ITRAP']
            tmap.dungeon['decor'][pos] = random.choice(decor)

            if self.item_attempts < consts.ITEMS_PER_ROOM:
                n = random.randint(1, 100)
                pitems = list(filter(lambda x: n < x.probability,
                                     sorted(items.DUNGEON_ITEMS,
                                            key=lambda x: x.probability)))
                if len(pitems) > 0:
                    tmap.dungeon['items'][pos] = [pitems[0]]
                    self.item_attempts += 1
                else:
                    tmap.dungeon['items'][pos] = []
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
            tmap.dungeon['areas'].append(Area(self.pos1[0]-1, self.pos1[1]-1, self.w+1, self.h+1, at='Marble'))
            for x in range(0, self.w):
                for y in range(0, self.h):
                    self.create_block(tmap, 60, (x, y))
                    
            gap = random.randint(1, math.floor(self.w/2)-3)
            for x in range(gap, self.w-gap):
                for y in range(gap, self.h-gap):
                    pos = utils.tuple_add(self.pos1, (x, y))
                    if x != gap+1: 
                        tmap.place_cell(pos, is_wall=True)

            for x in range(gap+1, self.w-gap-1):
                for y in range(gap+1, self.h-gap-1):
                    pos = utils.tuple_add(self.pos1, (x, y))
                    tmap.place_cell(pos)
        elif self.room_type == 'Pool':
            for x in range(0, self.w):
                for y in range(0, self.h):
                    if x > 0 and y > 0 and x < self.w-1 and y < self.h-1:
                        tmap.dungeon['water'][x, y] = True
                    else:
                        tmap.place_cell((x,y), is_wall=False)
                        tmap.dungeon['items'][x,y] = []
                        tmap.dungeon['decor'][x,y] = None
