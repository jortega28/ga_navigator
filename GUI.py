import pygame
import random
from threading import Thread
import Entity
import time

# Pygame inits
pygame.init()
size = width, height = 600, 800
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
gameDisplay = pygame.display.set_mode(size, pygame.DOUBLEBUF)
pygame.display.set_caption('Genetic Algorithm Navigator')
clock = pygame.time.Clock()

# Images
img_normal_player = "textures/player.png"
img_mutant_player = "textures/player_mutant.png"
img_dead_player = "textures/player_dead.png"
img_goal = "textures/goal.png"
img_spawn = "textures/spawn.png"
img_kill_barrier = "textures/kill_barrier.png"

# Level to load up
level = "levels/scatter_level.txt"

# Entity list excluding players
entities = []

# List of players and dead players
players = []
dead_players = []
threads = []
offsprings = []
spawnpoint = [0, 0]
goal = [0, 0]

# Genetic Algorithm Inits
generation = 1
generation_size = 50
generation_run_time = 100   # -1 for infinite
sim_speed_multiplier = 1000

# Wait time before each reset
reset_wait = 1
ready_to_start = False
wait_for_enter = True

# Stat keeping
total_players = generation_size
total_mutations = 0
pop_mutations = 0
tendency_mutations = 0
best_fitness = -1000000000000
best_fitness_occurrence = 0
best_fitness_memory = []
best_fitness_tendencies = (10, 10, 10, 10)
goals_reached = 0
goals_reached_per_gen = 0
start_time = time.time()
first_goal_reached = "never"
next_gen_start_time = time.time()


def get_elapsed_time():
    return time.time() - start_time


def load_level(level_name):
    x, y = 0, 0
    no_goal = True
    no_spawn = True
    level = open(level_name, "r")
    for line in level:
        for c in line:
            if c == "X":
                # Barrier
                b = Entity.Barrier("b" + "_" + str(x) + "_" + str(y), img_kill_barrier, [x, y], True)
                entities.append(b)
            elif c == "G" and no_goal:
                # Goal
                global goal
                g = Entity.Entity("Goal", img_goal, [x, y])
                entities.append(g)
                goal = [x, y]
            elif c == "O" and no_spawn:
                # Spawn
                global spawnpoint
                s = Entity.Entity("Spawn", img_spawn, [x, y])
                entities.append(s)
                spawnpoint = [x, y]
            x += 25
        y += 25
        x = 0


def update_player(player):
    # Update player list
    i = 0
    while i < len(players):
        if player.get_name() == players[i].get_name():
            players[i] = player
        i += 1


def draw_players():
    # Draw all players onto the screen
    for player in players:
        gameDisplay.blit(player.get_image(), player.get_pos())


def place_entities():
    # Place all entities on the screen
    for entity in entities:
        gameDisplay.blit(entity.get_image(), entity.get_pos())


def remove_entity(item):
    # Remove a specific entity
    for entity in entities:
        if entity.get_name() == item.get_name():
            entities.remove(entity)


def check_collision():
    # Used for global collision checking (this method is slow)
    global first_goal_reached
    # Check if that entity is a barrier that can kill
    # If so check for collision with all players
    for player in players:
        # If player is already dead then don't check collision
        if not player.is_dead():
            for entity in entities:
                if isinstance(entity, Entity.Barrier):
                    if entity.is_killer():
                        if check_intersect(player, entity):
                            # We have a kill
                            # Check player death again due to threading progression
                            if not player.is_dead():
                                player.kill(False)
                                dead_players.append(player)
                if isinstance(entity, Entity.Entity):
                    if entity.get_name() == "Goal":
                        if check_intersect(player, entity):
                            # Player reached goal
                            if first_goal_reached == "never":
                                first_goal_reached = generation
                            if not player.is_dead():
                                player.kill(True)
                                dead_players.append(player)


def check_self_collision(ai):
    # Used for individual player/thread collision checking
    global first_goal_reached
    for player in players:
        if player.get_name() == ai.get_name():
            for entity in entities:
                if isinstance(entity, Entity.Barrier):
                    ex, ey = entity.get_pos()
                    px, py = player.get_pos()
                    diffx = abs(ex-px)
                    diffy = abs(ey-py)
                    # Before checking intersection check to make sure entity is in range for collision
                    if diffx < 10 or diffy < 10:
                        if entity.is_killer():
                            if check_intersect(player, entity):
                                # We have a kill
                                if not player.is_dead():
                                    player.kill(False)
                                    dead_players.append(player)
                if isinstance(entity, Entity.Entity):
                    if entity.get_name() == "Goal":
                        ex, ey = entity.get_pos()
                        px, py = player.get_pos()
                        diffx = abs(ex - px)
                        diffy = abs(ey - py)
                        if diffx < 10 or diffy < 10:
                            if check_intersect(player, entity):
                                # Player reached goal
                                if first_goal_reached == "never":
                                    first_goal_reached = generation
                                if not player.is_dead():
                                    player.kill(True)
                                    dead_players.append(player)


def dead_check(player):
    # Check to see if a specific player is dead
    for dead in dead_players:
        if player.get_name() == dead.get_name():
            return True
    return False


def get_dead_player(player):
    # Get dead player object
    for dead in dead_players:
        if player.get_name() == dead.get_name():
            return dead


def check_intersect(player, entity):
    # Create ranges and sets for players hitbox
    hitbox = player.get_hitbox()
    hrange_x = hitbox[0]
    hrange_y = hitbox[1]
    prx = range(hrange_x[0], hrange_x[1])
    pry = range(hrange_y[0], hrange_y[1])
    prx_set = set(prx)
    pry_set = set(pry)
    krange_x = 0
    krange_y = 0
    if isinstance(entity, Entity.Barrier):
        # Create ranges for entity killzone
        killzone = entity.get_killzone()
        krange_x = killzone[0]
        krange_y = killzone[1]
    elif isinstance(entity, Entity.Entity):
        killzone = entity.get_interaction_zone()
        krange_x = killzone[0]
        krange_y = killzone[1]
    krx = range(krange_x[0], krange_x[1])
    kry = range(krange_y[0], krange_y[1])
    # Check the intersection of both x and y ranges if intersection set is empty there is no collision
    if len(prx_set.intersection(krx)) != 0 and len(pry_set.intersection(kry)) != 0:
        return True
    else:
        return False


def player_mind(ai):
    global goals_reached
    global goals_reached_per_gen
    # Add self to player list
    players.append(ai)
    # Movement loop
    xc, yc = 0, 0
    random_moves = False

    # Wait until notified
    while not ready_to_start:
        time.sleep(1)

    # While not dead
    while not dead_check(ai):
        # Check to see if ai has genetics if so make moved based on the genetics otherwise make random moves
        if ai.has_genetics():
            x, y = ai.next_gene()
            if x == 0 and y == 0:
                random_moves = True
            else:
                ai.move(x, y)
                update_player(ai)
                time.sleep(.05/sim_speed_multiplier)
        else:
            random_moves = True
        # If no more genes remain or no genes exist then do random moves
        if random_moves:
            tleft, tdown, tright, tup = ai.get_all_tendencies()
            tendency_sum = tleft + tdown + tright + tup
            sleft = tleft
            sdown = tleft+tdown
            sright = tleft+tdown+tright
            sup = tendency_sum
            r = random.randint(1, tendency_sum)
            if 0 < r <= sleft:
                # Left
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

            ai.move(xc, yc)
            update_player(ai)

            xc, yc = 0, 0
            time.sleep(.05/sim_speed_multiplier)
        # Check own collision
        check_self_collision(ai)
    dead_self = get_dead_player(ai)

    # Stat keeping
    if dead_self.goal_reached:
        goals_reached += 1
        goals_reached_per_gen += 1
    # Kill self
    ai.kill(dead_self.goal_reached)
    update_player(ai)


def text_objects(text, font):
    text_surface = font.render(text, True, white)
    return text_surface, text_surface.get_rect()


def text_creator(text, showtime):
    current_time = time.time()
    while time.time() - current_time < showtime:
        large_text = pygame.font.Font('freesansbold.ttf', 50)
        text_surf, text_rect = text_objects(text, large_text)
        text_rect.center = (round(width / 2), 95)
        gameDisplay.blit(text_surf, text_rect)

        pygame.display.update()


def display_message(text, showtime):
    # Show message on screen for a set amount of time
    # Check to make sure there isn't another thread already showing text
    thread_exists = False
    for thread in threads:
        if thread.getName() == "text_thread":
            thread_exists = True

    if not thread_exists:
        # Have a new thread display the message
        t = Thread(target=text_creator, name="text_thread", args=(text, showtime,))
        t.start()
        threads.append(t)


def next_generation(new_offsprings):
    global total_players
    global total_mutations
    global best_fitness
    global best_fitness_occurrence
    global best_fitness_memory
    global next_gen_start_time
    global goals_reached_per_gen
    global pop_mutations
    global tendency_mutations
    global best_fitness_tendencies

    fit_parent_a = -1000000000000000
    parent_a = ""
    fit_parent_b = -1000000000000000
    parent_b = ""
    all_fitness = []
    all_moves = []
    # Find most fit parents
    for player in players:
        fitness = player.get_fitness()
        all_fitness.append(fitness)
        all_moves.append(player.get_memory_size())
        if fitness > fit_parent_a:
            fit_parent_a = fitness
            parent_a = player
        elif fitness > fit_parent_b:
            fit_parent_b = fitness
            parent_b = player
    # If parent b has a shorter memory, swap them, if equal or longer nothing will happen
    if parent_a.get_memory_size() > parent_b.get_memory_size():
        parent_a, parent_b = parent_b, parent_a

    # Stat keeping
    if parent_a.get_fitness() > best_fitness:
        best_fitness = parent_a.get_fitness()
        best_fitness_occurrence = generation
        best_fitness_memory = parent_a.get_memory()
        best_fitness_tendencies = parent_a.get_all_tendencies()
    elif parent_b.get_fitness() > best_fitness:
        best_fitness = parent_b.get_fitness()
        best_fitness_occurrence = generation
        best_fitness_memory = parent_b.get_memory()
        best_fitness_tendencies = parent_a.get_all_tendencies()

    # Generate new generation
    mutants = 0
    pop_mutants = 0
    tendency_mutants = 0
    if new_offsprings:
        i = 0
        while i < generation_size:
            crossover = parent_a.crossover(parent_b)
            clength = len(crossover)-1
            if crossover[clength] == (10, 10):
                # Mutation Occurred
                mutants += 1
                total_mutations += 1
                crossover.pop(clength)
                # Set color of mutant to be green
                offspring = Entity.Player("AI" + str(i), img_mutant_player, spawnpoint, goal)
            elif crossover[clength] == (11, 11):
                # Pop mutation occurred
                mutants += 1
                total_mutations += 1
                pop_mutations += 1
                pop_mutants += 1
                crossover.pop(clength)
                offspring = Entity.Player("AI" + str(i), img_mutant_player, spawnpoint, goal)
            elif crossover[clength] == (12, 12):
                # Tendency mutation occurred
                mutants += 1
                total_mutations += 1
                tendency_mutations += 1
                tendency_mutants += 1
                crossover.pop(clength)
                clength -= 1
                tleft, tdown, tright, tup = crossover[clength]
                crossover.pop(clength)
                offspring = Entity.Player("AI" + str(i), img_mutant_player, spawnpoint, goal)
                offspring.set_all_tendencies((tleft, tdown, tright, tup))
            else:
                offspring = Entity.Player("AI" + str(i), img_normal_player, spawnpoint, goal)
                offspring.set_all_tendencies(parent_a.crossover_tendencies(parent_b.get_all_tendencies()))

            offspring.set_genetics(crossover)
            offsprings.append(offspring)
            total_players += 1
            i += 1

    #Stats
    print("=====Statistics===========================")
    current_time = time.time()
    print("Generation " + str(generation) + " run time..." + str(round(current_time-next_gen_start_time)) + " seconds.")
    next_gen_start_time = current_time
    print("Most fit parents in generation " + str(generation) + "... " + str(fit_parent_a) + " and " + str(fit_parent_b))
    print("# of moves made by fittest parents " + str(parent_a.get_memory_size()) + " and " + str(parent_b.get_memory_size()))
    print("Average Fitness: " + str(sum(all_fitness) / len(all_fitness)))
    print("Average # of moves: " + str(sum(all_moves) / len(all_moves)))
    print("# of goals reached this generation... " + str(goals_reached_per_gen))
    goals_reached_per_gen = 0
    if new_offsprings:
        print("Mutant offsprings produced for generation " + str(generation+1) + "... " + str(mutants))
        regular_mutants = mutants-tendency_mutants-pop_mutants
        print(str(regular_mutants) + " regular mutants, " + str(tendency_mutants) + " tendency mutants and " + str(pop_mutants) + " pop mutants")

    return offsprings


def reset_values():
    # Reset relevant values for generation reset
    global dead_players
    global players
    global generation
    global threads
    global offsprings

    players = []
    dead_players = []
    threads = []
    generation += 1
    offsprings = []


def loop():
    global goal
    global ready_to_start
    global wait_for_enter
    global start_time
    crashed = False

    load_level(level)
    # Create players for all AI
    i = 0
    ai_players = []
    while i < generation_size:
        ai = Entity.Player("AI" + str(i), img_normal_player, spawnpoint, goal)
        ai_players.append(ai)
        i += 1

    # Create threads for all players
    for ai in ai_players:
        t = Thread(target=player_mind, args=(ai,))
        t.start()
        threads.append(t)

    # Create Display
    gameDisplay.fill(black)
    draw_players()
    place_entities()
    pygame.display.update()

    while not crashed:
        # Wait for enter to be pressed before starting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            if event.type == pygame.KEYDOWN and wait_for_enter:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    wait_for_enter = False
                    start_time = time.time()

        if not wait_for_enter:
            # Display next generation text for 1 second
            gameDisplay.fill(black)
            draw_players()
            place_entities()
            pygame.display.update()
            if not ready_to_start:
                display_message("Generation " + str(generation), 1)
                time.sleep(1)
            ready_to_start = True

        if len(dead_players) == generation_size:
            # Generation is dead
            for thread in threads:
                while thread.is_alive():
                    "Wait for threads to wrap up"
            ready_to_start = False
            gameDisplay.fill(black)
            draw_players()
            place_entities()
            check_collision()
            pygame.display.update()
            time.sleep(reset_wait)
            gameDisplay.fill(black)
            if generation == generation_run_time:
                next_generation(False)
                print("=====End Simulation Statistics===========================")
                elapsed_time = get_elapsed_time()
                print("Generation limit " + str(generation_run_time) + " reached... run time " + str(round(elapsed_time)) + " seconds.")
                print("Average run time per generation... " + str(round(elapsed_time/generation)))
                print("Best fitness... " + str(best_fitness) + " occurred at generation " + str(best_fitness_occurrence))
                print("Best fitness memory size... " + str(len(best_fitness_memory)))
                l, d, r, u = best_fitness_tendencies
                print("Best fitness tendencies... Left: " + str(l) + " Down: " + str(d) + " Right: " + str(r) + " Up: " + str(u))
                print("A total of " + str(total_players) + " players entered the level.")
                print("Total # of mutations... " + str(total_mutations))
                regular_mutants = total_mutations - tendency_mutations - pop_mutations
                print(str(regular_mutants) + " regular mutants, " + str(tendency_mutations) + " tendency mutants and " + str(pop_mutations) + " pop mutants")
                print("First goal reached at generation " + str(first_goal_reached))
                goal_percent = str(round((goals_reached/total_players)*100, 3))
                print("Goals reached: " + str(goals_reached) + "/" + str(total_players) + " or " + goal_percent + "%")
                dead = total_players-goals_reached
                dead_percent = str(round((dead/total_players) * 100, 3))
                print("Dead players: " + str(dead) + "/" + str(total_players) + " or " + dead_percent + "%")
                print("Ending program...")
                return
            # Create next generation
            new_gen = next_generation(True)
            # Prep all values for reset and create new generation
            reset_values()
            # Start up new threads for the new generation
            print("Starting generation " + str(generation) + "...")
            for ai in new_gen:
                t = Thread(target=player_mind, args=(ai,))
                t.start()
                threads.append(t)
            gameDisplay.fill(black)

        clock.tick(60)


loop()
pygame.quit()
quit()
