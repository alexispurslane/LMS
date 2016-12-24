class Item:
    def __init__(self, name='Unknown item', weight=1, probability=50, char='*'):
        self.name = name
        self.weight = weight
        self.probability = probability
        self.char = char

    def equip(self, player):
        pass

class Armor(Item):
    def __init__(self, name='Unknown armor', weight=3, probability=40, char=']'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)

    def equip(self, player):
        player.defence = self.weight
    
class Weapon(Item):
    def __init__(self, name='Unknown weapon', weight=2, attack=5, probability=20, char='|'):
        super().__init__(name=name, weight=weight, probability=probability, char=char)
        self.attack = attack
        
    def equip(self, player):
        player.attack = self.attack

ITEMS = [
    Weapon('Broad sword', weight=10, attack=20, probability=10, char='|'),
    Weapon('Fencing foil', weight=1, attack=15, probability=8, char=')'),
    Weapon('Thrusting sword', weight=5, attack=15, char='/', probability=15)
]
