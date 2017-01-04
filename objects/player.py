import tdl, copy
import utils, consts, math, items

class Player:
    def __init__(self, race):
        self.x = 0
        self.y = 0
        self.light_source_radius = 1
        self.hunger = 0
        self.level = 0
        self.exp = 0

        # Setup character's race.
        self.race = race
        self.max_health = self.health = self.race.first_level['max_health']
        self.max_strength = self.strength = self.race.first_level['strength']
        self.attack = self.race.first_level['strength']
        self.max_attack = self.attack
        self.inventory = self.race.first_level['inventory']
        self.speed = self.max_speed = self.race.speed
        self.max_defence = self.defence = 0
        self.killed_monsters = 0
        self.ranged_weapon = None
        self.missles = []
        self.dequips = []

        self.inventory = self.inventory+[items.FOOD_RATION]*8

        for item in self.inventory:
            item.equip(self)

    def remember_to_dequip(self, item):
        self.dequips.append(item)

    def learn(self, GS, monster):
        self.exp += math.floor(monster.attack/2)
        self.level_up(GS)

    def rest(self):
        if self.health < self.max_health:
            self.health += 1
            
    def level_up(self, GS):
        s = math.floor(self.exp/(40+self.level*5))
        prevlev = self.level
        if s >= 1 and s <= self.race.levels:
            self.level = s
            if self.level > prevlev:
                GS['messages'].insert(0, 'YOU HAVE LEVELED UP TO LEVEL '+str(self.level))
            ratio = self.health/self.max_health
            self.max_health = (self.level+1)*self.race.level_up_bonus
            self.health = self.max_health*ratio
            self.max_strength += math.floor(self.race.level_up_bonus/10)
            self.strength = self.max_strength

    def attack_monster(self, GS, monster):
        if monster.speed < self.speed:
            monster.attack_player(self, GS)
            self.health += self.defence
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
        
    def add_inventory_item(self, item):
        self.inventory.append(copy.copy(item))
        self.inventory.sort(key = lambda x: x.weight)
        self.speed = 4 + max(0, self.inventory[0].weight-self.strength)
        # item.equip(self) Autoequip

    def remove_inventory_item(self, i):
        item = self.inventory[i]
        item.dequip(self)
        self.inventory.remove(item)

    def total_weight(self):
        total = 0
        for i in self.inventory:
            total += i.weight
            
        return total

    def light(self):
        if self.total_weight() <= 5:
            return 'light'
        else:
            return ''

    def fast(self):
        if self.speed <= 5:
            return 'fast'
        else:
            return ''

    def attributes(self):
        attrs = [self.light(), self.fast()]
        return ', '.join(attrs)+' '+self.race.name

    def move(self, event, GS):
        for item in self.dequips:
            item.lasts -= 1
            if item.lasts <= 0:
                item.dequip(self)
                GS['messages'].insert(0, 'Your '+type(item).__name__+' flickers out.')
                self.dequips.remove(item)
        
        if self.health < 12:
            GS['messages'].insert(0, 'Your health is low. You should rest <r>.')
            
        if self.health < self.max_health and GS['turns'] % 4 == 0:
            self.health += 1
            self.hunger += 1

        if self.hunger > 20:
            GS['messages'].insert(0, 'You feel hungry. Your stomach gurgles. You feel weak.')
            self.health -= 1

        dX, dY = consts.GAME_KEYS['M'][event.keychar.upper()]
        nX = self.x + dX
        nY = self.y + dY
        if nX >= GS['terrain_map'].width-1 and GS['terrain_map'].more_forests():
            GS['messages'].insert(0, "You move on through the forest.")
            (self.x, self.y) = GS['terrain_map'].generate_new_map()
        if (nX, nY) == GS['terrain_map'].downstairs and GS['terrain_map'].in_dungeons():
            GS['messages'].insert(0, "You decend.")
            (self.x, self.y) = GS['terrain_map'].generate_new_map()
        if (nX, nY) in GS['terrain_map'].doors and not GS['terrain_map'].is_walkable(nX, nY):
            GS['terrain_map'].doors[nX, nY] = False
            GS['terrain_map'].terrain_map.walkable[nX, nY] = True
            GS['terrain_map'].terrain_map.transparent[nX, nY] = True
            nX, nY = self.x, self.y
        if GS['terrain_map'].is_walkable(nX, nY):
            self.x = nX
            self.y = nY
            if (nX, nY) in GS['terrain_map'].water:
                GS['messages'].insert(0, "You slosh through the cold water.")
        else:
            GS['messages'].insert(0, "You hit a tree")

        m = GS['terrain_map'].monster_at(nX, nY)
        if m:
            (self_dead, monster_dead) = self.attack_monster(GS, m)
            GS['messages'].insert(0, "You attack the "+type(m).__name__)
            if not monster_dead:
                GS['messages'].insert(0, "The "+type(m).__name__+" attacks you")
                GS['messages'].insert(0, "It's health is now "+str(m.health))
            else:
                GS['messages'].insert(0, "You vanquish the "+type(m).__name__)
                GS['terrain_map'].proweling_monsters.remove(m)
                GS['terrain_map'].spawned_items[m.x, m.y] = items.FOOD_RATION
            if self_dead:
                GS['messages'].insert(0, "You have died.")
                GS['screen'] = 'DEATH'
                
        GS['terrain_map'].dungeon_decor[nX, nY] = None
            

