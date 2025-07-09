import pygame
from settings import SCREEN_WIDTH

def draw_hud(screen, player):
    font = pygame.font.SysFont("Arial", 24)

    health_bar = pygame.Rect(20, 20, player.health * 2, 20)
    pygame.draw.rect(screen, (255, 0, 0), health_bar)

    lives = font.render(f"Lives: {player.lives}", True, (255, 255, 255))
    screen.blit(lives, (20, 50))

    score = font.render(f"Score: {player.score}", True, (255, 255, 0))
    screen.blit(score, (SCREEN_WIDTH - 150, 20))
