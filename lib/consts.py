import utils, draw, itertools, math, tdl

################### GAME SETTINGS ###################
FONT_SIZE        = 12
GAME_TITLE       = 'Last Man Standing'
FLOOR_LEVEL      = 0.43
WATER_LEVEL      = 0.0000049
STONE_LEVEL      = 0.95
WIDTH, HEIGHT    = int(1280/FONT_SIZE), int(800/FONT_SIZE)
FOV              = True
CUMULATE_FOV     = True
MESSAGE_NUMBER   = HEIGHT-12
FOREST_LEVELS    = 0
MAX_ROOMS        = 70
ITEMS_PER_ROOM   = 2
DUNGEON_LEVELS   = 20
DEBUG            = True
DIFFICULTY       = 15

MIN_ROOM_WIDTH = 8
MIN_ROOM_HEIGHT = 4
MAX_ROOM_SIZE = math.floor(WIDTH/8.83)

MAP = {
    'OCTAVES': 2, # Controls the amount of detail in the noise.
    
    'DIMS': 2,    # n of dimensions
    
    'HURST': 0.9, # The hurst exponent describes the raggedness of the resultant
                  # noise, with a higher value leading to a smoother noise. It
                  # should be in the 0.0-1.0 range.
    
    'LA': 0.2     # A multiplier that determines how quickly the frequency
                  # increases for each successive octave.
}

################### PLAYER MOVEMENT ###################
GAME_MOVEMENT_KEYS = {
    'l': [1, 0],
    'h': [-1, 0],
    'k': [0, -1],
    'j': [0, 1],
    'y': [-1, -1],
    'u': [1, -1],
    'b': [-1, 1],
    'n': [1, 1],

    # For losers
    'right': [1, 0],
    'left': [-1, 0],
    'up': [0, -1],
    'down': [0, 1],
}

################### PLAYER ACTIONS ###################

# Have the player pick up an item
def pickup(GS, p):
    dun_items = GS['terrain_map'].dungeon['items']
    if p.pos in dun_items and len(dun_items[p.pos]) > 0:
        item = dun_items[p.pos].pop()
        GS['messages'].insert(0, 'You pick up a '+item.name)
        
        p.add_inventory_item(item)

# Have the player rest until no more rest is needed.
# Hunger builds more slowly and monsters each get a turn.
def auto_rest(GS, p):
    while p.health < p.max_health:
        p.rest()
        if self.poisoned > 0 and GS['turns'] % 4:
            self.poisoned -= 2
            self.health -= 1
        if GS['turns'] % 6 == 0:
            p.hunger += 1
        utils.monster_turn(GS)
        
        GS['turns'] += 1

# Fire the first available missle using the player's current ranged weapon at
# the closest monster that A* can find a path to and is in the player's LoS.
def fire(GS, p):
    if p.ranged_weapon != None:
        click = tdl.event.wait(timeout=1000, flush=True)
        if click and click.type == 'MOUSEDOWN' and click.button == 'LEFT':
            target = GS['terrain_map'].monster_at(click.cell)
            if target:
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
                    pos = utils.tuple_add(target.pos, adj)
                    if GS['terrain_map'].get_type(x, y) != 'STONE':
                        GS['terrain_map'].dungeon['items'][pos] = missle
        else:
            GS['messages'].insert(0, 'Nevermind.')

# Switches between inventory and HUD screens.
def inventory(GS, p):
    if GS['side_screen'] == 'INVENTORY':
        GS['side_screen'] == 'HUD'
    else:
        GS['side_screen'] = 'INVENTORY'

# Resets all screens back to the default playing setup. 
def reset(GS, p):
    if DEBUG: print('Screens reset')
    GS['side_screen'] = 'HUD'
    
    if GS['screen'] != 'DEATH' or GS['screen'] != 'CHARSEL' or GS['screen'] != 'INTRO':
        GS['screen'] = 'GAME'

# Quits the game and prints ending player state.
def quit(GS, p):
    print('\nGame Stats')
    print('----------')
    print('  Turns: ' + str(GS['turns']))
    print('  Score: ' + str(p.score(GS)))
    print('  Kills: ' + str(p.killed_monsters))
    print('  Exp:   ' + str(p.exp))
    print('  Inventory:\n' +\
          ',\n'.join(list(map(lambda x:
                              '    '+x[0].name+' x'+str(len(list(x[1]))),
                              itertools.groupby(p.inventory)))))
    exit(0)

def auto_move(d):
    event = tdl.event.KeyDown(d, d, False, False, False, False, False)
    def do(GS, p):
        changed = True
        while changed:
            pp = p.pos
            p.move(event, GS)
            changed = pp != p.pos
    return do
    
GAME_ACTION_KEYS = {
    '.': lambda GS, p: p.rest(),
    ',': pickup,
    ';': auto_rest,
    'f': fire,
    'i': inventory,
    'escape': inventory,
    'q': quit,

    # Auto-movement
    'L': auto_move('l'),
    'H': auto_move('h'),
    'K': auto_move('k'),
    'J': auto_move('j'),
    'Y': auto_move('y'),
    'U': auto_move('u'),
    'B': auto_move('b'),
    'N': auto_move('n'),
}

 
################### ALL GAME KEYS ###################
GAME_KEYS = {
    'M': GAME_MOVEMENT_KEYS,
    'A': GAME_ACTION_KEYS
}


################### HELPER CONSTS ###################
# Abbreviations of the player's stats for use on the HUD bar.
ABBREV = {
    'LL': 'level',
    'HT': 'health',
    'ST': 'strength',
   'AT': 'attack',
    'SP': 'speed',
    'DF': 'defence'
}
