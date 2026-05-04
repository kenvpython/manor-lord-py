from __future__ import annotations

import pygame

from manorlord.config import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_MAP_BG,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from manorlord.core.turn import TurnManager
from manorlord.systems import default_systems
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label, Panel


HUD_HEIGHT = 80
SIDEBAR_WIDTH = 320


class MapViewScene(Scene):
    def on_enter(self) -> None:
        self.turn_manager = TurnManager(default_systems())

        self.hud_panel = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        self.sidebar_panel = Panel(
            pygame.Rect(
                SCREEN_WIDTH - SIDEBAR_WIDTH,
                HUD_HEIGHT,
                SIDEBAR_WIDTH,
                SCREEN_HEIGHT - HUD_HEIGHT,
            )
        )

        self.turn_label = Label("Turn: 1", self.theme.heading, topleft=(24, 22))
        self.gold_label = Label("Gold: 0", self.theme.heading, topleft=(220, 22))
        self.ruler_label = Label("", self.theme.body, topleft=(460, 30))

        self.sidebar_title = Label(
            "Realm",
            self.theme.heading,
            color=COLOR_ACCENT,
            topleft=(SCREEN_WIDTH - SIDEBAR_WIDTH + 20, HUD_HEIGHT + 18),
        )
        self.sidebar_lines: list[Label] = []
        self.log_lines: list[Label] = []

        self.end_turn_button = Button(
            pygame.Rect(SCREEN_WIDTH - SIDEBAR_WIDTH + 60, SCREEN_HEIGHT - 80, 200, 50),
            "End Turn",
            self.theme.heading,
            self._end_turn,
        )
        self.menu_button = Button(
            pygame.Rect(SCREEN_WIDTH - 110, 20, 90, 40),
            "Menu",
            self.theme.body,
            self._back_to_menu,
        )

        self._refresh_hud()

    def _end_turn(self) -> None:
        if self.state is None:
            return
        self.turn_manager.advance_turn(self.state)
        self._refresh_hud()

    def _back_to_menu(self) -> None:
        from manorlord.ui.scenes.main_menu import MainMenuScene

        self.manager.set_state(None)
        self.manager.change_scene(MainMenuScene(self.manager))

    def _refresh_hud(self) -> None:
        if self.state is None:
            return
        self.turn_label.text = f"Turn: {self.state.turn}"
        realm = self.state.player_realm
        treasury = realm.treasury if realm else 0
        self.gold_label.text = f"Gold: {treasury}"
        player = self.state.player
        if player is not None:
            self.ruler_label.text = f"{player.title.display_name} {player.full_name}, age {player.age}"

        sidebar_x = SCREEN_WIDTH - SIDEBAR_WIDTH + 20
        y = HUD_HEIGHT + 60
        lines: list[Label] = []
        if realm is not None:
            lines.append(Label(realm.name, self.theme.body, topleft=(sidebar_x, y)))
            y += 30
            lines.append(Label(f"Income: {realm.income}", self.theme.body, color=COLOR_TEXT_DIM, topleft=(sidebar_x, y)))
            y += 26
            lines.append(Label(f"Troops: {realm.troops}", self.theme.body, color=COLOR_TEXT_DIM, topleft=(sidebar_x, y)))
            y += 26
            lines.append(Label(f"Provinces: {len(realm.province_ids)}", self.theme.body, color=COLOR_TEXT_DIM, topleft=(sidebar_x, y)))
            y += 40
        lines.append(Label("Recent events", self.theme.body, color=COLOR_ACCENT, topleft=(sidebar_x, y)))
        y += 28
        for entry in self.state.log[-6:]:
            lines.append(Label(entry, self.theme.small, color=COLOR_TEXT_DIM, topleft=(sidebar_x, y)))
            y += 20
        self.sidebar_lines = lines

    def handle_event(self, event: pygame.event.Event) -> None:
        self.end_turn_button.handle_event(event)
        self.menu_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)

        map_rect = pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT)
        pygame.draw.rect(surface, COLOR_MAP_BG, map_rect)
        pygame.draw.rect(surface, COLOR_BORDER, map_rect, width=2)

        placeholder = self.theme.body.render(
            "(Map placeholder — provinces will render here)",
            True,
            COLOR_TEXT_DIM,
        )
        surface.blit(
            placeholder,
            placeholder.get_rect(center=(map_rect.centerx, map_rect.centery)),
        )

        self.hud_panel.draw(surface)
        self.sidebar_panel.draw(surface)
        self.turn_label.draw(surface)
        self.gold_label.draw(surface)
        self.ruler_label.draw(surface)
        self.sidebar_title.draw(surface)
        for line in self.sidebar_lines:
            line.draw(surface)
        self.menu_button.draw(surface)
        self.end_turn_button.draw(surface)
