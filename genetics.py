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
    def __init__(self, dna_len: int = 12, dna: list = None, parents : list = []):
        self.dna_len = dna_len

        if dna is None:
            self.dna = np.random.randint(0, 2, size=(dna_len, dna_len))
        else:
            self.dna = np.array(dna)

        self.game = GameOfLife(*GameOfLifeDrawer.get_grid_dims(*WINDOW_SIZE, 8))
        self.game.state = self.make_state()
        self.score = 0
        self.id = uuid.uuid4().hex
        self.parents = parents

    def make_state(self):
        state = np.zeros((self.game.grid_dim_x, self.game.grid_dim_y), dtype=np.int8)
        position = self.get_starting_position()


        start_x = position[0]
        start_y = position[1]
        end_x = start_x + self.dna_len
        end_y = start_y + self.dna_len
        state[start_x:end_x, start_y:end_y] = self.dna

        return state
    
    def get_starting_position(self):
        # Starts at midle
        # return self.game.grid_dim_x // 2, self.game.grid_dim_y // 2

        # Starts at midle of left edge of the grid
        return 10, self.game.grid_dim_y // 2
    
    def is_dead(self):
        # An animal is dead if there are no alive cells in the game of life state
        return np.sum(self.game.state) == 0
    
    def breed(self, other: 'Animal'):
        # Take the first half of the rows from self.dna
        dna_1 = self.dna[:self.dna_len // 2, :]
        # Take the second half of the rows from other.dna
        dna_2 = other.dna[self.dna_len // 2:, :]
        
        new_dna = np.vstack((dna_1, dna_2))

        # Randomly mutate some genes in the new DNA
        for i in range(15):
            # Mutate a single gene with a 10% probability
            if random.random() < 0.10:
                row = random.randint(0, self.dna_len - 1)
                col = random.randint(0, self.dna_len - 1)
                new_dna[row, col] = 1 - new_dna[row, col]
                print(f"Mutation occurred at ({row}, {col})")

        animal = Animal(self.dna_len, new_dna.tolist(), parents=[self.id, other.id])
        return animal
    
    def compute_objective(self):
        # The objective function is the sum of all alive cells in the game of life state
        # return np.sum(self.game.state)


        #
        # For the movement task
        #
        # Get the center of mass of the alive cells and mesure the distance to the center of the right end of the grid
        alive_cells = np.argwhere(self.game.state == 1)
        if len(alive_cells) == 0:
            return 0

        # Calculate the center of mass
        center_of_mass = np.mean(alive_cells, axis=0)

        # Define the target point: center of the right edge of the grid
        target_point = np.array([self.game.grid_dim_x - 1, self.game.grid_dim_y // 2])

        # Calculate the distance to the target point
        distance = np.linalg.norm(center_of_mass - target_point)
        return 1 / (1 + distance)  # Higher score for closer distance

    
    def dump(self):
        return {
            'id': self.id,
            'dna': [[int(gene) for gene in row] for row in self.dna],
            'score': int(self.score),
            'parents': self.parents
        }


def run_animal(dna_len, dna: list = None, iterations: int = 100, display: bool = True, parents: list = []):
    animal = Animal(dna_len, dna, parents=parents)
    
    if display:
        drawer = GameOfLifeDrawer(animal.game, window_size=WINDOW_SIZE, cell_size=8)

    last_score = 0
    for i in range(iterations):
        if display and i % 50 == 0:
            drawer.draw_state()
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()

        animal.game.state = animal.game.compute_next_state()
        if i % 10 == 0: 
            if animal.is_dead(): 
                print(f"Animal died after {i} iterations.")
                break

            new_score = animal.compute_objective()
            if new_score == last_score:
                print(f"Animal is stuck after {i} iterations, ending simulation.")
                break

            last_score = new_score   

    if display:
        pg.quit()

    animal.score = animal.compute_objective()
    print(f"Animal Score: {animal.score}, ID: {animal.id}, Parents: {animal.parents}")
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
    population_size: int = 80
    dna_len: int = 26
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
        result = [pool.apply_async(run_animal, (dna_len, animal.dna, iterations, display,animal.parents)) for animal in population]
        population = sorted([r.get() for r in result], key=lambda x: x.score, reverse=True)


    print("Simulation finished. Best animal:", population[0].dump())


if __name__ == "__main__":
    run_simulation()
    


