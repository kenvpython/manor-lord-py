from __future__ import annotations

import math
import random
from pathlib import Path

import pygame

from manorlord.config import (
    COLOR_BORDER_DARK,
    COLOR_GOLD_HIGHLIGHT,
    COLOR_INK,
    COLOR_INK_BROWN,
    COLOR_INK_LIGHT,
    COLOR_OCEAN,
    COLOR_OCEAN_DEEP,
    COLOR_OCEAN_FOAM,
    COLOR_PARCHMENT,
    COLOR_PARCHMENT_DEEP,
    COLOR_PARCHMENT_LIGHT,
    COLOR_PARCHMENT_SHADOW,
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
)
from manorlord.core.game_state import GameState
from manorlord.ui import map_decor
from manorlord.ui._geom import chaikin, point_in_polygon


MAP_RECT = pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT)
USER_MAP_IMAGE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "images" / "map.png"
)


def _soften(color: tuple[int, int, int], factor: float = 0.85) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in color)  # type: ignore[return-value]


def _draw_radial_gradient(
    surface: pygame.Surface,
    center: tuple[int, int],
    inner_color: tuple[int, int, int],
    outer_color: tuple[int, int, int],
    radius: int,
    steps: int = 24,
) -> None:
    cx, cy = center
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        if r <= 0:
            continue
        color = (
            int(outer_color[0] + (inner_color[0] - outer_color[0]) * (1 - t)),
            int(outer_color[1] + (inner_color[1] - outer_color[1]) * (1 - t)),
            int(outer_color[2] + (inner_color[2] - outer_color[2]) * (1 - t)),
        )
        pygame.draw.circle(surface, color, (cx, cy), r)


def _draw_corner_stain(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
    max_alpha: int,
) -> None:
    blob = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    cx = cy = radius
    steps = 16
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        if r <= 0:
            continue
        alpha = int(max_alpha * (1 - t) ** 1.5)
        pygame.draw.circle(blob, (*color, alpha), (cx, cy), r)
    surface.blit(blob, (center[0] - radius, center[1] - radius))


def _build_ocean(rect: pygame.Rect) -> pygame.Surface:
    surface = pygame.Surface(rect.size).convert()
    rng = random.Random(91)
    for y in range(rect.height):
        t = y / max(1, rect.height)
        color = (
            int(COLOR_OCEAN_DEEP[0] + (COLOR_OCEAN[0] - COLOR_OCEAN_DEEP[0]) * t),
            int(COLOR_OCEAN_DEEP[1] + (COLOR_OCEAN[1] - COLOR_OCEAN_DEEP[1]) * t),
            int(COLOR_OCEAN_DEEP[2] + (COLOR_OCEAN[2] - COLOR_OCEAN_DEEP[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (rect.width, y))
    for _ in range(70):
        cx = rng.randint(20, rect.width - 20)
        cy = rng.randint(20, rect.height - 20)
        length = rng.randint(40, 110)
        amp = rng.uniform(1.5, 3.2)
        steps = 24
        pts: list[tuple[float, float]] = []
        for i in range(steps + 1):
            t = i / steps
            x = cx - length / 2 + t * length
            y = cy + math.sin(t * math.tau) * amp
            pts.append((x, y))
        if len(pts) >= 2:
            pygame.draw.aalines(surface, COLOR_OCEAN_FOAM, False, pts, 1)
    return surface


def _build_parchment(rect: pygame.Rect) -> pygame.Surface:
    surface = pygame.Surface(rect.size).convert()
    surface.fill(COLOR_PARCHMENT)
    _draw_radial_gradient(
        surface,
        (rect.width // 2, rect.height // 2),
        COLOR_PARCHMENT_LIGHT,
        COLOR_PARCHMENT,
        radius=max(rect.width, rect.height) // 2 + 100,
        steps=20,
    )
    rng = random.Random(1337)
    pixels = pygame.PixelArray(surface)
    flecks = (rect.width * rect.height) // 28
    base_r, base_g, base_b = COLOR_PARCHMENT
    for _ in range(flecks):
        x = rng.randrange(rect.width)
        y = rng.randrange(rect.height)
        jitter = rng.randint(-14, 8)
        pixels[x, y] = (
            max(0, min(255, base_r + jitter)),
            max(0, min(255, base_g + jitter)),
            max(0, min(255, base_b + jitter)),
        )
    del pixels
    for cx, cy in (
        (60, 60),
        (rect.width - 80, 80),
        (80, rect.height - 80),
        (rect.width - 70, rect.height - 60),
    ):
        _draw_corner_stain(surface, (cx, cy), 220, COLOR_PARCHMENT_SHADOW, 110)
    edge = pygame.Surface(rect.size, pygame.SRCALPHA)
    margin = 60
    for i in range(margin):
        alpha = int(150 * (1 - i / margin) ** 2)
        if alpha <= 0:
            continue
        pygame.draw.rect(
            edge,
            (*COLOR_PARCHMENT_DEEP, alpha),
            pygame.Rect(i, i, rect.width - 2 * i, rect.height - 2 * i),
            width=1,
        )
    surface.blit(edge, (0, 0))
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

        parchment = _build_parchment(rect)
        smoothed_for_mask = list(self._smoothed_polygons.values())
        mask = _build_continent_mask(rect, smoothed_for_mask)
        masked_parchment = parchment.convert_alpha()
        masked_parchment.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        layer.blit(masked_parchment, (0, 0))

        tint_layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        for realm in self.state.realms.values():
            tint = _soften(realm.color, 0.85)
            for pid in realm.province_ids:
                smoothed = self._smoothed_polygons.get(pid)
                if smoothed and len(smoothed) >= 3:
                    pygame.draw.polygon(tint_layer, (*tint, 60), smoothed)
        layer.blit(tint_layer, (0, 0))

        for pid, province in self.state.provinces.items():
            smoothed = self._smoothed_polygons.get(pid)
            if smoothed is None or len(smoothed) < 3:
                continue
            seed = province.id * 100003 + sum(ord(c) for c in province.terrain)
            map_decor.scatter_terrain(layer, smoothed, province.terrain, seed)

        for pid, smoothed in self._smoothed_polygons.items():
            if len(smoothed) < 3:
                continue
            pygame.draw.polygon(layer, COLOR_INK_BROWN, smoothed, width=4)
            pygame.draw.polygon(layer, COLOR_INK_LIGHT, smoothed, width=1)

        for realm in self.state.realms.values():
            cap_id = realm.capital_province_id
            if cap_id is None:
                continue
            province = self.state.provinces.get(cap_id)
            if province is None:
                continue
            cx, cy = province.center
            map_decor.draw_castle(
                layer,
                (cx, cy - 36),
                size=22,
                ink=COLOR_INK_BROWN,
                fill=COLOR_PARCHMENT_LIGHT,
                banner_color=realm.color,
            )

        compass_center = (rect.width - 120, rect.height - 120)
        map_decor.draw_compass(
            layer,
            compass_center,
            radius=58,
            ink=COLOR_INK_BROWN,
            accent=COLOR_GOLD_HIGHLIGHT,
            paper=COLOR_PARCHMENT_LIGHT,
        )

        title_font = pygame.font.SysFont("serif", 36, bold=True)
        map_decor.draw_scroll_title(
            layer,
            center=(rect.width // 2, 56),
            text="The Eight Realms",
            font=title_font,
            paper=COLOR_PARCHMENT_LIGHT,
            ink=COLOR_INK_BROWN,
            shadow=COLOR_PARCHMENT_DEEP,
        )

        pygame.draw.rect(layer, COLOR_BORDER_DARK, layer.get_rect(), width=4)
        pygame.draw.rect(layer, COLOR_INK_LIGHT, layer.get_rect().inflate(-8, -8), width=1)

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
        screen_y = self.rect.y + cy + 8

        name_color = COLOR_GOLD_HIGHLIGHT if highlight else COLOR_INK
        name_surf = self.font_label.render(realm.name, True, name_color)
        sub_surf = self.font_small.render(province.terrain.title(), True, COLOR_INK_BROWN)

        scroll_w = max(name_surf.get_width(), sub_surf.get_width()) + 56
        scroll_h = name_surf.get_height() + sub_surf.get_height() + 18
        scroll_rect = pygame.Rect(0, 0, scroll_w, scroll_h)
        scroll_rect.center = (screen_x, screen_y)
        map_decor.draw_scroll_label(
            surface,
            scroll_rect,
            paper=COLOR_PARCHMENT_LIGHT,
            ink=COLOR_INK_BROWN,
            shadow=COLOR_PARCHMENT_DEEP,
        )

        name_rect = name_surf.get_rect(center=(screen_x, screen_y - sub_surf.get_height() // 2))
        sub_rect = sub_surf.get_rect(center=(screen_x, screen_y + name_surf.get_height() // 2))
        surface.blit(name_surf, name_rect)
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
