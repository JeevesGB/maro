import pygame
from settings import TILE_SIZE, GRAVITY, PLAYER_SPEED, JUMP_POWER, MAX_LIVES

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

        self.direction = pygame.math.Vector2(0, 0)
        self.on_ground = False

        self.health = 100
        self.lives = MAX_LIVES
        self.score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction.x = -PLAYER_SPEED
        elif keys[pygame.K_RIGHT]:
            self.direction.x = PLAYER_SPEED
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.on_ground:
            self.direction.y = -JUMP_POWER
            self.on_ground = False

    def apply_gravity(self):
        self.direction.y += GRAVITY
        self.rect.y += self.direction.y

    def check_collision(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.direction.y > 0:
                    self.rect.bottom = tile.rect.top
                    self.direction.y = 0
                    self.on_ground = True
                elif self.direction.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.direction.y = 0

    def update(self, tiles):
        self.handle_input()
        self.rect.x += self.direction.x
        self.apply_gravity()
        self.check_collision(tiles)
