# Genetic Algorithm Navigator
The genetic algorithm navigator is a program developed to demonstrate the use of a genetic algorithm in path creating situations. A population of AI players are generated, each of which is its own independently controlled thread. The AI players will initially navigate at random and through the use of core genetic algorithm concepts (ex. crossovers, mutations, fitness, etc.) the AI population will generate offspring with a potentially a higher fitness. Subsequent generations will be more adept than the previous and through this simulated genetic process the AIs will learn to find the shortest path to the goal location.  

![alt text](examples/demo1.gif?raw=true "Scatter Duo Demo 1")<br/>
<sup>Example 1: Two individual instances running with a generation size of 50 each.</sup>

# Setup and Usage
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

<b>Sim Speed Multiplier-</b> After every move each AI thread sleeps for .05 seconds (otherwise the players move too fast to see). A higher number here will make each AI player move faster.

<b>Reset Wait-</b> The number of seconds the program should wait before clearing all the dead players from the screen and resetting the generation.

<b>Wait for Enter-</b> This is a boolean that decides whether or not the program should wait for an enter key press before starting the simulation.

In the Entity.py file some key variable are the following:
```
# Mutation Chances
self.mutation_chance = 20000  # 1 out of this number * size of genes
self.pop_mutation_chance = 50  # 1 out of this number
self.tendency_mutation_chance = 50  # 1 out of this number

# Mutation Severity
self.tendency_mutation_severity = 1  # How much should be added/removed from tendencies during mutation
self.pop_severity = 2   # Percent of tail that will be popped
self.mutation_severity = .5  # This is a multiplier, 2 = x2 severity, .5 = 1/2 severity (best to keep this under 1 maybe 1.25 max)
```

<b>Mutation Chance-</b> This is the chance that a normal mutation will occur (1 out of X). This chance is ran for every gene in an AI's genetics, this means true mutation chance is (1/Mutation Chance) * Size of Genetics.

<b>Pop Mutation Chance-</b> This is the chance that a pop mutation will occur (1 out of X). This chance is ran once on creation of an offspring.

<b>Tendency Mutation Chance-</b> This is the chance that a tendency mutation will occur (1 out of X). This chance is ran once on creation of an offspring.

<b>Tendency Mutation Severity-</b> This is the severity of a tendency mutation. This number is added to the randomly selected tendency (left, down, right or up). 

<b>Pop Severity-</b> This is the severity of a pop mutation. In a pop mutation a certain percentage of the end of an AI's genetics is removed. This number is that percent removed.

<b>Mutation Severity-</b> This is the severity of a normal mutation. In a normal mutation a range is selected in an AI's genetics to be randomly mutated. With this value at 1 the whole genetic sequence is subject to change, this is usually not desired so this number should be between 0 and 1. A number higher than 1 increases the chance that the entire genetics are changed (if desired).
