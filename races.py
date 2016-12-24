import utils, items

defaults = {
    'max_health': 25,
    'strength': 1,
    'inventory': [
        items.Weapon('Short sword', attack=12, weight=2)
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
    'strength': 5,
    'inventory': []
}, {
    'name': 'Half-Giant',
    'bonus': 2,
    'speed': 10,
    'levels': 3
})
