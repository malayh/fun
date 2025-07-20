import pygame as pg
import numpy as np
import sys

WINDOW_SIZE = (2000, 1600)
# WINDOW_SIZE = (3840, 2160)

class GameOfLife:
    def __init__(self, grid_dim_x: int, grid_dim_y: int):
        self.grid_dim_x = grid_dim_x
        self.grid_dim_y = grid_dim_y
        self.state = np.zeros((self.grid_dim_x, self.grid_dim_y), dtype=np.int8)

    def count_alive_neighbors(self, x: int, y: int) -> int:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        count = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_dim_x and 0 <= ny < self.grid_dim_y:
                count += self.state[nx][ny]

        return count
    
    def compute_next_state(self) -> np.ndarray:
        new_state = np.zeros((self.grid_dim_x, self.grid_dim_y), dtype=np.int8)
         
        for x in range(self.grid_dim_x):
            for y in range(self.grid_dim_y):
                alive_neighbors = self.count_alive_neighbors(x, y) 
                # live cell rules
                if self.state[x][y] == 1:
                    # underpopulation and overpopulation rules
                    if alive_neighbors < 2 or alive_neighbors > 3:
                        new_state[x][y] = 0
                    # survival rule
                    else:
                        new_state[x][y] = 1
                # dead cell rules
                else:
                    # reproduction rule
                    if alive_neighbors == 3:
                        new_state[x][y] = 1

        return new_state

    
class GameOfLifeDrawer:
    @staticmethod
    def get_grid_dims(window_x: int, window_y: int, cell_size: int) -> tuple:
        return window_x // cell_size, window_y // cell_size
    
    def __init__(self, game: GameOfLife, window_size: tuple = WINDOW_SIZE, cell_size: int = 8):
        self.game = game

        self.window_size = window_size
        self.cell_size = cell_size
        
        pg.init()
        self.screen = pg.display.set_mode(window_size)


    def activate_cell(self, x: int, y: int):
        if 0 <= x < self.game.grid_dim_x and 0 <= y < self.game.grid_dim_y:
            cell_rect = pg.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            pg.draw.rect(self.screen, (255, 255, 255), cell_rect)

        
    def deactivate_cell(self, x: int, y: int):
        if 0 <= x < self.game.grid_dim_x and 0 <= y < self.game.grid_dim_y:
            cell_rect = pg.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            pg.draw.rect(self.screen, (0, 0, 0), cell_rect)

    def draw_state(self):
        for x in range(self.game.grid_dim_x):
            for y in range(self.game.grid_dim_y):
                if self.game.state[x][y] == 1:
                    self.activate_cell(x, y)
                else:
                    self.deactivate_cell(x, y)


    def draw(self, iterations: int = 100_00):
        running = True

        while running and iterations > 0:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            self.draw_state()
            pg.display.flip()
            self.game.state = self.game.compute_next_state()
            iterations -= 1

        pg.quit()
        


def setup_glider(state, x: int, y: int):
    glider_pattern = [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
    ]
    for dx, dy in glider_pattern:
        if 0 <= x + dx < len(state) and 0 <= y + dy < len(state[0]):
            state[x + dx][y + dy] = 1

def setup_pulsar(state, x: int, y: int):
    pulsar_pattern = [
        (0, 2), (0, 3), (0, 4), (0, 5), (0, 6),
        (1, 1), (1, 7),
        (2, 0), (2, 8),
        (3, 1), (3, 7),
        (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
        (5, 1), (5, 7),
        (6, 0), (6, 8),
        (7, 1), (7, 7),
        (8, 2), (8, 3), (8, 4), (8, 5), (8, 6)
    ]
    for dx, dy in pulsar_pattern:
        if 0 <= x + dx < len(state) and 0 <= y + dy < len(state[0]):
            state[x + dx][y + dy] = 1 
        
def setup_random(state, x: int, y: int):
    import random
    for i in range(x):
        for j in range(y):
            state[i][j] = random.randint(0, 1)

def setup_glider_gun(state, x: int, y: int):
    pattern = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1], [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]]

    for dx, row in enumerate(pattern):
        for dy, cell in enumerate(row):
            if cell == 1:
                if 0 <= x + dx < len(state) and 0 <= y + dy < len(state[0]):
                    state[x + dx][y + dy] = 1
    


def main():
    cell_size = 10
    game = GameOfLife(*GameOfLifeDrawer.get_grid_dims(*WINDOW_SIZE, cell_size))
    drawer = GameOfLifeDrawer(game, window_size=WINDOW_SIZE, cell_size=cell_size)

    # setup_glider_gun(game.state, 10, 10)

    for i in range(game.grid_dim_x):
        setup_pulsar(game.state, i, 0)

    for i in range(game.grid_dim_x):
        setup_glider(game.state,0,game.grid_dim_x-i)

    for i in range(game.grid_dim_y):
        setup_pulsar(game.state, game.grid_dim_y - 1, i)

    for i in range(game.grid_dim_y):
        setup_glider(game.state, game.grid_dim_y - 1, game.grid_dim_y - i - 1)

    drawer.draw()
    


if __name__ == "__main__":
    main()
