import tdl
import random, math
import monsters, colors, consts, utils, items

class TerrainMap:
    def __init__(self, w, h):
        self.terrain_map = tdl.map.Map(w, h)
        self.forest_level = 0
        self.width = w
        self.height = h
        self.proweling_monsters = []
        self.monsterN = 0
        self.water = {}
        self.spawned_items = {}
        
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
        
        playerX, playerY = None, None
        noise = tdl.noise.Noise(mode='FBM', octaves=2, dimensions=2, hurst=0.6, lacunarity=0.1)
        def get_type(x,y):
            l = noise.get_point(x, y)
            if l > consts.FLOOR_LEVEL and l < consts.LARGE_TREE_LEVEL:
                return 'TREE'
            elif l >= consts.LARGE_TREE_LEVEL:
                return 'LARGE_TREE'
            elif l <= consts.FLOOR_LEVEL and l > consts.WATER_LEVEL:
                return 'FLOOR'
            elif l <= consts.WATER_LEVEL:
                return 'WATER'

        def adjacent_water(x, y):
            return (max(x-1, 0), y) in self.water or\
                   (max(x+1, 0), y) in self.water or\
                   (x, max(y+1, 0)) in self.water or\
                   (x, max(y-1, 0)) in self.water

        choices = monsters.select_by_difficulty(self.forest_level)
        ms = [random.choice(choices)() for i in range(random.randint(7, 14))]
        
        if self.forest_level == consts.FOREST_LEVELS:
            ms.append(monsters.FlyingDragon())
            
        for x, y in self.terrain_map:
            self.terrain_map.transparent[x, y] = get_type(x,y) == 'FLOOR' or\
                                                 get_type(x, y) == 'WATER'
            self.terrain_map.walkable[x, y] = get_type(x, y) == 'WATER' or\
                                              get_type(x,y) == 'FLOOR' or\
                                              get_type(x,y) == 'TREE'
            if random.randint(1, 100) < 99 and\
               (len(self.water) < 4 or adjacent_water(x, y)) and\
               get_type(x, y) == 'FLOOR':
                self.water[x,y] = True
            if self.terrain_map.transparent[x, y] and not playerX and not playerY:
                playerX = x
                playerY = y
            elif get_type(x, y) == 'WATER':
                self.water[x, y] = True
            elif self.terrain_map.transparent[x, y]:
                r = random.randint(1, 100)
                if r <= 50 and self.monsterN < len(ms) and not get_type(x, y) == 'WATER':
                    monster = ms[self.monsterN]
                    monster.x = x
                    monster.y = y
                    if type(monster).__name__ == 'Witch':
                        partner = monsters.Wizard()
                        partner.x = x+1
                        partner.y = y
                        self.proweling_monsters.append(partner)
                    self.monsterN += 1
                    self.proweling_monsters.append(monster)
            else:
                if get_type(x,y) == 'FLOOR':
                    n = random.randint(1, 100)
                    for item in sorted(items.ITEMS, key=lambda i: i.weight):
                        if n < item.probability:
                            self.spawned_items[x, y] = item

        self.forest_level += 1
        return (playerX, playerY)

    def generate_new_dungeon_map(self):
        return None
    
    def generate_final_level(self):
        return None

    def generate_new_map(self):
        if self.more_forests():
            return self.generate_new_forest_map()
        elif self.more_dungeons():
            return self.generate_new_dungeon_map()
        else:
            return self.generate_final_level()

    def draw_map(self, console, player):
        if consts.FOV:
            fov = self.terrain_map.compute_fov(player.x, player.y, cumulative=True)
        else:
            fov = self.terrain_map
        for x, y in fov:
            if not self.on_map(x+1,y):
                console.drawChar(x, y, '>', bg=colors.brown, fg=colors.grey)
            elif (x, y) in self.water and self.water[x, y]:
                console.drawChar(x, y, '~', bg=colors.blue)
            elif (x, y) in self.spawned_items:
                console.drawChar(x, y, self.spawned_items[x, y].char, bg=colors.brown)
            elif self.terrain_map.transparent[x, y]:
                console.drawChar(x, y, '.', bg=colors.brown)
            elif not self.terrain_map.walkable[x, y]:
                console.drawChar(x, y, 'T', fg=colors.dark_green, bg=colors.brown)
            elif not self.terrain_map.transparent[x, y]:
                console.drawChar(x, y, 't', fg=colors.green, bg=colors.brown)

