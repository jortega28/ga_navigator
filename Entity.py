import pygame.image
import random

class Entity:
    # An entity will be any drawable object on the GUI
    # An entity is defined as a drawable PNG with coordinates

    def __init__(self, name, img_file, start_pos):
        self.name = name
        self.img_file = img_file
        self.start_pos = start_pos
        self.current_pos = start_pos
        self.image = pygame.image.load(img_file)
        self.size = [self.image.get_width(), self.image.get_height()]

    def get_image(self):
        return self.image

    def set_image(self, img_name):
        self.img_file = img_name
        self.image = pygame.image.load(img_name)

    def get_pos(self):
        return self.current_pos[0], self.current_pos[1]

    def get_start_pos(self):
        return self.start_pos[0], self.start_pos[1]

    def get_name(self):
        return self.name

    def get_interaction_zone(self):
        # For calculating interactions between entities
        interaction = [self.start_pos[0], self.start_pos[0] + self.size[0]], [self.start_pos[1], self.start_pos[1] + self.size[1]]
        return interaction

class Barrier(Entity):
    # A barrier inherits from Entity
    # A barrier is defined the same as an entity but is able to kill other entities
    pass

    def __init__(self, name, img_file, start_pos, killer):
        self.name = name
        self.img_file = img_file
        self.start_pos = start_pos
        self.current_pos = start_pos
        self.killer = killer
        self.image = pygame.image.load(img_file)
        self.size = [self.image.get_width(), self.image.get_height()]

    def set_kill(self, killer):
        # Accept boolean to decide if this barrier can kill
        self.killer = killer

    def is_killer(self):
        if self.killer is True:
            return True
        else:
            return False

    def get_killzone(self):
        # Killzone/killarea is the same as the starting position x + 25 and y + 25
        # If killer is false then coordinates outside the display will be provided
        if self.killer is True:
            killzone = [self.start_pos[0], self.start_pos[0] + self.size[0]], [self.start_pos[1], self.start_pos[1] + self.size[1]]
            return killzone
        else:
            return [[-1, -1], [-1, -1]]

    def get_barrier(self):
        # Same as killzone size but will always return a range ([x1 -> x2], [y1 -> y2])
        return [self.start_pos[0], self.start_pos[0] + self.size[0]], [self.start_pos[1], self.start_pos[1] + self.size[1]]

class Player(Entity):
    # Player inherits from entity
    # Unlike an entity a Player object will have a non-static position
    # It will also have memory and other variables for the genetic algorithm
    pass

    def __init__(self, name, img_file, start_pos, goal):
        self.name = name
        self.img_file = img_file
        self.start_pos = start_pos
        self.goal = goal
        self.goal_reached = False
        self.fitness = 0
        self.genetics = []
        self.tendency_right = 10
        self.tendency_left = 10
        self.tendency_up = 10
        self.tendency_down = 10
        self.mutation_chance = 20000  # 1 out of this number * size of genes
        self.pop_mutation_chance = 50  # 1 out of this number
        self.tendency_mutation_chance = 50  # 1 out of this number
        self.tendency_mutation_severity = 1  # How much should be added/removed from tendencies during mutation
        self.pop_severity = 2   # Percent of tail that will be popped
        self.mutation_severity = .5  # This is a multiplier, 2 = x2 severity, .5 = 1/2 severity (best to keep this under 1 maybe 1.25 max)
        self.current_gene = 0
        self.memory = []
        self.image = pygame.image.load(img_file)
        self.size = [self.image.get_width(), self.image.get_height()]
        self.current_pos = start_pos
        self.hitbox = [self.current_pos[0], self.current_pos[0] + self.size[0]], [self.current_pos[1], self.current_pos[1] + self.size[1]]
        self.dead = False

    def is_dead(self):
        return self.dead

    def kill(self, goal_reached):
        # Kill player but make note of whether or not he was killed due to reaching the goal
        if goal_reached:
            self.goal_reached = goal_reached
        self.dead = True
        self.set_image("textures/player_dead.png")
        return self.dead

    def set_hitbox(self, x, y):
        self.hitbox = [[x, x + self.size[0]], [y, y + self.size[1]]]

    def get_hitbox(self):
        return self.hitbox

    def update_pos(self, x, y):
        # Move Player to completely different position on screen
        self.current_pos = [x, y]
        self.set_hitbox(x, y)

    def move(self, x, y):
        # Move Player a certain amount
        self.current_pos = [self.current_pos[0] + x, self.current_pos[1] + y]
        self.set_hitbox(self.current_pos[0] + x, self.current_pos[1] + y)
        self.add_memory(x, y)

    def get_memory(self):
        return self.memory

    def get_memory_size(self):
        return len(self.memory)

    def set_memory(self, new_memory):
        self.memory = new_memory

    def add_memory(self, x, y):
        self.memory.append((x, y))

    def has_genetics(self):
        if self.genetics is None:
            return False
        else:
            return True

    def set_genetics(self, genes):
        # Moves/genetics from parent
        self.genetics = genes

    def get_genetics(self):
        return self.genetics

    def next_gene(self):
        # Get next gene in sequence
        nextg = (0, 0)
        if self.current_gene < len(self.genetics):
            nextg = self.genetics[self.current_gene]
            self.current_gene += 1
        return nextg

    def get_tendency_severity(self):
        return self.get_tendency_severity()

    def set_all_tendencies(self, tendencies):
        tleft, tdown, tright, tup = tendencies
        self.tendency_left, self.tendency_down, self.tendency_right, self.tendency_up = tleft, tdown, tright, tup

    def get_all_tendencies(self):
        return self.tendency_left, self.tendency_down, self.tendency_right, self.tendency_up

    def crossover_tendencies(self, tendencies):
        # Crossover tendencies from another parent
        mate_tendencies = list(tendencies)
        my_tendencies = list((self.tendency_left, self.tendency_down, self.tendency_right, self.tendency_up))
        r = random.randint(0, len(my_tendencies)-1)
        my_crossa = my_tendencies[:r]
        partner_crossb = mate_tendencies[r:]
        offspring_tendencies = tuple(my_crossa + partner_crossb)
        return offspring_tendencies

    def mutate(self, genes):
        # Lottery number for mutation
        m = random.randint(0, self.mutation_chance)
        gene_size = len(genes)
        i = 0
        mutation_occurs = False
        # If gene pool is < 10 no mutation will occur
        while i < gene_size and gene_size > 10:
            r = random.randint(0, self.mutation_chance)
            if r == m:
                mutation_occurs = True
                i = gene_size
            else:
                i += 1

        if mutation_occurs and gene_size > 10:
            # Start gene mutation
            mutation_point = random.randint(0, gene_size)
            mutation_size = random.randint(0, gene_size)
            # Calculate mutation severity
            mutation_size = mutation_size*self.mutation_severity
            left = mutation_point-(mutation_size/2)
            left = round(left)
            if left < 0:
                left = 0
            right = mutation_point+(mutation_size/2)
            right = round(right)
            if right > gene_size:
                right = gene_size-1

            # Now the mutation will be performed
            while left < right:
                xc, yc = 0, 0
                tleft, tdown, tright, tup = self.get_all_tendencies()
                tendency_sum = sum(self.get_all_tendencies())
                sleft = tleft
                sdown = tleft + tdown
                sright = tleft + tdown + tright
                sup = tendency_sum
                r = random.randint(1, tendency_sum)
                if 0 < r <= sleft:
                    # left
                    xc = -5
                elif sleft < r <= sdown:
                    # Down
                    yc = 5
                elif sdown < r <= sright:
                    # Right
                    xc = 5
                elif sright < r <= sup:
                    # Up
                    yc = -5
                genes[left] = (xc, yc)
                left += 1
            # Append touple to indicate mutation
            genes.append((10, 10))

        # Pop mutation chance
        pop_mutation_occurs = False
        if not mutation_occurs:
            pm = random.randint(0, self.pop_mutation_chance)
            r = random.randint(0, self.pop_mutation_chance)
            if pm == r:
                # Pop mutation occurs
                pop_mutation_occurs = True
                pop_amount = round(gene_size*(self.pop_severity/100))
                i = 0
                new_genes = genes[:(gene_size-pop_amount)]
                genes = new_genes
                genes.append((11, 11))

        # Tendency Mutation
        if not mutation_occurs and not pop_mutation_occurs:
            tm = random.randint(0, self.tendency_mutation_chance)
            r = random.randint(0, self.tendency_mutation_chance)
            if tm == r:
                # Tendency mutation occurs
                r = random.randint(1, 4)
                tleft, tdown, tright, tup = self.tendency_left, self.tendency_down, self.tendency_right, self.tendency_up
                if r == 1:
                    r = random.randint(1, 2)
                    if r == 2 or tleft <= self.tendency_mutation_severity:
                        tleft += self.tendency_mutation_severity
                    else:
                        tleft -= self.tendency_mutation_severity
                elif r == 2:
                    r = random.randint(1, 2)
                    if r == 2 or tright <= self.tendency_mutation_severity:
                        tright += self.tendency_mutation_severity
                    else:
                        tright -= self.tendency_mutation_severity
                elif r == 3:
                    r = random.randint(1, 2)
                    if r == 2 or tup <= self.tendency_mutation_severity:
                        tup += self.tendency_mutation_severity
                    else:
                        tup -= self.tendency_mutation_severity
                elif r == 4:
                    r = random.randint(1, 2)
                    if r == 2 or tdown <= self.tendency_mutation_severity:
                        tdown += self.tendency_mutation_severity
                    else:
                        tdown -= self.tendency_mutation_severity
                genes.append((tleft, tdown, tright, tup))
                genes.append((12, 12))

        return genes

    def get_fitness(self):
        self.fitness = self.calculate_fitness()
        return self.fitness

    def calculate_fitness(self):
        total = 0
        currentx, currenty = self.get_pos()
        goalx, goaly = self.goal[0], self.goal[1]
        for x, y in self.memory:
            xdiff = goalx-currentx
            ydiff = goaly-currenty
            newx = goalx-(currentx+x)
            newy = goaly-(currenty+y)
            newx, xdiff, newy, ydiff = abs(newx), abs(xdiff), abs(newy), abs(ydiff)
            if newx < xdiff:
                # +10 to fitness for good move
                total += 10
            elif newx > xdiff:
                # -10 to fitness for bad move
                total -= 10
            if newy < ydiff:
                # +10 to fitness for good move
                total += 10
            elif newy > ydiff:
                # -10 to fitness for bad move
                total -= 10
        # Reward for low move count on reaching the goal, minimum earned regardless of moves is 1000
        if self.goal_reached:
            # Every additional move nets you -10 reward
            reward = 20000-((self.get_memory_size()-200)*10)
            if reward < 1000:
                reward = 1000
            total += reward

        # Distance reward (how far from goal was the player if he died before reaching it)
        # Additionally a move penalty
        if not self.goal_reached:
            xdiff = goalx - currentx
            ydiff = goaly - currenty
            xdiff, ydiff = abs(xdiff), abs(ydiff)
            dist = 800+600
            dist -= (xdiff+ydiff)
            total += dist
            # Move Penalty
            penalty = self.get_memory_size()*.25
            total -= penalty
        else:
            # If goal reached double player's total fitness
            total = total*2
        return total

    def crossover(self, partner):
        # Receive a player to breed with and select a random crossover point
        # The player passed into this method should have a longer or equal memory size
        # Only second half of genetics will be crossed over
        parter_moves = partner.get_memory()
        my_memory = self.get_memory()
        my_memory_size = self.get_memory_size()
        r = random.randint(0, (my_memory_size-1))
        # Subtract 1 to prevent repeating death
        r -= 1
        my_crossa = my_memory[:r]
        partner_crossb = parter_moves[r:]
        offspring_genetics = my_crossa + partner_crossb
        # Check to make sure this is not first generation
        # Run mutate on genes to check for possible mutation
        if self.has_genetics():
            offspring_genetics = self.mutate(offspring_genetics)
        return offspring_genetics
