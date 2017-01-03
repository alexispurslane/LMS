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
        items.SHORT_SWORD
    ]
}
default_settings = {
    'name': 'Human',
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

HUMAN      = Race() # Its raceist!
HALF_GIANT = Race({
    'max_health': 100,
    'strength': 10,
    'inventory': [],
    'skills': {
        'weapon': 0.9,
        'spell': 0.5,
        'range': 0
    }
}, {
    'name': 'Half-Giant',
    'bonus': 2,
    'speed': 10,
    'levels': 3
})
ELF = Race({
    'max_health': 18,
    'strength': 2,
    'inventory': [
        items.FENCING_FOIL,
        items.LIGHT_BOW,
        items.ELVEN_HELM
    ]+[items.MAHOGENY_ARROW]*7+[items.REGULAR_ARROW]*20,
    'skills': {
        'weapon': 0.98,
        'spell': 1,
        'range': 1.2
    }
}, {
    'name': 'Elf',
    'bonus': 30,
    'speed': 2,
    'levels': 13
})

RACES = [HUMAN, HALF_GIANT, ELF]
