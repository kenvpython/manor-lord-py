from collections.abc import Callable

import pygame

from manorlord.config import (
    COLOR_ACCENT,
    COLOR_BORDER,
    COLOR_PANEL,
    COLOR_PANEL_HOVER,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
)


class Label:
    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int] = COLOR_TEXT,
        center: tuple[int, int] | None = None,
        topleft: tuple[int, int] | None = None,
    ) -> None:
        self.font = font
        self.color = color
        self._text = text
        self.center = center
        self.topleft = topleft
        self._render()

    def _render(self) -> None:
        self.surface = self.font.render(self._text, True, self.color)
        if self.center is not None:
            self.rect = self.surface.get_rect(center=self.center)
        elif self.topleft is not None:
            self.rect = self.surface.get_rect(topleft=self.topleft)
        else:
            self.rect = self.surface.get_rect()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value == self._text:
            return
        self._text = value
        self._render()

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        font: pygame.font.Font,
        on_click: Callable[[], None],
    ) -> None:
        self.rect = rect
        self.label = label
        self.font = font
        self.on_click = on_click
        self.hovered = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        bg = COLOR_PANEL_HOVER if self.hovered else COLOR_PANEL
        pygame.draw.rect(surface, bg, self.rect, border_radius=4)
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, width=2, border_radius=4)
        text_color = COLOR_ACCENT if self.hovered else COLOR_TEXT
        text_surf = self.font.render(self.label, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class Panel:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, COLOR_PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_BORDER, self.rect, width=2, border_radius=6)


__all__ = ["Button", "Label", "Panel", "COLOR_TEXT_DIM"]
