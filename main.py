#!/usr/local/bin/python3
import tdl
import time
import math, random

# Note to self: This uses libtcod 1.5.2, libtcod 1.6.1 is now out, but to use it
# The lib is *very* different, and more verbose. https://bitbucket.org/libtcod/libtcod

import sys
sys.path.append('generators/')
sys.path.append('lib/')
sys.path.append('nouns/')
sys.path.append('objects/')

import maps, monsters, consts, colors, utils, races, player, draw

# I'm truely sorry.
def run_game(GS):
    tdl.setFont('font/consolas12x12_gs_tc.png', greyscale=True, altLayout=True)
    GS = GS or {
        'console': tdl.init(consts.WIDTH, consts.HEIGHT, 'Last Man Standing'),
        'screen': 'INTRO',
        'player': player.Player(races.SOLDIER),
        'terrain_map': maps.TerrainMap(math.floor(consts.WIDTH/2), consts.HEIGHT),
        'messages': list(reversed([
            'After the apocolyptic culmination of humanity\'s battle',
            'with the dark god Chaom, you are the last trained warrior left.',
            'Your task is to clear out the last lurking monsters that served',
            'Chaom in order to protect your people. The portal to the next ',
            'dungeon level will appear once you have destroyed all the monsters.',
            'You have heat vision, so you can see monsters through doors.',
            'You are on your own. Best of luck, soldier.'
        ])),
        'selection': 0,
        'side_screen': 'HUD',
        'turns': 0
    }
        
    while True:
        if GS['player'].health <= 0:
            GS['screen'] = 'DEATH'
        draw.draw_screen(GS)

        tdl.event.set_key_repeat(delay=400, interval=1)
        for event in tdl.event.get():
            if event.type == 'QUIT':
                consts.quit(GS, GS['player'])
            elif event.type == 'KEYDOWN' and GS['side_screen'] == 'INVENTORY':
                if event.keychar.upper() == 'UP':
                    GS['selection'] -= 1
                    GS['selection'] %= len(GS['player'].inventory)
                elif event.keychar.upper() == 'DOWN':
                    GS['selection'] += 1
                    GS['selection'] %= len(GS['player'].inventory)
                elif event.keychar.upper() == 'D':
                    pos = GS['player'].pos
                    GS['terrain_map'].spawned_items[pos] = GS['player'].inventory[GS['selection']]
                    GS['player'].remove_inventory_item(GS['selection'])
                elif event.keychar.upper() == 'W':
                    GS['player'].inventory[GS['selection']].equip(GS['player'])
                elif event.keychar.upper() == 'T':
                    GS['player'].inventory[GS['selection']].dequip(GS['player'])
                elif event.keychar.upper() == 'I':
                    GS['side_screen'] = 'HUD'

            elif event.type == 'KEYDOWN' and GS['screen'] == 'DEATH':
                if event.keychar.upper() == 'R':
                    run_game(None)
            elif event.type == 'KEYDOWN' and GS['screen'] == 'INTRO':
                GS['screen'] = 'CHARSEL'
            elif event.type == 'KEYDOWN' and GS['screen'] == 'CHARSEL':
                if event.keychar.isalpha() and len(event.keychar.lower()) == 1:
                    racen = ord(event.keychar.lower())-97
                    if racen < len(races.RACES):
                        selected_race = races.RACES[racen]
                        GS['player'] = player.Player(selected_race)
                        
                        GS['player'].pos = GS['terrain_map'].generate_new_map()
                        
                        GS['terrain_map'].dungeon['monsters'] = sorted(
                            GS['terrain_map'].dungeon['monsters'], key=lambda m: m.speed)
                        
                        GS['screen'] = 'GAME'
            elif event.type == 'KEYDOWN' and GS['screen'] == 'GAME':
                if event.keychar.upper() in consts.GAME_KEYS['M'] and GS['side_screen'] != 'MAN':
                    GS['player'].move(event, GS)
                elif event.keychar.upper() in consts.GAME_KEYS['A']:
                    consts.GAME_KEYS['A'][event.keychar.upper()](GS, GS['player'])
                elif event.keychar == '?' and GS['side_screen'] == 'HUD':
                    GS['side_screen'] = 'MAN'
                elif event.keychar == '?' and GS['side_screen'] == 'MAN':
                    GS['side_screen'] = 'HUD'

                if GS['side_screen'] == 'HUD':
                    utils.monster_turn(GS)
                    GS['turns'] += 1

run_game(None)
