# level.py
import pygame
from tile import Tile
from player import Player
from settings import TILE_SIZE

class Level:
    def __init__(self, layout, screen):
        self.screen = screen
        self.tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        self.setup_level(layout)

    def setup_level(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if cell == 'X':
                    tile = Tile(x, y)
                    self.tiles.add(tile)
                elif cell == 'P':
                    player = Player(x, y)
                    self.player.add(player)

    def run(self):
        self.tiles.draw(self.screen)
        self.player.update(self.tiles)
        self.player.draw(self.screen)
