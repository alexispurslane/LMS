import tdl
import random, math
import monsters, colors, consts, utils, items, dungeons, forests

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

    spawn_monsters(self, player_x, player_y)
    self.forest_level += 1
    return (player_x, player_y)

def spawn_monsters(self, player_x, player_y):
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
