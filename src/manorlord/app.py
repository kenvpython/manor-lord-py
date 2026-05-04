import pygame

from manorlord.config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from manorlord.ui.scene import SceneManager
from manorlord.ui.scenes.main_menu import MainMenuScene
from manorlord.ui.theme import Theme


class App:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.theme = Theme()
        self.manager = SceneManager(self.theme)
        self.manager.change_scene(MainMenuScene(self.manager))

    def run(self) -> None:
        running = True
        while running and not self.manager.should_quit:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                self.manager.handle_event(event)
            self.manager.update(dt)
            self.manager.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
