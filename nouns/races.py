import utils, items, colors

defaults = {
    'max_health': 25,
    'strength': 5,
    'skills': {
        'weapon': 1,
        'spell': 0.8,
        'range': 0.8
    },
    'inventory': [
        items.LONG_DAGGAR,
        items.ROBE,
        items.LEATHER_CAP,
        items.SMALL_ROUND_SHEILD,
        
        items.TORCH
    ]
}
default_settings = {
    'name': 'Warrior',
    'bonus': 20,
    'speed': 4,
    'levels': 8,
    'color': colors.white,
    'description': """
    A jack of all trades, but master of none, the
    Warrior is handy with any blade and resiliant but
    lacks skill in ranged weapons and spellcasting. He
    learns quickly and well but can't progress very
    far. He is naturally fairly slow, and weighed down
    by his substantial, well-rounded starting gear.
    """,
    'suggested_difficulty': 16
}

class Race:
    def __init__(self, first_level=defaults, settings=default_settings):
        self.first_level = first_level
        self.level_up_bonus = settings['bonus']
        self.speed = settings['speed']
        self.name = settings['name']
        self.skills = first_level['skills']
        self.levels = settings['levels']
        self.color = settings['color']
        self.description = settings['description']
        self.suggested_difficulty = settings['suggested_difficulty']

WARRIOR      = Race() # Its raceist!
BERSERKER = Race({
    'max_health': 100,
    'strength': 10,
    'inventory': [
        items.TORCH,
        items.HAND_AXE,
        items.VIKING_HELM,
        items.GAMBESON
    ],
    'skills': {
        'weapon': 1.2,
        'spell': 0.5,
        'range': 0.1
    }
}, {
    'name': 'Berserker',
    'bonus': 10,
    'speed': 10,
    'levels': 10,
    'color': colors.red,
    'description': """
    A close range fighter, the Berserker is slow but
    immensly strong and extremely resiliant.  He has
    two more levels than the Warrior, but learns at a
    third of the pace, forcing him to rely heavily on
    artifacts and weapons to progress. He starts out
    with excellent (if spartan) equipment, and while
    he is extremely skilled with weapons, and can use
    some spells, he doesn't have ranged combat skills.
    """,
    'suggested_difficulty': 18
})
BOWMAN = Race({
    'max_health': 18,
    'strength': 2,
    'inventory': [
        items.LONG_DAGGAR,
        items.CROSSBOW,
        items.LEATHER_CAP,
        items.TORCH,
        items.GAMBESON
    ]+[items.IRON_BOLT]*21+[items.THROWING_KNIFE]*8,
    'skills': {
        'weapon': 0.9,
        'spell': 1,
        'range': 1.3
    }
}, {
    'name': 'Bowman',
    'bonus': 25,
    'speed': 2,
    'levels': 16,
    'description': """
    Light and fast, the Bowman is fragile to start
    with but can progress quickly and far. He is
    compitent with close range combat but excells at
    spellcasting and ranged combat. He starts out with
    light but excellent quality gear that should last
    him succesfully throughout the game.
    """,
    'color': colors.light_blue,
    'suggested_difficulty': 14
})

RACES = [WARRIOR, BERSERKER, BOWMAN]
