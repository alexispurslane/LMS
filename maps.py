import tdl
import random, math
import monsters, colors, consts, utils, items

class TerrainMap:
    def __init__(self, w, h):
        self.terrain_map = tdl.map.Map(w, h)
        self.forest_level = 0
        self.dungeon_level = 0
        self.width = w
        self.height = h
        self.proweling_monsters = []
        self.monsterN = 0
        self.water = {}
        self.spawned_items = {}
        self.noise = None
        self.downstairs = None
        self.dungeon_decor = {}
        
    def adjacent_water(self, x, y):
        return (max(x-1, 0), y) in self.water or\
            (max(x+1, 0), y) in self.water or\
            (x, max(y+1, 0)) in self.water or\
            (x, max(y-1, 0)) in self.water

    def all_around_floor(self, x, y):
        return self.get_type(max(x-1, 0), y) == 'FLOOR' and\
            self.get_type(max(x-2, 0), y) == 'FLOOR' and\
            self.get_type(max(x-3, 0), y) == 'FLOOR' and\
            self.get_type(max(x+1, 0), y) == 'FLOOR' and\
            self.get_type(max(x+2, 0), y) == 'FLOOR' and\
            self.get_type(max(x+3, 0), y) == 'FLOOR' and\
            self.get_type(x, max(y+1, 0)) == 'FLOOR' and\
            self.get_type(x, max(y+2, 0)) == 'FLOOR' and\
            self.get_type(x, max(y+3, 0)) == 'FLOOR' and\
            self.get_type(x, max(y-1, 0)) == 'FLOOR' and\
            self.get_type(x, max(y-2, 0)) == 'FLOOR' and\
            self.get_type(x, max(y-3, 0)) == 'FLOOR'
    
    def get_type(self, x, y):
        if self.more_forests():
            l = self.noise.get_point(x, y)
            if l > consts.FLOOR_LEVEL and l < consts.STONE_LEVEL:
                return 'TREE'
            elif l >= consts.STONE_LEVEL:
                return 'STONE'
            elif l <= consts.FLOOR_LEVEL and l > consts.WATER_LEVEL:
                return 'FLOOR'
            elif l <= consts.WATER_LEVEL:
                return 'WATER'
        elif self.more_dungeons():
            if self.terrain_map.transparent[x, y]:
                return 'FLOOR'
            else:
                return 'STONE'
        
    def on_map(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def monster_at(self, x, y):
        for m in self.proweling_monsters:
            if m.x == x and m.y == y:
                return m
        return None
    
    def is_walkable(self, x, y, player=utils.Point(-1, -1)):
        return self.on_map(x,y) and not self.monster_at(x, y)\
            and not x == player.x and not y == player.y\
            and self.terrain_map.walkable[x, y]

    def more_forests(self):
        return self.forest_level < consts.FOREST_LEVELS

    def more_dungeons(self):
        return self.dungeon_level < consts.DUNGEON_LEVELS
    
    def generate_new_forest_map(self):
        self.proweling_monsters = []
        self.monsterN = 0
        self.water = {}
        self.terrain_map = tdl.map.Map(self.width, self.height)
        self.spawned_items = {}
        
        player_x, player_y = None, None
        self.noise = tdl.noise.Noise(
            mode='FBM',
            octaves=consts.MAP['OCTAVES'],
            dimensions=consts.MAP['DIMS'],
            hurst=consts.MAP['HURST'],
            lacunarity=consts.MAP['LA']) 

        for x, y in self.terrain_map:
            # FOV setup
            self.terrain_map.transparent[x, y] = self.get_type(x,y) == 'FLOOR' or\
                                                 self.get_type(x, y) == 'WATER'
            self.terrain_map.walkable[x, y] = self.get_type(x, y) == 'WATER' or\
                                              self.get_type(x,y) == 'FLOOR' or\
                                              self.get_type(x,y) == 'TREE'

            # Generate items
            if self.get_type(x,y) == 'FLOOR' and\
               self.all_around_floor(x, y):
                n = random.randint(1, 100)
                for item in items.ITEMS:
                    if n < item.probability:
                        self.spawned_items[x, y] = item

            # Generate water
            if random.randint(1, 100) < 99 and\
               (len(self.water) < 10 or self.adjacent_water(x, y)) and\
               self.get_type(x, y) == 'FLOOR':
                self.water[x,y] = True

            # Insert player
            if self.terrain_map.transparent[x, y] and not player_x and not player_y:
                player_x = x
                player_y = y

        self.spawn_monsters('FOREST', player_x, player_y)
        self.forest_level += 1
        return (player_x, player_y)

    def spawn_monsters(self, location, player_x, player_y):
        if location == 'FOREST':
            self.spawn_forest_monsters(player_x, player_y)
            
    def spawn_forest_monsters(self, player_x, player_y):
        # Spawn monsters
        choices = monsters.select_by_difficulty(self.forest_level)
        ms = [random.choice(choices)() for i in range(random.randint(40, 80))]
        if self.forest_level == consts.FOREST_LEVELS:
            ms.append(monsters.FlyingDragon())

        while len(ms) > 0:
            m = ms[-1]
            x = random.randint(0, self.width-2)
            y = random.randint(0, self.height-1)
            if self.terrain_map.transparent[x, y] and not (player_x == x and player_y == y)\
               and not self.get_type(x, y) == 'WATER' and not self.adjacent_water(x, y):
                m.x, m.y = x, y
                if type(m).__name__ == 'Witch':
                    partner = monsters.Wizard()
                    partner.x = x+1
                    partner.y = y
                    self.proweling_monsters.append(partner)
                ms.remove(m)
                self.proweling_monsters.append(m)

    def draw_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)):
            self.terrain_map.transparent[x, y] = True
            self.terrain_map.walkable[x, y] = True

    def draw_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)):
            self.terrain_map.transparent[x, y] = True
            self.terrain_map.walkable[x, y] = True
    
    def generate_new_dungeon_map(self):
        self.noise = tdl.noise.Noise(
            mode='FBM',
            octaves=consts.MAP['OCTAVES'],
            dimensions=consts.MAP['DIMS'],
            hurst=consts.MAP['HURST'],
            lacunarity=consts.MAP['LA'])  # For water this time
        rooms = []
        self.proweling_monsters = []

        for r in range(0, consts.MAX_ROOMS):
            w = random.randint(consts.MIN_ROOM_SIZE, consts.MAX_ROOM_SIZE)
            h = random.randint(consts.MIN_ROOM_SIZE, consts.MAX_ROOM_SIZE)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            room = utils.Room(x, y, w, h)

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
                    r2 = rooms[len(rooms) - 1]
                    if random.randint(1, 2) == 1:
                        self.draw_h_corridor(r2.center.x, r1.center.x, r1.center.y)
                        self.draw_v_corridor(r1.center.y, r2.center.y, r1.center.x)
                    else:
                        self.draw_v_corridor(r1.center.y, r2.center.y, r1.center.x)
                        self.draw_h_corridor(r2.center.x, r1.center.x, r1.center.y)
                    
                rooms.append(room)
                
                for i in range(0, max(self.dungeon_level*2, 1)):
                    ms = monsters.select_by_difficulty(self.dungeon_level, in_forest=True)
                    m = random.choice(ms)()
                    m.x = room.center.x
                    m.y = room.center.y
                    if random.randint(1, 2)==1:
                        m.x += 1
                    else:
                        m.y += 1
                    self.proweling_monsters.append(m)
                    
                room.draw_into_map(self)

        self.downstairs = (rooms[-1].center.x, rooms[-1].center.y)
        return (rooms[0].center.x, rooms[0].center.y)
    
    def generate_final_level(self):
        return None

    def generate_new_map(self):
        self.terrain_map = tdl.map.Map(self.width, self.height)
        if self.more_forests():
            return self.generate_new_forest_map()
        elif self.more_dungeons():
            return self.generate_new_dungeon_map()
        else:
            return self.generate_final_level()

    def draw_map(self, console, player):
        if consts.FOV:
            fov = self.terrain_map.compute_fov(player.x, player.y, cumulative=consts.CUMULATE_FOV, radius=20)
        else:
            fov = self.terrain_map

        for x, y in fov:
            if self.more_forests():
                self.draw_forest_tile(console, (x, y), (0, 0, 0))
            elif self.more_dungeons():
                self.draw_dungeon_tile(console, (x, y), (0, 0, 0))

    def draw_dungeon_tile(self, console, pos, tint):
        (x, y) = pos
        if pos == self.downstairs:
            console.drawChar(x, y, '>', fg=colors.grey)
        elif (x, y) in self.water and self.water[x, y]:
            l = self.noise.get_point(x, y)
            color = colors.blue
            if l > 0.17:
                color = colors.light_blue
            elif l > 0.04:
                color = colors.medium_blue
            console.drawChar(x, y, '~', bg=color)
        elif (x, y) in self.spawned_items:
            console.drawChar(x, y, self.spawned_items[x, y].char,
                             fg=colors.tint(self.spawned_items[x, y].fg, tint))
        elif self.get_type(x, y) == 'FLOOR':
            console.drawChar(x, y, '.')
        elif self.get_type(x, y) == 'STONE':
            console.drawChar(x, y, '#', fg=colors.dark_grey, bg=colors.lighten(colors.grey))
        elif pos in self.dungeon_decor:
            if self.dungeon_decor[pos] == 'FM':
                console.drawChar(x, y, '"', fg=(21, 244, 238), bg=colors.black)
            elif self.dungeon_decor[pos] == 'RB':
                console.drawChar(x, y, '`', fg=colors.dark_grey, bg=colors.black)
    
    def draw_forest_tile(self, console, pos, tint):
        (x, y) = pos
        if not self.on_map(x+1,y):
            console.drawChar(x, y, '>', fg=colors.grey)
        elif (x, y) in self.water and self.water[x, y]:
            l = self.noise.get_point(x, y)
            color = colors.blue
            if l > 0.17:
                color = colors.light_blue
            elif l > 0.04:
                color = colors.medium_blue
            console.drawChar(x, y, '~', bg=color)
        elif (x, y) in self.spawned_items:
            console.drawChar(x, y, self.spawned_items[x, y].char,
                             fg=colors.tint(self.spawned_items[x, y].fg, tint))
        elif self.get_type(x, y) == 'FLOOR':
            console.drawChar(x, y, '.')
        elif self.get_type(x, y) == 'STONE':
            console.drawChar(x, y, '#', fg=colors.dark_grey, bg=colors.grey)
        elif self.get_type(x, y) == 'TREE':
            console.drawChar(x, y, 'T', fg=colors.tint(colors.green, tint))
