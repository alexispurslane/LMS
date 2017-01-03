import colors, utils, random

class Monster:
    def __init__(self, char, fg):
        self.char = char
        self.x = 0
        self.y = 0
        self.fg = fg

    def attack_player(self, player, GS):
        player.health -= self.attack
        self.special_action(GS, player)
        
    def move(self, GS):
        adj = [
            utils.Point(self.x+1, self.y),
            utils.Point(self.x-1, self.y),
            utils.Point(self.x, self.y+1),
            utils.Point(self.x, self.y-1)
        ]
        sight = int(self.speed/2)
        if sight < 8: sight = 8
        if GS['player'].light(): sight = 1

        if utils.Point(GS['player'].x, GS['player'].y) in adj:
            GS['messages'].insert(0, 'The '+type(self).__name__+' attacks you suddenly!')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].insert(0, 'You destroy the sneaky '+type(self).__name__)
        elif utils.dist(self, GS['player']) <= sight:
            valid = list(filter(lambda p:
                                GS['terrain_map'].is_walkable(p.x, p.y),
                                adj))
            if random.randint(0, 20) <= 5:
                if len(valid) > 0:
                    like = list(filter(lambda p: not (p.x, p.y) in GS['terrain_map'].water, valid))
                    choices = []

                    if len(like) > 0:
                        choices = like
                    else:
                        choices = valid

                    chosen = min(choices, key=lambda p: utils.dist(p, GS['player']))
                    self.x, self.y = chosen.x, chosen.y
            else:
                if len(valid) > 0:
                    chosen = random.choice(valid)
                    self.x, self.y = chosen.x, chosen.y

# g - goblin
# G - giant
# D - dragon
# d - baby dragon
# w - witch
# W - wyvern
# f - fury
# F - flying dragon

def create_monster(name, char, color, speed=0, health=0, attack=0, sound='sniffling', special_action=lambda self, GS, p: -1):
    def __init__(self):
        Monster.__init__(self, char, color)
        
    globals()[name] = type(name, (Monster,), {
        '__init__': __init__,
        'speed': speed,
        'health': health,
        'attack': attack,
        'sound': sound,
        'special_action': special_action
    })

create_monster('Fury', 'f', colors.yellow,
               speed=1,
               health=80,
               attack=8,
               sound='flapping')

create_monster('BabyDragon', 'd', colors.red,
               speed=4,
               health=30,
               attack=15,
               sound='scratching')

create_monster('Dragon', 'D', colors.dark_red,
               health = 300,
               speed = 15,
               attack = 80,
               sound = 'scraping')

create_monster('Goblin', 'g', colors.green,
               speed = 3,
               health = 20,
               attack = 8,
               sound = 'pattering')

create_monster('Giant', 'G', colors.dark_green,
               health = 50,
               speed = 20,
               attack = 25,
               sound = 'thumping')

def filtch(self, GS, player):
    item = random.choice(player.inventory)
    player.inventory.remove(item)
    GS['messages'].insert(0, 'The Wizard filtches your ' + item.name + ' and throws it away.')
    p = player
    GS['terrain_map'].spawned_items[p.x+2, p.y+2] = item
    
create_monster('Wizard', 'i', colors.light_blue,
               health = 11,
               speed = 2,
               attack = 4,
               sound = 'grumbling',
               special_action=filtch)

create_monster('Witch', 'w', colors.grey,
               health = 11,
               speed = 3,
               attack = 2,
               sound = 'tapping')

create_monster('Wyvern', 'W', colors.grey,
               speed = 10,
               health = 80,
               attack = 7,
               sound = 'swishing')
        
create_monster('FlyingDragon', 'F', colors.dark_yellow,
               speed = 6,
               health = 200,
               attack = 70,
               sound = 'crashing')

regular_monsters = [Fury, Wyvern, Witch, Wizard, Giant, Goblin, BabyDragon]

def select_by_difficulty(d, in_forest=True):
    if in_forest:
        return list(filter(lambda m: m().health <= 12*(d+1), regular_monsters))
    else:
        return list(filter(lambda m: m().health <= 15*(d+1), regular_monsters))
