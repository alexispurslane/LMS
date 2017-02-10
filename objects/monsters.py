import random, math, yaml, copy, os, time
import colors, utils, consts, items

class Monster:
    def __init__(self,
                 name,
                 char,
                 fg,
                 speed=0,
                 health=0,
                 attack=0,
                 special_action=lambda self, GS, p: -1,
                 agressive=False,
                 ranged=False):
        self.char = char
        self.name = name
        self.pos = (0, 0)
        self.fg = fg
        self.speed = speed
        self.health = health
        self.attack = attack
        self.special_action = special_action
        self.agressive = agressive
        self.ranged = ranged
        self.drops = [items.FOOD_RATION]*8 + [items.TORCH, items.SWORD, items.GAMBESON]
        
        self.sight = int(self.speed/2)
        if self.sight < 8:
            self.sight = 8
            if self.ranged:
                self.sight += 3
        
        if self.health >= 20:
            self.drops.append(items.ITEMS)

    # Removes the monster's attack value from the players health, then
    # runs the monster's special action on the player reference.
    def attack_player(self, player, GS):
        miss = random.randint(0, 100) - (self.sight+5)*10
        hit_level = miss_level = ""
        if miss <= 90:
            hit_level = "tremendously "
        elif miss <= 70:
            hit_level = "head-on "
        elif miss <= 60:
            hit_level = "roundly "
        elif miss <= 30:
            hit_level = "painfully "
        elif miss <= 10:
            hit_level = "weakly "
        elif miss <= 0:
            hit_level = "barely "
        elif miss >= 15:
            miss_level = "barely "
        elif miss >= 30:
            miss_level = "closely "
        elif miss >= 50:
            miss_level = "widely "
            
        if miss <= 0:
            GS['messages'].insert(0, "red: The monster hits you "+hit_level+".")
            player.health -= self.attack
            self.special_action(self, GS, player)
        else:
            GS['messages'].insert(0, "green: The monster "+miss_level+"misses you.")

    # Decide wether to approach the player or not.
    def choose(self, player, lst, key):
        if self.agressive:
            return min(lst, key=key)
        elif self.ranged:
            return max(lst, key=key)
        elif self.speed > player.speed:
            if self.health > player.health:
                return min(lst, key=key)
            else:
                return max(lst, key=key)
        else:
            if player.attack < self.attack:
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
        adj = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        
        choices = self.get_movement_choices(GS['terrain_map'], adj)
        sight = self.sight
        if GS['player'].light():
            self.sight = 3

        if GS['player'].pos in adj:
            GS['messages'].insert(0, 'red: The '+self.name+' attacks you.')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].insert(0, 'yellow: You destroy the '+self.name)
                GS['terrain_map'].dungeon['monsters'].remove(self)
                
                if self.pos in GS['terrain_map'].dungeon['items']:
                    GS['terrain_map'].dungeon['items'][self.pos].append(random.choice(self.drops))
                else:
                    GS['terrain_map'].dungeon['items'][self.pos] = [random.choice(self.drops)]
        elif utils.dist(self.pos, GS['player'].pos) <= self.sight:
            if self.ranged:
                p = GS['player']
                m = self
                
                ox = max(0, GS['player'].pos[0]-math.floor(WIDTH/4))
                oy = max(0, GS['player'].pos[1]-math.floor(HEIGHT/2))
                
                start = (m.pos[0]-ox, m.pos[1]-oy)
                end = (p.pos[0]-ox, p.pos[1]-oy)
                
                draw.draw_line(GS, start, end, self.fg,
                               start_char=self.char, end_char='@')
                time.sleep(0.3)
                p.health -= self.speed
                
            elif len(choices) > 0:
                self.pos = self.choose(
                    GS['player'],
                    choices,
                    lambda p: utils.dist(p, GS['player'].pos))
        else:                            # Monster moves in random direction.
            if len(choices) > 0:
                self.pos = random.choice(choices)
                
        self.sight = sight


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
    if len(valid) > 0 and random.randint(1,2) == 1:
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
        items = list(filter(lambda x: x.weight <= 4, player.inventory))

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
