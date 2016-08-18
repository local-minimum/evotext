# EVOtext

This is a small python3 module that simulates evolution on a random text string with the following characteristics.

* Constant population size
* No meiosis (crossover)
* SNP mutations (random single position mutation based on mutation frequency and will change in accordance to a normal distribution).
* Fitness function consideres all offsets in genome where WORD could be written and returns the sum of the square found correctly placed characters of all offsets
* Fecundency is uniform within set range and inversly correlated to (2 - fitness) parenting from the most fit in descending fitness order.

Output is in glorious text mode, showing the most common character across the population for each position and color coding those positions that have a character from the sought word.

## Dependencies

Numpy

## How to use

From command-line you simlpy type:

  `./evotext.py`

Or if you want to be fancy

  `./evotext.py WORD 200 50`
  
Where the first number is the number of characters you want in each genome and second number is the population size

## How to abuse

This I don't know, but would love to be informed of

## Licence

The licence is specified in the python-file
