# Genetic Algorithm Navigator
The genetic algorithm navigator is a program developed to demonstrate the use of a genetic algorithm in path creating situations. A population of AI players are generated, each of which is its own independently controlled thread. The AI players will initially navigate at random and through the use of core genetic algorithm concepts (ex. crossovers, mutations, fitness, etc.) the AI population will generate offspring with a potentially a higher fitness. Subsequent generations will be more adept than the previous and through this simulated genetic process the AIs will learn to find the shortest path to the goal location.  

![alt text](examples/demo1.gif?raw=true "Scatter Duo Demo 1")<br/>
<sup>Example 1: Two individual instances running with a generation size of 50 each.</sup>

# Setup and Usage
If pygame is not installed use the following command:

```python3 -m pip install -U pygame --user```

To run the program use:

```python3 GUI.py```

I am currently working on a prompt which will ask for relevant variables on execution of the program. Until then here is an explanation of various variables and how they work.

In the GUI.py file some key variable are the following:
```
# Generation Variables
generation_size = 50
generation_run_time = 100
sim_speed_multiplier = 1000

# Wait time before each reset and enter key wait
reset_wait = 1
wait_for_enter = True
```

<b>Generation Size-</b> This is the number of AI players created for each generation. Each AI player is assigned its own thread so this number should be kept lower on less powerful computers.

<b>Generation Run Time-</b> This is the number of generations the program should run for. At the end of this run time some statistics will be shown. To run infinitely set this variable to a negative number.

<b>Sim Speed Multiplier-</b> After every move each AI thread sleeps for .05 seconds (otherwise the players move too fast to see). This number is divided into this sleep time thus a higher number here will make each AI player move faster.

<b>Reset Wait-</b> The number of seconds the program should wait before clearing all the dead players from the screen and resetting the generation.

<b>Wait for Enter-</b> This is a boolean that decides whether or not the program should wait for an enter key press before starting the simulation.

In the Entity.py file some key variable are the following:
```
# Mutation Chances
self.mutation_chance = 20000
self.pop_mutation_chance = 50
self.tendency_mutation_chance = 50

# Mutation Severity
self.tendency_mutation_severity = 1
self.pop_severity = 2
self.mutation_severity = .5
```

<b>Mutation Chance-</b> This is the chance that a normal mutation will occur (1 out of X). This chance is ran for every gene in an AI's genetics, this means true mutation chance is (1/Mutation Chance) * Size of Genetics.

<b>Pop Mutation Chance-</b> This is the chance that a pop mutation will occur (1 out of X). This chance is ran once on creation of an offspring.

<b>Tendency Mutation Chance-</b> This is the chance that a tendency mutation will occur (1 out of X). This chance is ran once on creation of an offspring.

<b>Tendency Mutation Severity-</b> This is the severity of a tendency mutation. This number is added to the randomly selected tendency (left, down, right or up). 

<b>Pop Severity-</b> This is the severity of a pop mutation. In a pop mutation a certain percentage of the end of an AI's genetics is removed. This number is that percent removed.

<b>Mutation Severity-</b> This is the severity of a normal mutation. In a normal mutation a range is selected in an AI's genetics to be randomly mutated. With this value at 1 the whole genetic sequence is subject to change, this is usually not desired so this number should be between 0 and 1. A number higher than 1 increases the chance that the entire genetics are changed (if desired).

# How it works

This will be a step-by-step explanation of how AI players are created and evolve. A genetic algorithm is used but some changes and additions are made to adhere to this application.

#### Initial Population

An initial population is generated with equal tendencies. Tendencies consist of left, down, right and up. Each is set to 10 giving all AI players a 25% chance to make any move. The genetics of an AI player is the memory of moves made, since the initial population of AI players have no genetics passed down from a parent the players will make random movements based on their tendencies.

#### Dead Population and Fitness Calculation

Upon the death of the current generation fitness will be calculated based on several factors. The memory of moves is examined and run through fitness calculation. The memory of an AI typically looks like the following:

```AI_MEMORY = [(0, 5), (0, -5), (5, 0), (-5, 0), ...]```

Calculation 1- Each touple represents a change to the (x, y) of the AI when it makes a move. When calculating fitness these x and y values are examined, if the change in xy brings the player closer to the goal then add 10 to the fitness, otherwise, subtract 10 from total fitness.

Calculation 2- If the goal is reached by an AI player a reward is generated for the AI. The max reward possible is 20,000 but from this pool 10 fitness is removed for every additional move made over 200. See formula below:

```reward = 20000-((MEMORY_SIZE-200)*10)```

If the reward drops below 1000 then the AI player will receive a minimum of a 1000 fitness reward.

Calculation 3- If the AI did not reach the goal it will still receive a penalty for the number of moves its performed, 25% of the number of moves taken by the AI will be subtracted from total fitness. Formula below:

```penalty = MEMORY_SIZE * .25```

Final Calculation- The resulting fitness from the previous calculations are doubled if the goal was reached.

#### Most Fit Parents and Crossover

After fitness is calculated for all AI players the 2 most fit individuals are chosen to be be parents. The parent with the longer memory/genetics is chosen to be parent b and the shorter is a. Now the memory from parent a is crossed with parent b but this is where we have a slight difference from the traditional crossover method. We still pick a crossover point but instead of generating 2 offspring by swapping both the 1st and 2nd half of the genes we instead only crossover the 2nd half of genes from the parent with the longer memory. See example below:

```
parent_a_genes = [a, a, a, a, a, a, a]
parent_b_genes = [b, b, b, b, b, b, b, b, b, b]
random_crossover_point = 6
crossover_ab = [a, a, a, a, a, a | b, b, b, b]
```

The resulting crossover will be the genes/memory of the offspring. A random crossover point is select for every offspring.

Finally, we crossover the tendencies of both parents. This is done exactly the same as the genes, the only difference is that the number of tendencies are always the same (left, down, right, up). Example below:

```
parent_a_tendencies = [11, 15, 9, 12]
parent_b_tendencies = [14, 12, 16, 8]
random_crossover_point = 1
crossover_ab = [11 | 12, 16, 8]
```

#### Mutation

