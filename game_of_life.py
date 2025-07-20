import pygame as pg
import sys

WINDOW_SIZE = (2000, 1600)
# WINDOW_SIZE = (3840, 2160)

class GameOfLife:
    def __init__(self, screen, grid_size: int):
        self.screen = screen
        self.grid_size = grid_size

        width, height = self.screen.get_size()
        self.grid_dim_x, self.grid_dim_y = width // self.grid_size, height // self.grid_size

        self.state = [[0 for _ in range(self.grid_dim_y)] for _ in range(self.grid_dim_x)]
        print(f"Grid dimensions: {self.grid_dim_x} x {self.grid_dim_y}")

    def make_grid(self):
        width, height = self.screen.get_size()
        for x in range(0, width, self.grid_size):
            pg.draw.line(self.screen, (20, 20, 20), (x, 0), (x, height))
        for y in range(0, height, self.grid_size):
            pg.draw.line(self.screen, (20, 20, 20), (0, y), (width, y))

        pg.display.flip()
        
        grid_dim_x = width // self.grid_size
        grid_dim_y = height // self.grid_size
        return grid_dim_x, grid_dim_y
    

    def activate_cell(self, x: int, y: int):
        if 0 <= x < self.grid_dim_x and 0 <= y < self.grid_dim_y:
            cell_rect = pg.Rect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
            pg.draw.rect(self.screen, (255, 255, 255), cell_rect)
    
    def deactivate_cell(self, x: int, y: int):
        if 0 <= x < self.grid_dim_x and 0 <= y < self.grid_dim_y:
            cell_rect = pg.Rect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
            pg.draw.rect(self.screen, (0, 0, 0), cell_rect)
    

    def count_alive_neighbors(self, x: int, y: int) -> int:
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        count = 0
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_dim_x and 0 <= ny < self.grid_dim_y:
                count += self.state[nx][ny]

        return count

    def compute_next_state(self):
        new_state = [[0 for _ in range(self.grid_dim_y)] for _ in range(self.grid_dim_x)]
       
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
        self.state = new_state

    def draw_state(self):
        for x in range(self.grid_dim_x):
            for y in range(self.grid_dim_y):
                if self.state[x][y] == 1:
                    self.activate_cell(x, y)
                else:
                    self.deactivate_cell(x, y)

    def run(self):
        running = True
        while running:        
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

            # self.make_grid()
            self.draw_state()
            pg.display.flip()
            self.compute_next_state()

        pg.quit()
        sys.exit()


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
    pg.init()
    screen = pg.display.set_mode(WINDOW_SIZE)
    pg.display.set_caption("Game of Life")

    grid = GameOfLife(screen, 8)

    # setup_random(grid.state, grid.grid_dim_x, grid.grid_dim_y)
    # setup_glider_gun(grid.state, 0, 0)
    # setup_glider_gun(grid.state, 0, 40)
    # setup_glider_gun(grid.state, 0, 80)
    # setup_glider_gun(grid.state, 0, 120)
    # setup_glider_gun(grid.state, 0, 160)

    for i in range(grid.grid_dim_x):
        setup_pulsar(grid.state, i, 0)

    for i in range(grid.grid_dim_x):
        setup_glider(grid.state,0,grid.grid_dim_x-i)

    for i in range(grid.grid_dim_y):
        setup_pulsar(grid.state, grid.grid_dim_y - 1, i)

    for i in range(grid.grid_dim_y):
        setup_glider(grid.state, grid.grid_dim_y - 1, grid.grid_dim_y - i - 1)

    grid.run()


if __name__ == "__main__":
    main()
