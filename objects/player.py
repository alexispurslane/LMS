import tdl, copy, random
import utils, consts, math, items

class Player:
    def __init__(self, race):
        self.pos = (0, 0)
        
        self.light_source_radius = 1
        self.hunger = 0
        self.killed_monsters = 0
        
        self.level = 0
        self.exp = 0
        
        self.prev_pos = (-1,-1)

        # Setup character's race.
        self.race = race

        # Setup player's stats.
        self.max_health = self.health = self.race.first_level['max_health']
        self.speed = self.max_speed = self.race.speed
        
        self.max_strength = self.strength = self.race.first_level['strength']
        self.max_attack = self.attack = self.race.first_level['strength']
        self.max_defence = self.defence = 0

        # Setup player's inventory
        self.inventory = list(map(copy.copy, self.race.first_level['inventory']))
        self.inventory = self.inventory+[items.FOOD_RATION]*8
        self.dequips = []
        
        for item in self.inventory:
            item.equip(self)
        
        # Book-keeping
        self.ranged_weapon = None
        self.missles = []

    # Calculate the player's overall score.
    def score(self):
        return (self.level + self.killed_monsters) * self.defence + self.exp

    # Calculate new XP points based on monster danger-level.
    # If the XP is enough to graduate the player to the next level,
    # calls level_up with the current level calculated via the exp.
    def learn(self, GS, monster):
        self.exp += math.floor(monster.attack/2)
        s = math.floor(self.exp/(40+self.level*5))
        
        if s >= 1 and s <= self.race.levels:
            self.level_up(GS, s)

    # Convenience function for resting.
    def rest(self):
        if self.health < self.max_health:
            self.health += 1

    # Handles leveling a player up, takes the calculated level as an argument,
    # checks if it is a new level, and if so upgrades the player's stats.
    def level_up(self, GS, s):
        prevlev = self.level
        self.level = s
        if self.level > prevlev:
            GS['messages'].insert(0, 'YOU HAVE LEVELED UP TO LEVEL '+str(self.level))
            
        ratio = self.health/self.max_health
        self.max_health = (self.level+1)*self.race.level_up_bonus
        self.health = self.max_health*ratio
        self.max_strength += math.floor(self.race.level_up_bonus/10)
        self.strength = self.max_strength

    # If the monster is faster, the monster attacks first, otherwise the player
    # attacks first. The monster is passed a reference to the player to do special
    # actions and decrease health, then the player adds the defence number back to
    # his health and attacks the monster back if he is still alive.
    def attack_monster(self, GS, monster):
        if monster.speed < self.speed:
            monster.attack_player(self, GS)
            self.health += min(self.max_health - self.health, self.defence)
            if self.health > 0:
                monster.health -= self.attack
        elif monster.speed >= self.speed:
            monster.health -= self.attack
            if monster.health > 0:
                monster.attack_player(self, GS)
                self.health += self.defence
                
        if self.health > 0 and monster.health <= 0:
            self.learn(GS, monster)
        if monster.health <= 0:
            self.killed_monsters += 1
        return (self.health <= 0, monster.health <= 0)

    # Adds a copy of the inventory item to the inventory (this is because all
    # inventory items are the same object from the items.ITEMS list), sorts it,
    # And calculates the player's new speed value based on the new weight of the
    # combined inventory.
    def add_inventory_item(self, item):
        self.inventory.append(copy.copy(item))
        self.inventory.sort(key = lambda x: x.weight)
        self.speed = 4 + sum(list(map(lambda x: max(0, x.weight-self.strength), self.inventory)))

    # Removes the i-th item from the inventory, dequips it, and resorts the inventory.
    def remove_inventory_item(self, i):
        item = self.inventory[i]
        item.dequip(self)
        self.inventory.remove(item)
        self.inventory.sort(key = lambda x: x.weight)

    # Calculates the total weight of the player's entire inventory.
    def total_weight(self):
        total = 0
        for i in self.inventory:
            total += i.weight
            
        return total

    # For the Ranger:
    # If the player has two or less armor items and three or less weapons,
    # he is light, and therefore quiet.
    # For others:
    # If he has less than two armor items and three or less weapons, he is light,
    # and quiet.
    def light(self):
        num_armor = len(list(filter(lambda a: isinstance(a, items.Armor), self.inventory)))
        num_weapon = len(list(filter(lambda a: isinstance(a, items.Weapon), self.inventory)))

        if self.race.name == 'Ranger':
            if num_armor <= 2 and num_weapon <= 3:
                return 'light'
        else:
            if num_armor < 2 and num_weapon <= 3:
                return 'light'

    def fast(self):
        if self.speed <= 5:
            return 'fast'
        else:
            return ''

    # Formats and calculates the player's attributes nicely.
    def attributes(self):
        attrs = [self.light(), self.fast()]
        attrs = [x for x in attrs if x is not None]
        
        return ', '.join(attrs)

    # Moves the player and deals with any results of that. FIXME: Refactor this!
    def move(self, event, GS):
        for item in self.dequips:
            item.lasts -= 1
            if item.lasts <= 0:
                item.dequip(self)
                GS['messages'].insert(0, 'Your '+type(item).__name__+' flickers out.')
                self.dequips.remove(item)
                
        if self.health/self.max_health < 0.46:
            GS['messages'].insert(0, 'Your health is low. You should rest <r>.')
            
        if self.health < self.max_health and GS['turns'] % 4 == 0:
            self.health += 1
            
        if GS['turns'] % 4 == 0:
            self.hunger += 1

        if self.hunger > 20 and GS['turns'] % 3 == 0:
            GS['messages'].insert(0, 'You feel hungry. Your stomach gurgles. You feel weak.')
            self.health -= 1

        delta = consts.GAME_KEYS['M'][event.keychar.upper()]
        new_pos = utils.tuple_add(self.pos, delta)
        n_x, n_y = new_pos
        
        if n_x >= GS['terrain_map'].width-1 and GS['terrain_map'].more_forests():
            GS['messages'].insert(0, "You move on through the forest.")
            self.pos = GS['terrain_map'].generate_new_map()
            
        if new_pos == GS['terrain_map'].dungeon['down_stairs'] and\
           GS['terrain_map'].is_dungeons() and\
           len(GS['terrain_map'].dungeon['monsters']) == 0:
            
            GS['messages'].insert(0, "You decend.")
            self.pos = GS['terrain_map'].generate_new_map()

        if new_pos == GS['terrain_map'].dungeon['up_stairs'] and\
           len(GS['terrain_map'].dungeons) > 0:
            
            if GS['terrain_map'].restore_dungeon(GS['terrain_map'].dungeon_level-1):
                GS['messages'].insert(0, "You ascend.")
                self.pos = GS['terrain_map'].dungeon['player_starting_pos']
                
        if new_pos in GS['terrain_map'].dungeon['doors'] and\
           not GS['terrain_map'].is_walkable(new_pos):
            
            GS['terrain_map'].dungeon['doors'][new_pos] = False
            GS['terrain_map'].dungeon['visited'].walkable[new_pos] = True
            GS['terrain_map'].dungeon['visited'].transparent[new_pos] = True
            new_pos = self.pos
            n_x, n_y = new_pos

        if GS['terrain_map'].is_walkable(new_pos):
            self.prev_pos = self.pos
            self.pos = new_pos
            if new_pos in GS['terrain_map'].dungeon['water']:
                GS['messages'].insert(0, "You slosh through the cold water.")
        else:
            GS['messages'].insert(0, "You hit a wall. Stoppit.")
            new_pos = self.pos
            n_x, n_y = new_pos
            
        m = GS['terrain_map'].monster_at(new_pos)
        speed = self.speed
        if utils.streight_line(self.prev_pos, (new_pos)) and self.light() and m:
            GS['messages'].insert(0, "You gallantly charge the monster!")
            self.speed = 0
            
        if m != None:
            (self_dead, monster_dead) = self.attack_monster(GS, m)
            GS['messages'].insert(0, "You attack the "+type(m).__name__)
            
            if not monster_dead:
                GS['messages'].insert(0, "The "+type(m).__name__+" attacks you")
                GS['messages'].insert(0, "It's health is now "+str(m.health))
            else:
                GS['messages'].insert(0, "You vanquish the "+type(m).__name__)
                
                GS['terrain_map'].dungeon['monsters'].remove(m)
                GS['terrain_map'].dungeon['items'][m.pos].append(random.choice(m.drops))
                
            if self_dead:
                GS['messages'].insert(0, "You have died.")
                GS['screen'] = 'DEATH'
                
            self.speed = speed

        decor = GS['terrain_map'].dungeon['decor']
        if decor[new_pos] == 'FM':
            decor[new_pos] = None
        elif decor[new_pos] == 'FR' or decor[new_pos] == 'FL':
            decor[new_pos] = None
            player.health -= 1
            GS['messages'].insert(0, 'The fire burns you.')
            

