from __future__ import annotations

import pygame

from manorlord.config import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_TEXT_DIM,
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
)
from manorlord.core.turn import TurnManager
from manorlord.systems import default_systems
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label, Panel
from manorlord.ui.world_map import WorldMapRenderer


SIDEBAR_X = SCREEN_WIDTH - SIDEBAR_WIDTH


class MapViewScene(Scene):
    def on_enter(self) -> None:
        self.turn_manager = TurnManager(default_systems())
        self.renderer = WorldMapRenderer(
            self.state,
            font_label=self.theme.subheading,
            font_small=self.theme.small,
        )
        self.hovered_realm_id: int | None = None

        self.hud_panel = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        self.sidebar_panel = Panel(
            pygame.Rect(SIDEBAR_X, HUD_HEIGHT, SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT),
        )

        self.turn_label = Label("Turn: 1", self.theme.heading, color=COLOR_ACCENT, topleft=(40, 22))
        self.gold_label = Label("Gold: 0", self.theme.heading, topleft=(280, 22))
        self.troops_label = Label("Troops: 0", self.theme.heading, topleft=(530, 22))
        self.ruler_label = Label("", self.theme.body, color=COLOR_TEXT_DIM, topleft=(40, 72))

        self.end_turn_button = Button(
            pygame.Rect(SIDEBAR_X + 60, SCREEN_HEIGHT - 100, SIDEBAR_WIDTH - 120, 60),
            "End Turn",
            self.theme.heading,
            self._end_turn,
        )
        self.menu_button = Button(
            pygame.Rect(SCREEN_WIDTH - 160, 30, 130, 50),
            "Menu",
            self.theme.body,
            self._back_to_menu,
        )

        self.sidebar_lines: list[Label] = []
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
        player_realm = self.state.player_realm
        self.gold_label.text = f"Gold: {player_realm.treasury if player_realm else 0}"
        self.troops_label.text = f"Troops: {player_realm.troops if player_realm else 0}"
        player = self.state.player
        if player is not None and player_realm is not None:
            self.ruler_label.text = (
                f"{player.title.display_name} {player.full_name}, age {player.age} — {player_realm.name}"
            )
        self._refresh_sidebar()

    def _refresh_sidebar(self) -> None:
        if self.state is None:
            return
        x = SIDEBAR_X + 30
        y = HUD_HEIGHT + 24
        lines: list[Label] = []

        focus_realm_id = self.hovered_realm_id or self.state.player_realm.id if self.state.player_realm else None
        is_inspect = self.hovered_realm_id is not None and self.hovered_realm_id != (self.state.player_realm.id if self.state.player_realm else None)

        if focus_realm_id is None:
            self.sidebar_lines = lines
            return

        realm = self.state.realms[focus_realm_id]
        lord = self.state.characters[realm.owner_id]

        header = "Foreign Realm" if is_inspect else "Your Realm"
        lines.append(Label(header, self.theme.subheading, color=COLOR_ACCENT, topleft=(x, y)))
        y += 50

        lines.append(Label("■", self.theme.body, color=realm.color, topleft=(x, y)))
        lines.append(Label(realm.name, self.theme.body, topleft=(x + 30, y)))
        y += 36

        lines.append(Label(f"{lord.title.display_name} {lord.full_name}", self.theme.body, topleft=(x, y)))
        y += 30
        lines.append(Label(f"age {lord.age}", self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
        y += 30

        lines.append(Label(f"Treasury: {realm.treasury}", self.theme.body, topleft=(x, y)))
        y += 28
        lines.append(Label(f"Income: {realm.income}", self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
        y += 24
        lines.append(Label(f"Troops: {realm.troops}", self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
        y += 24
        lines.append(Label(
            f"Provinces: {len(realm.province_ids)}",
            self.theme.small,
            color=COLOR_TEXT_DIM,
            topleft=(x, y),
        ))
        y += 36

        for line in self._wrap(realm.description, 32):
            lines.append(Label(line, self.theme.body_italic, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 26

        if not is_inspect:
            y += 10
            lines.append(Label("Recent events", self.theme.body, color=COLOR_ACCENT, topleft=(x, y)))
            y += 32
            for entry in self.state.log[-7:]:
                lines.append(Label(entry, self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
                y += 22

        self.sidebar_lines = lines

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        result: list[str] = []
        current: list[str] = []
        length = 0
        for word in words:
            extra = len(word) + (1 if current else 0)
            if length + extra > width:
                result.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += extra
        if current:
            result.append(" ".join(current))
        return result

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            new_hover = self.renderer.realm_at(event.pos)
            if new_hover != self.hovered_realm_id:
                self.hovered_realm_id = new_hover
                self._refresh_sidebar()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            settlement_id = self.renderer.settlement_at(event.pos)
            if settlement_id is not None:
                from manorlord.ui.scenes.settlement_detail import SettlementDetailScene

                self.manager.change_scene(SettlementDetailScene(self.manager, settlement_id))
                return

        self.end_turn_button.handle_event(event)
        self.menu_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        player_realm_id = self.state.player_realm.id if self.state and self.state.player_realm else None
        self.renderer.draw(
            surface,
            hovered_realm_id=self.hovered_realm_id,
            selected_realm_id=player_realm_id,
        )
        self.hud_panel.draw(surface)
        self.sidebar_panel.draw(surface)
        self.turn_label.draw(surface)
        self.gold_label.draw(surface)
        self.troops_label.draw(surface)
        self.ruler_label.draw(surface)
        for line in self.sidebar_lines:
            line.draw(surface)
        self.menu_button.draw(surface)
        self.end_turn_button.draw(surface)
