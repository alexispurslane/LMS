import utils, consts, math, items

class Player:
    def __init__(self, race):
        self.x = 0
        self.y = 0
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
        self.defence = 0
        self.killed_monsters = 0
        self.ranged_weapon = None
        self.missles = []

        for item in self.inventory:
            item.equip(self)

    def learn(self, GS, monster):
        self.exp += math.floor(monster.attack/2)
        self.level_up(GS)

    def rest(self):
        if self.health < self.max_health:
            self.health += 1
            
    def level_up(self, GS):
        s = math.floor(self.exp/(60+self.level*4))
        prevlev = self.level
        if s >= 1 and s <= self.race.levels:
            self.level = s
            if self.level > prevlev:
                GS['messages'].insert(0, 'YOU HAVE LEVELED UP TO LEVEL '+str(self.level))
            self.max_health = (self.level+1)*self.race.level_up_bonus
            self.strength += math.floor(self.race.level_up_bonus/10)

    def attack_monster(self, GS, monster):
        if monster.speed < self.speed:
            self.health -= monster.attack
            self.health += self.defence
            if self.health > 0:
                monster.health -= self.attack
        elif monster.speed >= self.speed:
            monster.health -= self.attack
            if monster.health > 0:
                self.health -= monster.attack
                self.health += self.defence
                
        if self.health > 0 and monster.health <= 0:
            self.learn(GS, monster)
        if monster.health <= 0:
            self.killed_monsters += 1
        return (self.health <= 0, monster.health <= 0)
        
    def add_inventory_item(self, item):
        self.inventory.append(item)
        self.inventory.sort(key = lambda x: x.weight)
        self.speed = 4 + max(0, self.inventory[0].weight-self.strength)
        item.equip(self) # Autoequip for now.

    def move(self, event, GS):
        if self.health < 12:
            GS['messages'].insert(0, 'Your health is low. You should rest <r>.')
        dX, dY = consts.GAME_KEYS['M'][event.keychar.upper()]
        nX = self.x + dX
        nY = self.y + dY
        if nX >= consts.WIDTH-1 and GS['terrain_map'].more_forests():
            GS['messages'].insert(0, "You move on through the forest")
            (self.x, self.y) = terrain_map.generate_new_map() 
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
            if self_dead:
                GS['messages'].insert(0, "You have died.")
                GS['screen'] = 'DEATH'
            

