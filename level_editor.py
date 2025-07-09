import pygame
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import json
import os

# Constants
TILE_SIZE = 32
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
UI_HEIGHT = 50  # Space at top for buttons
GRID_WIDTH = SCREEN_WIDTH
GRID_HEIGHT = SCREEN_HEIGHT - UI_HEIGHT

FPS = 60

# Tile info
TILE_TYPES = {
    "G": (50, 200, 50),    # Ground
    "W": (50, 50, 200),    # Water
    "P": (150, 75, 0),     # Platform
    "E": (200, 0, 0),      # Enemy
    "C": (255, 215, 0),    # Coin
    "S": (255, 255, 255),  # Spike
    " ": (0, 0, 0),        # Empty space
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

# Keyboard shortcuts for tiles 1-7
SHORTCUT_KEYS = {
    pygame.K_1: "G",
    pygame.K_2: "W",
    pygame.K_3: "P",
    pygame.K_4: "E",
    pygame.K_5: "C",
    pygame.K_6: "S",
    pygame.K_7: " ",
}

class Button:
    def __init__(self, rect, text, callback, font, bg=(100,100,100), fg=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg = bg
        self.fg = fg
        self.hover = False

    def draw(self, surface):
        color = (150,150,150) if self.hover else self.bg
        pygame.draw.rect(surface, color, self.rect)
        label = self.font.render(self.text, True, self.fg)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

class LevelEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Mario-style Level Editor")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)

        self.cols = GRID_WIDTH // TILE_SIZE
        self.rows = GRID_HEIGHT // TILE_SIZE

        self.grid = [[" " for _ in range(self.cols)] for _ in range(self.rows)]

        # Undo/redo stacks
        self.undo_stack = []
        self.redo_stack = []

        self.selected_tile = "G"
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = UI_HEIGHT  # start below UI bar

        # UI Buttons
        self.buttons = []
        self.create_buttons()

        # Load tile icons
        self.icons = {}
        for tile in TILE_TYPES:
            path = os.path.join("icons", f"{tile}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.icons[tile] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
            except Exception as e:
                print(f"Failed to load icon {path}: {e}")
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
                surf.fill(TILE_TYPES[tile])
                self.icons[tile] = surf

        # For clickable tile palette positions
        self.tile_icon_rects = []

        # Panning variables
        self.panning = False
        self.pan_start = (0,0)

        # Tk root for dialogs
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()  # Hide main window

    def create_buttons(self):
        btn_w = 100
        btn_h = 30
        padding = 10
        font = pygame.font.SysFont("Arial", 20)
        self.buttons.append(Button((padding, 10, btn_w, btn_h), "Load Level", self.load_level_dialog, font))
        self.buttons.append(Button((padding*2+btn_w, 10, btn_w, btn_h), "Save Level", self.save_level_dialog, font))

    def draw_ui(self):
        pygame.draw.rect(self.screen, (50,50,50), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        for btn in self.buttons:
            btn.draw(self.screen)

        # Draw tile icons on top left for selection
        x = 10 + 220  # offset to right to not overlap buttons
        y = 10
        tile_size = 32
        self.tile_icon_rects.clear()
        for tile in TILE_TYPES:
            img = self.icons.get(tile)
            if img:
                icon = pygame.transform.smoothscale(img, (tile_size, tile_size))
                rect = pygame.Rect(x, y, tile_size, tile_size)
                self.screen.blit(icon, rect.topleft)
                if tile == self.selected_tile:
                    pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 100), rect, 1)
                self.tile_icon_rects.append((rect, tile))
                x += tile_size + 5

        # Text info next to icons
        name = TILE_NAMES.get(self.selected_tile, "Unknown")
        text = self.font.render(f"Selected Tile: {name} ({self.selected_tile}) - Shortcuts 1-7", True, (255,255,255))
        self.screen.blit(text, (x + 10, 15))

    def draw_grid(self):
        self.screen.fill((0, 0, 0), (0, UI_HEIGHT, SCREEN_WIDTH, GRID_HEIGHT))
        tile_size = int(TILE_SIZE * self.zoom)
        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.grid[y][x]
                img = self.icons.get(tile)
                if img:
                    icon = pygame.transform.smoothscale(img, (tile_size, tile_size))
                    self.screen.blit(icon, (x * tile_size + self.offset_x, y * tile_size + self.offset_y))
                rect = pygame.Rect(
                    x * tile_size + self.offset_x,
                    y * tile_size + self.offset_y,
                    tile_size,
                    tile_size,
                )
                pygame.draw.rect(self.screen, (40, 40, 40), rect, 1)

    def grid_pos_from_mouse(self, mx, my):
        tile_size = int(TILE_SIZE * self.zoom)
        gx = int((mx - self.offset_x) / tile_size)
        gy = int((my - self.offset_y) / tile_size)
        if 0 <= gx < self.cols and 0 <= gy < self.rows:
            return gx, gy
        return None

    def place_tile(self, x, y, tile):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            old = self.grid[y][x]
            if old != tile:
                self.grid[y][x] = tile
                self.undo_stack.append((x, y, old, tile))
                self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        x, y, old, new = self.undo_stack.pop()
        self.grid[y][x] = old
        self.redo_stack.append((x, y, old, new))

    def redo(self):
        if not self.redo_stack:
            return
        x, y, old, new = self.redo_stack.pop()
        self.grid[y][x] = new
        self.undo_stack.append((x, y, old, new))

    def load_level_dialog(self):
        path = filedialog.askopenfilename(
            title="Load Level JSON",
            initialdir=os.path.join(os.getcwd(), "levels"),
            filetypes=[("JSON files", "*.json")]
        )
        if path:
            self.load_level(path)

    def save_level_dialog(self):
        filename = simpledialog.askstring("Save Level", "Enter filename (without extension):")
        if filename:
            if not filename.endswith(".json"):
                filename += ".json"
            path = os.path.join(os.getcwd(), "levels", filename)
            self.save_level(path)

    def load_level(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            grid_data = data.get("grid", [])
            for y in range(min(self.rows, len(grid_data))):
                for x in range(min(self.cols, len(grid_data[y]))):
                    self.grid[y][x] = grid_data[y][x]
            self.undo_stack.clear()
            self.redo_stack.clear()
            print(f"Loaded level from {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load level:\n{e}")

    def save_level(self, path):
        try:
            data = {"grid": self.grid}
            with open(path, "w") as f:
                json.dump(data, f)
            print(f"Saved level to {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save level:\n{e}")

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Handle UI buttons first
                    for btn in self.buttons:
                        btn.handle_event(event)

                    # Check if clicked tile icon palette
                    if event.pos[1] <= UI_HEIGHT:
                        for rect, tile in self.tile_icon_rects:
                            if rect.collidepoint(event.pos):
                                self.selected_tile = tile
                                break

                    # Place tile on grid with left click
                    if event.button == 1 and event.pos[1] > UI_HEIGHT:
                        pos = self.grid_pos_from_mouse(*event.pos)
                        if pos:
                            self.place_tile(pos[0], pos[1], self.selected_tile)

                    # Right-click to erase (place empty tile)
                    if event.button == 3 and event.pos[1] > UI_HEIGHT:
                        pos = self.grid_pos_from_mouse(*event.pos)
                        if pos:
                            self.place_tile(pos[0], pos[1], " ")

                    # Middle click to start panning
                    if event.button == 2:
                        self.panning = True
                        self.pan_start = event.pos

                    # Mouse wheel zoom
                    if event.type == pygame.MOUSEWHEEL:
                        old_zoom = self.zoom
                        if event.y > 0:
                            self.zoom = min(3, self.zoom + 0.1)
                        elif event.y < 0:
                            self.zoom = max(0.5, self.zoom - 0.1)
                        # Optional: adjust offset to zoom relative to mouse
                        mx, my = pygame.mouse.get_pos()
                        mx -= self.offset_x
                        my -= self.offset_y
                        scale_change = self.zoom / old_zoom
                        self.offset_x = mx - mx * scale_change + self.offset_x
                        self.offset_y = my - my * scale_change + self.offset_y

                elif event.type == pygame.MOUSEBUTTONUP:
                    # Stop panning
                    if event.button == 2:
                        self.panning = False

                elif event.type == pygame.MOUSEMOTION:
                    # Panning move
                    if self.panning:
                        dx = event.pos[0] - self.pan_start[0]
                        dy = event.pos[1] - self.pan_start[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.pan_start = event.pos

                elif event.type == pygame.KEYDOWN:
                    # Undo
                    if (event.mod & pygame.KMOD_CTRL) and event.key == pygame.K_z:
                        self.undo()
                    # Redo
                    elif (event.mod & pygame.KMOD_CTRL) and event.key == pygame.K_y:
                        self.redo()
                    # Keyboard shortcuts for tiles
                    elif event.key in SHORTCUT_KEYS:
                        self.selected_tile = SHORTCUT_KEYS[event.key]

            self.draw_ui()
            self.draw_grid()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    # Create levels folder if it doesn't exist
    if not os.path.exists("levels"):
        os.makedirs("levels")
    if not os.path.exists("icons"):
        os.makedirs("icons")

    editor = LevelEditor()
    editor.run()
