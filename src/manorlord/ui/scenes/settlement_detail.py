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
from manorlord.ui.scene import Scene
from manorlord.ui.widgets import Button, Label, Panel


SIDEBAR_X = SCREEN_WIDTH - SIDEBAR_WIDTH


class SettlementDetailScene(Scene):
    def __init__(self, manager: "SceneManager", settlement_id: int) -> None:
        super().__init__(manager)
        self.settlement_id = settlement_id

    def on_enter(self) -> None:
        self.hud_panel = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, HUD_HEIGHT))
        self.sidebar_panel = Panel(
            pygame.Rect(SIDEBAR_X, HUD_HEIGHT, SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT),
        )

        self.back_button = Button(
            pygame.Rect(SCREEN_WIDTH - 160, 30, 130, 50),
            "Back",
            self.theme.body,
            self._back,
        )

        self._refresh_content()

    def _back(self) -> None:
        from manorlord.ui.scenes.map_view import MapViewScene

        self.manager.change_scene(MapViewScene(self.manager))

    def _refresh_content(self) -> None:
        if self.state is None:
            self.content_lines: list[Label] = []
            return

        settlement = self.state.settlements.get(self.settlement_id)
        if settlement is None:
            self.content_lines = [Label("Unknown settlement", self.theme.heading, color=COLOR_ACCENT, topleft=(40, 30))]
            return

        realm = self.state.realms.get(settlement.realm_id)
        province = self.state.provinces.get(settlement.province_id)
        lord = self.state.characters.get(realm.owner_id) if realm else None

        x = 60
        y = HUD_HEIGHT + 40
        lines: list[Label] = []

        lines.append(Label(settlement.name, self.theme.heading, color=COLOR_ACCENT, topleft=(x, y)))
        y += 60

        lines.append(Label(f"Type: {settlement.kind.title()}", self.theme.subheading, topleft=(x, y)))
        y += 50

        if realm is not None:
            lines.append(Label(f"Realm: {realm.name}", self.theme.body, topleft=(x, y)))
            y += 40
        if province is not None:
            lines.append(Label(f"Province: {province.name} — {province.terrain.title()}", self.theme.body, topleft=(x, y)))
            y += 40

        lines.append(Label(f"Population: {settlement.population}", self.theme.body, topleft=(x, y)))
        y += 40

        if lord is not None:
            lines.append(Label(f"Ruler: {lord.title.display_name} {lord.full_name}", self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
            y += 36

        y += 20
        desc = self._flavor_text(settlement, province)
        for sentence in desc.split(". "):
            sentence = sentence.strip()
            if not sentence:
                continue
            if not sentence.endswith("."):
                sentence += "."
            for wrapped in self._wrap(sentence, 55):
                lines.append(Label(wrapped, self.theme.body, color=COLOR_TEXT_DIM, topleft=(x, y)))
                y += 32

        self.content_lines = lines

    @staticmethod
    def _flavor_text(settlement, province) -> str:
        terrain = province.terrain if province else "unknown"
        kind = settlement.kind
        flavor_map: dict[str, dict[str, str]] = {
            "capital": {
                "plains": "The capital bustles with traders and messengers along wide avenues.",
                "mountain": "Stone walls rise from the mountain slope, sheltering the realm's seat of power.",
                "forest": "Timber halls and carved gates mark the heart of the woodland realm.",
                "hills": "Terraced gardens crown the hilltop, visible for leagues in every direction.",
                "coast": "Harbor bells ring through salt-worn streets as ships moor at the capital's quays.",
                "swamp": "Raised walkways connect the stilted halls of this soggy but defensible capital.",
                "lakes": "Water gates and canal bridges weave through the lake-bound capital.",
                "city": "Towers of stone and glass loom over crowded market squares.",
            },
            "town": {
                "plains": "A modest trade post where grain wagons gather before the harvest roads.",
                "mountain": "Miners' lanterns flicker in the narrow lanes between stone storehouses.",
                "forest": "Lumber camps send their best timber through this quiet woodland town.",
                "hills": "Sheep markets and wool dye-vats color the streets of this hillside town.",
                "coast": "Fishing nets hang across every doorway, drying in the sea breeze.",
                "swamp": "Reed-thatch roofs and bog-iron forges give this town a stubborn character.",
                "lakes": "Boatwrights and net-weavers keep the lake trade moving through calm waters.",
                "city": "A dense borough of artisans and merchants, thick with workshop smoke.",
            },
            "village": {
                "plains": "Small fields ring a cluster of low cottages.",
                "mountain": "Terraced goat-pens cling to the slopes above stone cottages.",
                "forest": "Charcoal pits and trapper huts hide among the trees.",
                "hills": "Sheep trails wander between stone walls older than any living memory.",
                "coast": "A handful of boats pulled ashore, nets mended by weathered hands.",
                "swamp": "Stilted huts rise above the muck on ancient driven posts.",
                "lakes": "Reed baskets and dried fish hang from every eave.",
                "city": "Crowded alleys and shared courtyards hide behind the grander avenues.",
            },
        }
        return flavor_map.get(kind, flavor_map["village"]).get(terrain, "A quiet settlement, unknown to most travelers.")

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
        self.back_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_BG)
        self.hud_panel.draw(surface)
        self.sidebar_panel.draw(surface)
        for line in self.content_lines:
            line.draw(surface)
        self.back_button.draw(surface)
