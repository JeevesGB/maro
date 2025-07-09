import pygame
from settings import TILE_SIZE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((200, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self):
        pass  # Later add movement
