from __future__ import annotations

import math
from pathlib import Path

import pygame

from manorlord.config import (
    COLOR_BORDER_DARK,
    COLOR_GOLD_HIGHLIGHT,
    COLOR_INK,
    COLOR_INK_BROWN,
    COLOR_OCEAN,
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
)
from manorlord.core.game_state import GameState
from manorlord.ui._geom import chaikin, point_in_polygon


MAP_RECT = pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT)
USER_MAP_IMAGE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "images" / "map.png"
)
PARCHMENT_IMAGE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "images" / "parchment.jpg"
)


def _soften(color: tuple[int, int, int], factor: float = 0.85) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in color)  # type: ignore[return-value]


def _build_ocean(rect: pygame.Rect) -> pygame.Surface:
    surface = pygame.Surface(rect.size).convert()
    for y in range(rect.height):
        t = y / max(1, rect.height)
        color = (
            int(40 + (58 - 40) * t),
            int(56 + (78 - 56) * t),
            int(72 + (96 - 72) * t),
        )
        pygame.draw.line(surface, color, (0, y), (rect.width, y))
    return surface


def _build_parchment_fallback(rect: pygame.Rect) -> pygame.Surface:
    surface = pygame.Surface(rect.size).convert()
    surface.fill((218, 196, 154))
    return surface


def _build_continent_mask(rect: pygame.Rect, polygons: list[list[tuple[int, int]]]) -> pygame.Surface:
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    for poly in polygons:
        if len(poly) >= 3:
            pygame.draw.polygon(mask, (255, 255, 255, 255), poly)
    return mask


class WorldMapRenderer:
    def __init__(self, state: GameState, font_label: pygame.font.Font, font_small: pygame.font.Font) -> None:
        self.state = state
        self.font_label = font_label
        self.font_small = font_small
        self.rect = MAP_RECT
        self._smoothed_polygons: dict[int, list[tuple[int, int]]] = {}
        self._static_layer = self._build_static_layer()

    def _build_static_layer(self) -> pygame.Surface:
        rect = self.rect
        if USER_MAP_IMAGE_PATH.exists():
            try:
                image = pygame.image.load(str(USER_MAP_IMAGE_PATH)).convert()
                return pygame.transform.smoothscale(image, rect.size)
            except pygame.error:
                pass

        layer = _build_ocean(rect)

        for pid, province in self.state.provinces.items():
            if len(province.polygon) >= 3:
                self._smoothed_polygons[pid] = chaikin(list(province.polygon), iterations=2)

        smoothed_all = list(self._smoothed_polygons.values())
        mask = _build_continent_mask(rect, smoothed_all)

        if PARCHMENT_IMAGE_PATH.exists():
            try:
                parchment = pygame.image.load(str(PARCHMENT_IMAGE_PATH)).convert()
                parchment = pygame.transform.smoothscale(parchment, rect.size)
            except pygame.error:
                parchment = _build_parchment_fallback(rect)
        else:
            parchment = _build_parchment_fallback(rect)

        parchment_a = parchment.convert_alpha()
        parchment_a.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        layer.blit(parchment_a, (0, 0))

        tint_layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        for realm in self.state.realms.values():
            tint = _soften(realm.color, 0.85)
            for pid in realm.province_ids:
                smoothed = self._smoothed_polygons.get(pid)
                if smoothed and len(smoothed) >= 3:
                    pygame.draw.polygon(tint_layer, (*tint, 45), smoothed)
        layer.blit(tint_layer, (0, 0))

        for pid, smoothed in self._smoothed_polygons.items():
            if len(smoothed) < 3:
                continue
            pygame.draw.polygon(layer, COLOR_INK_BROWN, smoothed, width=2)

        pygame.draw.rect(layer, COLOR_BORDER_DARK, layer.get_rect(), width=4)
        return layer

    def realm_at(self, pos: tuple[int, int]) -> int | None:
        if not self.rect.collidepoint(pos):
            return None
        local = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        for realm in self.state.realms.values():
            for province_id in realm.province_ids:
                province = self.state.provinces.get(province_id)
                if province and point_in_polygon(local, province.polygon):
                    return realm.id
        return None

    def _draw_realm_outline(
        self,
        surface: pygame.Surface,
        realm_id: int,
        color: tuple[int, int, int],
        width: int,
    ) -> None:
        realm = self.state.realms.get(realm_id)
        if realm is None:
            return
        for pid in realm.province_ids:
            smoothed = self._smoothed_polygons.get(pid)
            if smoothed and len(smoothed) >= 3:
                screen_poly = [(self.rect.x + x, self.rect.y + y) for x, y in smoothed]
                pygame.draw.polygon(surface, color, screen_poly, width=width)

    def _draw_realm_glow(
        self,
        surface: pygame.Surface,
        realm_id: int,
        color: tuple[int, int, int],
        intensity: int,
    ) -> None:
        realm = self.state.realms.get(realm_id)
        if realm is None:
            return
        glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for pid in realm.province_ids:
            smoothed = self._smoothed_polygons.get(pid)
            if not smoothed or len(smoothed) < 3:
                continue
            for layer_idx in range(intensity, 0, -1):
                alpha = int(28 * (layer_idx / intensity))
                pygame.draw.polygon(glow, (*color, alpha), smoothed, width=layer_idx * 2)
        surface.blit(glow, self.rect.topleft)

    def _draw_realm_label(
        self,
        surface: pygame.Surface,
        realm_id: int,
        province_id: int,
        highlight: bool,
    ) -> None:
        realm = self.state.realms.get(realm_id)
        province = self.state.provinces.get(province_id)
        if realm is None or province is None:
            return
        cx, cy = province.center
        screen_x = self.rect.x + cx
        screen_y = self.rect.y + cy

        name_color = COLOR_GOLD_HIGHLIGHT if highlight else COLOR_INK
        name_surf = self.font_label.render(realm.name, True, name_color)
        sub_surf = self.font_small.render(province.terrain.title(), True, COLOR_INK_BROWN)

        shadow_offset = 1
        for so in ((shadow_offset, shadow_offset), (-shadow_offset, shadow_offset),
                   (shadow_offset, -shadow_offset), (-shadow_offset, -shadow_offset)):
            name_shadow = self.font_label.render(realm.name, True, (240, 220, 180))
            name_rect = name_shadow.get_rect(center=(screen_x + so[0], screen_y + so[1] - sub_surf.get_height() // 2))
            surface.blit(name_shadow, name_rect)

        name_rect = name_surf.get_rect(center=(screen_x, screen_y - sub_surf.get_height() // 2))
        surface.blit(name_surf, name_rect)

        sub_rect = sub_surf.get_rect(center=(screen_x, screen_y + name_surf.get_height() // 2))
        surface.blit(sub_surf, sub_rect)

    def draw(
        self,
        surface: pygame.Surface,
        hovered_realm_id: int | None = None,
        selected_realm_id: int | None = None,
    ) -> None:
        surface.blit(self._static_layer, self.rect.topleft)

        if hovered_realm_id is not None and hovered_realm_id != selected_realm_id:
            self._draw_realm_glow(surface, hovered_realm_id, COLOR_GOLD_HIGHLIGHT, intensity=3)
            self._draw_realm_outline(surface, hovered_realm_id, COLOR_GOLD_HIGHLIGHT, width=3)

        if selected_realm_id is not None:
            self._draw_realm_glow(surface, selected_realm_id, COLOR_GOLD_HIGHLIGHT, intensity=4)
            self._draw_realm_outline(surface, selected_realm_id, COLOR_GOLD_HIGHLIGHT, width=4)
            realm = self.state.realms.get(selected_realm_id)
            if realm is not None:
                self._draw_realm_outline(
                    surface,
                    selected_realm_id,
                    _soften(realm.color, 1.0),
                    width=2,
                )

        for realm in self.state.realms.values():
            for province_id in realm.province_ids:
                province = self.state.provinces.get(province_id)
                if province is None:
                    continue
                highlight = realm.id == hovered_realm_id or realm.id == selected_realm_id
                self._draw_realm_label(surface, realm.id, province_id, highlight)

        pygame.draw.rect(surface, COLOR_BORDER_DARK, self.rect, width=4)
