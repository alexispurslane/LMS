import tdl
import random, math
import monsters, colors, consts, utils, items, dungeons, forests, draw, area

# TODO: Add comments
# TODO: Refactor for less mutation
class TerrainMap:
    def __init__(self, w, h):
        self.forest_level = 0
        self.dungeon_level = 0
        self.rooms = []
        self.width = w
        self.height = h

        self.dungeon = {}
        self.reset_dungeon()

        self.dungeons = []

    # Restors the nth stored dungeon.
    def restore_dungeon(self, n):
        if n < len(self.dungeons):
            self.dungeon = self.dungeons[n]
            return True
        
        return False

    # Creates a new dungeon ready for creation.
    def reset_dungeon(self):
        self.dungeon = {
            'monsters': [],
            
            'water': {},
            'areas': [],
            'numbers': {},
            'noise': None,
            
            'down_stairs': (-20, -20),
            'up_stairs': (-20, -20),
            
            'decor': {},
            'items': {},
            'doors': {},
            'rooms': [],

            'player_starting_pos': (0, 0),

            'lighted': tdl.map.Map(self.width, self.height),
            'visited': tdl.map.Map(self.width, self.height)
        }

    # Checks if a water cell is adjacent to (x, y) co-ords.
    def adjacent_water(self, p):
        x, y = p
        return (max(x-1, 0), y) in self.water or\
            (max(x+1, 0), y) in self.water or\
            (x, max(y+1, 0)) in self.water or\
            (x, max(y-1, 0)) in self.water

    # FIXME: Refactor somehow.
    # This checks if there is a reasonable amount of floorspace around a point.
    # (For forest levels.)
    def all_around_floor(self, p):
        x, y = p
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

    # Retreives the type of the cell at (x, y).
    def get_type(self, p):
        x, y = utils.clamp_point(p, maxs=(self.width, self.height))
        if self.is_forests():
            l = self.dungeon['noise'].get_point(x, y)
            if l > consts.FLOOR_LEVEL and l < consts.STONE_LEVEL:
                return 'TREE'
            elif l >= consts.STONE_LEVEL:
                return 'STONE'
            elif l <= consts.FLOOR_LEVEL and l > consts.WATER_LEVEL:
                return 'FLOOR'
            elif l <= consts.WATER_LEVEL:
                return 'WATER'
        elif self.is_dungeons():
            if (x, y) in self.dungeon['doors']:
                return 'DOOR'
            elif self.dungeon['visited'].transparent[x, y]:
                return 'FLOOR'
            else:
                return 'STONE'

    # Checks if a point is on the map.
    def on_map(self, p):
        return p >= (0, 0) and p < (self.width, self.height)

    # Returns a monster at the given point.
    def monster_at(self, p):
        for m in self.dungeon['monsters']:
            if m.pos == p:
                return m
        return None

    def in_area(self, p):
        for a in self.dungeon['areas']:
            if a.inside(p):
                return a.area_type
        return 'Regular'

    # Checks if level is hard.
    def is_hell_level(self):
        return self.dungeon_level > math.floor(consts.DUNGEON_LEVELS/2)

    # Checks if the character can stand on a point.
    def is_walkable(self, p, player=(-1, -1)):
        return self.on_map(p) and not self.monster_at(p)\
            and p != player and self.dungeon['visited'].walkable[p]

    # Checks if the current level is in a forest.
    def is_forests(self):
        return self.forest_level < consts.FOREST_LEVELS

    # Checks if the current level is in a dungeon.
    def is_dungeons(self):
        return self.dungeon_level < consts.DUNGEON_LEVELS

    # Generates a new forest map (redirected to forests.py)
    def generate_new_forest_map(self):
        return forests.generate_new_forest_map(self)

    # Draws a horizontal corridor to the 'visited' map.
    def add_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)):
            x, y = utils.clamp_point((x, y), maxs=(self.width, self.height))
            self.dungeon['visited'].transparent[x, y] = True
            self.dungeon['visited'].walkable[x, y] = True
            self.dungeon['items'][x, y] = []
            
    # Draws a horizontal corridor to the 'visited' map.
    def add_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2)):
            x, y = utils.clamp_point((x, y), maxs=(self.width, self.height))
            self.dungeon['visited'].transparent[x, y] = True
            self.dungeon['visited'].walkable[x, y] = True
            self.dungeon['items'][x, y] = []
            
    # Generates a new dungeon map (ridirected to dungeons.py)
    # and saves it to the level list.
    def generate_new_dungeon_map(self):
        self.dungeon_level += 1
        return dungeons.generate_new_dungeon_map(self)

    # Generates the final level.
    # TODO: Not implemented
    def generate_final_level(self):
        return None

    def generate_areas(self):
        areas = []
        while len(areas) < 6:
            a = area.Area(random.randint(0, self.width-1),
                          random.randint(0, self.height-1),
                          random.randint(12, math.floor(self.width/4)),
                          random.randint(12, math.floor(self.height/4)))
            
            if a.pos2 < (self.width-1, self.height-1) and a.pos1 > (0, 0):
                areas.append(a)
                
        return areas
    
    # Generates the new map, forest or dungeon, appropriately by level number.
    # FIXME: Calls generate_final_level, which will return None.
    def generate_new_map(self):
        self.dungeons.append(self.dungeon)
        self.reset_dungeon()
        self.dungeon['areas'] = self.generate_areas()
        
        if self.is_forests():
            if consts.DEBUG: print('LEVEL: FOREST')
            return self.generate_new_forest_map()
        elif self.is_dungeons():
            if consts.DEBUG: print('LEVEL: DUNGEON')
            return self.generate_new_dungeon_map()
        else:
            if consts.DEBUG: print('LEVEL: FINAL')
            return self.generate_final_level()
        
    # Adds cell to terrain map.
    def place_cell(self, p, is_wall=False):
        pos = utils.clamp_point(p, maxs=(self.width, self.height))

        self.dungeon['visited'].transparent[pos] = not is_wall
        self.dungeon['visited'].walkable[pos] = not is_wall

        self.dungeon['lighted'].transparent[pos] = not is_wall
        self.dungeon['lighted'].walkable[pos] = not is_wall

    # Calculates the player's visited map and current FoV, then draws the visited
    # map while brightening the player's FoV.
    def draw_map(self, GS, console, player):
        if consts.FOV:
            rad = player.light_source_radius

            x, y = player.pos
            fov = self.dungeon['visited'].compute_fov(
                x, y,
                cumulative=consts.CUMULATE_FOV,
                radius=rad,
                sphere=True)
            
            fov2 = self.dungeon['lighted'].compute_fov(
                x, y,
                radius=rad,
                sphere=True)
            fov2 = [(f[0], f[1]) for f in fov2]
        else:
            fov2 = fov = self.dungeon['visited']

        # Draw up-stairs and down-stairs no matter what.
        if len(self.dungeon['monsters']) == 0:
            draw.draw_dungeon_tile(self, GS, console, self.dungeon['down_stairs'], (0,0,0))
            
        draw.draw_dungeon_tile(self, GS, console, self.dungeon['up_stairs'], (0,0,0))

        # Draw map
        for x, y in fov:
            tint = (-80, -80, -80)
            if (x, y) in fov2:
                tint = (0, 0, 0)
                
            if self.is_forests():
                draw.draw_forest_tile(self, console, (x, y), tint)
            elif self.is_dungeons():
                draw.draw_dungeon_tile(self, GS, console, (x, y), tint)
