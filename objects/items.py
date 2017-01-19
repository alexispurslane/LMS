import colors, consts

class Item:
    def __init__(self, name='Unknown item', weight=1, probability=50, char='*'):
        self.name = name
        self.weight = weight
        self.probability = probability
        self.char = char
        self.fg = colors.grey
        self.equipped = False

    def __eq__(self, other):
        return other != None and self.__dict__ == other.__dict__
    
    def equip(self, player):
        pass

class Armor(Item):
    def __init__(self, name='Unknown armor', weight=3, probability=40, char=']', defence=None):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.equipped = False

    def equip(self, player):
        if not self.equipped:
            if consts.DEBUG: print('equip '+self.name+' ('+str(self.equipped)+')')
            player.defence += self.defence or self.weight
            player.max_defence = player.defence
            self.equipped = True

    def dequip(self, player):
        if self.equipped:
            if consts.DEBUG: print('dequip '+self.name+' ('+str(self.equipped)+')')
            player.defence -= self.weight
            player.max_defence = player.defence
            self.equipped = False
    
class Weapon(Item):
    def __init__(self, name='Unknown weapon', weight=2, attack=5, probability=20, char='|'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.attack = attack
        self.equipped = False
        
    def equip(self, player):
        if not self.equipped:
            if consts.DEBUG: print('equip '+self.name+' ('+str(self.equipped)+')')
            player.max_attack = player.attack = self.attack
            self.equipped = True
        
    def dequip(self, player):
        if self.equipped:
            if consts.DEBUG: print('dequip '+self.name+' ('+str(self.equipped)+')')
            player.max_attack = player.attack = 0
            self.equipped = False

class Light(Item):
    def __init__(self, name='Torch', weight=1, radius=10, lasts=500, probability=55, char='\\'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.radius = radius
        self.lasts = lasts

    def equip(self, p):
        if self.lasts > 0:
            p.light_source_radius = self.radius
            p.dequips.append(self)

    def dequip(self, p):
        p.light_source_radius = 1

class Food(Item):
    def __init__(self, name='Food Ration', weight=0, nutrition=10, probability=55, char='%'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.nutrition = nutrition

    def equip(self, p):
        p.hunger -= self.nutrition
        p.hunger = max(0, p.hunger)
        p.inventory.remove(self)

    def dequip(self, p):
        pass

class RangedWeapon(Item):
    def __init__(self, name='Unknown ranged weapon', weight=2, probability=20, char=')',
                 missle_type='Arrow', range=8):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.missle_type = missle_type
        self.range = range

    def equip(self, player):
        player.ranged_weapon = self

    def dequip(self, player):
        player.ranged_weapon = None

class Missle(Item):
    def __init__(self, name='Regular Arrow', weight=0, probability=45, char='-', hit=15):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.missle_type = name.split()[1]
        self.hit = hit

    def equip(self, player):
        if not self.equipped:
            player.missles.append(self)
            self.equipped = True

    def dequip(self, player):
        if self.equipped:
            if self in player.missles:
                player.missles.remove(self)
            self.equipped = False

ITEMS = [
    Weapon('Broad sword', weight=10, attack=20, probability=5, char='|'),
    Weapon('Fencing foil', weight=1, attack=12, probability=10, char='`'),
    Weapon('Thrusting sword', weight=5, attack=15, char='/', probability=8),
    Weapon('Short sword', attack=12, weight=2, char='(', probability=12),
    Armor('Breastplate', probability=18, char='['),
    Armor('Chain Mail', probability=13, char='['),
    Armor('Mythril Mail', weight=0, probability=3, char=']', defence=11),
    Armor('Plate Armor', weight=10, probability=10, char='&'),
    Armor('Sheild', weight=2, probability=20),
    Armor('Wood Buckler', weight=3, probability=15, char='}'),
    Armor('Iron Buckler', weight=6, probability=15, char='{'),
    Armor('Elven Helm', weight=1, probability=5, char='*'),
    Armor('Viking Helm', weight=3, probability=8, char='*'),
    RangedWeapon('Light Bow', weight=1, probability=20, range=10),
    RangedWeapon('Heavy Bow', weight=3, probability=10, range=20),
    Missle('Mahogeny Arrow', hit=18, char='_', probability=12),
    Missle('Iron Arrow', hit=24, char='-', probability=10),
    Missle(),
    Light(probability=30),
    Food(),
    Food('Raw Meat', nutrition=20, char='='),
    Food('Bread', nutrition=15, char='m'),
]

for i in ITEMS: globals()[i.name.replace(' ', '_').upper()] = i

DUNGEON_ITEMS = ITEMS[:]
DUNGEON_ITEMS.remove(TORCH)
DUNGEON_ITEMS.remove(FOOD_RATION)
DUNGEON_ITEMS.remove(RAW_MEAT)
