import utils, items

defaults = {
    'max_health': 25,
    'strength': 1,
    'skills': {
        'weapon': 1,
        'spell': 0.8,
        'range': 0.8
    },
    'inventory': [
        items.SHORT_SWORD,
        items.TORCH
    ]
}
default_settings = {
    'name': 'Soldier',
    'bonus': 25,
    'speed': 4,
    'levels': 8
}

class Race:
    def __init__(self, first_level=defaults, settings=default_settings):
        self.first_level = first_level
        self.level_up_bonus = settings['bonus']
        self.speed = settings['speed']
        self.name = settings['name']
        self.levels = settings['levels']

SOLDIER      = Race() # Its raceist!
HEAVY = Race({
    'max_health': 100,
    'strength': 10,
    'inventory': [
        items.TORCH
    ],
    'skills': {
        'weapon': 0.9,
        'spell': 0.5,
        'range': 0
    }
}, {
    'name': 'Heavy Soldier',
    'bonus': 2,
    'speed': 10,
    'levels': 3
})
RANGER = Race({
    'max_health': 18,
    'strength': 2,
    'inventory': [
        items.FENCING_FOIL,
        items.LIGHT_BOW,
        items.ELVEN_HELM,
        items.TORCH
    ]+[items.MAHOGENY_ARROW]*7+[items.REGULAR_ARROW]*20,
    'skills': {
        'weapon': 0.98,
        'spell': 1,
        'range': 1.2
    }
}, {
    'name': 'Ranger',
    'bonus': 30,
    'speed': 2,
    'levels': 13
})

RACES = [SOLDIER, HEAVY, RANGER]
