import pygame

from manorlord.config import (
    FONT_BODY_SIZE,
    FONT_HEADING_SIZE,
    FONT_SMALL_SIZE,
    FONT_TITLE_SIZE,
)


class Theme:
    def __init__(self) -> None:
        pygame.font.init()
        self.title = pygame.font.SysFont("serif", FONT_TITLE_SIZE, bold=True)
        self.heading = pygame.font.SysFont("serif", FONT_HEADING_SIZE, bold=True)
        self.body = pygame.font.SysFont("serif", FONT_BODY_SIZE)
        self.small = pygame.font.SysFont("serif", FONT_SMALL_SIZE)
