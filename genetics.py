import pygame as pg
import numpy as np
import sys
import random
from game_of_life import GameOfLifeDrawer, GameOfLife
import multiprocessing as mp
import uuid
import json

WINDOW_SIZE = (2000, 1600)


# Rules
# 1. An animal lives for 1000 cycles
# 2. The animal will be scored based on how many cells are alive in the game of life
# 3. Once the population reaches 1000, top 10% will be selected for reproduction
# 4. During reproduction, the mates will cross their DNA

class Animal:
    def __init__(self, dna_len: int = 12, dna: list = None):
        self.dna_len = dna_len
        self.dna = np.random.randint(0, 2, size=dna_len) if dna is None else np.array(dna)

        self.game = GameOfLife(*GameOfLifeDrawer.get_grid_dims(*WINDOW_SIZE, 8))
        self.game.state = self.make_state()
        self.score = 0
        self.id = uuid.uuid4().hex
        self.parents = []

    def make_state(self):
        state = np.zeros((self.game.grid_dim_x, self.game.grid_dim_y), dtype=np.int8)
        position = (self.game.grid_dim_x // 2, self.game.grid_dim_y // 2)
        for i in range(self.dna_len):
            for j in range(self.dna_len):
                if self.dna[i] == 1:
                    x = position[0] + i - self.dna_len // 2
                    y = position[1] + j - self.dna_len // 2
                    if 0 <= x < self.game.grid_dim_x and 0 <= y < self.game.grid_dim_y:
                        state[x][y] = 1
        return state
    
    def breed(self, other: 'Animal'):
        dna_1 = self.dna[:self.dna_len // 2]
        dna_2 = other.dna[self.dna_len // 2:]
        new_dna = np.concatenate((dna_1, dna_2))

        for i in range(len(new_dna)):
            if random.random() < 0.1:  # 10% chance of mutation
                new_dna[i] = 1 - new_dna[i]
                print(f"Mutation occurred for gene {i}")
                break

        animal = Animal(self.dna_len, new_dna.tolist())
        animal.parents = [self, other]
        return animal
    
    def dump(self):
        return {
            'id': self.id,
            'dna': [int(gene) for gene in self.dna.tolist()],
            'score': int(self.score),
            'parents': [parent.id for parent in self.parents]
        }


def run_animal(dna_len, dna: list = None, iterations: int = 100, display: bool = True):
    animal = Animal(dna_len, dna)
    
    if display:
        drawer = GameOfLifeDrawer(animal.game, window_size=WINDOW_SIZE, cell_size=8)

    for i in range(iterations):
        if display:
            drawer.draw_state()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()

        animal.game.state = animal.game.compute_next_state()
        if i % 10 == 0 and np.sum(animal.game.state) <= 0:
            break
                
    animal.score = np.sum(animal.game.state)
    print(f"Animal Score: {animal.score}, DNA: {animal.dna.tolist()}")
    return animal

def make_babies(population: list):
    eligible = population[:len(population) // 2]
    if len(eligible) < 2:
        return []

    babies = []
    for i in range(0, len(eligible), 2):
        if i + 1 >= len(eligible):
            break

        parent1 = eligible[i]
        parent2 = eligible[i + 1]
        baby = parent1.breed(parent2)
        babies.append(baby)    

    print(f"Made {len(babies)} babies from {len(eligible)} parents.")
    return babies

def run_simulation():
    generations: int = 50
    population_size: int = 20
    dna_len: int = 50
    iterations: int = 500
    
    display = False
    pool = mp.Pool(8)


    gen_file = f"animals/genetics_{uuid.uuid4().hex[:6]}.json"
    data = {
        'generations': generations,
        'population_size': population_size,
        'dna_len': dna_len,
        'iterations': iterations,
        'generations': []
    }


    print("Starting simulation with population size:", population_size)
    result = [pool.apply_async(run_animal, (dna_len, None, iterations, display)) for _ in range(population_size)]
    population = sorted([r.get() for r in result], key=lambda x: x.score, reverse=True)
   
    for generation in range(generations):
        data['generations'].append({
            'best': population[0].dump(),
            'worst': population[-1].dump(),
        })

        with open(gen_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Generation {generation+1}/{generations}. Population size: {len(population)}, Best Score: {population[0].score}, Worst Score: {population[-1].score}")
        babies = make_babies(population)
        if not babies:
            print("No babies were made, ending simulation.")
            break

        # Delete bottom 10% of the population
        population = population[:int(len(population) * 0.75)]
        population.extend(babies)
        print(f"Population size after breeding: {len(population)}")

        # Run the next generation
        result = [pool.apply_async(run_animal, (dna_len, animal.dna, iterations, display)) for animal in population]
        population = sorted([r.get() for r in result], key=lambda x: x.score, reverse=True)


    print("Simulation finished. Best animal:", population[0].dump())


if __name__ == "__main__":
    run_simulation()
    


