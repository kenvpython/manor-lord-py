from __future__ import annotations

import pygame

from manorlord.config import COLOR_ACCENT, COLOR_BG, COLOR_TEXT_DIM, SCREEN_HEIGHT, SCREEN_WIDTH
from manorlord.core.new_game import new_game
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label


class MainMenuScene(Scene):
    def on_enter(self) -> None:
        cx = SCREEN_WIDTH // 2

        self.title = Label(
            "MANOR LORD",
            self.theme.title,
            color=COLOR_ACCENT,
            center=(cx, 180),
        )
        self.subtitle = Label(
            "A medieval strategy of blood, gold, and crowns.",
            self.theme.body,
            color=COLOR_TEXT_DIM,
            center=(cx, 240),
        )

        button_w, button_h, gap = 280, 56, 18
        top = 340
        rects = [
            pygame.Rect(cx - button_w // 2, top + i * (button_h + gap), button_w, button_h)
            for i in range(3)
        ]

        self.buttons = [
            Button(rects[0], "New Game", self.theme.heading, self._start_new_game),
            Button(rects[1], "Load (TODO)", self.theme.heading, self._noop),
            Button(rects[2], "Quit", self.theme.heading, self.manager.quit),
        ]

        self.footer = Label(
            "v0.1.0 — scaffold",
            self.theme.small,
            color=COLOR_TEXT_DIM,
            center=(cx, SCREEN_HEIGHT - 28),
        )

    def _noop(self) -> None:
        pass

    def _start_new_game(self) -> None:
        from manorlord.ui.scenes.map_view import MapViewScene

        self.manager.set_state(new_game())
        self.manager.change_scene(MapViewScene(self.manager))

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        self.title.draw(surface)
        self.subtitle.draw(surface)
        for button in self.buttons:
            button.draw(surface)
        self.footer.draw(surface)
