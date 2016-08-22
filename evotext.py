#!/usr/bin/env python3
"""
LICENSE
-------

You may use this code or any derivative of the code
for any purpose: good or evil; artistic, commercial
scientific or other on the one condition listed below:

* You must surrender your eternal soul to the devil.

    If you are a rational creature (don't have a soul),
    it will suffice that you say out loud:

    "Yeah yeah, I'll give the devil my 'soul'"
    doing air quotes while saying the word 'soul'.

"""
import curses
import numpy as np
import string
from collections import Counter
import time
import sys


def _exit(*args, **kwargs):
    """Hook to ensure terminal looks alright after any exception"""
    curses.endwin()
    sys.exit(-1)


def _denovo(n=256, l=26):
    """Initiate a genome of certain length"""
    return np.random.randint(0, l, n)


def _relative_fitness(population_restrided, encoded_selection_word, base=10):
    """Calculates the relative fitness of all genomes

    Absolute fitness is calculated as the number of correctly placed
    letters to the second power for all offsets in each genome.
    Then these values are summed up for the entire genome.


    Relative fitness is the individual absolute divided minus the
    lowest absolute fitness of the population divided by the size of
    the absolute fitness span.

    In math:

    (fitness - min(fitness)) / (max(fitness) - min(fitness))

    :param population_restrided: A wordlength-restrided population
    :param encoded_selection_word: The word as int array
    :return: fittness array
    """
    occurancies = np.power(base, np.sum(population_restrided == encoded_selection_word, axis=-1)).sum(axis=-1)

    fitness_range = occurancies.max() - occurancies.min()
    if occurancies.max() == 0:

        return np.zeros_like(occurancies, dtype=np.float)

    elif fitness_range == 0:

        return np.ones_like(occurancies, dtype=np.float)

    else:

        return (occurancies - occurancies.min()) / fitness_range


def _select(population, relative_fitness, n_characters, fecundency=10):
    """For the next generation, size kept constant, reproduced or
    spontaneously create if missing.

    :param population: The population of genomes
    :param relative_fitness: The relative fitnesses of all genomes
    :param n_characters: Number of characters in alphabet
    :param fecundency: Number of offspring for those that survive
    """
    individual_fecundency = np.round(np.random.random(relative_fitness.shape) / (2 - relative_fitness) * fecundency)
    fecundency_order = np.argsort(individual_fecundency)[::-1]
    individual_fecundency = individual_fecundency.astype(np.int)
    survivors = np.cumsum(individual_fecundency[fecundency_order]) < population.shape[0]
    n_parents = survivors.sum()
    free_positions, = np.where(~survivors)
    free_pos = 0
    n_free = free_positions.size

    for i, parent in enumerate(fecundency_order):

        if i >= n_parents or free_pos >= n_free:
            break

        for clone in range(1, individual_fecundency[parent]):

            if free_pos >= n_free:
                break

            population[fecundency_order[free_positions[free_pos]]] = population[parent]
            free_pos += 1

    # TODO: This is not really biologically pleasing creating de novo competitors
    while free_pos < n_free:
        population[fecundency_order[free_positions[free_pos]]] = _denovo(population.shape[1], n_characters)
        free_pos += 1


def _mutate(population, mutation_size, mutation_frequency, n_characters):
    """SNP mutates based on frequency and mutation step from normal dist

    :param population: The population 2D array
    :param mutation_size: The width of the normal distribution
    :param mutation_frequency: Freq of mutation 0-1
    :param n_characters: Number of characters in alphabet
    :return:
    """
    mutators = np.random.random(population.shape) < mutation_frequency
    mutations = np.round(population[mutators] + np.random.standard_normal(mutators.sum()) * mutation_size).astype(int)
    mutations %= n_characters
    population[mutators] = mutations


def _display(population, encoding, evo_word, generation=None, max_width=80,
             pad_top=2, pad_left=1, aspect=2, screen=None):
    """ Displays current state on screen

    :param population: The population at its current state
    :param encoding: The characters allowed in the genome as a string
    :param evo_word: The word do select for
    :param generation: Optional. Number of generations to simulate default is infinite
    :param max_width: Optional. Maximum line width
    :param pad_top: Optional. Number of empty characters at top
    :param pad_left: Optional. Number of empty characters on the left
    :param aspect: Optional. The width to height ratio
    :param screen: Optional. A curses screen to use
    :return: The curses screen
    """
    modes, freqs = zip(*(Counter(v).most_common(1)[0] for v in population.T))
    characters = len(modes)
    line_width = int(min(aspect * np.round(np.sqrt(characters/aspect)), max_width - pad_left))

    if screen is None:
        screen = curses.initscr()
        sys.__excepthook__ = _exit
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.noecho()
        curses.curs_set(False)

    screen.clear()

    if generation is not None and pad_top > 0:
        screen.addstr(0, 0, "Generation: {0}".format(str(generation)).zfill(6))

    line = pad_top
    pos = 0
    while pos < characters:

        word = np.choose(modes[pos: pos + line_width], encoding)
        for id_c, c in enumerate(word):
            if c in evo_word:
                screen.addstr(line, pad_left + id_c, c, curses.color_pair(2))
            else:
                screen.addstr(line, pad_left + id_c, c, curses.color_pair(1))

        pos += word.size
        line += 1

    screen.refresh()

    return screen


def simulate(selection_word="DEMO", characters=string.ascii_uppercase, generations=-1,
             population_size=1000, text_length=800, mutation_size=5, mutation_frequency=0.02,
             fps=12, fecundency=10, fitness_base=10):
    """The simluation function

    :param selection_word:
        Optional. The word to select for
    :param characters:
        Optional. The characters allowed in the genomes
    :param generations:
        Optional. The number of generations
    :param population_size:
        Optional. Number of genomes.
    :param text_length:
        Optional. Length of each genome.
    :param mutation_size:
        Optional. Mutations occurs as SNPs and there's a
        gaussian probability function centered around the current
        character for what the new character state will be.
        Mutation width decides the width of the gaussian in terms
        of sigmas.
    :param mutation_frequency:
        Optional. Frequency of mutations
    :param fps:
        Optional. Simulation speed, max frames per seconds.
    :param fecundency:
        Optional. The maximum number of offsprings one genome
        can have.
    :param fitness_base:
        Optional. The higher value the more more complete phrases
        are promoted over single occurencies of characters in the
        phrase. Useful range is 1 - 10.
    """

    def eternal_generator():

        gen = 0
        while True:
            yield gen
            gen += 1

    n_characters = len(characters)

    encoded_selection_word = np.array([characters.index(c) for c in selection_word])

    population = np.array([_denovo(text_length, n_characters) for _ in range(population_size)])
    population_restrided = np.lib.stride_tricks.as_strided(
        population,
        shape=(population.shape[0], population.shape[1] - encoded_selection_word.size + 1, encoded_selection_word.size),
        strides=(population.strides[0], population.strides[1], population.strides[1]))

    screen = None
    cycle_time = 1.0 / fps

    if generations > 0:
        generator = range(generations)
    else:
        generator = eternal_generator()

    for generation in generator:

        t = time.clock()

        _mutate(population, mutation_size, mutation_frequency, n_characters)
        relative_fitness = _relative_fitness(population_restrided, encoded_selection_word, base=fitness_base)
        _select(population, relative_fitness, n_characters, fecundency=fecundency)

        screen = _display(population, characters, selection_word, screen=screen, generation=generation)

        delta = cycle_time - (time.clock() - t)
        if delta > 0:
            time.sleep(delta)

    time.sleep(3)
    curses.endwin()


if __name__ == "__main__":

    if len(sys.argv) > 3:
        pop_size = int(sys.argv[3])
    else:
        pop_size = 500

    if len(sys.argv) > 2:
        text_length = int(sys.argv[2])
    else:
        text_length = 400

    if len(sys.argv) > 3:
        fitness_base = int(sys.argv[3])
    else:
        fitness_base = 10

    if len(sys.argv) > 1:
        text = sys.argv[1].upper()
        if " " in text:
            characters=string.ascii_uppercase + " "
        simulate(text, text_length=text_length, population_size=pop_size, characters=characters)
    else:
        simulate("DEMO", text_length=text_length, population_size=pop_size)
