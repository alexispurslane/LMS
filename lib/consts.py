import utils, draw, itertools, math, tdl, random, colors, animation, pickle, time

################### GAME SETTINGS ###################
FONT_SIZE        = 12
GAME_TITLE       = 'Last Man Standing'
FLOOR_LEVEL      = 0.43
WATER_LEVEL      = 0.0000049
STONE_LEVEL      = 0.95
WIDTH, HEIGHT    = int(1280/FONT_SIZE), int(800/FONT_SIZE)
FOV              = True
CUMULATE_FOV     = True
MESSAGE_NUMBER   = 8
FOREST_LEVELS    = 0
MAX_ROOMS        = 85
ITEMS_PER_ROOM   = 2
WIZARD_MODE      = False
DUNGEON_LEVELS   = 9
DEBUG            = False
DIFFICULTY       = 18
EDGE_POS         = math.ceil(WIDTH/2)+2
MAP_WIDTH, MAP_HEIGHT = WIDTH, HEIGHT
MAX_INVENTORY    = 12

MIN_ROOM_WIDTH = 4
MIN_ROOM_HEIGHT = 4
MAX_ROOM_SIZE = math.floor(WIDTH/8.83)

def quit(GS):
    # with open('.gamesave', 'w') as gsf:
    #     if not GS['screen'] == 'DEATH':
    #         pickle.dump(GS, gsf, -1)
    #     else: pass
    exit()

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
        item = dun_items[p.pos][-1]
        if p.add_inventory_item(item):
            GS['messages'].append('You pick up a '+item.name)
            del dun_items[p.pos][-1]
        else:
            GS['messages'].append('Your inventory is full.')
            
# Hunger builds more slowly and monsters each get a turn.
def auto_rest(GS, p):
    while p.health < p.max_health:
        p.rest()
        if p.poisoned > 0 and GS['turns'] % 4:
            p.poisoned -= 2
            p.health -= 1
        if GS['turns'] % 6 == 0:
            p.hunger += 1
        utils.monster_turn(GS)
        
        draw.draw_game_screen(GS, 0)
        tdl.flush()
        time.sleep(0.01)
        
        GS['turns'] += 1
        
# Fire the first available missle using the player's current ranged weapon at
def fire(GS, p):
    if len(p.missles) <= 0:
        GS['messages'].append('red: You have no missles to shoot with!')
    else:
        rng = 4
        if p.ranged_weapon:
            rng = p.ranged_weapon.range
            
        ms = list(filter(lambda m:
                        utils.dist(m.pos, p.pos) <= rng and\
                        GS['terrain_map'].dungeon['lighted'].fov[m.pos],
                        GS['terrain_map'].dungeon['monsters']))
        
        ox = max(0, GS['player'].pos[0]-math.floor(WIDTH/4))
        oy = max(0, GS['player'].pos[1]-math.floor(HEIGHT/2))
        for i, m in enumerate(ms):
            start = (p.pos[0]-ox, p.pos[1]-oy)
            end = (m.pos[0]-ox, m.pos[1]-oy)
            draw.draw_line(GS, start, end, colors.light_blue,
                           start_char='@', end_char=str(i))

        if len(ms) > 0:
            key = tdl.event.wait(timeout=None, flush=True)
            while not ('KEY' in key.type and (key.keychar.isnumeric() or key.keychar == 'ESCAPE')):
                GS['messages'].append('Please type number or ESC.')
                draw.draw_hud_screen(GS)
                key = tdl.event.wait(timeout=None, flush=True)

            if key.keychar != 'ESCAPE':
                GS['messages'].append('yellow: You shoot the '+utils.ordinal(key.keychar)+' target!')
                target = ms[int(key.keychar)%len(ms)]
                skill = p.race.skills['range']
                handicap = max(0, math.ceil(1-skill))+5
                
                tpe = ''
                if p.ranged_weapon:
                    tpe = p.ranged_weapon.missle_type
                    
                missle = list(filter(lambda m:
                                     not p.ranged_weapon or tpe in m.missle_type,
                                     p.missles))[-1]
                # Animation
                start = (p.pos[0]-ox, p.pos[1]-oy)
                end = (target.pos[0]-ox, target.pos[1]-oy)
                animation.FireMissleAnimation().run(GS, [missle, start, end])
                
                if target and random.randint(0,max(1, int(100-p.exp*skill-handicap))) < target.speed*20+5:
                    if tpe == '':
                        target.health -= (missle.hit-2)
                    else:
                        target.health -= missle.hit
                    GS['messages'].append('yellow: You hit the '+target.name+'.')
                    if target.health <= 0:
                        GS['messages'].append('green: Your shot hit home! The '+target.name+' dies.')
                        GS['terrain_map'].dungeon['monsters'].remove(target)
                        p.killed_monsters += 1
                        p.learn(GS, target)
                        
                    p.missles.remove(missle)
                    missle.equipped = False
                    GS['terrain_map'].dungeon['items'][target.pos].append(missle)
                else:
                    GS['messages'].append('red: You miss the enemy.')
            else:
                GS['messages'].append('grey: Nevermind.')
        else:
            GS['messages'].append('red: There are no enemies in range.')

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
def auto_move(d):
    event = tdl.event.KeyDown(d, d, False, False, False, False, False)
    def do(GS, p):
        turns = 0
        changed = True
        while changed:
            pp = p.pos
            p.move(event, GS)
            p.hunger += 1
            changed = pp != p.pos
            if turns % 3 == 0:
                utils.monster_turn(GS)
            draw.draw_game_screen(GS, 0)
            tdl.flush()
            time.sleep(0.01)
            turns += 1
    return do

def skills(GS, p):
    if GS['side_screen'] != 'SKILLS':
        GS['side_screen'] = 'SKILLS'
    else:
        GS['side_screen'] = 'HUD'

GAME_ACTION_KEYS = {
    '.': lambda GS, p: p.rest(),
    ',': pickup,
    ';': auto_rest,
    'f': fire,
    'i': inventory,
    'm': skills,

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

# CHAR CONSTANTS
TCOD_CHAR_HLINE=196 # (HorzLine)
TCOD_CHAR_VLINE=179 # (VertLine)
TCOD_CHAR_NE=191 # (NE)
TCOD_CHAR_NW=218 # (NW)
TCOD_CHAR_SE=217 # (SE)
TCOD_CHAR_SW=192 # (SW)

# Double lines walls:
TCOD_CHAR_DHLINE=205 # (DoubleHorzLine)
TCOD_CHAR_DVLINE=186 # (DoubleVertLine)
TCOD_CHAR_DNE=187 # (DoubleNE)
TCOD_CHAR_DNW=201 # (DoubleNW)
TCOD_CHAR_DSE=188 # (DoubleSE)
TCOD_CHAR_DSW=200 # (DoubleSW)

# Single line vertical/horizontal junctions (T junctions):
TCOD_CHAR_TEEW=180 # (TeeWest)
TCOD_CHAR_TEEE=195 # (TeeEast)
TCOD_CHAR_TEEN=193 # (TeeNorth)
TCOD_CHAR_TEES=194 # (TeeSouth)

# Double line vertical/horizontal junctions (T junctions):
TCOD_CHAR_DTEEW=185 # (DoubleTeeWest)
TCOD_CHAR_DTEEE=204 # (DoubleTeeEast)
TCOD_CHAR_DTEEN=202 # (DoubleTeeNorth)
TCOD_CHAR_DTEES=203 # (DoubleTeeSouth)

# Block characters:
TCOD_CHAR_BLOCK1=176 # (Block1)
TCOD_CHAR_BLOCK2=177 # (Block2)
TCOD_CHAR_BLOCK3=178 # (Block3)

# Cross-junction between two single line walls:
TCOD_CHAR_CROSS=197 # (Cross)

# Arrows:
TCOD_CHAR_ARROW_N=24 # (ArrowNorth)
TCOD_CHAR_ARROW_S=25 # (ArrowSouth)
TCOD_CHAR_ARROW_E=26 # (ArrowEast)
TCOD_CHAR_ARROW_W=27 # (ArrowWest)

# Arrows without tail:
TCOD_CHAR_ARROW2_N=30 # (ArrowNorthNoTail)
TCOD_CHAR_ARROW2_S=31 # (ArrowSouthNoTail)
TCOD_CHAR_ARROW2_E=16 # (ArrowEastNoTail)
TCOD_CHAR_ARROW2_W=17 # (ArrowWestNoTail)

# Double arrows:
TCOD_CHAR_DARROW_H=29 # (DoubleArrowHorz)
TCOD_CHAR_ARROW_V=18 # (DoubleArrowVert)

# GUI stuff:
TCOD_CHAR_CHECKBOX_UNSET=224
TCOD_CHAR_CHECKBOX_SET=225
TCOD_CHAR_RADIO_UNSET=9
TCOD_CHAR_RADIO_SET=10

# Sub-pixel resolution kit:
TCOD_CHAR_SUBP_NW=226 # (SubpixelNorthWest)
TCOD_CHAR_SUBP_NE=227 # (SubpixelNorthEast)
TCOD_CHAR_SUBP_N=228 # (SubpixelNorth)
TCOD_CHAR_SUBP_SE=229 # (SubpixelSouthEast)
TCOD_CHAR_SUBP_DIAG=230 # (SubpixelDiagonal)
TCOD_CHAR_SUBP_E=231 # (SubpixelEast)
TCOD_CHAR_SUBP_SW=232 # (SubpixelSouthWest)

# Miscellaneous characters:
TCOD_CHAR_SMILY = 1 # (Smilie)
TCOD_CHAR_SMILY_INV = 2 # (SmilieInv)
TCOD_CHAR_HEART = 3 # (Heart)
TCOD_CHAR_DIAMOND = 4 # (Diamond)
TCOD_CHAR_CLUB = 5 # (Club)
TCOD_CHAR_SPADE = 6 # (Spade)
TCOD_CHAR_BULLET = 7 # (Bullet)
TCOD_CHAR_BULLET_INV = 8 # (BulletInv)
TCOD_CHAR_MALE = 11 # (Male)
TCOD_CHAR_FEMALE = 12 # (Female)
TCOD_CHAR_NOTE = 13 # (Note)
TCOD_CHAR_NOTE_DOUBLE = 14 # (NoteDouble)
TCOD_CHAR_LIGHT = 15 # (Light)
TCOD_CHAR_EXCLAM_DOUBLE = 19 # (ExclamationDouble)
TCOD_CHAR_PILCROW = 20 # (Pilcrow)
TCOD_CHAR_SECTION = 21 # (Section)
TCOD_CHAR_POUND = 156 # (Pound)
TCOD_CHAR_MULTIPLICATION = 158 # (Multiplication)
TCOD_CHAR_FUNCTION = 159 # (Function)
TCOD_CHAR_RESERVED = 169 # (Reserved)
TCOD_CHAR_HALF = 171 # (Half)
TCOD_CHAR_ONE_QUARTER = 172 # (OneQuarter)
TCOD_CHAR_COPYRIGHT = 184 # (Copyright)
TCOD_CHAR_CENT = 189 # (Cent)
TCOD_CHAR_YEN = 190 # (Yen)
TCOD_CHAR_CURRENCY = 207 # (Currency)
TCOD_CHAR_THREE_QUARTERS = 243 # (ThreeQuarters)
TCOD_CHAR_DIVISION = 246 # (Division)
TCOD_CHAR_GRADE = 248 # (Grade)
TCOD_CHAR_UMLAUT = 249 # (Umlaut)
TCOD_CHAR_POW1 = 251 # (Pow1)
TCOD_CHAR_POW3 = 252 # (Pow2)
TCOD_CHAR_POW2 = 253 # (Pow3)
TCOD_CHAR_BULLET_SQUARE = 254 # (BulletSquare)
