# Genetic Algorithm Navigator
The genetic algorithm navigator is a program developed to demonstrate the use of a genetic algorithm in path creating situations. A population of AI players are generated, each of which is its own independently controlled thread. The AI players will initially navigate at random and through the use of core genetic algorithm concepts (ex. crossovers, mutations, fitness, etc.) the AI population will generate offspring with a potentially a higher fitness. Subsequent generations will be more adept than the previous and through this simulated genetic process the AIs will learn to find the shortest path to the goal location.  

Below are some examples of the program running. The red squares are barriers that kill the AI, the green square is the goal that the AI are trying to reach, the blue circles are the AI players and the green circles are mutated AI players.

![alt text](examples/demo1.gif?raw=true "Scatter Duo Demo 1")<br/>
<sup>Example 1: Two individual instances running with a generation size of 50 each. These are the first few generations.</sup>

![alt text](examples/demo2.gif?raw=true "Scatter Duo Demo 2")<br/>
<sup>Example 2: The same instances as in example 1 but in a later generation. Generation 62 and 79 respectively.</sup>

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

<b>Calculation 1-</b> Each touple represents a change to the (x, y) of the AI when it makes a move. When calculating fitness these x and y values are examined, if the change in xy brings the player closer to the goal then add 10 to the fitness, otherwise, subtract 10 from total fitness.

<b>Calculation 2-</b> If the goal is reached by an AI player a reward is generated for the AI. The max reward possible is 20,000 but from this pool 10 fitness is removed for every additional move made over 200. See formula below:

```reward = 20000-((MEMORY_SIZE-200)*10)```

If the reward drops below 1000 then the AI player will receive a minimum of a 1000 fitness reward.

<b>Calculation 3-</b> If the AI did not reach the goal it will still receive a penalty for the number of moves its performed, 25% of the number of moves taken by the AI will be subtracted from total fitness. Formula below:

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

In this application we have 3 forms of mutation, all of which cannot not happen simultaneously. The three forms of mutation are referred to as normal mutations, pop mutations and tendency mutations.

<b>Normal Mutations-</b> In a normal mutation a point is selected in an AI's genes/memory and then a severity of mutation is randomly generated based on the size of it's genes. This severity is used to determine a range of genes that will be randomly mutated based on current tendencies. The severity along with the mutation chance can be modified. The the chance of mutation increases with a larger gene size, this encourages more mutations when an AI is performing poorly due to having too large of a genes/memory pool.

````
mutation_chance = 5
mutation_severity = .5
AI_MEMORY = [(0, 5), (0, -5), (5, 0), (-5, 0), (-5, 0)]
lottery_number = random number out of mutation_chance = 3
for AI_MEMORY size roll_number = random number out of mutation chance = 3 
if roll_number = lottery_number then we have mutation

random_point = 3
random_severity_size = random number out of AI_MEMORY size = 2
severity = random_severity_size * mutation_severity = 1
range = random_point-1 --> random_point --> random_point+1
mutated_memory = [(0, 5) | RANDOM, RANDOM, RANDOM | (-5, 0)]
````

The above example shows how the mutation occurs logistically. A lottery number is generated out of the mutation chance and numbers are rolled equal to the size of the memory until the lotto is won or the attempts run out. If we have a mutation then a point in the memory is selected which will be the center of the mutation range. A mutation range is selected based on a random number obtained from the 0 --> the size of the AI's memory. This size is then multiplied by the mutation severity to either reduce or increase severity. The range for mutation is then created with the random point being at the center random_point-r --> random_point --> random_point+r

<b>Pop Mutations-</b> In a pop mutation a certain percentage is removed from the end of an AI's memory. The percentage is equal to the severity and the chance of this mutation occurring is run only once through the lottery. This form of mutation helps prevent AI from repeating its parents death.
 
````
pop_mutation_chance = 100
pop_mutation_severity = 20
AI_MEMORY = [(0, 5), (0, -5), (5, 0), (-5, 0), (-5, 0)]
lottery_number = random number out of mutation chance = 45
roll_number = random number out of mutation chance = 45
if roll_number = lottery_number then we have a pop mutation

amount_to_remove = pop_mutation_severity% out of AI_MEMORY size = 20% of 5 = 1
pop_mutation_memory = [(0, 5), (0, -5), (5, 0), (-5, 0) | REMOVED]
````

The above example shows how the mutation occurs logistically. A lottery number is generated out of the mutation chance and a number is rolled out of that mutation chance, if the numbers match then a mutation occurs. The severity is the percentage of the end of the memory to be removed so X percent is removed from the end of the memory.

<b>Tendency Mutations-</b> In a tendency mutation a tendency is randomly selected to be increased or decreased at random based on the tendency mutation severity.

````
tendency_mutation_chance = 100
tendency_mutation_severity = 1
tendencies= [left, down, right, up] = [10, 10, 10, 10]
lottery_number = random number out of mutation chance = 45
roll_number = random number out of mutation chance = 45
if roll_number = lottery_number then we have a tendency mutation

select_random_tendency = 3
select_plus_or_minus_randomly = PLUS = +tendency_mutation_severity = +1
new_tendencies = [10, 10 | 10+1 | 10] = [10, 10 | 11 | 10]
````

The above example shows how the mutation occurs logistically. A lottery number is generated out of the mutation chance and a number is rolled out of that mutation chance, if the numbers match then a mutation occurs. A tendency is randomly selected and the it is then randomly decided whether or not the tendency will be increased or decreased by the tendency severity.

#### Next Generation

The crossovers and mutations occur every time an offspring is created between the two most fit parents. The next generation will be equal in size to the previous one. Once the next generation dies off the same steps above will be repeated each resulting in a more fit population.

## Author Contact

Justin Ortega: justinortega028@gmail.com

## Resources

* [Pygame Documentation](https://www.pygame.org/docs/)
* [Python Thread Documentation](https://docs.python.org/2.4/lib/thread-objects.html)
* [TowardsDataScience GA Example](https://towardsdatascience.com/introduction-to-genetic-algorithms-including-example-code-e396e98d8bf3)

