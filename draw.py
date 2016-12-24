import tdl, math, re
import maps, monsters, consts, colors, utils, races, player

def display_stat(name, obj):
    a = getattr(obj, 'max_'+consts.ABBREV[name])
    b = getattr(obj, consts.ABBREV[name])
    return '%s: %d(%d)' % (name, b, a)

def draw_hud(GS):
    for i in range(0, consts.HEIGHT):
        GS['console'].drawChar(math.ceil(consts.WIDTH/2), i, '|')

    player = GS['player']
    rows = [
        'LL: '+str(player.level)+'('+str(player.race.levels)+') '+player.race.name,
        display_stat('HT', player)+' '+display_stat('ST', player)+' '+display_stat('SP', player),
        display_stat('AT', player)+' EX: '+str(player.exp)
    ]
    GS['console'].drawStr(math.ceil(consts.WIDTH/2)+2, consts.HEIGHT-3, rows[0])
    GS['console'].drawStr(math.ceil(consts.WIDTH/2)+2, consts.HEIGHT-2, rows[1], bg=colors.grey)
    GS['console'].drawStr(math.ceil(consts.WIDTH/2)+2, consts.HEIGHT-1, rows[2], bg=colors.grey)

    occurences = {}
    for (i, m) in enumerate(GS['messages']):
        c = int(255/(i+1))
        if c < 0: c = 0 # cap
        if GS['turns'] == 0: c = 255

        nm = re.sub(r" \(x.*\)", "", m)
        if nm in occurences:
            occurences[nm] = occurences[nm] + 1
        else:
            occurences[nm] = 1
        
        GS['console'].drawStr(math.ceil(consts.WIDTH/2)+1, i, m, fg=(c, c, c))

    GS['messages'] = utils.f7(GS['messages'])
    for (i, m) in enumerate(GS['messages']):
        m = re.sub(r" \(x.*\)", "", m)
        if occurences[m] > 1:
            GS['messages'][i] = m+' (x'+str(occurences[m])+')'
    
    if len(GS['messages']) > consts.MESSAGE_NUMBER:
        return [GS['messages'][0]]
    else:
        return GS['messages']

def draw_screen(GS):
    console = GS['console']
    console.clear()

    if GS['screen'] == 'GAME':
        GS['messages'] = draw_hud(GS)
        GS['terrain_map'].draw_map(GS['console'], GS['player'])
        for m in GS['terrain_map'].proweling_monsters:
            if GS['terrain_map'].terrain_map.fov[m.x, m.y] or not consts.FOV:
                GS['console'].drawChar(m.x, m.y, m.char, fg=m.fg, bg=colors.brown)
        console.drawChar(GS['player'].x, GS['player'].y, '@', bg=colors.brown)
    elif GS['screen'] == 'INTRO':
        console.drawStr(int(consts.WIDTH/2)-12, 2, 'Welcome to Alchemy Sphere')
        console.drawStr(int(consts.WIDTH/2)-13, 3, '*press any key to continue*')
    elif GS['screen'] == 'DEATH':
        console.drawStr(int(consts.WIDTH/2)-2, 2, 'R.I.P', fg=(255, 0, 0))
        p = GS['player']
        console.drawStr(int(consts.WIDTH/2)-4, 3, 'Score: ' + str(p.attack/2+p.strength))
        console.drawStr(int(consts.WIDTH/2)-10, 4, '*press R to restart*')

    tdl.flush()

