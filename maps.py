import tdl
import random, math
import monsters, colors, consts, utils, items, dungeons, forests, draw

class TerrainMap:
    def __init__(self, w, h):
        self.terrain_map = tdl.map.Map(w, h)
        self.alt_terrain_map = tdl.map.Map(w, h)
        self.forest_level = 0
        self.dungeon_level = 0
        self.rooms = []
        self.width = w
        self.height = h
        self.proweling_monsters = []
        self.monsterN = 0
        self.water = {}
        self.spawned_items = {}
        self.noise = None
        self.downstairs = None
        self.doors = {}
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
        if self.in_forests():
            l = self.noise.get_point(x, y)
            if l > consts.FLOOR_LEVEL and l < consts.STONE_LEVEL:
                return 'TREE'
            elif l >= consts.STONE_LEVEL:
                return 'STONE'
            elif l <= consts.FLOOR_LEVEL and l > consts.WATER_LEVEL:
                return 'FLOOR'
            elif l <= consts.WATER_LEVEL:
                return 'WATER'
        elif self.in_dungeons():
            if self.terrain_map.transparent[x, y]:
                return 'FLOOR'
            elif (x, y) in self.doors:
                return 'DOOR'
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

    def in_forests(self):
        return self.forest_level < consts.FOREST_LEVELS

    def in_dungeons(self):
        return self.dungeon_level < consts.DUNGEON_LEVELS

    def generate_new_forest_map(self):
        return forests.generate_new_forest_map(self)

    def add_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)):
            self.terrain_map.transparent[x, y] = True
            self.terrain_map.walkable[x, y] = True
            
    def add_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)):
            self.terrain_map.transparent[x, y] = True
            self.terrain_map.walkable[x, y] = True
            
    def generate_new_dungeon_map(self):
        return dungeons.generate_new_dungeon_map(self)
    
    def generate_final_level(self):
        return None

    def generate_new_map(self):
        self.terrain_map = tdl.map.Map(self.width, self.height)
        self.alt_terrain_map = tdl.map.Map(self.width, self.height)
        
        if self.in_forests():
            if consts.DEBUG: print('LEVEL: FOREST')
            return self.generate_new_forest_map()
        elif self.in_dungeons():
            if consts.DEBUG: print('LEVEL: DUNGEON')
            return self.generate_new_dungeon_map()
        else:
            if consts.DEBUG: print('LEVEL: FINAL')
            return self.generate_final_level()

    def draw_map(self, console, player):
        if consts.FOV:
            rad = math.ceil(player.light_source_radius/2)
            for room in self.rooms:
                if room.intersects(utils.Room(player.x, player.y, 1, 1)):
                    rad = player.light_source_radius
                    
            fov = self.terrain_map.compute_fov(player.x, player.y, cumulative=consts.CUMULATE_FOV, radius=rad, sphere=True)
            fov2 = self.alt_terrain_map.compute_fov(player.x, player.y, radius=rad, sphere=True)
        else:
            fov = self.terrain_map

        for x, y in fov:
            tint = (-100, -80, -80)
                
            if self.in_forests():
                draw.draw_forest_tile(self, console, (x, y), tint)
            elif self.in_dungeons():
                draw.draw_dungeon_tile(self, console, (x, y), tint)

        for x, y in fov2:
            if player.light_source_radius == 10:
                tint = (0, 0, -80)
            else:
                tint = (0, 0, 0)

            if self.in_forests():
                draw.draw_forest_tile(self, console, (x, y), tint)
            elif self.in_dungeons():
                draw.draw_dungeon_tile(self, console, (x, y), tint)
