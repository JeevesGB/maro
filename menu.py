import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)

    def run(self):
        while True:
            self.screen.fill((0, 0, 0))
            title = self.font.render("Maro Platformer", True, (255, 255, 255))
            start = self.font.render("Press ENTER to Start", True, (255, 255, 255))
            quit_game = self.font.render("Press ESC to Quit", True, (255, 255, 255))
            self.screen.blit(title, (250, 150))
            self.screen.blit(start, (220, 250))
            self.screen.blit(quit_game, (220, 300))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "start"
                    elif event.key == pygame.K_ESCAPE:
                        return "quit"

    def pause(self):
        while True:
            self.screen.fill((30, 30, 30))
            text = self.font.render("Paused - Press ESC to Resume", True, (255, 255, 255))
            quit_text = self.font.render("Press Q to Quit", True, (255, 255, 255))
            self.screen.blit(text, (150, 200))
            self.screen.blit(quit_text, (200, 250))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "resume"
                    elif event.key == pygame.K_q:
                        return "quit"
