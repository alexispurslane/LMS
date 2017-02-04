import random, math, yaml, copy, os
import colors, utils, consts, items

class Monster:
    def __init__(self, name, char, fg, speed=0, health=0, attack=0, special_action=lambda self, GS, p: -1):
        self.char = char
        self.name = name
        self.pos = (0, 0)
        self.fg = fg
        self.speed = speed
        self.health = health
        self.attack = attack
        self.special_action = special_action
        self.drops = [items.FOOD_RATION]*8 + [items.TORCH]
        if self.health >= 20:
            self.drops.append(items.ITEMS)

    # Removes the monster's attack value from the players health, then
    # runs the monster's special action on the player reference.
    def attack_player(self, player, GS):
        player.health -= self.attack
        self.special_action(self, GS, player)

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
            GS['messages'].insert(0, 'red: The '+self.name+' attacks you suddenly!')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].insert(0, 'yellow: You destroy the sneaky '+self.name)
                GS['terrain_map'].dungeon['monsters'].remove(self)
                
                if self.pos in GS['terrain_map'].dungeon['items']:
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


############################ MONSTER ACTIONS ############################ 
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
        slime = copy.copy(Slime)
        slime.pos = random.choice(valid)
        GS['terrain_map'].dungeon['monsters'].append(slime)
        
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
        items = list(filter(lambda x: x.weight < 4, player.inventory))

        if len(items) > 0:
            item = random.choice(items)
            player.remove_inventory_item(player.inventory.index(item))
        
            GS['messages'].insert(0, 'light_blue: The Imp steals your ' + item.name + ' and throws it.')
            GS['terrain_map'].dungeon['items'][pos].append(item)
    
def poison(self, GS, player):
    if player.defence <= 5:
        if player.poisoned <= 0 and random.randint(1, 100) < 80:
            player.poisoned = self.health
            GS['messages'].insert(0, 'green: You have been poisoned!')
    else:
        GS['messages'].insert(0, 'grey: You\'re armor protects you from bite.')
 
def create_monster(name, mon):
    color = None
    try:
        color = getattr(colors, mon['color'])
    except:
        color = eval(mon['color'])
        
    globals()[name] = Monster(name,
                              mon['char'],
                              color,
                              mon['speed'],
                              mon['health'],
                              mon['attack'])
    if 'action' in mon:
        globals()[name].special_action = globals()[mon['action']]

############################ LOAD MONSTERS ############################ 
monsters = []
yaml_monsters = []
with open("./objects/conf/monsters.yaml", 'r') as stream:
    yaml_monsters = yaml.load(stream)['monsters']

for m in yaml_monsters:
    k, v = list(m.items())[0]
    create_monster(k, v)
    monsters.append(globals()[k])
      
# Selects the correct monster for the current difficulty level based on health and attack.
def select_by_difficulty(d, in_forest=True):
    n = consts.DIFFICULTY
    return list(map(copy.copy, filter(lambda m:
                                      (m.health <= n*(d+1) and\
                                       m.attack >= (n-10)*d) or m == Snake,
                                      monsters)))
