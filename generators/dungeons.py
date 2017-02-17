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
    def __init__(self, pos=(8, 8), direction=0):
        self.pos, self.direction = pos, direction
        self.smoothing = 0.4
        self.wiggle_max = 0.8

    def wander(self):
        self.perturb_direction()
        return self.walk()

    def create_child(self):
        return Walker(self.pos, self.direction + 2*random.randint(0, 2) - 1)

    def walk(self, d=None):
        if not d: d = self.direction_with_smoothing_fuzz()
        d = round(d) % 4
        self.pos = utils.tuple_add(self.pos, ([1, 0, -1, 0][d],
                                              [0, 1, 0, -1][d]))
        return self

    def direction_with_smoothing_fuzz(self):
        return self.direction + random.random() * self.smoothing - self.smoothing / 2

    def perturb_direction(self):
        self.direction += random.random() * self.wiggle_max - (self.wiggle_max / 2)

def generate_new_catacomb_map(self):
    while len(self.dungeon['rooms']) < 7:
        self.dungeon['rooms'] = []
        create_dungeon(self)
    self.dungeon['up_stairs'] = self.dungeon['rooms'][3].center
    return self.dungeon['rooms'][3].center

def create_dungeon(self, walk_length=1200, has_stairs=True, walker=Walker()):
    while walk_length > 0:
        walk_length -= 1
        
        self.place_cell(walker.pos, is_wall=False)
        walker.wander()

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
    width = random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)
    height = random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)

    room = area.Room(walker.pos[0], walker.pos[1], width, height)
    room.draw_into_map(0, tmap)
    tmap.dungeon['rooms'].append(room)
