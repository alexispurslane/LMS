import tdl, math, re, random
import maps, monsters, consts, colors, utils, races, player, items
from itertools import groupby
from pyfiglet import Figlet

def display_stat(name, obj):
    a = getattr(obj, 'max_'+name)
    b = getattr(obj, name)
    return '%d/%d' % (b, a)

def draw_stats(GS):
    console = GS['console']
    player = GS['player']
    base = math.ceil(consts.WIDTH/2)+1
    bounds = len('Health: ')+3
    start = consts.MESSAGE_NUMBER+1
    draw_square(console, base, start, consts.WIDTH-base-2, 11,
                text=(player.race.name + ' ('+player.attributes()+')').upper())
    base += 1
    
    # Health
    hp = math.floor(player.health/player.max_health*100)
    color = colors.red
    if hp >= 90:
        color = colors.green
    elif hp >= 40:
        color = colors.yellow

    ratio = 12/player.max_health
    bar = " "*math.floor(ratio*player.health)
    underbar = " "*math.ceil(ratio*(player.max_health - player.health))
    console.drawStr(base+bounds-3, start+1, bar, bg=color)
    color2 = colors.dark_grey
    if player.poisoned:
        color2 = colors.extreme_darken(colors.dark_green)
    console.drawStr(base+bounds-3+len(bar), start+1, underbar, bg=color2)

    s = 'Health: '+display_stat("health", player)
    for i, c in enumerate(s):
        console.drawChar(base+i, start+1, c,
                         fg=colors.extreme_darken(colors.dark_green),
                         bg=console.get_char(base+i, start+1)[2])
    
    # Hunger
    if player.hunger >= 40:
        console.drawStr(base+bounds+13, start+1, 'Very Hungry', fg=colors.red)
    elif player.hunger >= 20:
        console.drawStr(base+bounds+13, start+1, 'Hungry', fg=colors.yellow)
    elif player.hunger >= 15:
        console.drawStr(base+bounds+13, start+1, 'Getting Hungry', fg=colors.green)

    # Light Source Radius
    nm = len(GS['terrain_map'].dungeon['monsters'])
    console.drawStr(base, start+2, 'LoS dist: ' + str(player.light_source_radius))
    console.drawStr(base+bounds+4, start+2, 'Dungeon '+str(GS['terrain_map'].dungeon_level))

    # Kills
    console.drawStr(base, start+3, 'Monsters: ' + str(nm))
    console.drawStr(base+bounds+4, start+3, 'Kills: ' + str(player.killed_monsters))

    # Level
    lvl = math.floor(player.level/player.race.levels)
    color = colors.light_blue
    if lvl <= 50:
        color = colors.dark_yellow
    console.drawStr(base, start+4,
                    'Level: '+str(player.level)+'/'+str(player.race.levels),
                    fg=color)

    console.drawStr(base+bounds+4, start+4, 'Exp: '+str(player.exp))

    # Other Stats
    l = {
        'Strength': (player.strength, (0,100,0)),
        'Speed': (player.speed, colors.light_blue),
        'Attack': (player.attack, colors.red),
        'Armor': (player.defence, colors.dark_yellow)
    }
    i = 5
    for k, v in l.items():
        console.drawStr(base, start+i, k+': ', fg=v[1])
        console.drawStr(base+len(k)+2, start+i, ' '*math.floor(v[0]), bg=v[1])
        i += 1

    # Ranged Weapon
    if player.ranged_weapon:
        console.drawStr(base, start+9, 'RW: '+str(player.ranged_weapon.name))
        console.drawStr(base+bounds+4, start+9, 'Missles: '+str(len(player.missles)))

    # Game State
    console.drawStr(base, start+10, 'Turn '+str(GS['turns']))
    console.drawStr(base+bounds+4, start+10, 'Score: '+str(player.score(GS)))

def draw_messages(GS):
    console = GS['console']
    ms = 'MESSAGES\n'+'\n'.join(list(reversed(GS['messages'])))
    if len(GS['messages']) >= consts.MESSAGE_NUMBER:
        GS['messages'] = [GS['messages'][0]]
    base = math.floor(consts.WIDTH/2)+1
    draw_square(console, base, 0, consts.WIDTH-base-2, consts.MESSAGE_NUMBER,
                text=ms, spacing=1)
    return GS['messages']
    
def draw_hud_screen(GS):
    console = GS['console']
    draw_stats(GS)
    return draw_messages(GS)

def draw_inventory_screen(GS):
    console = GS['console']
    placing = 0
    for (i, grp) in enumerate(GS['player'].inventory):
        item, number = grp[0], grp[1]
        item_display = ""
        if isinstance(item, items.Armor):
            item_display = 'Character: %s\nWeight: %d\nDefence: %d'\
                           % (item.char, item.weight, item.defence)
        elif isinstance(item, items.Weapon):
            item_display = 'Character: %s\nWeight: %d\nAttack: %d'\
                           % (item.char, item.weight, item.attack)
        elif isinstance(item, items.RangedWeapon):
            item_display = 'Character: %s\nWeight: %d\nRange: %d'\
                           % (item.char, item.weight, item.range)
        elif isinstance(item, items.Missle):
            item_display = 'Character: %s\nHit Damage: %d'\
                           % (item.char, item.hit)
        elif isinstance(item, items.Light):
            item_display = 'Character: %s\nRadius: %d\nLasts (turns): %d'\
                           % (item.char, item.radius, item.lasts)
        elif isinstance(item, items.Food):
            item_display = 'Character: %s\nNutrition Value:%d'\
                           % (item.char, item.nutrition)

        item_display += '\nAmount: '+str(number)
        color = colors.light_blue
        color2 = colors.white
        if item.equipped:
            color2 = color = colors.red
        
        try:
            if i == GS['selection']:
                color2 = color = colors.grey
        except: pass
        
        console.drawStr(consts.EDGE_POS+1, placing, str(i+1)+') '+item.name, bg=color)
        for line in item_display.split("\n"):
            placing += 1
            console.drawStr(consts.EDGE_POS+5, placing, line, fg=color2)
        placing += 2

def draw_man_screen(GS):
    with open('manual.txt', 'r') as myfile:
        manual = myfile.read().split("\n")
        
        for (i, line) in enumerate(manual):
            if line != '' and line[0] == '*':
                GS['console'].drawStr(consts.EDGE_POS-1, i, line, fg=colors.red)
            else:
                GS['console'].drawStr(consts.EDGE_POS, i, line)
    return GS['messages']
        
def draw_hud(GS):
    consts.EDGE_POS = math.ceil(consts.WIDTH/2)+2
    return globals()['draw_'+GS['side_screen'].lower()+'_screen'](GS) or GS['messages']

frame = 0
def draw_screen(GS):
    console = GS['console']
    global frame
    
    console.clear()

    globals()['draw_'+GS['screen'].lower()+'_screen'](GS, frame)
    frame += 1

    tdl.flush()

def draw_static(console, frame):
    pass

def draw_charsel_screen(GS, frame):
    console = GS['console']
    selected_race = None
    for (i, race) in enumerate(races.RACES):
        color = colors.black
        if i+1 == GS['selection']:
            selected_race = race
            color = colors.grey
        console.drawStr(int(consts.WIDTH/2)-28, i*2+5,
                        str(i+1)+') '+race.name,
                        bg=color)

    if selected_race:
        race = selected_race 
        race_display = """BASELINE STATS
        dark_yellow: Level Up Bonus -> %d
        light_blue: Speed -> %d
        light_blue: Number of Levels -> %d
        grey: Strength -> %d
        green: Health -> %d
        Description -> %s""" % (race.level_up_bonus, race.speed, race.levels,
                 race.first_level['strength'],
                 race.first_level['max_health'],
                 race.description)
        draw_square(console, int(consts.WIDTH/2)-27, 30, 54, 30, race_display)

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

    story = """
    Ragnorak has come and gone, and left the gods and their mortal enemies,
    the ice giants, extinct races, the hollow echos of their great exploits
    the only remnant of their passing in the world. Fate decreed it so.....
    And Fate decrees also that a warrior of Norse stock, brave and worthy, 
    undertake to destroy, in revenge for the gods' fall, the ice giant's 
    last remaining kin and minions.
    """.split('\n')

    for (i, line) in enumerate(story):
        console.drawStr(int(consts.WIDTH/2)-30, 20+i, line, fg=colors.grey)

    draw_static(console, frame)

def draw_death_screen(GS, frame):
    console = GS['console']
    player = GS['player']
    
    console.drawStr(consts.WIDTH/2-11, 0, 'Game Stats')
    console.drawStr(0, 1, chr(consts.TCOD_CHAR_DHLINE)*consts.WIDTH)
    console.drawStr(consts.WIDTH/2-11, 3, 'Turns: ' + str(GS['turns']), fg=colors.yellow)
    console.drawStr(consts.WIDTH/2-11, 4, 'Score: ' + str(player.score(GS)), fg=colors.green)
    console.drawStr(consts.WIDTH/2-11, 5, 'Kills: ' + str(player.killed_monsters), fg=colors.red)
    console.drawStr(consts.WIDTH/2-11, 6, 'Exp:   ' + str(player.exp), fg=colors.light_blue)
    console.drawStr(consts.WIDTH/2-11, 7, 'Inventory: ')
    for i, g in enumerate(groupby(player.inventory)):
        console.drawStr(consts.WIDTH/2-7, 8+i, g[0][0].name + ' x'+str(len(list(g[1]))))

def draw_game_screen(GS, frame):
    console = GS['console']
    GS['terrain_map'].draw_map(GS, GS['map_console'], GS['player'], frame)
    ox = max(0, GS['player'].pos[0]-math.floor(consts.WIDTH/4))
    oy = max(0, GS['player'].pos[1]-math.floor(consts.HEIGHT/2))
    GS['console'].blit(GS['map_console'], 0, 0, -1, -1, ox, oy)
    for m in GS['terrain_map'].dungeon['monsters']:
        fov = GS['terrain_map'].dungeon['lighted'].fov
        if fov[m.pos] or not consts.FOV:
            bg_color = GS['map_console'].get_char(m.pos[0], m.pos[1])[2]
            GS['console'].drawChar(m.pos[0]-ox, m.pos[1]-oy, m.char, fg=m.fg, bg=bg_color)

    bg_color = GS['map_console'].get_char(GS['player'].pos[0], GS['player'].pos[1])[2]
    if bg_color == (0, 0, 0):
        bg_color = GS['map_console'].get_char(GS['player'].pos[0], GS['player'].pos[1])[1]
    console.drawChar(GS['player'].pos[0]-ox, GS['player'].pos[1]-oy, '@', bg=bg_color,
                     fg=GS['player'].race.color)
    GS['messages'] = draw_hud(GS)


# Refactor to use self.dungeon
def draw_dungeon_tile(terrain_map, GS, console, pos, tint):
    x, y = pos
    if pos == terrain_map.dungeon['down_stairs']:
        console.drawChar(x, y, chr(consts.TCOD_CHAR_ARROW2_S), fg=colors.grey, bg=colors.red)
    elif pos == terrain_map.dungeon['up_stairs']:
        console.drawChar(x, y, chr(consts.TCOD_CHAR_ARROW2_N), fg=colors.grey, bg=colors.blue)
    elif pos in terrain_map.dungeon['items'] and terrain_map.dungeon['items'][pos] != []:
        items = terrain_map.dungeon['items'][pos]
        back = (12,12,12)
        if len(items) > 1:
            back = colors.white
        console.drawChar(x, y, items[-1].char,
                         fg=colors.tint(items[-1].fg, tint),
                         bg=back)
    elif terrain_map.dungeon['decor'][pos] and terrain_map.get_type(pos) == 'STONE':
        decor = terrain_map.dungeon['decor']
        if decor[pos] == 'FM':
            console.drawChar(x, y, '{', fg=colors.tint(colors.grey, tint),
                             bg=colors.tint((0, 100, 0), tint))
    elif terrain_map.dungeon['decor'][pos]:
        decor = terrain_map.dungeon['decor']
        
        if decor[pos] == 'FM':
            if terrain_map.in_area(pos) == 'Planted':
                console.drawChar(x, y, chr(consts.TCOD_CHAR_SPADE), fg=colors.tint(colors.green, tint))
            else:
                area = terrain_map.in_area(pos)
                color = colors.tint((12, 12, 12), tint)
                if area == 'Marble':
                    color = colors.tint((20,20,20), tint)
                elif area == 'Cave':
                    color = colors.tint(colors.extreme_darken(colors.dark_brown), tint)

                console.drawChar(x, y, ' ', fg=colors.tint(colors.darkmed_grey, tint), bg=color)
        elif decor[pos] == 'FR':
            console.drawChar(x, y, '^', fg=colors.darken(colors.red),
                             bg=colors.red)
        elif decor[pos] == 'FL':
            console.drawChar(x, y, '^', fg=colors.darken(colors.yellow),
                             bg=colors.darken(colors.red))
    elif terrain_map.get_type(pos) == 'FLOOR':
        area = terrain_map.in_area(pos)
        color = colors.tint((12, 12, 12), tint)
        if area == 'Marble':
            color = colors.tint((20,20,20), tint)
        elif area == 'Cave':
            color = colors.tint(colors.extreme_darken(colors.dark_brown), tint)
            
        console.drawChar(x, y, ' ', fg=color, bg=color)
    elif terrain_map.get_type(pos) == 'DOOR':
        if terrain_map.dungeon['doors'][pos]:
            console.drawChar(x, y, chr(consts.TCOD_CHAR_CHECKBOX_SET),
                             fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.extreme_darken(colors.brown), tint))
        else:
            console.drawChar(x, y, chr(consts.TCOD_CHAR_CHECKBOX_UNSET),
                             fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.black, tint))
    elif terrain_map.get_type(pos) == 'STONE':
        area = terrain_map.in_area(pos)
        color = colors.tint(colors.darkmed_grey, tint)
        fg = colors.tint(colors.darken(colors.brown), tint)
        char = chr(consts.TCOD_CHAR_BLOCK2)
        if area == 'Marble':
            color = colors.tint(colors.white, tint)
            fg = colors.tint(colors.darken(colors.white), tint)
            char = chr(consts.TCOD_CHAR_BLOCK3)
        elif area == 'Cave':
            color = colors.tint(colors.brown, tint)
            fg = colors.tint(colors.black, tint)
            char = chr(consts.TCOD_CHAR_BLOCK1)
        
        console.drawChar(x, y, char, bg=color, fg=fg)

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
        console.drawChar(x, y, ' ')
    elif terrain_map.get_type(x, y) == 'STONE':
        console.drawChar(x, y, '#', fg=colors.dark_grey, bg=colors.grey)
    elif terrain_map.get_type(x, y) == 'TREE':
        console.drawChar(x, y, 'T', fg=colors.tint(colors.green, tint))

def draw_line(GS, a, b, color, char=None, start_char=None, end_char=None):
    console = GS['console']

    if char == None:
        going_right = a[0] > b[0]
        vertical_up =  a[0] == b[0] and a[1] > b[1]
        vertical_down =  a[0] == b[0] and a[1] <= b[1]
        if vertical_up:
            char = chr(consts.TCOD_CHAR_ARROW_N)
        elif vertical_down:
            char = chr(consts.TCOD_CHAR_ARROW_S)
        elif going_right:
            char = chr(consts.TCOD_CHAR_ARROW_W)
        elif not going_right:
            char = chr(consts.TCOD_CHAR_ARROW_E)
        
    points = tdl.map.bresenham(a[0], a[1], b[0], b[1])
    result = True
    for pnt in points:
        if GS['terrain_map'].get_type(pnt) == 'STONE':
            result = False
            break
        else:
            console.drawChar(pnt[0], pnt[1], char, fg=color)
    if start_char:
        console.drawChar(a[0], a[1], start_char, fg=colors.white, bg=colors.black)
    if end_char:
        console.drawChar(b[0], b[1], end_char, fg=colors.black, bg=colors.white)
    return result

def draw_square(console, x, y, width, height, text='', spacing=2):
    # height = min(max(0, height), consts.HEIGHT)
    # width = min(max(0, width), consts.WIDTH)
    for i in range(1, height):
        console.drawChar(x, y+i, chr(consts.TCOD_CHAR_VLINE))
        console.drawChar(width+x, y+i, chr(consts.TCOD_CHAR_VLINE))
        
    console.drawStr(x, y, chr(consts.TCOD_CHAR_HLINE)*width)
    console.drawChar(x, y, chr(consts.TCOD_CHAR_NW))
    
    console.drawStr(x+width, y+height, chr(consts.TCOD_CHAR_SE))
    console.drawStr(x, y+height, chr(consts.TCOD_CHAR_HLINE)*width)
    console.drawChar(x+width, y, chr(consts.TCOD_CHAR_NE))
    
    console.drawStr(x, y+height, chr(consts.TCOD_CHAR_SW))

    for i, line in enumerate(text.split('\n')):
        color = colors.white
        if len(line.split(': ')) > 1:
            color = eval("colors." + line.split(': ')[0])
            line = line.split(': ')[1]
        console.drawStr(x+1, y+i*spacing, line.strip(), fg=color)
