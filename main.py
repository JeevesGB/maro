import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from level import Level
from menu import Menu

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Maro")

menu = Menu(screen)
state = "menu"
level = None
current_level_index = 0

running = True
while running:
    if state == "menu":
        action = menu.run()
        if action == "start":
            from maps import levels
            level = Level(levels[current_level_index], screen)
            state = "game"
        elif action == "quit":
            running = False

    elif state == "game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "paused"

        screen.fill((135, 206, 235))
        level.run()

        if level.player.health <= 0 or level.player.lives <= 0:
            state = "menu"

        pygame.display.update()
        clock.tick(FPS)

    elif state == "paused":
        action = menu.pause()
        if action == "resume":
            state = "game"
        elif action == "quit":
            running = False

pygame.quit()
