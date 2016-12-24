import utils, items

defaults = {
    'max_health': 25,
    'strength': 1,
    'inventory': [
        items.Weapon('Short sword', attack=12, weight=2)
    ]
}

class Race:
    def __init__(self, first_level=defaults, speed=4, name='Human', levels=8):
        self.first_level = first_level
        self.level_up_bonus = 25
        self.speed = speed
        self.name = name
        self.levels = levels

HUMAN = Race() # Its raceist!
