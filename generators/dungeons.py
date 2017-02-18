import tdl, random, math, copy
from functools import *
from operator import *
import monsters, colors, consts, utils, items, dungeons, forests, area

def generate_new_dungeon_map(self):
    r = random.randint(1, 10)
    rtype = 'catacomb'
    if r <= 3:
        rtype = 'barrack'
    return globals()['generate_new_'+rtype+'_map'](self)

# Each cell must have a decor set to None and an items set to []
# Must return starting location of player, up_stairs, and down_stairs

class Walker:
    def __init__(self, pos=(10, 13), direction=0):
        self.pos, self.direction = pos, direction
        self.smoothing = 0.4
        self.wiggle_max = 0.7

    def wander(self, tmap):
        self.perturb_direction()
        return self.walk(tmap)

    def create_child(self):
        return Walker(self.pos, self.direction + 2*random.randint(0, 2) - 1)

    def walk(self, tmap, d=None):
        if not d: d = self.direction_with_smoothing_fuzz()
        d = round(d) % 4
        npos = utils.tuple_add(self.pos, ([1, 0, -1, 0][d],
                                          [0, 1, 0, -1][d]))
        if tmap.on_map_bordered(npos):
            self.pos = npos
            
        return self

    def direction_with_smoothing_fuzz(self):
        return self.direction + random.random() * self.smoothing - self.smoothing / 2

    def perturb_direction(self):
        self.direction += random.random() * self.wiggle_max - (self.wiggle_max / 2)

def generate_new_catacomb_map(self):
    self.dungeon['rooms'] = []
    while len(self.dungeon['rooms']) < 10:
        self.dungeon['rooms'] = []
        create_dungeon(self)
        
    self.dungeon['up_stairs'] = self.dungeon['rooms'][3].center
    self.dungeon['player_starting_pos'] = self.dungeon['rooms'][0].center
    return self.dungeon['player_starting_pos']

def create_dungeon(self, walk_length=1600, has_stairs=True, walker=Walker()):
    encounter = 0
    while walk_length > 0:
        walk_length -= 1
        
        if self.on_map(walker.pos):
            self.place_cell(walker.pos, is_wall=False)
            
        walker.wander(self)

        if walk_length % 80 == 0:
            create_room(self, walker)

        if walk_length % 40 == 0:
            child_walk_length = random.randint(0, walk_length)
            walk_length -= child_walk_length
            if child_walk_length > walk_length:
                create_dungeon(self, child_walk_length, has_stairs, walker.create_child())
                has_stairs = False
            else:
                create_dungeon(self, child_walk_length, False, walker.create_child())

    if has_stairs:
        self.dungeon['down_stairs'] = walker.pos

def create_room(tmap, walker):
    width = max(1, min(tmap.width-walker.pos[0]-1, random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)))
    height = max(1, min(tmap.height-walker.pos[1]-1, random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)))

    room = area.Room(walker.pos[0], walker.pos[1], width, height)
    tmap.dungeon['rooms'].append(room)
    room.draw_into_map(len(tmap.dungeon['rooms'])-1, tmap)

class BSPTree:
    def __init__(self, width, height, x, y, min_split_s=8, children=[None, None]):
        self.width = width
        self.height = height
        self.x = x
        self.y = y
        self.min_split_s = min_split_s
        self.corridors = []
        self.children = copy.copy(children)

    def partition_vertical(self, x):
        self.children[0] = BSPTree(x, self.height, self.x, self.y)
        self.children[1] = BSPTree(self.width - x, self.height, self.x + x, self.y)
        
    def partition_horizontal(self, y):
        self.children[0] = BSPTree(self.width, y, self.x, self.y)
        self.children[1] = BSPTree(self.width, self.height - y, self.x, self.y + y)

    def random_partition(self):
        if self.width > self.min_split_s:
            if random.randint(0, 1) == 0:
                try:
                    self.partition_horizontal(random.randint(self.min_split_s, self.height - self.min_split_s))
                except: return False
            else:
                try:
                    self.partition_vertical(random.randint(self.min_split_s, self.width - self.min_split_s))
                except: return False
            return True
        else:
            return False

    def traverse(self, callback):
        callback(self)
        if self.children[0] != None and self.children[1] != None:
            self.children[0].traverse(callback)
            self.children[1].traverse(callback)

    def create_rooms(self, tmap):
        if self.children[0] != None and self.children[1] != None:
            self.children[0].create_rooms(tmap)
            self.children[1].create_rooms(tmap)
        else:
            w, h = 7, 7
            try:
                w, h = (random.randint(7, self.width-1),
                        random.randint(7, self.height-1))
            except: pass

            x, y = self.x, self.y
            try:
                x, y = (random.randint(self.x+1, self.x+self.width-w-1),
                        random.randint(self.y+1, self.y+self.height-h-1))
            except: pass
            
            r = area.Room(x,y,w,h)
            tmap.dungeon['rooms'].append(r)
            r.draw_into_map(0, tmap)
            
    def __str__(self):
        return "BSP(width=%d, height=%d, x=%d, y=%d)" % (self.width, self.height, self.x, self.y)
            
def generate_new_barrack_map(self):
    trees = []
    base = BSPTree(self.width, self.height, 0, 0)
    trees.append(base)

    did_split = True
    while did_split:
        did_split = False
        for t in trees:
            if t.children[0] == None and t.children[1] == None:
                if t.width > consts.MAX_ROOM_SIZE-2 or t.height > consts.MAX_ROOM_SIZE-2 or random.randint(0, 100) < 75:
                    if t.random_partition():
                        did_split = True
                        trees.append(t.children[0])
                        trees.append(t.children[1])

    base.create_rooms(self)
    
    for i, room in enumerate(self.dungeon['rooms']):
        room.add_corridor(self, self.dungeon['rooms'][i-1])

    self.dungeon['down_stairs'] = self.dungeon['rooms'][-1].center
    self.dungeon['player_starting_pos'] = self.dungeon['rooms'][-1].center
    self.dungeon['up_stairs'] = random.choice(self.dungeon['rooms']).center
    return self.dungeon['rooms'][-1].center
