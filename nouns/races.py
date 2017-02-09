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
        items.SWORD,
        items.GAMBESON,
        items.VIKING_HELM,
        items.ROUND_SHEILD,
        
        items.TORCH
    ]
}
default_settings = {
    'name': 'Warrior',
    'bonus': 20,
    'speed': 4,
    'levels': 8,
    'color': colors.white,
    'suggested_difficulty': 16
}

class Race:
    def __init__(self, first_level=defaults, settings=default_settings):
        self.first_level = first_level
        self.level_up_bonus = settings['bonus']
        self.speed = settings['speed']
        self.name = settings['name']
        self.levels = settings['levels']
        self.color = settings['color']
        self.suggested_difficulty = settings['suggested_difficulty']

WARRIOR      = Race() # Its raceist!
BERSERKER = Race({
    'max_health': 100,
    'strength': 10,
    'inventory': [
        items.TORCH,
        items.DANE_AXE,
        items.VIKING_HELM,
        items.LEATHER_BREASTPLATE
    ],
    'skills': {
        'weapon': 0.9,
        'spell': 0.5,
        'range': 0
    }
}, {
    'name': 'Berserker',
    'bonus': 10,
    'speed': 10,
    'levels': 10,
    'color': colors.red,
    'suggested_difficulty': 18
})
BOWMAN = Race({
    'max_health': 18,
    'strength': 2,
    'inventory': [
        items.DAGGAR,
        items.ELM_BOW,
        items.ELVEN_HELM,
        items.TORCH,
        items.ROBE
    ]+[items.WOOD_ARROW]*21,
    'skills': {
        'weapon': 0.98,
        'spell': 1,
        'range': 1.2
    }
}, {
    'name': 'Bowman',
    'bonus': 25,
    'speed': 2,
    'levels': 13,
    'color': colors.light_blue,
    'suggested_difficulty': 14
})

RACES = [WARRIOR, BERSERKER, BOWMAN]
