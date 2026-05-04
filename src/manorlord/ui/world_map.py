from __future__ import annotations

import random
from pathlib import Path

import pygame

from manorlord.config import (
    COLOR_BORDER_DARK,
    COLOR_INK,
    COLOR_PARCHMENT,
    COLOR_PARCHMENT_DEEP,
    HUD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SIDEBAR_WIDTH,
)
from manorlord.core.game_state import GameState


MAP_RECT = pygame.Rect(0, HUD_HEIGHT, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT - HUD_HEIGHT)
USER_MAP_IMAGE_PATH = (
    Path(__file__).resolve().parents[3] / "assets" / "images" / "map.png"
)


def _point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            if p1y != p2y:
                x_intersect = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                if p1x == p2x or x <= x_intersect:
                    inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def _build_parchment_background(rect: pygame.Rect) -> pygame.Surface:
    surface = pygame.Surface(rect.size).convert()
    surface.fill(COLOR_PARCHMENT)
    rng = random.Random(1337)
    pixels = pygame.PixelArray(surface)
    for _ in range(rect.width * rect.height // 30):
        x = rng.randrange(rect.width)
        y = rng.randrange(rect.height)
        jitter = rng.randint(-12, 8)
        base = COLOR_PARCHMENT
        pixels[x, y] = (
            max(0, min(255, base[0] + jitter)),
            max(0, min(255, base[1] + jitter)),
            max(0, min(255, base[2] + jitter)),
        )
    del pixels

    vignette = pygame.Surface(rect.size, pygame.SRCALPHA)
    margin = 80
    for i in range(margin):
        alpha = int(120 * (1 - i / margin) ** 2)
        if alpha <= 0:
            continue
        pygame.draw.rect(
            vignette,
            (*COLOR_BORDER_DARK, alpha),
            pygame.Rect(i, i, rect.width - 2 * i, rect.height - 2 * i),
            width=1,
        )
    surface.blit(vignette, (0, 0))
    return surface


class WorldMapRenderer:
    def __init__(self, state: GameState, font_label: pygame.font.Font, font_small: pygame.font.Font) -> None:
        self.state = state
        self.font_label = font_label
        self.font_small = font_small
        self.rect = MAP_RECT
        self._background = self._load_background()
        self._polygons_screen: dict[int, list[tuple[int, int]]] = {}
        self._compute_screen_polygons()

    def _load_background(self) -> pygame.Surface:
        if USER_MAP_IMAGE_PATH.exists():
            try:
                image = pygame.image.load(str(USER_MAP_IMAGE_PATH)).convert()
                return pygame.transform.smoothscale(image, self.rect.size)
            except pygame.error:
                pass
        return _build_parchment_background(self.rect)

    def _compute_screen_polygons(self) -> None:
        for province in self.state.provinces.values():
            if not province.polygon:
                continue
            screen_poly = [(self.rect.x + px, self.rect.y + py) for px, py in province.polygon]
            owner_realm_id = next(
                (rid for rid, r in self.state.realms.items() if province.id in r.province_ids),
                None,
            )
            if owner_realm_id is not None:
                self._polygons_screen.setdefault(owner_realm_id, []).extend(screen_poly)

    def realm_at(self, pos: tuple[int, int]) -> int | None:
        if not self.rect.collidepoint(pos):
            return None
        local = (pos[0] - self.rect.x, pos[1] - self.rect.y)
        for realm in self.state.realms.values():
            for province_id in realm.province_ids:
                province = self.state.provinces.get(province_id)
                if province and _point_in_polygon(local, province.polygon):
                    return realm.id
        return None

    def draw(
        self,
        surface: pygame.Surface,
        hovered_realm_id: int | None = None,
        selected_realm_id: int | None = None,
    ) -> None:
        surface.blit(self._background, self.rect.topleft)

        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        for realm in self.state.realms.values():
            color = realm.color
            for province_id in realm.province_ids:
                province = self.state.provinces.get(province_id)
                if not province or not province.polygon:
                    continue
                screen_poly = [(self.rect.x + px, self.rect.y + py) for px, py in province.polygon]
                local_poly = [(px, py) for px, py in province.polygon]

                base_alpha = 130 if realm.id == hovered_realm_id else 100
                if realm.id == selected_realm_id:
                    base_alpha = 170
                pygame.draw.polygon(overlay, (*color, base_alpha), local_poly)

                pygame.draw.polygon(surface, COLOR_BORDER_DARK, screen_poly, width=4)

                if realm.id == selected_realm_id:
                    pygame.draw.polygon(surface, color, screen_poly, width=6)
                    pygame.draw.polygon(
                        surface,
                        (255, 230, 160),
                        screen_poly,
                        width=2,
                    )
                elif realm.id == hovered_realm_id:
                    pygame.draw.polygon(surface, (255, 230, 160), screen_poly, width=3)

        surface.blit(overlay, self.rect.topleft)

        for realm in self.state.realms.values():
            for province_id in realm.province_ids:
                province = self.state.provinces.get(province_id)
                if not province:
                    continue
                cx, cy = province.center
                screen_x = self.rect.x + cx
                screen_y = self.rect.y + cy

                label = self.font_label.render(realm.name, True, COLOR_INK)
                shadow = self.font_label.render(realm.name, True, (240, 220, 180))
                label_rect = label.get_rect(center=(screen_x, screen_y))
                surface.blit(shadow, label_rect.move(2, 2))
                surface.blit(label, label_rect)

                sub = self.font_small.render(province.terrain.title(), True, COLOR_INK)
                sub_rect = sub.get_rect(center=(screen_x, screen_y + 30))
                surface.blit(sub, sub_rect)

        pygame.draw.rect(surface, COLOR_BORDER_DARK, self.rect, width=4)
