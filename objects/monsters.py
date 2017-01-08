import colors, utils, random, math, consts

class Monster:
    def __init__(self, char, fg):
        self.char = char
        self.x = 0
        self.y = 0
        self.fg = fg

    def attack_player(self, player, GS):
        player.health -= self.attack
        self.special_action(GS, player)

    def choose(self, player, lst, key):
        if self.speed > player.speed:
            if self.health > player.health:
                return min(lst, key=key)
            else:
                return max(lst, key=key)
        else:
            if math.floor(player.health/self.attack) <= 2:
                return min(lst, key=key)
            elif self.health > player.health:
                return min(lst, key=key)
            else:
                return max(lst, key=key)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
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
            if random.randint(0, 20) <= 15:
                if len(valid) > 0:
                    like = list(filter(lambda p: not (p.x, p.y) in GS['terrain_map'].water, valid))
                    choices = []

                    if len(like) > 0:
                        choices = like
                    else:
                        choices = valid

                    chosen = self.choose(GS['player'], choices, lambda p: utils.dist(p, GS['player']))
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
               health = 26,
               attack = 12,
               sound = 'pattering')

create_monster('Giant', 'G', colors.dark_green,
               health = 50,
               speed = 20,
               attack = 25,
               sound = 'thumping')

def breed(self, GS, player):
    if consts.DEBUG: print("Slime breeding.")
    posns = [
        (self.x+1, self.y),
        (self.x+2, self.y),
        (self.x-1, self.y),
        (self.x-2, self.y),
        (self.x, self.y+1),
        (self.x, self.y+2),
        (self.x, self.y-1),
        (self.x, self.y-2),
    ]
    valid = list(filter(lambda p: GS['terrain_map'].is_walkable(p[0], p[1]), posns))
    if len(valid) > 0:
        pos = random.choice(valid)
        GS['terrain_map'].proweling_monsters[pos] = Slime()
        
create_monster('Slime', 's', (27, 226, 21),
               health=15,
               speed=1,
               attack = 1,
               sound = 'squeltching')

def filtch(self, GS, player):
    posns = [
        (self.x+1, self.y),
        (self.x+2, self.y),
        (self.x-1, self.y),
        (self.x-2, self.y),
        (self.x, self.y+1),
        (self.x, self.y+2),
        (self.x, self.y-1),
        (self.x, self.y-2),
    ]
    valid = list(filter(lambda p: GS['terrain_map'].is_walkable(p[0], p[1]), posns))
    if len(valid) > 0:
        pos = random.choice(valid)
        item = random.choice(player.inventory)
        player.inventory.remove(item)
        GS['messages'].insert(0, 'The Wizard filtches your ' + item.name + ' and throws it away.')
        GS['terrain_map'].spawned_items[pos] = item
    
create_monster('Imp', 'i', colors.light_blue,
               health = 15,
               speed = 4,
               attack = 8,
               sound = 'grumbling',
               special_action=filtch)

create_monster('Hag', 'h', colors.grey,
               health = 12,
               speed = 4,
               attack = 5,
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

regular_monsters = [Fury, Wyvern, Hag, Imp, Giant, Goblin, BabyDragon, Slime, Slime, Slime]

def select_by_difficulty(d, in_forest=True):
    return list(filter(lambda m: m().health <= 15*(d+1) and m().attack >= 8*d, regular_monsters))
