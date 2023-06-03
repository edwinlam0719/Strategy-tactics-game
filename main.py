import math
import operator
import random
import sys
import time
import heapq

character_special_moves = {
  "Gallahyde":  ["fire", "heal","strike","pow","toxic"],
  "Asyll":      ["fire", "pow", "heal"],
  "Luce":       ["fire", "pow"],
  "Omios":      ["fire", "heal","strike","pow","toxic"],
  "Shin":       ["fire", "heal","strike","pow","toxic"],
  "Seraphim":   ["fire", "heal","strike","pow","toxic"],
  "Polne":      ["fire","strike"],
  "Ultomos":    ["fire","strike"],
  "Atamus":     ["fire", "heal","strike","pow","toxic"],
  "Etriv":      ["fire", "heal","strike","pow","toxic"]
}

# for element's weaknesses
elements = {
    "fire":     ["water"],
    "water":    ["earth"],
    "earth":    ["fire"],
    "dark":     ["light"],
    "light":    ["dark"],
    "cursed":   ["dark", "light"],
    "blessed":  ["water", "earth","fire"]
}
special_moves = {
  "fire":   {"damage": 20,  "heal": 0, "range": 2, "type": 'magic', "cooldown": 2, "base_hit_rate": 0.4, "buff": "weak", "base_crit_rate": 0.1},
  "heal":   {"damage": 0,   "heal": 0, "range": 2, "type": "magic", "cooldown": 2, "base_hit_rate": 1, "buff": "none", "base_crit_rate": 0},
  "strike": {"damage": 40,  "heal": 0, "range": 2, "type": 'physical', "cooldown": 0, "base_hit_rate": 0.45, "buff": "none", "base_crit_rate": 0.35},
  "pow":    {"damage": 100, "heal": 0, "range": 2, "type": 'physical', "cooldown": 2,"base_hit_rate": 0.25, "buff": "none", "base_crit_rate": 0.2},
  "toxic":  {"damage": 0,   "heal": 0, "range": 3, "type": 'status effect', "cooldown": 3,"base_hit_rate": 0.15, "buff": "poison", "base_crit_rate": 0}
}


#includes debuffs as well, but they dont use cooldowns or range
class Buff:
    def __init__(self, name, duration, cooldown, range, type, affect_hp=0, attack_buff=0, m_attack_buff=0, defense_buff=0, m_defense_buff=0, speed_buff=0, luck_buff=0, dex_buff=0):
        self.name = name
        self.duration = duration
        self.cooldown = cooldown
        self.range = range
        self.type = type
        self.affect_hp = affect_hp
        self.attack_buff = attack_buff
        self.m_attack_buff = m_attack_buff
        self.defense_buff = defense_buff
        self.m_defense_buff = m_defense_buff
        self.speed_buff = speed_buff
        self.luck_buff = luck_buff
        self.dex_buff = dex_buff

empower =   Buff("empower", duration=1, cooldown = 100, range = 4, type = "percent", affect_hp=0, attack_buff='150%', m_attack_buff='100%', defense_buff='100%', m_defense_buff='100%', luck_buff='100%', dex_buff='100%')
weak =      Buff("weak", duration=6, cooldown = 0, range = 0, type = "flat", affect_hp=0, attack_buff=-4, m_attack_buff=0, defense_buff=0, m_defense_buff=0, luck_buff=0, dex_buff=0)
psyche =    Buff("psyche", duration=1, cooldown = 1, range = 1, type = "flat", affect_hp=0, attack_buff=0, defense_buff=5, m_attack_buff=0, m_defense_buff=0, luck_buff=0, dex_buff=0)
none =      Buff("none", duration=0, cooldown = 0, range = 0, type = "flat", affect_hp=0, attack_buff=0, defense_buff=0, m_attack_buff=0, m_defense_buff=0, luck_buff=0, dex_buff=0)
poison =    Buff("poison", duration=3, cooldown = 0, range = 0, type = "flat", affect_hp=-20, m_attack_buff=0, defense_buff=0, m_defense_buff=0, luck_buff=0, dex_buff=0)

buff_list = {
    "empower": empower,
    "weak": weak,
    "psyche": psyche,
    "none": none,
    "poison": poison
}

character_buff_moves = {
  "Gallahyde":  ["empower","none", "psyche"],
  "Asyll":      ["empower","none", "psyche"],
  "Luce":       ["empower","none", "psyche"],
  "Omios":      ["empower","none", "psyche"],
  "Shin":       ["empower","none", "psyche"],
  "Seraphim":   ["empower","none", "psyche"],
  "Polne":      ["empower","none", "psyche"],
  "Ultomos":    ["empower","none", "psyche"],
  "Atamus":     ["empower","none", "psyche"],
  "Etriv":      ["empower","none", "psyche"]
}

class Player:
    def __init__(self, name, id, max_hp, attack, m_attack, defense, m_defense, speed, luck, dex, element, x, y, movement, ap, level, team):
        self.name = name
        self.id = id
        self.max_hp = max_hp
        self.current_hp = max_hp
        self.attack = attack
        self.m_attack = m_attack
        self.defense = defense
        self.m_defense = m_defense
        self.speed = speed
        self.luck = luck 
        self.dex = dex
        self.element = element
        self.x = x
        self.y = y
        self.movement = movement 
        self.ap = ap
        self.level = level
        self.team = team
        self.buffs = []
        self.turnsSinceAttack = {}       
        self.actions = {
            "2": self.move,  # action name: method
            "1": self.attack_enemy,
            "3": self.heal,
            "4": self.apply_buff,    
            "5": self.none
            }
        self.heuristics = [
            {"name": "attack_enemy", "weight": 0.4},
            {"name": "heal", "weight": 0.3},
            {"name": "apply_buff", "weight": 0.2},
            {"name": "move", "weight": 0.1}
            ]
    
    def justattacked_TSA(self, move_name):
        for move in character_special_moves[self.name]:
            if move == move_name:
                self.turnsSinceAttack.update({move:0})      
            #print(move)
            #print(self.turnsSinceAttack[move])

    def justbuffed_TSA(self, buff_name):
        for move in character_buff_moves[self.name]:
            if move == buff_name:
                self.turnsSinceAttack[move] = 0
            value = self.turnsSinceAttack.get(move, 0)
            #print(move)
            #print(value)

    def intialize_TSA(self):
        for move in character_special_moves[self.name]:
            self.turnsSinceAttack.update({move:special_moves[move]["cooldown"]})      
            #print(move)
            #print(self.turnsSinceAttack[move])

    def intialize_TSA_buff(self):
        for move in character_buff_moves[self.name]:
            self.turnsSinceAttack.update({move:buff_list[move].cooldown})      
            #print(move)
            #print(self.turnsSinceAttack[move])

    # self means u have access to all of Players attributes
    def none(self):
        print("Did Nothing :)")

    def set_level(self):
        self.max_hp += self.level / 5
        self.current_hp = self.max_hp
        self.attack += self.level / 5
        self.m_attack += self.level / 5 
        self.defense += self.level / 5
        self.m_defense += self.level / 5
        self.speed += self.level / 5
        self.luck += self.level / 5
        self.dex += self.level / 5

    def move(self, new_x, new_y):
        # Check if the new position is within the bounds of the grid
        while True:
            try:
                overlap = False
                for player in players:
                    #print("self x: " + str(player.x + 1) + " self y: " + str(player.y + 1)  + " new x: " + str(new_x) +  " new y: " + str(new_y))
                    if new_x == player.x + 1 and new_y == player.y + 1:
                        if new_x != self.x + 1 and new_y != self.y + 1: 
                            overlap = True               
                #check if OOB
                if 0 <= new_x <= num_rows and 0 <= new_y <= num_columns and overlap == False:
                    #check if in movement range
                    # Loop through all the rows and columns of the board

                    # Calculate the distance of the current position from the player's starting position
                    distance = abs(new_x - (self.x + 1)) + abs(new_y - (self.y + 1))
                    #print("dist of row: "+ str(new_x) + " - " + str(self.x))
                    #print("dist of col: "+ str(new_y) + " - " + str(self.y))
                    #print(str(distance) + " <= " + str(self.movement))
                    # Check if the current position is within the player's movement range

                    if distance <= self.movement:
                        # Player can move to this position
                        self.x = abs(new_x - 1)
                        self.y = abs(new_y - 1)
                        break
                    else:
                        # Player cannot move to this position
                        print(f"Player cannot move here due to the distance, {distance} <= {self.movement}")
                        new_x = int(input("Enter new x coordinate: "))
                        new_y = int(input("Enter new y coordinate: "))
                else:
                    print("Invalid input, may be overlap, OOB, beyond movement range")
                    new_x = int(input("Enter new x coordinate: "))
                    new_y = int(input("Enter new y coordinate: "))
                    
                    # Prompt the user to enter a new position if the current one is invalid
            except ValueError:
                print("Invalid input, no strings")      

    def take_damage(self, damage):
        self.current_hp -= damage
        if self.current_hp < 0:
            self.current_hp = 0
        if self.current_hp <= 0:
            print(self.name + " has DIEDDDDDDDDDDDDDDDDDDDD")
            #print(f"{self.x}, {self.y}")
            board[self.x][self.y] = '[  ]'
            #print("GTFO THE BOARD")
            players.remove(self)
            

    def apply_modifier(player, stat, modifier):
        if isinstance(modifier, int) or isinstance(modifier, float):
            # Add modifier if it is an integer or float
            # code is crashing here after being passed by remove_buff
            setattr(player, stat, getattr(player, stat) + modifier)
        elif isinstance(modifier, str) and modifier[-1] == '%':
            # Multiply by modifier if it is a string ending in '%'
            setattr(player, stat, getattr(player, stat) * (float(modifier[:-1]) / 100))
        else:
            raise ValueError("Invalid modifier type")

    def remove_modifier(player, stat, modifier):
        if isinstance(modifier, int) or isinstance(modifier, float):
            # Subtract modifier if it is an integer or float
            setattr(player, stat, getattr(player, stat) - modifier)
        elif isinstance(modifier, str) and modifier[-1] == '%':
            # Divide by modifier if it is a string ending in '%'
            setattr(player, stat, getattr(player, stat) / (float(modifier[:-1]) / 100))
        else:
            raise ValueError("Invalid modifier type")

    def apply_buff(self, target, buff):       
            # buff is a string used to reference buff object in dict       
            # buff string is appended, not the object
            buff_object = buff_list[buff] 
            target.buffs.append(buff_object)
            index = target.buffs.index(buff_object)
            #print(f"{self.name} applied {buff_list[buff].name} to {target.name}")
            # modifier needs to know which Player stat is being changed
            # the buff object has attack_buff, which represents the incremental value to attack
            # but we have to manually clarify it into the function call
            # how do we circumvent it, by calling modifiers for all possible stats
            # all buffs in the Buff Class are initialized to 0
            target.apply_modifier("attack", buff_list[buff].attack_buff)
            target.apply_modifier("defense", buff_list[buff].defense_buff)
            target.apply_modifier("m_attack", buff_list[buff].m_attack_buff)
            target.apply_modifier("m_defense", buff_list[buff].m_defense_buff)
            target.apply_modifier("speed", buff_list[buff].speed_buff)
            target.apply_modifier("luck", buff_list[buff].luck_buff)
            target.apply_modifier("dex", buff_list[buff].dex_buff)
            #if buff applied is poison, do calculations to change value 
            if buff == "poison": 
                #buff which is poison, has not been applied yet
                              
                #print(target.buffs[index].duration)
                #print("<")
                #this value should never change
                #print(buff_list[buff].duration)
                #target.buffs[index].duration is the current duration of poison while the other is the hard defined duration of poison
                #print(f"{target.buffs[index].duration} < {buff_list[buff].duration}")
                #if target.buffs[index].duration < buff_list[buff].duration:
                if target.max_hp == target.current_hp:
                    new_value = buff_list[buff].affect_hp
                    target.apply_modifier("current_hp", buff_list[buff].affect_hp)
                    #target.buffs[index].duration -= 1
                    print(f"{buff} just did {new_value}")
                else:
                    #this should be a special version based on missing hp
                    new_value = buff_list[buff].affect_hp
                    target.apply_modifier("current_hp", new_value)
                    #target.buffs[index].duration -= 1
                    print(f"{buff} just did {new_value}")

            
            #target.apply_modifier("current_hp", buff_list[buff].affect_hp)
            print(f"{target.name}'s Stats: ")
            print("-------------------------------------------")
            print("Attack:    {:<4}    Magic Attack:  {:<8}".format(target.attack, target.m_attack))
            print("Defense:   {:<4}    Magic Defense: {:<8}".format(target.defense, target.m_defense))
            print("Speed:     {:<4}    Luck:          {:<8}".format(target.speed, target.luck))
            print("Dexterity: {:<4}".format(target.dex))
            
            print(f"{buff} new duration: {target.buffs[index].duration}")
            print(f"{buff} is now TSA: 0")
            self.justbuffed_TSA(buff)

    def remove_buff(self):
        for buff in self.buffs:
            if buff.duration <= 0:
                if buff.type == "flat":
                    self.apply_modifier("attack", -int(buff.attack_buff))
                    self.apply_modifier("defense", -int(buff.defense_buff))
                    self.apply_modifier("m_attack", -int(buff.m_attack_buff))
                    self.apply_modifier("m_defense", -int(buff.m_defense_buff))
                    self.apply_modifier("speed", -int(buff.speed_buff))
                    self.apply_modifier("luck", -int(buff.luck_buff))
                    self.apply_modifier("dex", -int(buff.dex_buff))
                    removed_buff = self.buffs.remove(buff)       
                    print(removed_buff)
                elif buff.type == "percent":
                    self.remove_modifier("attack", (buff.attack_buff))
                    self.remove_modifier("defense", (buff.defense_buff))
                    self.remove_modifier("m_attack", (buff.m_attack_buff))
                    self.remove_modifier("m_defense",(buff.m_defense_buff))
                    self.remove_modifier("speed",(buff.speed_buff))
                    self.remove_modifier("luck",(buff.luck_buff))
                    self.remove_modifier("dex",(buff.dex_buff))
                    removed_buff = self.buffs.remove(buff)       
                    print(removed_buff)
                elif buff.type == "status effect":
                    removed_buff = self.buffs.remove(buff)       
                    print(removed_buff)

    def check_dot(self):
        for buff in self.buffs:
            if buff.name == "poison":
                print("CHECKING FOR DOTS...")
                self.apply_buff(self, "poison")               
                self.buffs.remove(buff)
                

    def calc_hit_rate(self, enemy, base_hit_rate):
        hit_rate = base_hit_rate + (self.dex / (self.dex + enemy.dex)) 
        return hit_rate

    def calc_crit_rate(self, enemy, base_crit_rate):
        crit_rate = base_crit_rate + (self.luck / (self.luck + enemy.luck)) 
        return crit_rate / 10

    def attack_enemy(self, enemy, character, move, move_name, element):    
        while True:     
            distance = abs(self.x - enemy.x) + abs(self.y - enemy.y)
            hit_rate = self.calc_hit_rate(enemy, move["base_hit_rate"])  
            # Generate random number
            rand = random.uniform(0, 1)
            crit_rate = self.calc_crit_rate(enemy, move["base_crit_rate"])
            # Generate random number
            rand_crit = random.uniform(0, 1)
            if distance <= move["range"]:
                # Check if attack hits
                if rand < hit_rate:
                    # Attack hits
                    if move["type"] == "physical":
                        damage = (self.attack + move["damage"]) - enemy.defense
                        print(self.attack)
                        print(move["damage"])
                        print(damage)
                    elif move["type"] == "magic":
                        damage = (self.m_attack + move["damage"]) - enemy.m_defense
                    elif move["type"] == "status effect":
                        damage = move["damage"]
                    if element in elements[enemy.element]:
                        # Attack element is strong against enemy element
                        print("It's Super Effective")
                        damage *= 1.2
                    elif enemy.element in elements[element]:
                        # Attack element is weak against enemy element
                        print("It's Not Very Effective")
                        damage *= 0.8    
                    if damage > 0:
                        if rand_crit < crit_rate:
                            crit_damage = damage * 1.5                           
                            self.justattacked_TSA(move_name)
                            enemy.take_damage(damage)
                            if move["buff"] != 'none':
                                enemy.apply_buff(enemy, buff_list[move["buff"]].name)
                            break
                        else:
                            print(self.name, "used", move_name, "and dealt", str(damage), "points of damage to", enemy.name)                      
                            self.justattacked_TSA(move_name)
                            enemy.take_damage(damage)
                            print(f"{enemy.name} HP: {enemy.current_hp}")
                        
                            if move["buff"] != 'none':
                                enemy.apply_buff(enemy, buff_list[move["buff"]].name)
                                print(buff_list[move["buff"]].name + " has been applied!")
                            #buff_list[move["buff"]] is a buff object, not a string
                            #but the parameters of apply_buff needs a string of buff name
                            #this is because buff_list is a dict with buff objects                        
                            break
                    else:
                        self.justattacked_TSA(move_name)                      
                        enemy.take_damage(0)
                        
                        if move["buff"] != 'none':
                            enemy.apply_buff(enemy, buff_list[move["buff"]].name)
                            print(buff_list[move["buff"]].name + " has been applied!")
                        break
                else: 
                    # Attack misses
                    print(f"{move_name} missed!!!")
                    break
            else: 
                    print("Invalid move, out of range") 
                    break
                   
    def heal(self):
        move = special_moves['heal']
        self.current_hp += move['damage']
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        print(self.name + " healed " + str(self.current_hp))

    def astar(self, start, end):
        # The four directions to move on the grid
        directions = [(0,1), (0,-1), (1,0), (-1,0)]

        # The priority queue for the A* algorithm
        heap = []

        # A dictionary to keep track of the visited cells
        visited = {}

        # A dictionary to store the cost to reach each cell
        cost = {}

        # A dictionary to store the parent of each cell (for reconstructing the path)
        parent = {}

        # Initialize the starting cell
        cost[start] = 0
        heap.append((0, start))
        visited[start] = True
        parent[start] = None

        while heap:
            # Get the cell with the lowest cost
            current_cost, current_cell = heapq.heappop(heap)

            # Check if we have reached the end
            if current_cell == end:
                break

            # Visit all the neighbors of the current cell
            for direction in directions:
                row = current_cell[0] + direction[0]
                col = current_cell[1] + direction[1]

                # Check if the cell is out of bounds or an obstacle
                if row < 0 or row >= num_rows or col < 0 or col >= num_columns or board[row][col] == "[XX]":
                    continue

                # Calculate the cost of the cell
                new_cost = current_cost + 1

                # Check if we have already visited the cell or if the new cost is lower than the previous one
                if (row, col) not in visited or new_cost < cost[(row, col)]:
                    cost[(row, col)] = new_cost
                    new = (row, col)
                    #manhat
                    manhat_dist = abs(end[0] - new[0]) + abs(end[1] - new[1])
                    priority = new_cost + manhat_dist
                    heapq.heappush(heap, (priority, (row, col)))
                    visited[(row, col)] = True
                    parent[(row, col)] = current_cell

        # Reconstruct the path
        path = []
        cell = end
        while cell != start:
            path.append(cell)
            cell = parent[cell]
        path.append(start)

        # Reverse the path
        path = path[::-1]

        return(path)

    #enemies is a list of human players, or team A

    def ai_turn(self):
        enemies_inrange = self.get_attack_range()
        action = ""
        #calculate attack heur based on each move vs each enemy, choose the max heur out of all moves
        specials = character_special_moves[self.name]
        attack_options = []
        for enemy in enemies_inrange:
            distance = abs(self.x - enemy.x) + abs(self.y - enemy.y)
            for move in specials:
                attack_damage = special_moves[move]["damage"]
                attack_cooldown = special_moves[move]["cooldown"]
                attack_range = special_moves[move]["range"]               
                #check if a special move is on cooldown
                #print(move)
                #print(attack_cooldown)
                
                #print(f"{self.turnsSinceAttack[move]} == {attack_cooldown}")
                if self.turnsSinceAttack[move] == attack_cooldown:                                                                       
                    heuristic = 0                               
                    heuristic += ((self.attack / 999) - (enemy.attack / 999))                  
                    heuristic += ((self.m_attack / 999) - (enemy.m_attack / 999))                    
                    heuristic += ((self.defense / 999) - (enemy.defense/ 999))                     
                    heuristic += ((self.m_defense / 999) - (enemy.m_defense / 999))                    
                    heuristic += ((self.luck / 999) - (enemy.luck / 999))                    
                    heuristic += ((self.dex / 999) - (enemy.dex / 999))
                    #HIGHER means better head to head in stats
                    #heuristic /= self.level                 
                    heuristic *= 100
                    if heuristic < 0:
                        heuristic = 0
                    #print(f"Stat h2h: {heuristic}")
                    #if winning head to head, double heuristic
                    if heuristic > 0:
                        heuristic *= 1.25
                        #print(f"Winning Stat h2h: {heuristic}")
                    # if your hp ratio is more than enemy hp ratio
                    #print(f"{self.current_hp} divide {self.max_hp}")
                    if enemy.current_hp < enemy.max_hp:

                        heuristic += ((self.current_hp / self.max_hp) - (enemy.current_hp / enemy.max_hp))
                        #print(f"AI hp ratio vs Enemy hp: {heuristic}")
                        # if enemy low on hp, higher weight

                        heuristic *= (enemy.current_hp / enemy.max_hp) * 2                              
                        #print(f"Enemy hp ratio: {heuristic}")

                    # if enemy is further and has lower hp, higher weight
                    heuristic += ((1 /distance) * (1 / (self.current_hp / enemy.current_hp))) 
                    #print(f"Enemy closeness and hp ratio: {heuristic}")

                    if special_moves[move]["type"] == "physical":
                        damage_ratio = ((self.attack + attack_damage) - enemy.defense)                      
                        #if move can kill
                        #print(damage_ratio)
                        #print(enemy.current_hp)
                        if (damage_ratio > enemy.current_hp):
                            heuristic *= (damage_ratio / 10)
                            #print(f"Kill Damage: {heuristic}")
                        elif damage_ratio < 0:
                            heuristic += 0
                        else:
                            heuristic += damage_ratio 
                            #print(f"Damage: {heuristic}")
                    elif special_moves[move]["type"] == "magic":
                        damage_ratio =  ((self.m_attack + attack_damage) - enemy.m_defense)
                        #print(damage_ratio)
                        #print(enemy.current_hp)
                        #print("yooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
                        if (damage_ratio > enemy.current_hp):
                            heuristic *= (damage_ratio / 10)
                            #print(f"Kill Damage: {heuristic}")
                        elif damage_ratio < 0:
                            heuristic += 0
                        else:
                            heuristic += damage_ratio 
                            #print(f"Damage: {heuristic}")
                    
                    hit_rate = self.dex + special_moves[move]["base_hit_rate"]
                    heuristic += (hit_rate - enemy.dex) * 2
                    #print(f"Hit Rate: {heuristic}")
                    heuristic += attack_damage * 1.5 / self.level
                    #print(f"attack damage: {heuristic}")
                    # If the attack has a long cooldown, increase the heuristic value
                    if attack_cooldown > 1:
                        heuristic *= 1.05      
                        #print(f"Cooldown, longer is better: {heuristic}")
                    # If the enemy is out of range, decrease the heuristic value                 
                    

                    # target glass cannons based on current move type
                    # ex) attack = 500, defense 100, heur = 5
                    if enemy.attack / enemy.defense > 1:
                        heuristic += (enemy.attack / enemy.defense) * 2
                        #print(f"glass cannon attack: {heuristic}")
                    if enemy.m_attack / enemy.m_defense > 1:
                        heuristic += (enemy.m_attack / enemy.m_defense) * 2
                        #print(f"glass cannon m_attack: {heuristic}")
                    if self.element in elements[enemy.element]:
                        # Attack element is strong against enemy element
                       heuristic *= 1.5
                       #print(f"element effective: {heuristic}")
                    elif enemy.element in elements[self.element]:
                        # Attack element is weak against enemy element
                       heuristic *= 0.75
                       #print(f"element NOT effective: {heuristic}")
                    
                    for buff in enemy.buffs:
                        if buff == "poison":
                            heuristic *= 1.25
                        elif buff == "weak":
                            heuristic *= 1.3    

                    if special_moves[move]["buff"] != "none":
                        if buff_list[special_moves[move]["buff"]].affect_hp < 0:
                            heuristic *= 1.5
                            #print(f"apply effect WITH damage: {heuristic}")
                        else:  
                            heuristic *= 1.25
                            #print(f"apply effect NO damage: {heuristic}")  

                    if distance > attack_range:
                        heuristic *= 0
                        #print(f"out of range: {heuristic}")        

                    heuristic /= 1
                    s_tuple = (enemy.name, move, heuristic)
                    attack_options.append(s_tuple)
             
        #attack heur needss randomness, sort it, split it, pick from split batch
        print(attack_options)

        #MOVEMENT 
        possible_moves = self.get_possible_move_tiles(players)
        best_tile = None
        move_options = []
        #start will always be self.x and self.y
        start = (self.x, self.y)               
        # check the end position of all enemies, and approach their 2nd to last position
        for enemy in players:              
            if enemy.team != self.team:
                #print(moves)
                distance = abs(start[0] - enemy.x) + abs(start[1] - enemy.y)
                end = (enemy.x, enemy.y)
                path = self.astar(start, end) 
                heuristic_value = 0
                #print(path[-2])               
                best_list = []      
                for move in possible_moves:
                    #print(f"Possible Moves: {move} == {path[-2]}")                  
                    diff = abs(path[-2][0] - move[0]) + abs(path[-2][1] - move[1])
                    best_list.append((diff, move))
                    
                    #will cause a dupe with 0 heur if condition is met
                    if move == path[-2]:                                                         
                        m_tuple = (enemy.name, move, heuristic_value)
                        move_options.append(m_tuple)
                
                best_list.sort()
                rand_best_list = []
                rand_best_list.append(best_list[0])
                #rand_best_list.append(best_list[1])
                #rand_best_list.append(best_list[2])
                print(f"{enemy.name}")
                random_option = random.choice(rand_best_list)
                #print(random_option[0])
                print(random_option)
                health_ratio = enemy.current_hp / enemy.max_hp
                heuristic_value = 0
                heuristic_value += health_ratio * 2
                #print(heuristic_value)
                #print(heuristic_value * 0.75)

                if enemy.attack / enemy.defense > 1:
                    heuristic_value *= 1.05
                    #print(f"glass cannon attack: {heuristic_value}")
                if enemy.m_attack / enemy.m_defense > 1:
                    heuristic_value *= 1.05
                    #print(f"glass cannon m_attack: {heuristic_value}")

                if self.element in elements[enemy.element]:
                    # Attack element is strong against enemy element
                    heuristic_value *= 1.05
                    #print(f"element effective: {heuristic}")
                elif enemy.element in elements[self.element]:
                    # Attack element is weak against enemy element
                    heuristic_value *= 0.75
                    #print(f"element NOT effective: {heuristic}")
                    
                for buff in enemy.buffs:
                    if buff == "poison":
                        heuristic_value *= 1.05
                    elif buff == "weak":
                        heuristic_value *= 1.03  
                
                m_tuple = (enemy.name, random_option[1], heuristic_value)
                move_options.append(m_tuple)             
                #print(best_list)   

                #print(enemy.name)
                #print(heuristic_value)
        print("MOVE OPTIONS")      
        print(move_options)
        #buff
        

        char_buffs = character_buff_moves[self.name]
        buff_options = []  # Initialize the dictionary outside of the loop
        for player in players:           
            if self.team == player.team:
                for buff_string in char_buffs:
                    buff_heur = 0
                    
                    if self.turnsSinceAttack[buff_string] == buff_list[buff_string].cooldown:
                        distance = abs(self.x - player.x) + abs(self.y - player.y)
                        if distance <= buff_list[buff_string].range:
                            if buff_list[buff_string].type == "flat":
                                #print(f"{buff_string} is {buff_list[buff_string].type} ")
                                buff_heur += 0.1

                                attack_buff_int = buff_list[buff_string].attack_buff
                                m_attack_buff_int = buff_list[buff_string].m_attack_buff
                                defense_buff_int = buff_list[buff_string].defense_buff
                                m_defense_buff_int = buff_list[buff_string].m_defense_buff
                                luck_buff_int = buff_list[buff_string].luck_buff
                                dex_buff_int = buff_list[buff_string].dex_buff

                                if attack_buff_int > 0:
                                    buff_heur += attack_buff_int / 10
                                elif m_attack_buff_int > 0:
                                    buff_heur += m_attack_buff_int / 10
                                elif defense_buff_int > 0:
                                    buff_heur += defense_buff_int / 10
                                elif m_defense_buff_int > 0:
                                    buff_heur += m_defense_buff_int / 10
                                elif luck_buff_int > 0:
                                    buff_heur += luck_buff_int / 10
                                elif dex_buff_int > 0:
                                    buff_heur += dex_buff_int / 10 

                            elif buff_list[buff_string].type == "percent":
                                #print(f"{buff_string} is {buff_list[buff_string].type} ")
                                buff_heur += 0.12

                                attack_buff_int = int(buff_list[buff_string].attack_buff.replace('%', ''))
                                m_attack_buff_int = int(buff_list[buff_string].m_attack_buff.replace('%', ''))
                                defense_buff_int = int(buff_list[buff_string].defense_buff.replace('%', ''))
                                m_defense_buff_int = int(buff_list[buff_string].m_defense_buff.replace('%', ''))
                                luck_buff_int = int(buff_list[buff_string].luck_buff.replace('%', ''))
                                dex_buff_int = int(buff_list[buff_string].dex_buff.replace('%', ''))
                        
                                if attack_buff_int > 100:
                                    buff_heur += attack_buff_int / 100
                                elif m_attack_buff_int > 100:
                                    buff_heur += m_attack_buff_int / 100
                                elif defense_buff_int > 100:
                                    buff_heur += defense_buff_int / 100 
                                elif m_defense_buff_int > 100:
                                    buff_heur += m_defense_buff_int / 100 
                                elif luck_buff_int > 100:
                                    buff_heur += luck_buff_int / 100 
                                elif dex_buff_int > 100:
                                    buff_heur += dex_buff_int / 100 
                    
                            buff_heur *= 2
                            b_tuple = (player.name, buff_string, buff_heur)
                            buff_options.append(b_tuple)    
                    
        #print(buff_options)
        print("--------------------------------------------------------------------")
        #combine all option lists into one and sort it, split it, and pick randomly
        all = attack_options + move_options + buff_options
        all.sort(key=lambda x: x[2], reverse=True)
        #print(all)
        #keep top percentage of all
        num_elements = (len(all)//2)
        split_all = all[:num_elements]
        print("--------------------------------------------------------------------")
        print(split_all)
        ran = []
        ran.append(all[0])
        #ran.append(all[1])

        random_option = random.choice(ran)
        print("Option: " + str(random_option))
        #print(type(random_option[1])) 
        #print(random_option[1])
        for move in special_moves:
            if move == random_option[1]:
                action = "1"   
        
        if type(random_option[1]) == tuple:
            action = "2"
            
        for buff in buff_list:
            if buff == random_option[1]:
                action = "4"  
                
        print("Action: " + action)

        if action == "1":            
            self.attack_enemy(player_dict[random_option[0]], self.name, special_moves[random_option[1]], random_option[1], self.element)
        elif action == "2":
            coord = random_option[1] 
            new_x = coord[0] + 1
            new_y = coord[1] + 1
            print(f"Human Coords: ({new_x}, {new_y})")
            board[self.x][self.y] = '[  ]'
            self.move(new_x, new_y)
            board[new_x-1][new_y-1] = '[' + self.id + ']'

            #update board
            for rank in board:
                print(' '.join(rank))
            print("-------------------------------------------")

        elif action == "4":
            #target.apply_buff(target, move)

            self.apply_buff(player_dict[random_option[0]], random_option[1])

    # can be used for ai as well
    def get_attack_range(self):
        # Find all players within attack range of the current player
        attackable_players = []
        for player in players:
            if player.name != self.name:
                if player.team != self.team:
                    specials = character_special_moves[self.name]
                    temp = []
                    for move in specials:
                       temp.append(special_moves[move]["range"])
                    if abs(player.x - self.x) + abs(player.y - self.y) - self.movement <= max(temp):
                        #print(player.name)
                        attackable_players.append(player)
        return attackable_players

    def get_possible_move_tiles(self, players):
        # Initialize the list of possible move tiles
        move_tiles = []
        overlap = False
        # Iterate through all tiles within the player's movement range
        for i in range(-self.movement, self.movement + 1):
            for j in range(-self.movement, self.movement + 1):
                # Calculate the new x and y coordinates if the player moved to this tile
                new_x = self.x + i
                new_y = self.y + j               
                distance = abs(new_x - (self.x)) + abs(new_y - (self.y))        
                print(f"{player.x} And {player.y}")
                if new_x == player.x and new_y == player.y:
                    if new_x != self.x and new_y != self.y: 
                        overlap = True                
                # Check if the new coordinates are within the boundaries of the grid and if the tile is unoccupied by another player
                if (distance <= self.movement and overlap == False and 0 <= new_x < 10) and (0 <= new_y < 5) and not any(p.x == new_x and p.y == new_y for p in players):
                    # Add the new coordinates as a tuple to the list of possible move tiles
                    #print(f"Player: {distance} <= {self.movement}")
                    move_tiles.append((new_x, new_y))
                    print(f"NEW COORDS: ({new_x}, {new_y})")
                    print(f"NEW HUMAN COORDS: ({new_x + 1}, {new_y + 1})")
        return move_tiles

    

# board is represented as a list of lists of strings
# each string represents a square on the board
# 10 x 5
board = [
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]'],
    ['[  ]', '[  ]', '[  ]', '[  ]', '[  ]']
]
num_rows = len(board)
#print(num_rows)  # Outputs: 10

num_columns = len(board[0])
#print(num_columns)  # Outputs: 5

#havent made classes as in warrior, mage, assassin
                                                                              #add 1 to x/y for human coords
#                  name         id   hp     a   ma  d   md  s   l   dx  el         x   y  mov ap lvl team
players = [Player("Gallahyde", "A0", 500,   30, 12, 25, 9,  5,  3,  3, "cursed",   0,  0, 3,  2, 100,  "Team A"), 
           Player("Asyll",     "A1", 330,   32, 10, 19, 3,  4,  2,  3, "dark" ,    0,  1, 2,  2, 100,  "Team A"), 
           Player("Luce",      "A2", 300,   15, 29, 7,  4,  3,  2,  2, "blessed",  0,  2, 4,  2, 100,  "Team A"),
           Player("Shin",      "A3", 220,   14, 10, 10, 4,  6,  2,  2, "earth",    0,  3, 5,  2, 100,  "Team A"),
           Player("Seraphim",  "A4", 290,   18, 34, 8,  13, 2,  2,  2, "water",    0,  4, 2,  2, 100,  "Team A"),
           Player("Polne",     "B5", 210,   18, 11, 6,  4,  7,  2,  2, "fire",     9,  0, 3,  2, 100,  "Team B"),
           Player("Ultomos",   "B6", 210,   19, 10, 10, 3,  1,  2,  2, "earth",    9,  1, 4,  2, 100,  "Team B"),
           Player("Atamus",    "B7", 330,   30, 6,  9,  4,  5,  2,  2, "dark",     9,  2, 3,  2, 100,  "Team B"),
           Player("Etriv",     "B8", 290,   12, 16, 8,  8,  7,  2,  2, "water",    9,  3, 2,  2, 100,  "Team B"),
           Player("Omios",     "B9", 405,   20, 14, 11, 9,  2,  2,  2, "light"  ,  9,  4, 4,  2, 100,  "Team B")]

player_dict = {}
for player in players:
    player_dict[player.name] = player

def check_gameover(players):
    # Check if each team has been wiped out
    team_a_wiped_out = has_been_wiped_out(team_a_players)
    team_b_wiped_out = has_been_wiped_out(team_b_players)

    # Determine the winner based on which team has been wiped out
    if team_a_wiped_out:
        print("winner is Team B")
        return True
    elif team_b_wiped_out:
        print("winner is Team A")
        return True
    else: 
    # Otherwise, the game is not over
        return False

def has_been_wiped_out(players):
    # Iterate through the players in the team
    for player in players:
        print(f"{player.name} HP: {player.current_hp}")
        # If any player has a current hit point value greater than 0, the team has not been wiped out
        if player.current_hp > 0:
            return False
    # If none of the players have a current hit point value greater than 0, the team has been wiped out
    return True


# Original Player Lineup W/O SPEED
players_org = players
#temp copy
players_temp = players

players_id = players
players_id.sort(key=lambda x: x.id)


# Create an empty dictionary to store the lists
teams = {}

# Iterate through the players list
for player in players_temp:
    # Get the player's team
    team = player.team
    # If the team is not in the dictionary yet, create a new empty list for it
    if team not in teams:
        teams[team] = []
    # Add the player to the appropriate list
    teams[team].append(player)

team_a_players = teams["Team A"]
team_b_players = teams["Team B"]

for team, players_temp in teams.items():
    print(f"Team: {team}")
    print("Players:")
    for player in players_temp:
        print(f"  {player.name}")

# place each player on the board
for player in players:
    board[player.x][player.y] = '[' + player.id + ']' 

# sort the players by speed
players.sort(key=lambda x: x.speed, reverse=True)

#turnorder
print("Turn Order: ")
order = 1
for player in players:
    print(f"{order}) {player.name}" )
    order += 1

for player in players:
    print(f"{player.name} INITIALIZED TSA" )
    player.intialize_TSA()    
    player.intialize_TSA_buff()
    player.set_level()

# create a flag to track if the game is over
game_over = False
turn_counter = 0
movement_limit = 1
global_turn = 0
# start the game loop
while not game_over:
  # print the board
    for rank in board:
      print(' '.join(rank))
    print("-------------------------------------------")
    # loop through each player in turn
    for player in players:  
        
        curr_movement = 0
        print(player.name + "'s status: ")
        player.check_dot()
        for buff in player.buffs:
            #print(buff_list[buff.name].duration)
            player.remove_buff()
            print(buff.name + ", " + str(buff.duration))
        
            #player.get_attack_range()     
            
        # check if the player is still alive        
        if player.current_hp > 0:
            print("Player HP: " + str(player.current_hp))
            # prompt the player for their action
            print("Coordinates: " + str(player.x + 1) + ', ' + str(player.y + 1))   

            #print(f"THIS PLAYER WAS CHOSEN BY TURN ORDER: {player.speed}")
            if player.team == "Team A" or player.team == "Team B":
                for turn_counter in range(player.ap):     
                    print("Coordinates: " + str(player.x + 1) + ', ' + str(player.y + 1))   
                    print(f"THE AI, {player.name}, IS CHOOSING ITS MOVE")
                    #time.sleep(0.01)
                    player.ai_turn()

                    turn_counter += 1
                    print(turn_counter)
                    
                    #update board
                    for rank in board:
                        print(' '.join(rank))
                    print("-------------------------------------------")
                    game_over = check_gameover(players)
                    if game_over is True:
                        print(f"Global Turn: {global_turn}")
                        sys.exit()
                        break
            else:
                for turn_counter in range(player.ap):               
                    while True:
                        try:
                            for buff in player.buffs:
                                #print(buff_list[buff.name].duration)
                                print(buff.name + ", " + str(buff.duration))
                            print("-------------------------------------------")
                            print("1) : attack")
                            print("2) : move")
                            print("3) : heal")
                            print("4) : buff")
                            print("5) : none")
                            print("-------------------------------------------")
                        
                                           
                            print(turn_counter)

                            action = input(f"{player.id}: {player.name}, what action?TurnCount={turn_counter}: ")
                            print("-------------------------------------------")

                            if action in player.actions:
                                action_method = player.actions[action]
                                break
                            else:
                                print("Invalid action. Please choose a valid action.")
                        except ValueError:
                            print("Invalid input. Please enter a valid action.")

                    if action_method:
                    # perform the chosen action
                      if action == "1":
                          while True:
                            try:
                                  #btw players can target themselves.
                                  for x in players_id:
                                      if x.name != player.name:
                                        print(x.id + ": " + x.name)
                                  
                                  target = input("Which enemy number do you want to attack?")      
                                  print("-------------------------------------------")
                                  target_int = int(target)
                          
                                  if 1 <= target_int <= len(players):
                                      enemy = players_id[target_int - 1]
                                      print(f"Player HP: {player.current_hp} vs Enemy HP: {enemy.current_hp}")
                                      print(player.team + ": " + player.name + " vs " + enemy.team + ": " + enemy.name)
                                      break
                                  else:
                                      print("invalid number")
                            except ValueError:
                                print("invalid, not a number, try again")

                          if enemy.team != player.team: 
                              if enemy.current_hp <= 0:
                                  print("invalid target")
                                  break

                              if player.name in character_special_moves:
                                  specials = character_special_moves[player.name]
                                  print(f"Moves: {', '.join(specials)}")
                                  print("-------------------------------------------")

                              while True:
                                #check if attack in range
                                #move_temp is the string name of move
                                move_temp = input("What move do you want to do?(No buffs or heals)")
                                if move_temp in character_special_moves[player.name]:
                                    # this is bugged
                                    

                                    if player.turnsSinceAttack[move_temp] < special_moves[move_temp]["cooldown"]:
                                        cooldown_remain = special_moves[move_temp]["cooldown"] - player.turnsSinceAttack[move_temp]
                                        print(f"{move_temp} is on cooldown for {cooldown_remain} global turns.")
                                    else:
                                        move = special_moves[move_temp]
                                        break                             
                                else: 
                                    print(player.name, "does not have access to the", move_temp, "move")

                              print("-------------------------------------------")
                              player.attack_enemy(enemy, player.name, move, move_temp, player.element)

                          else:
                              print("same team target")
                          print("-------------------------------------------")

                          print("Enemy: " + enemy.name + " | HP: " + str(enemy.current_hp))
                          if enemy.current_hp <= 0:
                              #del players[target_int - 1]
                              board[enemy.x][enemy.y] = '[  ]' 
                              print(f"{enemy.name} fainted!")
                              game_over = check_gameover(players)
                              if game_over is True:
                                  break
                          #update board
                          for rank in board:
                              print(' '.join(rank))
                          print("-------------------------------------------")
                          turn_counter += 1
                  
                      elif action == "2":
                          #movement limit check
                          if curr_movement != movement_limit:
                              while True:
                                  try:
                                      new_x = int(input("Enter new x coordinate: "))
                                      new_y = int(input("Enter new y coordinate: "))
                                      break
                                  except ValueError:
                                      print("not an int")
                  
                              #remove old pos
                              board[player.x][player.y] = '[  ]' 
                              action_method(new_x, new_y)
                              board[player.x][player.y] = '[' + player.id + ']' 
                              print("New Coordinates: " + str(player.x + 1) + ', ' + str(player.y + 1) )
                              #increment movement, only once per turn
                              curr_movement += 1
                              #update board
                              for rank in board:
                                  print(' '.join(rank))
                              print("-------------------------------------------")
                              #print("Increment turn_counter for action points")
                              turn_counter += 1
                          else:
                              #wish i used a switch case or something
                              print("You have already moved this turn")
                      elif action == "3":
                          player.heal()
                      elif action == "5":
                          player.none()
                      elif action == "4":
                          while True:
                                try:      
                                    if player.name in character_special_moves:
                                      specials = character_buff_moves[player.name]
                                      print(f"Moves: {', '.join(specials)}")
                                      print("-------------------------------------------")
                                    #ask for move                               
                                    while True:
                                        move = input("What move do you want to do?(No attacks)")
                                        #check if player has access to move
                                        if move in character_buff_moves[player.name]:
                                            #ask for target
                                            #print(player.turnsSinceAttack[move])
                                            #print("<")
                                            #print(buff_list[move].cooldown)
                                            
                                            if player.turnsSinceAttack[move] < buff_list[move].cooldown:
                                                cooldown_remain = buff_list[move].cooldown - player.turnsSinceAttack[move]
                                                print(f"{move} is on cooldown for {cooldown_remain} global turns.")
                                            else:

                                                for x in players_id:
                                                    if x.team == player.team:
                                                        print(x.id + ": " + x.name)
                                                target_int = int(input("Which ally number do you want to target?")) 
                                                print("-------------------------------------------")
                                            
                                                #check if target is OOB of player list
                                                if 1 <= target_int <= len(players):
                                                    #assign target as player based on players_id list
                                                    target = players_id[target_int - 1]
                                                    if target.team == player.team:
                                                        distance = abs(player.x - target.x) + abs(player.y - target.y)
                                                        if distance <= buff_list[move].range:
                                                            #apply buff
                                                            player.apply_buff(target, move)
                                                            print("-------------------------------------------")
                                                            break
                                                        else:
                                                          print("buff out of range")
                                                    else:
                                                        print("Target is not on your team.")

                                        else: 
                                            print(player.name, "does not have access to the", move, "move")
                                                                                               
                                    else:
                                      print("invalid buff")                               
                                    break
                                except ValueError:
                                    print("Invalid move or target")
                      else:
                          print("Invalid action. Choose either 'attack' or 'heal'.")
        else: 
            print(f"{player.name} fainted!")
                  
    print("Global Turn: " + str(global_turn))
    global_turn += 1
    for player in players_id:
        #print(player.name + ": ")
        #create new buff object becuz of previous bug with shared durations
        for i in range(len(player.buffs)):
            buff = player.buffs[i]
            new_duration = buff.duration
            new_buff = Buff(buff.name, duration=new_duration, cooldown=buff.cooldown, range=buff.range, type=buff.type, affect_hp=buff.affect_hp)
            player.buffs[i] = new_buff           
        for buff in player.buffs:
            #print(buff.name)
            #print("")
            #print(buff_list[buff.name].duration)
            buff.duration -= 1
            #print("Buff: " + buff.name + " " + str(buff.duration))
            #print(f"HEY: {player.buffs[0].duration}")
            if buff.duration <= 0:
                player.buffs.remove(buff)
            
        #for move in player.turnsSinceAttack:
            #print(move)
            #print(player.turnsSinceAttack[move])
        for move in player.turnsSinceAttack:
            if move not in buff_list:
                if player.turnsSinceAttack[move] != special_moves[move]["cooldown"]:
                    player.turnsSinceAttack[move] += 1
            if move not in special_moves:
                if player.turnsSinceAttack[move] != buff_list[move].cooldown:
                    player.turnsSinceAttack[move] += 1
            #print(player.turnsSinceAttack[move])
    # check if the game is over
    game_over = check_gameover(players)