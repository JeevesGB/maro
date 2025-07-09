import pygame 
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS 
from level import Level
from maps import levels #maps - game levels 

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Maro")

current_level_index = 0 
level = Level(levels[current_level_index], screen)

running = True 
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False 
    
    screen.fill((135,206,235)) #light blue sky
    level.run()
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()