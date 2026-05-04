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
from manorlord.core.new_game import create_world, set_player
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label, Panel
from manorlord.ui.world_map import WorldMapRenderer


SIDEBAR_X = SCREEN_WIDTH - SIDEBAR_WIDTH


class RealmSelectScene(Scene):
    def on_enter(self) -> None:
        self.manager.set_state(create_world())
        self.renderer = WorldMapRenderer(
            self.state,
            font_label=self.theme.subheading,
            font_small=self.theme.small,
        )
        self.hovered_realm_id: int | None = None
        self.selected_realm_id: int | None = None

        self.hud_panel = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        self.sidebar_panel = Panel(
            pygame.Rect(SIDEBAR_X, HUD_HEIGHT, SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT),
        )

        self.title = Label(
            "选择你的领地",
            self.theme.heading,
            color=COLOR_ACCENT,
            topleft=(40, 30),
        )
        self.subtitle = Label(
            "悬停查看，点击选择，然后开始。",
            self.theme.body,
            color=COLOR_TEXT_DIM,
            topleft=(40, 78),
        )

        self.sidebar_lines: list[Label] = []

        self.begin_button = Button(
            pygame.Rect(SIDEBAR_X + 40, SCREEN_HEIGHT - 100, SIDEBAR_WIDTH - 80, 60),
            "开始",
            self.theme.heading,
            self._begin,
        )
        self.back_button = Button(
            pygame.Rect(SCREEN_WIDTH - 160, 30, 130, 50),
            "返回",
            self.theme.body,
            self._back,
        )

        self._refresh_sidebar()

    def _back(self) -> None:
        from manorlord.ui.scenes.main_menu import MainMenuScene

        self.manager.set_state(None)
        self.manager.change_scene(MainMenuScene(self.manager))

    def _begin(self) -> None:
        if self.selected_realm_id is None or self.state is None:
            return
        from manorlord.ui.scenes.map_view import MapViewScene

        set_player(self.state, self.selected_realm_id)
        self.manager.change_scene(MapViewScene(self.manager))

    def _refresh_sidebar(self) -> None:
        if self.state is None:
            return
        x = SIDEBAR_X + 30
        y = HUD_HEIGHT + 30
        lines: list[Label] = []

        focused = self.selected_realm_id or self.hovered_realm_id

        if focused is None:
            lines.append(Label("未选择领地", self.theme.subheading, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 50
            lines.append(Label("将鼠标悬停在地图上", self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 30
            lines.append(Label("了解各领地。", self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
        else:
            realm = self.state.realms[focused]
            lord = self.state.characters[realm.owner_id]
            province_ids = realm.province_ids
            province = self.state.provinces[province_ids[0]] if province_ids else None

            color_chip = Label("■", self.theme.heading, color=realm.color, topleft=(x, y))
            lines.append(color_chip)
            lines.append(Label(realm.name, self.theme.subheading, color=COLOR_ACCENT, topleft=(x + 50, y + 4)))
            y += 60

            lines.append(Label(f"{lord.title.display_name} {lord.full_name}", self.theme.body, topleft=(x, y)))
            y += 36
            lines.append(Label(f"年龄 {lord.age}", self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 32

            stats = f"统{lord.martial}  外{lord.diplomacy}  管{lord.stewardship}  谋{lord.intrigue}"
            lines.append(Label(stats, self.theme.small, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 36

            if province is not None:
                lines.append(Label(
                    f"{province.name} — {province.terrain}",
                    self.theme.body,
                    topleft=(x, y),
                ))
                y += 32
                lines.append(Label(
                    f"人口：{province.population}",
                    self.theme.small,
                    color=COLOR_TEXT_DIM,
                    topleft=(x, y),
                ))
                y += 24
                lines.append(Label(
                    f"基础税收：{province.base_tax}",
                    self.theme.small,
                    color=COLOR_TEXT_DIM,
                    topleft=(x, y),
                ))
                y += 32

            lines.append(Label(f"国库：{realm.treasury}", self.theme.body, color=COLOR_ACCENT, topleft=(x, y)))
            y += 40

            for line in self._wrap(realm.description, 28):
                lines.append(Label(line, self.theme.body_italic, color=COLOR_TEXT_DIM, topleft=(x, y)))
                y += 28

        self.sidebar_lines = lines

    @staticmethod
    def _wrap(text: str, width: int) -> list[str]:
        words = text.split()
        lines: list[str] = []
        current: list[str] = []
        length = 0
        for word in words:
            if length + len(word) + (1 if current else 0) > width:
                lines.append(" ".join(current))
                current = [word]
                length = len(word)
            else:
                current.append(word)
                length += len(word) + (1 if length else 0)
        if current:
            lines.append(" ".join(current))
        return lines

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            new_hover = self.renderer.realm_at(event.pos)
            if new_hover != self.hovered_realm_id:
                self.hovered_realm_id = new_hover
                self._refresh_sidebar()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = self.renderer.realm_at(event.pos)
            if clicked is not None:
                self.selected_realm_id = clicked
                self._refresh_sidebar()

        self.begin_button.handle_event(event)
        self.back_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        self.renderer.draw(
            surface,
            hovered_realm_id=self.hovered_realm_id,
            selected_realm_id=self.selected_realm_id,
        )
        self.hud_panel.draw(surface)
        self.sidebar_panel.draw(surface)
        self.title.draw(surface)
        self.subtitle.draw(surface)
        for line in self.sidebar_lines:
            line.draw(surface)
        self.back_button.draw(surface)
        if self.selected_realm_id is not None:
            self.begin_button.draw(surface)
