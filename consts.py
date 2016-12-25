import utils, draw

FONT_SIZE        = 8
FLOOR_LEVEL      = 0.43
WATER_LEVEL      = 0.0000049
STONE_LEVEL      = 0.95
WIDTH, HEIGHT    = int(1280/FONT_SIZE)-30, int(480/FONT_SIZE)
FOV              = True
CUMULATE_FOV     = False
MESSAGE_NUMBER   = 31
FOREST_LEVELS    = 7
DUNGEON_LEVELS   = 10

MAP = {
    'OCTAVES': 2, # Controls the amount of detail in the noise.
    'DIMS': 2,    # n of dimensions
    'HURST': 0.9, # The hurst exponent describes the raggedness of the resultant
                  # noise, with a higher value leading to a smoother noise. It
                  # should be in the 0.0-1.0 range.
    'LA': 0.2     # A multiplier that determines how quickly the frequency
                  # increases for each successive octave.
}

GAME_MOVEMENT_KEYS = {
    'L': [1, 0],
    'H': [-1, 0],
    'K': [0, -1],
    'J': [0, 1],
    'Y': [-1, -1],
    'U': [1, -1],
    'N': [-1, 1],
    'B': [1, 1],
}
def pickup(GS, p):
    if (p.x, p.y) in GS['terrain_map'].spawned_items:
        item = GS['terrain_map'].spawned_items[p.x, p.y]
        GS['messages'].insert(0, 'You pick up a '+item.name)
        del GS['terrain_map'].spawned_items[p.x, p.y]
        p.add_inventory_item(item)

def auto_rest(GS, p):
    while p.health < p.max_health:
        p.rest()
        utils.monster_turn(GS)
        draw.draw_game_screen(GS)
        GS['turns'] += 1

def fire(GS, p):
    print('FIRED')
    targets = filter(
        lambda m:
        GS['terrain_map'].terrain_map.compute_path(p.x, p.y, m.x, m.y,
                                                   diagonal_cost=0) != [] and\
        dist(m, p) < p.ranged_weapon.range,
        GS['terrain_map'].proweling_monsters)
    if p.ranged_weapon:
        target = min(targets, key=lambda m: utils.dist(m, p))
        missle = list(filter(lambda m: m.missle_type == p.ranged_weapon.missle_type, p.missles))[0]
        target.health -= missle.hit
        p.missles.remove(missle)
        adj = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]
        for a in adj:
            x = target.x + a[0]
            y = target.y + a[1]
            if GS['terrain_map'].get_type(x, y) != 'STONE':
                GS['terrain_map'].spawned_items[x, y] = missle

def inventory(GS, p):
    print('INVENTORY')
    GS['side_screen'] = 'INVENTORY'

GAME_ACTION_KEYS = {
    '.': lambda GS, p: p.rest(),
    ',': pickup,
    ';': auto_rest,
    'F': fire,
    'I': inventory
}
GAME_KEYS = {
    'M': GAME_MOVEMENT_KEYS,
    'A': GAME_ACTION_KEYS
}

ABBREV = {
    'LL': 'level',
    'HT': 'health',
    'ST': 'strength',
    'AT': 'attack',
    'SP': 'speed'
}
