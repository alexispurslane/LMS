import tdl
import random, math
import monsters, colors, consts, utils, items, dungeons, forests

def connect_rooms(self, r1, r2):
    if random.randint(1, 2) == 1:
        self.add_h_corridor(r2.center[0]+1, r1.center[0], r1.center[1])
        self.add_v_corridor(r1.center[1], r2.center[1]+1, r1.center[0])
    else:
        self.add_v_corridor(r1.center[1], r2.center[1]+1, r1.center[0])
        self.add_h_corridor(r2.center[0]+1, r1.center[0], r1.center[1])
        
    r1.connected = True
    r2.connected = True

def generate_new_dungeon_map(self):
    self.dungeon['decor'][0, 0] = None
    for pos in self.dungeon['visited']:
        self.dungeon['decor'][pos] = None
        
    self.dungeon['rooms'] = []
    proweling_monsters = []

    w = 8
    h = 8
    x = random.randint(1, self.width - w - 1)
    y = random.randint(1, self.height - h - 1)
    room = utils.Room(x, y, w, h)
    room.connected = True
    self.dungeon['rooms'].append(room)
    room.draw_into_map(0, self)

    for number in range(0, consts.MAX_ROOMS):
        w = random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)
        h = random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)
        x = random.randint(1, self.width - w - 1)
        y = random.randint(1, self.height - h - 1)
        room = utils.Room(x, y, w, h)

        w2 = random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)
        h2 = random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)
        x2, y2 = random.choice(room.edge_points())
        adjoin = utils.Room(x2, y2, w2, h2)

        failed = False
        for r in self.dungeon['rooms']:
            if room.intersects(r):
                failed = True

        if not failed:
            #################### ADD PASSAGES ####################
            connect_rooms(self, room, self.dungeon['rooms'][-1])

            #################### ADD ROOM TO MAP ####################
            room.draw_into_map(number, self)
            self.dungeon['rooms'].append(room)

            #################### ADD ADJOINING ROOM ####################
            if self.on_map(adjoin.pos1) and self.on_map(adjoin.pos2):
                adjoin.draw_into_map(number, self) # Add adjoining room to map
                self.dungeon['rooms'].append(adjoin)
                adjoin.connected = True

            #################### ADD MONSTERS ####################
            cal_size = math.floor(room.w*room.h/100)
            x_i, y_i = (0, 0)
            for i in range(0, max(self.dungeon_level*2+1+cal_size, 4)):
                ms = monsters.select_by_difficulty(self.dungeon_level)
                m = random.choice(ms)()
                m.pos = room.center

                offset = (0, 0)
                if random.randint(1, 2) == 1 or y_i > math.floor(room.h/2):
                    offset = (x_i, 0)
                    x_i += 1
                else:
                    offset = (0, y_i)
                    y_i += 1
                    
                m.pos = utils.tuple_add(m.pos, offset)

                if self.is_walkable(m.pos):
                    proweling_monsters.append(m)
                    
            self.dungeon['monsters'] = proweling_monsters

    last_was_door = False
    for x, y in self.dungeon['visited']:
        #################### BLOCK EDGES ####################
        y_extreme = y == 1 or y == self.height-1
        x_extreme = x == self.width-1 or x == 1
        wall = x_extreme or y_extreme
        if self.get_type((x, y)) == 'FLOOR':
            self.place_cell((x, y), is_wall=wall)
        
        #################### ADD DOORS ####################
        if self.on_map((x, y)):
            opening = (self.get_type((x+1, y+1)) == 'FLOOR' or\
                       self.get_type((x-1, y+1)) == 'FLOOR')
            if self.get_type((x-1, y))  == 'STONE' and\
                self.get_type((x+1, y)) == 'STONE' and\
                self.get_type((x, y))   == 'FLOOR' and\
                opening and\
                self.get_type((x, y+1)) == 'FLOOR' and\
                last_was_door < 3:
                
                self.dungeon['doors'][x, y] = True
                
                self.dungeon['visited'].transparent[x, y] = False
                self.dungeon['visited'].walkable[x, y] = False

                last_was_door += 1
            elif last_was_door >= 3:
                last_was_door = 0

    
    #################### ERROR CHECKING ####################
    for i, room in enumerate(self.dungeon['rooms']):
        if not room.connected:
            raise Exception('All locations should be accessable! (room #%d of %d is not)' %
                            (i, len(self.dungeon['rooms'])))
    
    #################### ADD CONSTANT ITEMS ####################
    self.dungeon['down_stairs'] = self.dungeon['rooms'][-1].center
    self.dungeon['up_stairs'] = self.dungeon['rooms'][0].center
    self.dungeon['player_starting_pos'] = self.dungeon['rooms'][1].center

    return self.dungeon['player_starting_pos']
