import random, math
import colors, utils, consts, items

class Monster:
    def __init__(self, char, fg):
        self.char = char
        self.pos = (0, 0)
        self.fg = fg
        self.drops = [items.FOOD_RATION]*8 + [items.TORCH]

    # Removes the monster's attack value from the players health, then
    # runs the monster's special action on the player reference.
    def attack_player(self, player, GS):
        player.health -= self.attack
        self.special_action(GS, player)

    # Decide wether to approach the player or not.
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

    # Check equality
    def __eq__(self, other):
        return other != None and self.__dict__ == other.__dict__

    # Gets the returns the points the monster would prefer to go to, or if there
    # are none, the points the monster *can* go to.
    def get_movement_choices(self, tmap, adj):
        valid = list(filter(lambda p:
                            tmap.is_walkable(p), adj))

        def liked(p):
            decor = tmap.dungeon['decor'][p]
            return not p in tmap.dungeon['water'] and decor != 'FL' and decor != 'FR'
        
        like = list(filter(liked, valid))
        
        if len(like) > 0:
            return like
        else:
            return valid

    # Move monster according to choose() and deal with movement effects.
    def move(self, GS):
        x, y = self.pos
        adj = [
            (x+1, y),
            (x-1, y),
            (x, y+1),
            (x, y-1)
        ]
        sight = int(self.speed/2)
        if sight < 8: sight = 8
        if GS['player'].light(): sight = 3
        
        choices = self.get_movement_choices(GS['terrain_map'], adj)

        if GS['player'].pos in adj:
            GS['messages'].insert(0, 'The '+type(self).__name__+' attacks you suddenly!')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].insert(0, 'You destroy the sneaky '+type(self).__name__)
                GS['terrain_map'].dungeon['monsters'].remove(self)
                if GS['terrain_map'].dungeon['items']:
                    GS['terrain_map'].dungeon['items'][self.pos].append(random.choice(self.drops))
                else:
                    GS['terrain_map'].dungeon['items'][self.pos] = [random.choice(self.drops)]
        elif utils.dist(self.pos, GS['player'].pos) <= sight:
            if random.randint(0, 20) <= self.speed: # Monster moves in proactive direction.
                if len(choices) > 0:
                    self.pos = self.choose(
                        GS['player'],
                        choices,
                        lambda p: utils.dist(p, GS['player'].pos))
            else:                            # Monster moves in random direction.
                if len(choices) >= 2:
                    self.pos = random.choice(choices)

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
    x, y = self.pos
    posns = [
        (x+1, y),
        (x-1, y),
        (x, y+1),
        (x, y-1),
    ]
    valid = list(filter(GS['terrain_map'].is_walkable, posns))
    if len(valid) > 0 and random.randint(1,3) == 1:
        GS['messages'].insert(0, "You chop the slime in half. The new half is alive!")
        if consts.DEBUG:
            print('Slime breeding.')
        slime = Slime()
        slime.pos = random.choice(valid)
        GS['terrain_map'].dungeon['monsters'].append(slime)
        
create_monster('Slime', 's', (27, 226, 21),
               health=13,
               speed=8,
               attack=1,
               sound='squeltching',
               special_action=breed)

def filtch(self, GS, player):
    x, y = self.pos
    posns = [
        (x+1, y),
        (x+2, y),
        (x-1, y),
        (x-2, y),
        (x, y+1),
        (x, y+2),
        (x, y-1),
        (x, y-2),
    ]
    valid = list(filter(lambda p: GS['terrain_map'].is_walkable(p), posns))
    
    if len(valid) > 0:
        pos = random.choice(valid)
        item = random.randint(0, len(player.inventory)-1)
        iitem = player.inventory[item]
        player.remove_inventory_item(item)
        
        GS['messages'].insert(0, 'The Wizard filtches your ' + iitem.name + ' and throws it away.')
        GS['terrain_map'].dungeon['items'][pos].append(iitem)
    
create_monster('Imp', 'i', colors.light_blue,
               health = 15,
               speed = 4,
               attack = 8,
               sound = 'grumbling',
               special_action=filtch)

create_monster('Rat', 'r', colors.brown,
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

regular_monsters = [Fury, Wyvern, Rat, Imp, Giant, Goblin, BabyDragon, Slime, Slime, Slime]

# Selects the correct monster for the current difficulty level based on health and attack.
def select_by_difficulty(d, in_forest=True):
    return list(filter(lambda m: m().health <= 15*(d+1) and m().attack >= 8*d, regular_monsters))
