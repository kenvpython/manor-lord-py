from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from manorlord.core.game_state import GameState
    from manorlord.ui.theme import Theme


class Scene:
    def __init__(self, manager: "SceneManager") -> None:
        self.manager = manager

    @property
    def theme(self) -> "Theme":
        return self.manager.theme

    @property
    def state(self) -> "GameState | None":
        return self.manager.state

    def on_enter(self) -> None:
        pass

    def on_exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError


class SceneManager:
    def __init__(self, theme: "Theme") -> None:
        self.theme = theme
        self.state: "GameState | None" = None
        self._current: Scene | None = None
        self._quit = False

    @property
    def current(self) -> Scene | None:
        return self._current

    @property
    def should_quit(self) -> bool:
        return self._quit

    def quit(self) -> None:
        self._quit = True

    def change_scene(self, scene: Scene) -> None:
        if self._current is not None:
            self._current.on_exit()
        self._current = scene
        scene.on_enter()

    def set_state(self, state: "GameState | None") -> None:
        self.state = state

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._current is not None:
            self._current.handle_event(event)

    def update(self, dt: float) -> None:
        if self._current is not None:
            self._current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self._current is not None:
            self._current.draw(surface)
