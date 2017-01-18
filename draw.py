import tdl, math, re, random
import maps, monsters, consts, colors, utils, races, player, items
from itertools import groupby
from pyfiglet import Figlet

def display_stat(name, obj):
    a = getattr(obj, 'max_'+name)
    b = getattr(obj, name)
    return '%d/%d' % (b, a)

def draw_hud_screen(GS, edge_pos):
    console = GS['console']
    if not GS['messages']:
        GS['messages'] = []
        
    #################### DRAW HEADS-UP DISPLAY ####################
    player = GS['player']
    base = math.ceil(consts.WIDTH/2)+1
    bounds = len('Health: '+display_stat('health', player))
    start = consts.MESSAGE_NUMBER

    console.drawStr(base, start-1, '-'*(base-1))

    # Description
    console.drawStr(base, start, player.race.name + ' ('+player.attributes()+')')
    
    # Health
    hp = math.floor(player.health/player.max_health*100)
    color = colors.red
    if hp >= 90:
        color = colors.green
    elif hp >= 40:
        color = colors.yellow
        
    console.drawStr(base, start+1, 'Health: '+display_stat('health', player),
                    fg=color)

    # Hunger
    if player.hunger >= 40:
        console.drawStr(base+bounds+4, start+2, 'Very Hungry', fg=colors.red)
    elif player.hunger >= 20:
        console.drawStr(base+bounds+4, start+2, 'Hungry', fg=colors.yellow)
    elif player.hunger >= 15:
        console.drawStr(base+bounds+4, start+2, 'Getting Hungry', fg=colors.green)

    # Light Source Radius
    nm = len(GS['terrain_map'].dungeon['monsters'])
    console.drawStr(base, start+3, 'LoS dist: ' + str(player.light_source_radius))

    # Kills
    console.drawStr(base, start+4, 'Monsters: ' + str(nm))
    console.drawStr(base+bounds+4, start+4, 'Kills: ' + str(player.killed_monsters))

    # Level
    lvl = math.floor(player.level/player.race.levels)
    color = colors.light_blue
    if lvl <= 50:
        color = colors.dark_yellow
    console.drawStr(base, start+5,
                    'Level: '+str(player.level)+'/'+str(player.race.levels),
                    fg=color)

    console.drawStr(base+bounds+4, start+5, 'Exp: '+str(player.exp))

    # Other Stats
    console.drawStr(base, start+6, 'Strength: '+str(player.strength), fg=(0,100,0))
    console.drawStr(base, start+7, 'Speed: '+str(player.speed), fg=colors.light_blue)
    console.drawStr(base, start+8, 'Attack: '+str(player.attack), fg=colors.red)
    console.drawStr(base, start+9, 'Armor: '+str(player.defence), fg=colors.dark_yellow)

    # Ranged Weapon
    if player.ranged_weapon:
        console.drawStr(base, start+10, 'Ranged Weapon: '+str(player.ranged_weapon.name))
        console.drawStr(base+bounds+4, start+10, 'Missles: '+str(len(player.missles)))

    # Game State
    console.drawStr(base, start+11, 'Turn '+str(GS['turns']))
    console.drawStr(base+bounds+4, start+11, 'Score: '+str(player.score(GS)))
    
    #################### DRAW MESSAGES ####################
    if len(GS['messages']) >= consts.MESSAGE_NUMBER:
        GS['messages'] = [GS['messages'][0]]
        
    for (i, m) in enumerate(reversed(GS['messages'])):
        c = int((i + 1) * (255 / len(GS['messages'])))
        c = max(0, min(c, 255))
        
        if GS['turns'] == 0:
            c = 255
        if len(m) > consts.WIDTH-1:
            m = m[:consts.WIDTH-1]
        GS['console'].drawStr(math.ceil(consts.WIDTH/2)+1, i, m, fg=(c, c, c))

    return GS['messages']

def draw_inventory_screen(GS, edge_pos):
    console = GS['console']
    lst = groupby(GS['player'].inventory)
    for (i, grp) in enumerate(lst):
        item, number = grp
        item_display = ""
        if isinstance(item, items.Armor):
            item_display = '(%s) -> W/D:%d' % (item.char, item.weight)
        elif isinstance(item, items.Weapon):
            item_display = '(%s) -> W:%d, A:%d' % (item.char, item.weight, item.attack)
        elif isinstance(item, items.RangedWeapon):
            item_display = '(%s) -> W:%d, R:%d' % (item.char, item.weight, item.range)
        elif isinstance(item, items.Missle):
            item_display = '(%s) -> H:%d' % (item.char, item.hit)
        elif isinstance(item, items.Light):
            item_display = '(%s) -> R:%d, L:%d' % (item.char, item.radius, item.lasts)
        elif isinstance(item, items.Food):
            item_display = '(%s) -> N:%d' % (item.char, item.nutrition)

        color = colors.black
        if item.equipped:
            color = colors.red
            
        try:
            if item == GS['player'].inventory[GS['selection']]:
                color = colors.grey
        except:
            pass
        
        console.drawStr(edge_pos+1, i+1, '('+str(i)+') '+item.name+' -> '+item_display+' (Pr'+str(item.probability)+'%) x'+str(len(list(number))),
                        bg=color)

def draw_man_screen(GS, edge_pos):
    with open('manual.txt', 'r') as myfile:
        manual = myfile.read().split("\n")
        
        for (i, line) in enumerate(manual):
            if line != '' and line[0] == '*':
                GS['console'].drawStr(edge_pos-1, i, line, fg=colors.red)
            else:
                GS['console'].drawStr(edge_pos, i, line)
    return GS['messages']
        
def draw_hud(GS):
    edge_pos = math.ceil(consts.WIDTH/2)+2
    for i in range(0, consts.HEIGHT):
        GS['console'].drawChar(edge_pos-2, i, '|')
        
    return globals()['draw_'+GS['side_screen'].lower()+'_screen'](GS, edge_pos)

frame = 0
def draw_screen(GS):
    global frame
    
    console = GS['console']
    console.clear()

    globals()['draw_'+GS['screen'].lower()+'_screen'](GS, frame)
    frame += 1

    tdl.flush()

def draw_static(console, frame):
    pass

def draw_charsel_screen(GS, frame):
    console = GS['console']
    for (i, race) in enumerate(races.RACES):
        race_display = 'LuB:%d, Sp:%d, MxL:%d; ST:%d, HT: %d' %\
                       (race.level_up_bonus, race.speed, race.levels,
                        race.first_level['strength'], race.first_level['max_health'])
        console.drawStr(int(consts.WIDTH/2)-28, i*2+5,
                        '('+chr(97+i)+') '+race.name+' -> '+race_display)

    draw_static(console, frame)

def draw_intro_screen(GS, frame):
    console = GS['console']
    
    f = Figlet(font='doom')
    l = 24
    for i, line in enumerate(f.renderText(consts.GAME_TITLE).split("\n")):
        if i == 0:
            l = math.floor(len(line)/2)
        console.drawStr(int(consts.WIDTH/2)-l, i+1, line, fg=colors.green)

    console.drawStr(int(consts.WIDTH/2)-12, 18, 'press any key to continue',
                    fg=colors.darken(colors.grey))

    draw_static(console, frame)

def draw_death_screen(GS, frame):
    console = GS['console']
    player = GS['player']
    
    console.drawStr(0, 1, 'Game Stats')
    console.drawStr(0, 2, '----------')
    console.drawStr(4, 3, 'Turns: ' + str(GS['turns']))
    console.drawStr(4, 4, 'Score: ' + str(player.score(GS)))
    console.drawStr(4, 5, 'Kills: ' + str(player.killed_monsters))
    console.drawStr(4, 6, 'Exp:   ' + str(player.exp))
    console.drawStr(4, 7, 'Inventory: ')
    for i, g in enumerate(groupby(player.inventory)):
        console.drawStr(8, 8+i, g[0].name + ' x'+str(len(list(g[1]))))

def draw_game_screen(GS, frame):
    console = GS['console']
    GS['messages'] = draw_hud(GS)
    GS['terrain_map'].draw_map(GS, GS['console'], GS['player'])
    
    for m in GS['terrain_map'].dungeon['monsters']:
        fov = GS['terrain_map'].dungeon['lighted'].fov
        if fov[m.pos] or not consts.FOV:
            color = (0,0,0)
            if m.pos in GS['terrain_map'].dungeon['water']:
                color = colors.blue
                
            GS['console'].drawChar(m.pos[0], m.pos[1], m.char, fg=m.fg, bg=color)

    color = (0,0,0)
    if GS['player'].pos in GS['terrain_map'].dungeon['water']:
        color = colors.blue
    elif GS['terrain_map'].dungeon['decor'][GS['player'].pos] == 'FM':
        color = (0, 100, 0)
        
    console.drawChar(GS['player'].pos[0], GS['player'].pos[1], '@', bg=color)


# Refactor to use self.dungeon
def draw_dungeon_tile(terrain_map, GS, console, pos, tint):
    if GS['mouse_cell'] == pos:
        tint = colors.yellow
    x, y = pos
    if pos == terrain_map.dungeon['down_stairs']:
        console.drawChar(x, y, '>', fg=colors.grey, bg=colors.red)
    elif pos == terrain_map.dungeon['up_stairs']:
        console.drawChar(x, y, '<', fg=colors.grey, bg=colors.blue)
    elif pos in terrain_map.dungeon['items'] and terrain_map.dungeon['items'][pos] != []:
        items = terrain_map.dungeon['items'][pos]
        console.drawChar(x, y, items[-1].char,
                            fg=colors.tint(items[-1].fg, tint))
    elif terrain_map.dungeon['decor'][pos] and terrain_map.get_type(pos) == 'STONE':
        decor = terrain_map.dungeon['decor']
        if decor[pos] == 'FM':
            console.drawChar(x, y, '{', fg=colors.tint(colors.grey, tint),
                             bg=colors.tint((0, 100, 0), tint))
    elif terrain_map.dungeon['decor'][pos]:
        decor = terrain_map.dungeon['decor']
        
        if decor[pos] == 'FM':
            console.drawChar(x, y, '"', fg=(57, 255, 20),
                             bg=(57, 255, 20))
        elif decor[pos] == 'FR':
            console.drawChar(x, y, '^', fg=colors.darken(colors.red),
                             bg=colors.red)
        elif decor[pos] == 'FL':
            console.drawChar(x, y, '^', fg=colors.darken(colors.yellow),
                             bg=colors.darken(colors.red))
    elif terrain_map.get_type(pos) == 'FLOOR':
        console.drawChar(x, y, ' ',
                         bg=colors.tint(
                             colors.extreme_darken(
                                 colors.very_dark_grey), tint))
    elif terrain_map.get_type(pos) == 'DOOR':
        if terrain_map.dungeon['doors'][pos]:
            console.drawChar(x, y, '-', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.extreme_darken(colors.brown), tint))
        else:
            console.drawChar(x, y, '\\', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.black, tint))
    elif terrain_map.get_type(pos) == 'STONE':
        color = colors.tint(colors.darkmed_grey, tint)
        
        console.drawChar(x, y, ' ', bg=color) 
    if pos in terrain_map.dungeon['numbers']:
        n = terrain_map.dungeon['numbers'][pos]
        console.drawStr(x, y, str(n), fg=colors.extreme_lighten((n, n, n)))

def draw_forest_tile(terrain_map, console, pos, tint):
    (x, y) = pos
    if not terrain_map.on_map(x+1,y):
        console.drawChar(x, y, '>', fg=colors.grey)
    elif (x, y) in terrain_map.water and terrain_map.water[x, y]:
        l = terrain_map.noise.get_point(x, y)
        color = colors.blue
        if l > 0.17:
            color = colors.light_blue
        elif l > 0.04:
            color = colors.medium_blue
        console.drawChar(x, y, '~', bg=color)
    elif (x, y) in terrain_map.spawned_items:
        console.drawChar(x, y, terrain_map.spawned_items[x, y].char,
                            fg=colors.tint(terrain_map.spawned_items[x, y].fg, tint))
    elif terrain_map.get_type(x, y) == 'FLOOR':
        console.drawChar(x, y, '.')
    elif terrain_map.get_type(x, y) == 'STONE':
        console.drawChar(x, y, '#', fg=colors.dark_grey, bg=colors.grey)
    elif terrain_map.get_type(x, y) == 'TREE':
        console.drawChar(x, y, 'T', fg=colors.tint(colors.green, tint))
