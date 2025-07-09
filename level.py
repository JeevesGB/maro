import pygame
from tile import Tile
from player import Player
from enemy import Enemy
from hud import draw_hud

class Level:
    def __init__(self, layout, surface):
        self.display_surface = surface
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        self.player = None

        self.setup_level(layout)

    def setup_level(self, layout):
        colors = {
            "G": (50, 200, 50),
            "P": (150, 75, 0),
            "C": (255, 215, 0),
        }

        for row_index, row in enumerate(layout):
            for col_index, cell in enumerate(row):
                x = col_index * 32
                y = row_index * 32

                if cell in ["G", "P"]:
                    self.tiles.add(Tile(x, y, colors[cell]))
                elif cell == "C":
                    coin = Tile(x, y, colors[cell])
                    self.coins.add(coin)
                elif cell == "E":
                    self.enemies.add(Enemy(x, y))
                elif cell == " ":
                    continue
                elif cell == "S":
                    self.tiles.add(Tile(x, y, (255, 255, 255)))
                elif cell == "M":  # Player start
                    self.player = Player(x, y)

        if not self.player:
            self.player = Player(100, 100)

    def run(self):
        self.tiles.draw(self.display_surface)
        self.coins.draw(self.display_surface)
        self.enemies.draw(self.display_surface)

        self.player.update(self.tiles)
        self.display_surface.blit(self.player.image, self.player.rect)

        self.handle_collisions()

        draw_hud(self.display_surface, self.player)

    def handle_collisions(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.health -= 1
                if self.player.health <= 0:
                    self.player.lives -= 1
                    self.player.health = 100

        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        self.player.score += len(hit_coins) * 10
