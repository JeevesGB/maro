import pygame
import json
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
UI_HEIGHT = 60
FPS = 60
TILE_SIZE = 32
BRUSH_SIZES = [1, 3, 5]
UNDO_LIMIT = 20

# Colors
COLORS = {
    "background": (30, 30, 30),
    "ui_bg": (45, 45, 45),
    "tile_border": (50, 50, 50),
    "highlight": (255, 255, 0),
    "copy_rect": (0, 255, 255, 100),
    "status_bar_bg": (20, 20, 20),
    "status_text": (200, 200, 200),
    "tooltip_bg": (0, 0, 0),
    "tooltip_text": (255, 255, 255)
}

# Tile definitions: letter, color, name
TILE_TYPES = {
    " ": ((70, 70, 70), "Empty"),
    "G": ((34, 139, 34), "Ground"),
    "W": ((100, 100, 255), "Water"),
    "E": ((255, 0, 0), "Enemy"),
    "C": ((255, 255, 0), "Coin"),
    "S": ((128, 128, 128), "Spike"),
    "#": ((50, 50, 50), "Wall"),
}

ENTITY_TILES = {"E", "C"}

SHORTCUT_KEYS = {
    pygame.K_1: "G",
    pygame.K_2: "W",
    pygame.K_3: "E",
    pygame.K_4: "C",
    pygame.K_5: "S",
    pygame.K_6: "#",
    pygame.K_0: " ",
}

# Helper: Tkinter root for dialogs (hidden)
root = tk.Tk()
root.withdraw()

class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.hovered = False

    def draw(self, screen):
        color = (100, 100, 100) if self.hovered else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect, border_radius=4)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2, border_radius=4)
        text_surf = self.font.render(self.text, True, (230, 230, 230))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

class Tooltip:
    def __init__(self, font):
        self.font = font
        self.text = None
        self.pos = (0, 0)

    def set_text(self, text, pos):
        self.text = text
        self.pos = pos

    def clear(self):
        self.text = None

    def draw(self, screen):
        if self.text:
            surf = self.font.render(self.text, True, COLORS["tooltip_text"])
            padding = 4
            bg_rect = pygame.Rect(self.pos[0], self.pos[1] - surf.get_height() - 6, surf.get_width() + padding * 2, surf.get_height() + padding)
            pygame.draw.rect(screen, COLORS["tooltip_bg"], bg_rect, border_radius=4)
            screen.blit(surf, (bg_rect.x + padding, bg_rect.y + padding // 2))

class EntityPropertyEditor:
    # Custom simple modal for editing enemy or coin properties
    def __init__(self, screen, font, tile_type, initial_props):
        self.screen = screen
        self.font = font
        self.tile_type = tile_type
        self.props = dict(initial_props)
        self.running = True
        self.result = None
        self.inputs = {}
        self.active_input = None
        self.message = ""

        # Setup UI rects and input fields based on tile type
        self.rect = pygame.Rect(150, 150, 400, 220)
        self.fields = []
        if tile_type == "E":
            self.fields = [
                {"label": "Health (1-1000)", "key": "health", "type": int, "min":1, "max":1000},
                {"label": "Speed (0.1-10.0)", "key": "speed", "type": float, "min":0.1, "max":10.0},
            ]
        elif tile_type == "C":
            self.fields = [
                {"label": "Value (1-100)", "key": "value", "type": int, "min":1, "max":100},
            ]
        # Initialize input text strings
        for f in self.fields:
            val = self.props.get(f["key"], "")
            self.inputs[f["key"]] = str(val)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.result = None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        self.result = None
                    elif event.key == pygame.K_RETURN:
                        if self.validate_and_save():
                            self.running = False
                    elif self.active_input is not None:
                        key = event.key
                        if key == pygame.K_BACKSPACE:
                            self.inputs[self.active_input] = self.inputs[self.active_input][:-1]
                        elif key == pygame.K_MINUS or key == pygame.K_PERIOD or (pygame.K_0 <= key <= pygame.K_9):
                            # Accept digits, minus, dot
                            char = event.unicode
                            self.inputs[self.active_input] += char
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if self.rect.collidepoint(mx, my):
                        # Check which input field clicked
                        y_start = self.rect.y + 40
                        for i, f in enumerate(self.fields):
                            input_rect = pygame.Rect(self.rect.x + 200, y_start + i*40, 180, 30)
                            if input_rect.collidepoint(mx, my):
                                self.active_input = f["key"]
                                break
                        else:
                            self.active_input = None
                    else:
                        self.active_input = None
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)
        return self.result

    def validate_and_save(self):
        # Validate all inputs according to their type and min/max
        new_props = {}
        try:
            for f in self.fields:
                raw = self.inputs.get(f["key"], "").strip()
                if f["type"] == int:
                    val = int(raw)
                elif f["type"] == float:
                    val = float(raw)
                else:
                    val = raw
                if "min" in f and val < f["min"]:
                    self.message = f"{f['label']} must be ≥ {f['min']}"
                    return False
                if "max" in f and val > f["max"]:
                    self.message = f"{f['label']} must be ≤ {f['max']}"
                    return False
                new_props[f["key"]] = val
            self.result = new_props
            return True
        except Exception as e:
            self.message = "Invalid input"
            return False

    def draw(self):
        self.screen.fill((0,0,0))
        # Dim background
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Window
        pygame.draw.rect(self.screen, COLORS["ui_bg"], self.rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS["highlight"], self.rect, 3, border_radius=8)

        # Title
        title_surf = self.font.render(f"Edit {self.tile_type} Properties", True, (255, 255, 255))
        self.screen.blit(title_surf, (self.rect.x + 20, self.rect.y + 10))

        # Draw fields and input boxes
        y_start = self.rect.y + 40
        for i, f in enumerate(self.fields):
            label_surf = self.font.render(f["label"], True, (200, 200, 200))
            self.screen.blit(label_surf, (self.rect.x + 20, y_start + i*40))
            input_rect = pygame.Rect(self.rect.x + 200, y_start + i*40, 180, 30)
            pygame.draw.rect(self.screen, (80, 80, 80), input_rect, border_radius=4)
            if self.active_input == f["key"]:
                pygame.draw.rect(self.screen, COLORS["highlight"], input_rect, 2, border_radius=4)
            text_surf = self.font.render(self.inputs.get(f["key"], ""), True, (230, 230, 230))
            self.screen.blit(text_surf, (input_rect.x + 5, input_rect.y + 5))

        # Instructions
        inst_surf = self.font.render("Enter=Save  ESC=Cancel", True, (150, 150, 150))
        self.screen.blit(inst_surf, (self.rect.x + 20, self.rect.bottom - 30))

        # Error message
        if self.message:
            msg_surf = self.font.render(self.message, True, (255, 100, 100))
            self.screen.blit(msg_surf, (self.rect.x + 20, self.rect.bottom - 60))


class LevelEditor:
    def __init__(self):
        pygame.display.set_caption("Polished Level Editor")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.cols, self.rows = 30, 20
        self.grid = [[" " for _ in range(self.cols)] for _ in range(self.rows)]
        self.entity_properties = {}

        self.selected_tile = "G"
        self.brush_index = 0
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = UI_HEIGHT

        self.panning = False
        self.pan_start = (0, 0)

        self.undo_stack = []
        self.redo_stack = []

        self.buttons = []
        self.font = pygame.font.SysFont("consolas", 20)
        self.font_small = pygame.font.SysFont("consolas", 16)

        # Create buttons
        btn_w, btn_h = 90, 30
        spacing = 10
        x_start = spacing
        y_start = (UI_HEIGHT - btn_h) // 2

        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Load", self.load_level_dialog, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Save", self.save_level_dialog, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Undo", self.undo, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Redo", self.redo, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Resize", self.resize_grid_dialog, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Help", self.show_help, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Copy", self.start_copy_mode, self.font))
        x_start += btn_w + spacing
        self.buttons.append(Button((x_start, y_start, btn_w, btn_h), "Paste", self.paste_clipboard, self.font))

        # Clipboard for copy/paste
        self.copy_mode = False
        self.copy_rect = None
        self.copy_start = None
        self.clipboard = None

        self.tooltip = Tooltip(self.font_small)

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            grid_x, grid_y = self.screen_to_grid(*mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Check UI buttons first
                        for b in self.buttons:
                            b.handle_event(event)
                        if not any(b.rect.collidepoint(event.pos) for b in self.buttons):
                            if self.copy_mode:
                                # If copying, finalize copy rect
                                if self.copy_start is None:
                                    self.copy_start = (grid_x, grid_y)
                                else:
                                    x1, y1 = self.copy_start
                                    x2, y2 = grid_x, grid_y
                                    rx, ry = min(x1,x2), min(y1,y2)
                                    rw, rh = abs(x2-x1)+1, abs(y2-y1)+1
                                    self.copy_rect = (rx, ry, rw, rh)
                                    self.make_clipboard()
                                    self.copy_mode = False
                                    self.copy_start = None
                            else:
                                self.save_undo()
                                self.paint_tiles(grid_x, grid_y)

                    elif event.button == 3:
                        # Right click to erase
                        if not any(b.rect.collidepoint(event.pos) for b in self.buttons):
                            self.save_undo()
                            self.paint_tiles(grid_x, grid_y, erase=True)

                    elif event.button == 2:
                        # Middle mouse button to pan
                        self.panning = True
                        self.pan_start = event.pos

                    elif event.button == 4:
                        # Scroll up = zoom in
                        self.zoom = min(3.0, self.zoom + 0.1)

                    elif event.button == 5:
                        # Scroll down = zoom out
                        self.zoom = max(0.5, self.zoom - 0.1)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:
                        self.panning = False

                elif event.type == pygame.MOUSEMOTION:
                    for b in self.buttons:
                        b.handle_event(event)
                    if self.panning:
                        dx = event.pos[0] - self.pan_start[0]
                        dy = event.pos[1] - self.pan_start[1]
                        self.offset_x += dx
                        self.offset_y += dy
                        self.pan_start = event.pos

                    if pygame.mouse.get_pressed()[0]:
                        if not any(b.rect.collidepoint(event.pos) for b in self.buttons) and not self.copy_mode:
                            self.save_undo()
                            self.paint_tiles(grid_x, grid_y)

                    # Tooltip update
                    tile = self.get_tile(grid_x, grid_y)
                    tile_name = TILE_TYPES.get(tile, ("?", "Unknown"))[1]
                    if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                        self.tooltip.set_text(f"{tile_name} ({tile})", (event.pos[0], event.pos[1]))
                    else:
                        self.tooltip.clear()

                elif event.type == pygame.KEYDOWN:
                    if event.key in SHORTCUT_KEYS:
                        self.selected_tile = SHORTCUT_KEYS[event.key]
                    elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.undo()
                    elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.redo()
                    elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.start_copy_mode()
                    elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        self.paste_clipboard()
                    elif event.key == pygame.K_ESCAPE:
                        self.copy_mode = False
                        self.copy_start = None

                    elif event.key == pygame.K_b:
                        self.brush_index = (self.brush_index + 1) % len(BRUSH_SIZES)

                    elif event.key == pygame.K_e:
                        # Edit properties of entity tile under mouse
                        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                            tile = self.get_tile(grid_x, grid_y)
                            if tile in ENTITY_TILES:
                                current_props = self.entity_properties.get((grid_x, grid_y), {})
                                editor = EntityPropertyEditor(self.screen, self.font, tile, current_props)
                                new_props = editor.run()
                                if new_props is not None:
                                    self.entity_properties[(grid_x, grid_y)] = new_props
                                else:
                                    print("Edit cancelled")

            self.clamp_offset()
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def screen_to_grid(self, sx, sy):
        gx = int((sx - self.offset_x) / (TILE_SIZE * self.zoom))
        gy = int((sy - self.offset_y) / (TILE_SIZE * self.zoom))
        return gx, gy

    def get_tile(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return None

    def set_tile(self, x, y, tile):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = tile
            if tile not in ENTITY_TILES:
                self.entity_properties.pop((x, y), None)

    def paint_tiles(self, x, y, erase=False):
        brush_size = BRUSH_SIZES[self.brush_index]
        half = brush_size // 2
        tile = " " if erase else self.selected_tile
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                self.set_tile(x + dx, y + dy, tile)

    def draw(self):
        self.screen.fill(COLORS["background"])
        # Draw grid tiles
        tile_area = pygame.Rect(0, self.offset_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.offset_y)
        for y in range(self.rows):
            for x in range(self.cols):
                tile = self.grid[y][x]
                color = TILE_TYPES.get(tile, ((255, 255, 255), "Unknown"))[0]
                rect = pygame.Rect(
                    self.offset_x + x * TILE_SIZE * self.zoom,
                    self.offset_y + y * TILE_SIZE * self.zoom,
                    TILE_SIZE * self.zoom,
                    TILE_SIZE * self.zoom,
                )
                if tile_area.colliderect(rect):
                    pygame.draw.rect(self.screen, color, rect)
                    pygame.draw.rect(self.screen, COLORS["tile_border"], rect, 1)

                    # Draw brush indicator on selected tile in palette (below)
                    if tile == self.selected_tile:
                        pygame.draw.rect(self.screen, COLORS["highlight"], rect, 3)

                    # Draw entities with a red overlay
                    if (x, y) in self.entity_properties:
                        pygame.draw.rect(self.screen, (255, 0, 0, 100), rect, 3)

        # Draw grid lines (optional)
        # for x in range(self.cols + 1):
        #     sx = self.offset_x + x * TILE_SIZE * self.zoom
        #     pygame.draw.line(self.screen, (80, 80, 80), (sx, self.offset_y), (sx, self.offset_y + self.rows * TILE_SIZE * self.zoom))
        # for y in range(self.rows + 1):
        #     sy = self.offset_y + y * TILE_SIZE * self.zoom
        #     pygame.draw.line(self.screen, (80, 80, 80), (self.offset_x, sy), (self.offset_x + self.cols * TILE_SIZE * self.zoom, sy))

        # Draw copy rectangle if copying
        if self.copy_mode and self.copy_start:
            mx, my = pygame.mouse.get_pos()
            gx, gy = self.screen_to_grid(mx, my)
            x1, y1 = self.copy_start
            x2, y2 = gx, gy
            rx, ry = min(x1,x2), min(y1,y2)
            rw, rh = abs(x2 - x1) + 1, abs(y2 - y1) + 1
            r = pygame.Rect(
                self.offset_x + rx * TILE_SIZE * self.zoom,
                self.offset_y + ry * TILE_SIZE * self.zoom,
                rw * TILE_SIZE * self.zoom,
                rh * TILE_SIZE * self.zoom,
            )
            s = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            s.fill(COLORS["copy_rect"])
            self.screen.blit(s, r.topleft)
            pygame.draw.rect(self.screen, COLORS["highlight"], r, 2)

        # Draw tile palette UI
        self.draw_palette()

        # Draw UI buttons
        pygame.draw.rect(self.screen, COLORS["ui_bg"], (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        for b in self.buttons:
            b.draw(self.screen)

        # Draw status bar
        self.draw_status_bar()

        # Draw tooltip
        self.tooltip.draw(self.screen)

    def draw_palette(self):
        # Draw tile selection palette below main grid area (bottom 60 px)
        y = SCREEN_HEIGHT - 60
        x = 10
        size = 40
        for tile_char, (color, name) in TILE_TYPES.items():
            rect = pygame.Rect(x, y + 10, size, size)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)
            if tile_char == self.selected_tile:
                pygame.draw.rect(self.screen, COLORS["highlight"], rect, 4)
            x += size + 10

            # Draw letter
            letter_surf = self.font.render(tile_char, True, (0, 0, 0))
            letter_rect = letter_surf.get_rect(center=rect.center)
            self.screen.blit(letter_surf, letter_rect)

            # Tooltips are handled in main loop on mouse hover

    def draw_status_bar(self):
        rect = pygame.Rect(0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT)
        pygame.draw.rect(self.screen, COLORS["status_bar_bg"], rect)
        status_text = (
            f"Selected: {self.selected_tile} ({TILE_TYPES[self.selected_tile][1]}) | "
            f"Brush Size: {BRUSH_SIZES[self.brush_index]} | Zoom: {self.zoom:.2f} | "
            f"Grid Size: {self.cols}x{self.rows} | "
            "Ctrl+Z Undo, Ctrl+Y Redo, Ctrl+C Copy, Ctrl+V Paste, ESC Cancel Copy"
        )
        surf = self.font_small.render(status_text, True, COLORS["status_text"])
        self.screen.blit(surf, (10, SCREEN_HEIGHT - UI_HEIGHT + 20))

    def clamp_offset(self):
        # Clamp offset to avoid showing blank outside grid
        grid_width = self.cols * TILE_SIZE * self.zoom
        grid_height = self.rows * TILE_SIZE * self.zoom
        self.offset_x = max(min(self.offset_x, SCREEN_WIDTH - 50), SCREEN_WIDTH - grid_width - 50)
        self.offset_y = max(min(self.offset_y, SCREEN_HEIGHT - 50), UI_HEIGHT)

    def save_undo(self):
        if len(self.undo_stack) >= UNDO_LIMIT:
            self.undo_stack.pop(0)
        # Deep copy grid and entity_properties
        grid_copy = [row[:] for row in self.grid]
        entity_copy = dict(self.entity_properties)
        self.undo_stack.append((grid_copy, entity_copy))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append((self.grid, self.entity_properties))
            self.grid, self.entity_properties = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append((self.grid, self.entity_properties))
            self.grid, self.entity_properties = self.redo_stack.pop()

    def load_level_dialog(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if not file_path:
                return
            with open(file_path, "r") as f:
                data = json.load(f)
            self.grid = data["grid"]
            self.cols = len(self.grid[0])
            self.rows = len(self.grid)
            self.entity_properties = {tuple(map(int,k.split(","))):v for k,v in data.get("entities", {}).items()}
            self.offset_x = 0
            self.offset_y = UI_HEIGHT
            self.undo_stack.clear()
            self.redo_stack.clear()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load level:\n{e}")

    def save_level_dialog(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if not file_path:
                return
            data = {
                "grid": self.grid,
                "entities": {f"{k[0]},{k[1]}": v for k, v in self.entity_properties.items()}
            }
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save level:\n{e}")

    def resize_grid_dialog(self):
        try:
            new_cols = simpledialog.askinteger("Resize Grid", "New width (columns):", initialvalue=self.cols, minvalue=5, maxvalue=100)
            if new_cols is None:
                return
            new_rows = simpledialog.askinteger("Resize Grid", "New height (rows):", initialvalue=self.rows, minvalue=5, maxvalue=100)
            if new_rows is None:
                return

            new_grid = [[" " for _ in range(new_cols)] for _ in range(new_rows)]
            new_entity_props = {}

            for y in range(min(self.rows, new_rows)):
                for x in range(min(self.cols, new_cols)):
                    new_grid[y][x] = self.grid[y][x]
                    if (x, y) in self.entity_properties:
                        new_entity_props[(x, y)] = self.entity_properties[(x, y)]

            self.grid = new_grid
            self.cols = new_cols
            self.rows = new_rows
            self.entity_properties = new_entity_props
            self.offset_x = 0
            self.offset_y = UI_HEIGHT
        except Exception as e:
            messagebox.showerror("Error", f"Failed to resize grid:\n{e}")

    def show_help(self):
        messagebox.showinfo("Help",
            "Level Editor Controls:\n"
            "- Left Click: Paint selected tile\n"
            "- Right Click: Erase tile\n"
            "- Mouse Wheel: Zoom\n"
            "- Middle Mouse Drag: Pan\n"
            "- Number Keys 1-6: Select tile type\n"
            "- B: Change brush size\n"
            "- E: Edit entity properties on tile\n"
            "- Ctrl+Z: Undo\n"
            "- Ctrl+Y: Redo\n"
            "- Ctrl+C: Copy area\n"
            "- Ctrl+V: Paste clipboard\n"
            "- ESC: Cancel copy mode"
        )

    def start_copy_mode(self):
        self.copy_mode = True
        self.copy_start = None
        self.copy_rect = None

    def make_clipboard(self):
        if not self.copy_rect:
            return
        rx, ry, rw, rh = self.copy_rect
        self.clipboard = []
        for y in range(ry, ry + rh):
            row = []
            for x in range(rx, rx + rw):
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    row.append(self.grid[y][x])
                else:
                    row.append(" ")
            self.clipboard.append(row)

        # Also copy entities inside region
        self.clipboard_entities = {}
        for (ex, ey), props in self.entity_properties.items():
            if rx <= ex < rx + rw and ry <= ey < ry + rh:
                self.clipboard_entities[(ex - rx, ey - ry)] = props

    def paste_clipboard(self):
        if not self.clipboard:
            return
        mx, my = pygame.mouse.get_pos()
        gx, gy = self.screen_to_grid(mx, my)

        self.save_undo()

        for y, row in enumerate(self.clipboard):
            for x, tile in enumerate(row):
                tx, ty = gx + x, gy + y
                if 0 <= tx < self.cols and 0 <= ty < self.rows:
                    self.grid[ty][tx] = tile
                    # Remove old entity if present
                    if (tx, ty) in self.entity_properties:
                        self.entity_properties.pop((tx, ty))
        for (ex, ey), props in self.clipboard_entities.items():
            nx, ny = gx + ex, gy + ey
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                self.entity_properties[(nx, ny)] = props

        self.copy_mode = False
        self.copy_start = None
        self.copy_rect = None

class EntityPropertyEditor:
    def __init__(self, screen, font, tile_type, current_props):
        self.screen = screen
        self.font = font
        self.tile_type = tile_type
        self.current_props = current_props.copy()
        self.result = None

        self.width = 400
        self.height = 300
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) // 2,
            (SCREEN_HEIGHT - self.height) // 2,
            self.width, self.height
        )

        self.active_input = None
        self.inputs = {}
        self.buttons = []
        self.done = False

        # Define properties per tile type
        self.props_def = {
            "E": ["name", "health", "damage"],
            "M": ["direction", "speed"],
            # Add more entity tile types as needed
        }

        self.create_ui()

    def create_ui(self):
        y = self.rect.top + 40
        x = self.rect.left + 20
        spacing = 40
        prop_names = self.props_def.get(self.tile_type, [])

        for prop in prop_names:
            label_surf = self.font.render(prop.capitalize() + ":", True, (255, 255, 255))
            label_rect = label_surf.get_rect(topleft=(x, y))
            self.inputs[prop] = {"rect": pygame.Rect(x + 100, y, 250, 30), "text": str(self.current_props.get(prop, ""))}
            y += spacing

        self.buttons.append(Button((self.rect.left + 70, self.rect.bottom - 60, 100, 40), "OK", self.ok, self.font))
        self.buttons.append(Button((self.rect.left + 220, self.rect.bottom - 60, 100, 40), "Cancel", self.cancel, self.font))

    def run(self):
        clock = pygame.time.Clock()
        while not self.done:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                    self.result = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # Check buttons
                    for b in self.buttons:
                        b.handle_event(event)
                    # Check inputs
                    for prop, data in self.inputs.items():
                        if data["rect"].collidepoint(pos):
                            self.active_input = prop
                            break
                    else:
                        self.active_input = None
                elif event.type == pygame.KEYDOWN:
                    if self.active_input:
                        if event.key == pygame.K_BACKSPACE:
                            self.inputs[self.active_input]["text"] = self.inputs[self.active_input]["text"][:-1]
                        elif event.key == pygame.K_RETURN:
                            self.ok()
                        else:
                            self.inputs[self.active_input]["text"] += event.unicode

            self.draw()
            pygame.display.flip()
        return self.result

    def draw(self):
        # Draw modal background
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(220)
        s.fill((50, 50, 50))
        self.screen.blit(s, self.rect.topleft)

        # Draw title
        title_surf = self.font.render(f"Edit {self.tile_type} Properties", True, (255, 255, 255))
        self.screen.blit(title_surf, (self.rect.left + 20, self.rect.top + 10))

        # Draw inputs
        for prop, data in self.inputs.items():
            label_surf = self.font.render(prop.capitalize() + ":", True, (255, 255, 255))
            self.screen.blit(label_surf, (data["rect"].left - 100, data["rect"].top + 5))

            input_rect = data["rect"]
            pygame.draw.rect(self.screen, (255, 255, 255), input_rect, 2)
            text_surf = self.font.render(data["text"], True, (255, 255, 255))
            self.screen.blit(text_surf, (input_rect.left + 5, input_rect.top + 5))

            if self.active_input == prop:
                pygame.draw.rect(self.screen, (255, 255, 0), input_rect, 2)

        # Draw buttons
        for b in self.buttons:
            b.draw(self.screen)

    def ok(self):
        props = {}
        for prop, data in self.inputs.items():
            props[prop] = data["text"]
        self.result = props
        self.done = True

    def cancel(self):
        self.result = None
        self.done = True

class Button:
    def __init__(self, rect, text, callback, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.callback()

    def draw(self, surface):
        color = (100, 100, 100) if not self.hovered else (150, 150, 150)
        pygame.draw.rect(surface, color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class Tooltip:
    def __init__(self, font):
        self.font = font
        self.text = ""
        self.pos = (0, 0)
        self.visible = False

    def set_text(self, text, pos):
        self.text = text
        self.pos = pos
        self.visible = True

    def clear(self):
        self.visible = False

    def draw(self, surface):
        if self.visible and self.text:
            text_surf = self.font.render(self.text, True, (255, 255, 255))
            bg_rect = text_surf.get_rect(topleft=(self.pos[0] + 10, self.pos[1] + 10))
            pygame.draw.rect(surface, (50, 50, 50), bg_rect.inflate(6, 6))
            surface.blit(text_surf, (self.pos[0] + 13, self.pos[1] + 13))

if __name__ == "__main__":
    editor = LevelEditor()
    editor.run()
