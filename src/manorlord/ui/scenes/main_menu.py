from __future__ import annotations

import pygame

from manorlord.config import COLOR_ACCENT, COLOR_BG, COLOR_TEXT_DIM, SCREEN_HEIGHT, SCREEN_WIDTH
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label


class MainMenuScene(Scene):
    def on_enter(self) -> None:
        cx = SCREEN_WIDTH // 2

        self.title = Label(
            "庄园领主",
            self.theme.title,
            color=COLOR_ACCENT,
            center=(cx, 260),
        )
        self.subtitle = Label(
            "一部关于血、金与王冠的中世纪策略。",
            self.theme.body,
            color=COLOR_TEXT_DIM,
            center=(cx, 360),
        )

        button_w, button_h, gap = 380, 78, 28
        top = 500
        rects = [
            pygame.Rect(cx - button_w // 2, top + i * (button_h + gap), button_w, button_h)
            for i in range(3)
        ]

        self.buttons = [
            Button(rects[0], "新游戏", self.theme.heading, self._start_new_game),
            Button(rects[1], "读取（待实现）", self.theme.heading, self._noop),
            Button(rects[2], "退出", self.theme.heading, self.manager.quit),
        ]

        self.footer = Label(
            "v0.2.0 — 八国争霸",
            self.theme.small,
            color=COLOR_TEXT_DIM,
            center=(cx, SCREEN_HEIGHT - 36),
        )

    def _noop(self) -> None:
        pass

    def _start_new_game(self) -> None:
        from manorlord.ui.scenes.realm_select import RealmSelectScene

        self.manager.change_scene(RealmSelectScene(self.manager))

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
