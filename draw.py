import tdl, math, re
import maps, monsters, consts, colors, utils, races, player, items
from itertools import groupby

def display_stat(name, obj):
    a = getattr(obj, 'max_'+consts.ABBREV[name])
    b = getattr(obj, consts.ABBREV[name])
    return '%s:%d/%d' % (name, b, a)

def draw_hud_screen(GS, edge_pos):
    if not GS['messages']:
        GS['messages'] = []
    player = GS['player']
    
    rows = [
        'LL: '+str(player.level)+'('+str(player.race.levels)+') | '+player.attributes()+' | '+ display_stat('HT', player)+' | '+display_stat('DF', player),
        display_stat('ST', player)+' | '+display_stat('SP', player)+' | '+ display_stat('AT', player)+' | EX:'+str(player.exp)+' | HR:'+str(player.hunger),
        'GAME INFO: T:'+str(GS['turns'])+
        ' | FL: '+str(GS['terrain_map'].forest_level)+'('+str(consts.FOREST_LEVELS)+')'+
        ' | DL: '+str(GS['terrain_map'].dungeon_level)+'('+str(consts.DUNGEON_LEVELS)+')'+
        ' | MC: '+str(len(GS['terrain_map'].proweling_monsters))+
        ' | ('+str(player.x)+','+str(player.y)+')'
    ]
    for i in range(len(rows)):
        color = colors.medium_blue
        if i <= 1:
            if GS['player'].health > GS['player'].max_health/2:
                color = colors.dark_green
            else:
                color = colors.red
        GS['console'].drawStr(edge_pos, (consts.HEIGHT-len(rows))+i,
                                rows[i].ljust(math.floor(consts.WIDTH/2)-2),
                                bg=color)

    if len(GS['messages']) > consts.MESSAGE_NUMBER:
        GS['messages'] = [GS['messages'][0]]
    occurences = {}
    for (i, m) in enumerate(GS['messages']):
        c = int(300/(i+1))
        # caps
        if c < 0: c = 0
        elif c > 255: c = 255
        if GS['turns'] == 0: c = 255

        nm = re.sub(r" \(x.*\)", "", m)
        if nm in occurences:
            occurences[nm] = occurences[nm] + 1
        else:
            occurences[nm] = 1

        if len(m) > 59: m = m[:59]
        GS['console'].drawStr(math.ceil(consts.WIDTH/2)+1, i, m, fg=(c, c, c))

    GS['messages'] = utils.f7(GS['messages'])
    for (i, m) in enumerate(GS['messages']):
        m = re.sub(r" \(x.*\)", "", m)
        if occurences[m] > 1:
            GS['messages'][i] = m+' (x'+str(occurences[m])+')'

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
        color = colors.black
        if i == GS['selection']:
            color = colors.grey
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

def draw_screen(GS):
    console = GS['console']
    console.clear()

    globals()['draw_'+GS['screen'].lower()+'_screen'](GS)

    tdl.flush()

def draw_charsel_screen(GS):
    console = GS['console']
    for (i, race) in enumerate(races.RACES):
        race_display = 'LuB:%d, Sp:%d, MxL:%d; ST:%d, HT: %d' %\
                       (race.level_up_bonus, race.speed, race.levels,
                        race.first_level['strength'], race.first_level['max_health'])
        console.drawStr(4, i+1, '('+chr(97+i)+') '+race.name+' -> '+race_display)

def draw_intro_screen(GS):
    console = GS['console']
    console.drawStr(int(consts.WIDTH/2)-12, 2, 'Welcome to Alchemy Sphere')
    console.drawStr(int(consts.WIDTH/2)-13, 3, '*press any key to continue*')

def draw_death_screen(GS):
    console = GS['console']
    console.drawStr(int(consts.WIDTH/2)-2, 2, 'R.I.P', fg=(255, 0, 0))
    p = GS['player']
    console.drawStr(int(consts.WIDTH/2)-4, 3, 'Final Level: ' + str(p.level))
    console.drawStr(int(consts.WIDTH/2)-4, 4, 'Final Score: ' + str(p.level+p.killed_monsters))
    console.drawStr(int(consts.WIDTH/2)-10, 5, '*press R to restart*')

def draw_game_screen(GS):
    console = GS['console']
    GS['messages'] = draw_hud(GS)
    GS['terrain_map'].draw_map(GS['console'], GS['player'])
    for m in GS['terrain_map'].proweling_monsters:
        fov = GS['terrain_map'].alt_terrain_map.fov
        if fov[m.x, m.y] or not consts.FOV:
            color = (0,0,0)
            if (m.x, m.y) in GS['terrain_map'].water:
                color = colors.blue
            elif GS['terrain_map'].dungeon_decor[m.x, m.y] == 'FM':
                color = (21, 244, 238)
                
            GS['console'].drawChar(m.x, m.y, m.char, fg=m.fg, bg=color)

    color = (0,0,0)
    if (GS['player'].x, GS['player'].y) in GS['terrain_map'].water:
        color = colors.blue
    elif GS['terrain_map'].dungeon_decor[GS['player'].x, GS['player'].y] == 'FM':
        color = (21, 244, 238)
    console.drawChar(GS['player'].x, GS['player'].y, '@', bg=color)


def draw_dungeon_tile(terrain_map, console, pos, tint):
    (x, y) = pos
    if pos == terrain_map.downstairs:
        console.drawChar(x, y, '>', fg=colors.grey, bg=colors.red)
    elif (x, y) in terrain_map.spawned_items:
        console.drawChar(x, y, terrain_map.spawned_items[x, y].char,
                            fg=colors.tint(terrain_map.spawned_items[x, y].fg, tint))
    elif terrain_map.get_type(x, y) == 'FLOOR':
        console.drawChar(x, y, '.', fg=colors.tint(colors.dark_grey, tint))
    elif terrain_map.get_type(x, y) == 'DOOR':
        if terrain_map.doors[x, y]:
            console.drawChar(x, y, '+', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.brown, tint))
        else:
            console.drawChar(x, y, '-', fg=colors.tint(colors.brown, tint),
                             bg=colors.tint(colors.black, tint))
    elif terrain_map.get_type(x, y) == 'STONE':
        console.drawChar(x, y, '=', fg=colors.tint(colors.dark_grey, tint),
                         bg=colors.tint(colors.lighten(colors.grey), tint))
    if pos in terrain_map.dungeon_decor:
        if terrain_map.dungeon_decor[pos] == 'FM':
            console.drawChar(x, y, '"', fg=(1, 224, 218), bg=(21, 244, 238))

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
