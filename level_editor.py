import pygame
import tkinter as tk
from tkinter import filedialog
import os
import sys

pygame.init()

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 650  # increased height for spacing
BUTTON_HEIGHT = 50
BUTTON_PADDING = 15
GRID_TOP = BUTTON_HEIGHT + 30  # space below buttons for grid start
GRID_WIDTH, GRID_HEIGHT = 20, 15  # grid cells

# Physics/game constants (unused here but good for your game)
GRAVITY = 0.8
PLAYER_SPEED = 5
JUMP_POWER = 15

# Tiles and colors
TILE_TYPES = {
    "G": (50, 200, 50),    # Ground
    "W": (50, 50, 200),    # Water
    "P": (150, 75, 0),     # Platform
    "E": (200, 0, 0),      # Enemy
    "C": (255, 215, 0),    # Coin
    "S": (255, 255, 255),  # Spike
    " ": (0, 0, 0),        # Empty space (black)
}

TILE_NAMES = {
    "G": "Ground",
    "W": "Water",
    "P": "Platform",
    "E": "Enemy",
    "C": "Coin",
    "S": "Spike",
    " ": "Empty",
}

# Setup display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")

font = pygame.font.SysFont(None, 28)  # bigger font for readability

# Create levels folder if not exists
LEVELS_DIR = "levels"
if not os.path.exists(LEVELS_DIR):
    os.makedirs(LEVELS_DIR)

# Initialize grid with empty spaces
grid = [[" " for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Current tile selected
current_tile = "G"

# Tkinter root for dialogs
root = tk.Tk()
root.withdraw()  # Hide the main window


# Button class for UI buttons
class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = (200, 200, 200)
        self.hover_color = (0, 120, 215)
        self.text_surf = font.render(text, True, (0, 0, 0))

    def draw(self, surf):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        text_rect = self.text_surf.get_rect(center=self.rect.center)
        surf.blit(self.text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# Buttons at top, spaced out nicely
button_width = 140
save_button = Button(BUTTON_PADDING, 10, button_width, BUTTON_HEIGHT - 20, "Save Level")
load_button = Button(BUTTON_PADDING * 2 + button_width, 10, button_width, BUTTON_HEIGHT - 20, "Load Level")

# Tile selector buttons - spaced with labels below
tile_buttons = []
tile_button_size = 40
tile_button_y = 10
tile_x_start = SCREEN_WIDTH - (len(TILE_TYPES) * (tile_button_size + 15)) - 10
for i, tile_char in enumerate(TILE_TYPES.keys()):
    rect = pygame.Rect(tile_x_start + i * (tile_button_size + 15), tile_button_y, tile_button_size, tile_button_size)
    tile_buttons.append((rect, tile_char))


def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile_char = grid[y][x]
            color = TILE_TYPES.get(tile_char, (0, 0, 0))
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + GRID_TOP, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 1)  # white grid lines


def save_level():
    file_path = filedialog.asksaveasfilename(
        title="Save Level",
        initialdir=os.path.abspath(LEVELS_DIR),
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt")],
    )
    if file_path:
        if not os.path.abspath(file_path).startswith(os.path.abspath(LEVELS_DIR)):
            print("Please save inside the levels folder.")
            return
        try:
            with open(file_path, "w") as f:
                for row in grid:
                    f.write("".join(row) + "\n")
            print(f"Level saved to {file_path}")
        except Exception as e:
            print("Error saving level:", e)


def load_level():
    file_path = filedialog.askopenfilename(
        title="Load Level",
        initialdir=os.path.abspath(LEVELS_DIR),
        filetypes=[("Text Files", "*.txt")],
    )
    if file_path:
        if not os.path.abspath(file_path).startswith(os.path.abspath(LEVELS_DIR)):
            print("Please load from the levels folder.")
            return
        try:
            with open(file_path, "r") as f:
                lines = f.readlines()
                for y in range(min(GRID_HEIGHT, len(lines))):
                    line = lines[y].rstrip("\n")
                    for x in range(min(GRID_WIDTH, len(line))):
                        if line[x] in TILE_TYPES:
                            grid[y][x] = line[x]
                        else:
                            grid[y][x] = " "
            print(f"Level loaded from {file_path}")
        except Exception as e:
            print("Error loading level:", e)


def main():
    global current_tile
    running = True
    while running:
        screen.fill((30, 30, 30))  # darker background

        # Draw buttons area background
        pygame.draw.rect(screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, BUTTON_HEIGHT))

        # Draw buttons
        save_button.draw(screen)
        load_button.draw(screen)

        # Draw tile selector buttons with labels
        for rect, tile_char in tile_buttons:
            pygame.draw.rect(screen, TILE_TYPES[tile_char], rect, border_radius=6)
            if tile_char == current_tile:
                pygame.draw.rect(screen, (0, 120, 215), rect, 4, border_radius=6)
            else:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)

            # Draw tile name label below button with spacing
            label = font.render(TILE_NAMES[tile_char], True, (220, 220, 220))
            label_rect = label.get_rect(center=(rect.centerx, rect.bottom + 18))
            screen.blit(label, label_rect)

        # Draw grid
        draw_grid()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if save_button.is_clicked(event):
                    save_level()

                elif load_button.is_clicked(event):
                    load_level()

                else:
                    # Check tile selector clicks
                    for rect, tile_char in tile_buttons:
                        if rect.collidepoint(event.pos):
                            current_tile = tile_char
                            break
                    else:
                        # Click inside grid area
                        x, y = event.pos
                        if y >= GRID_TOP:
                            grid_x = x // TILE_SIZE
                            grid_y = (y - GRID_TOP) // TILE_SIZE
                            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                                grid[grid_y][grid_x] = current_tile

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
