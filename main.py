import tdl
import math, random
import maps, monsters, consts, colors, utils, races, player, draw

# I'm truely sorry.
def run_game(GS):
    GS = GS or {
        'console': tdl.init(consts.WIDTH, consts.HEIGHT, 'Alchemy Sphere'),
        'screen': 'INTRO',
        'player': player.Player(races.HUMAN),
        'terrain_map': maps.TerrainMap(math.floor(consts.WIDTH/2), consts.HEIGHT),
        'messages': [
            'Welcome ye to the sphere of Alchemy,',
            'a terrible and dangerous World into which',
            'alchemists\' lowely apprentices are dispatched',
            'to either learn their trade the hard way',
            'or die epicly.',
            'Get ye to the last forest, from thence to the',
            'caves. You\'re pereformance will be evaluated.'
        ],
        'turns': 0
    }
        
    while True:
        draw.draw_screen(GS)

        for event in tdl.event.get():
            if event.type == 'QUIT':
                raise SystemExit('The window has been closed.')
            elif event.type == 'KEYDOWN' and GS['screen'] == 'DEATH':
                if event.keychar.upper() == 'R':
                    run_game(None)
            elif event.type == 'KEYDOWN' and GS['screen'] == 'INTRO':
                GS['screen'] = 'GAME'
                (GS['player'].x,
                 GS['player'].y) = GS['terrain_map'].generate_new_map()
            elif event.type == 'KEYDOWN' and GS['screen'] == 'GAME':
                if event.keychar.upper() in consts.GAME_KEYS['M']:
                    GS['player'].move(event, GS)
                if event.keychar.upper() in consts.GAME_KEYS['A']:
                    consts.GAME_KEYS['A'][event.keychar.upper()](GS, GS['player'])
                for m in GS['terrain_map'].proweling_monsters:
                    m.move(GS)
                GS['turns'] += 1

run_game(None)
