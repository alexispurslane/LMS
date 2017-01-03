import tdl
import random, math
import monsters, colors, consts, utils, items, dungeons, forests

def generate_new_dungeon_map(self):
    for pos in self.terrain_map:
        self.dungeon_decor[pos] = None
        rooms = []
        self.proweling_monsters = []

        w = 20
        h = 20
        x = random.randint(1, self.width - w - 1)
        y = random.randint(1, self.height - h - 1)
        room = utils.Room(x, y, w, h)
        rooms.append(room)
        room.draw_into_map(self)
        
        for r in range(0, consts.MAX_ROOMS):
            w = random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)
            h = random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            room = utils.Room(x, y, w, h)
            
            w2 = random.randint(consts.MIN_ROOM_WIDTH, consts.MAX_ROOM_SIZE)
            h2 = random.randint(consts.MIN_ROOM_HEIGHT, consts.MAX_ROOM_SIZE)
            x2, y2 = random.choice(room.edge_points())
            room2 = utils.Room(x2, y2, w2, h2)

            failed = False
            for r in rooms:
                if room.intersects(r):
                    failed = True

            if not failed:
                for i in range(0, consts.ITEMS_PER_ROOM):
                    if random.randint(1, 2) == 1:
                        n = random.randint(1, 100)
                        for item in items.ITEMS:
                            if n < item.probability:
                                if random.randint(1, 2) == 1:
                                    pos = random.randint(i, room.w-1)
                                    self.spawned_items[room.center.x+pos, room.center.y] = item
                                else:
                                    pos = random.randint(i, room.h-1)
                                    self.spawned_items[room.center.x, room.center.y+pos] = item
                                    
                if len(rooms) > 0:
                    r1 = room
                    r2 = rooms[-1]
                    if random.randint(1, 2) == 1:
                        self.add_h_corridor(r2.center.x, r1.center.x, r1.center.y)
                        self.add_v_corridor(r1.center.y, r2.center.y, r1.center.x)
                    else:
                        self.add_v_corridor(r1.center.y, r2.center.y, r1.center.x)
                        self.add_h_corridor(r2.center.x, r1.center.x, r1.center.y)
                        
                rooms.append(room)
                
                for i in range(0, max(self.dungeon_level*2, 4)):
                    ms = monsters.select_by_difficulty(self.dungeon_level)
                    m = random.choice(ms)()
                    m.x = room.center.x
                    m.y = room.center.y
                    if random.randint(1, 2)==1:
                        m.x += i
                    else:
                        m.y += i
                        self.proweling_monsters.append(m)
                        
                room.draw_into_map(self)

                if room2.x2 < self.width-1 and\
                   room2.y2 < self.height-1 and\
                   room2.x1 > 0 and room2.y1 > 0:
                    room2.draw_into_map(self)
                    rooms.append(room2)

        # place doors

        for x, y in self.terrain_map:
            if x > 0 and x < self.width - 1 and y > 0 and y < self.height - 1:
                opening = (self.get_type(x+1, y+1) == 'FLOOR' or\
                           self.get_type(x-1, y+1) == 'FLOOR')
                if self.get_type(x-1, y) == 'STONE' and\
                   self.get_type(x+1, y) == 'STONE' and\
                   self.get_type(x, y)   == 'FLOOR' and\
                   opening and self.get_type(x, y+1)   == 'FLOOR':
                    self.doors[x, y] = True
                    self.terrain_map.transparent[x, y] = False
                    self.terrain_map.walkable[x, y] = False

        self.downstairs = (rooms[-1].center.x, rooms[-1].center.y)
        self.rooms = rooms
        return (rooms[0].center.x, rooms[0].center.y)
