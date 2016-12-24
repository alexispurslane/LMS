import colors, utils, random

class Monster:
    def __init__(self, char, fg):
        self.char = char
        self.x = 0
        self.y = 0
        self.fg = fg
        
    def move(self, GS):
        adj = [
            utils.Point(self.x+1, self.y),
            utils.Point(self.x-1, self.y),
            utils.Point(self.x, self.y+1),
            utils.Point(self.x, self.y-1)
        ]
        sight = int(self.speed/6.25)
        if sight < 4: sight = 4

        small = True
        if self.health < GS['player'].health:
            small = utils.dist(self, GS['player']) >= 1 and self.speed > GS['player'].speed
            # Smaller, slower monsters will run away
            
        if utils.Point(GS['player'].x, GS['player'].y) in adj:
            GS['messages'].insert(0, 'The '+type(self).__name__+' attacks you suddenly!')
            (player_dead, monster_dead) = GS['player'].attack_monster(GS, self)
            if monster_dead:
                GS['messages'].insert(0, 'You destory the sneaky '+type(self).__name__)
        elif utils.dist(self, GS['player']) <= sight and small:
            valid = list(filter(lambda p:
                                GS['terrain_map'].is_walkable(p.x, p.y, GS['player']),
                                adj))
            if random.randint(0, 10) <= sight:
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
        adj = 'distant'
        dist = utils.dist(self, GS['player'])
        if dist <= 20:
            adj = 'faint'
        elif dist <= 10:
            adj = ''
        elif dist <= 8:
            adj = 'close'
        elif dist <= 4:
            adj = 'dangerously nearby'
        if not GS['terrain_map'].terrain_map.fov[self.x, self.y] and random.randint(1, 100) <= 20:
            GS['messages'].insert(0, 'You hear a '+adj+' '+self.sound+' sound')

# g - goblin
# G - giant
# D - dragon
# d - baby dragon
# w - witch
# W - wyvern
# f - fury
# F - flying dragon

def create_monster(name, char, color, speed=0, health=0, attack=0, sound='sniffling'):
    def __init__(self):
        Monster.__init__(self, char, color)
        
    globals()[name] = type(name, (Monster,), {
        '__init__': __init__,
        'speed': speed,
        'health': health,
        'attack': attack,
        'sound': sound,
    })

create_monster('Fury', 'f', colors.yellow,
               speed=1,
               health=80,
               attack=8,
               sound='flapping')

create_monster('BabyDragon', 'd', colors.red,
               speed=4,
               health=12,
               attack=15,
               sound='scratching')

create_monster('Dragon', 'D', colors.dark_red,
               health = 300,
               speed = 10,
               attack = 80,
               sound = 'scraping')

create_monster('Goblin', 'g', colors.green,
               speed = 3,
               health = 10,
               attack = 12,
               sound = 'pattering')

create_monster('Giant', 'G', colors.dark_green,
               health = 50,
               speed = 15,
               attack = 25,
               sound = 'thumping')

create_monster('Wizard', 'i', colors.blue,
               health = 10,
               speed = 2,
               attack = 8,
               sound = 'grumbling')

create_monster('Witch', 'w', colors.grey,
               health = 7,
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

regular_monsters = [Fury, Wyvern, Witch, Giant, Goblin, BabyDragon]

def select_by_difficulty(d, in_forest=True):
    if in_forest:
        return list(filter(lambda m: m().health <= 28.5*(d+1), regular_monsters))
    else:
        return list(filter(lambda m: m().health <= 42.8*(d+1), regular_monsters))
