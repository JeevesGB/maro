# level_editor.py

import pygame
import sys
import os
from settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_TYPES

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + 60))  # Extra space for GUI
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()

ROWS = SCREEN_HEIGHT // TILE_SIZE
COLS = SCREEN_WIDTH // TILE_SIZE
current_tile = "G"  # Default to ground tile

# Initialize grid
grid = [[" " for _ in range(COLS)] for _ in range(ROWS)]

# Store selector rects for clicks
tile_buttons = {}

def draw_grid():
    for y in range(ROWS):
        for x in range(COLS):
            char = grid[y][x]
            color = TILE_TYPES.get(char, (255, 0, 255))  # fallback pink
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (40, 40, 40), rect, 1)

def get_grid_pos(mouse_pos):
    x, y = mouse_pos
    return x // TILE_SIZE, y // TILE_SIZE

def save_level(filename="levels/level1.txt"):
    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(row) + "\n")

def load_level(filename="levels/level1.txt"):
    if not os.path.exists(filename):
        return
    with open(filename, "r") as f:
        lines = f.readlines()
        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                if x < COLS and y < ROWS:
                    grid[y][x] = char

def draw_tile_selector():
    global tile_buttons
    tile_buttons = {}
    padding = 10
    x = padding
    y = SCREEN_HEIGHT + 10

    for key, color in TILE_TYPES.items():
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        if key == current_tile:
            pygame.draw.rect(screen, (0, 255, 255), rect, 4)
        tile_buttons[key] = rect
        x += TILE_SIZE + padding

def handle_selector_click(pos):
    global current_tile
    for key, rect in tile_buttons.items():
        if rect.collidepoint(pos):
            current_tile = key

# --- Main loop ---
running = True
load_level()

while running:
    screen.fill((0, 0, 0))
    draw_grid()
    draw_tile_selector()
    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_level()
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if my < SCREEN_HEIGHT:
                x, y = get_grid_pos((mx, my))
                if event.button == 1:
                    grid[y][x] = current_tile
                elif event.button == 3:
                    grid[y][x] = " "
            else:
                handle_selector_click((mx, my))

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                save_level()
            elif event.key == pygame.K_l:
                load_level()

pygame.quit()
sys.exit()
