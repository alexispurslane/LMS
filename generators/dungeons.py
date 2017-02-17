import tdl, random, math, copy
from functools import *
from operator import *
import monsters, colors, consts, utils, items, dungeons, forests, area

def generate_new_dungeon_map(self):
    maps = [
        'catacomb',
        #'barrack'.
        #'standard'
    ]
    rtype = random.choice(maps)
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
    self.dungeon['player_starting_pos'] = self.dungeon['rooms'][0].pos1
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
