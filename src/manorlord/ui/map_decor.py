from __future__ import annotations

import math
import random
from typing import Callable

import pygame

from manorlord.ui._geom import point_in_polygon, polygon_bbox, random_point_in_polygon


_TERRAIN_PALETTE: dict[str, dict[str, tuple[int, int, int]]] = {
    "mountain": {"dark": (96, 76, 58), "mid": (138, 110, 78), "light": (198, 174, 134)},
    "hills": {"dark": (124, 104, 64), "mid": (158, 134, 84), "light": (208, 184, 128)},
    "forest": {"dark": (54, 78, 50), "mid": (88, 116, 64), "light": (148, 174, 96)},
    "plains": {"dark": (130, 108, 60), "mid": (176, 150, 90), "light": (212, 188, 124)},
    "swamp": {"dark": (74, 86, 62), "mid": (106, 116, 82), "light": (158, 162, 118)},
    "lakes": {"dark": (62, 90, 116), "mid": (96, 134, 162), "light": (172, 198, 218)},
    "coast": {"dark": (84, 112, 132), "mid": (132, 160, 180), "light": (196, 218, 232)},
    "city": {"dark": (110, 78, 56), "mid": (164, 124, 80), "light": (220, 188, 132)},
}


def terrain_palette(terrain: str) -> dict[str, tuple[int, int, int]]:
    return _TERRAIN_PALETTE.get(terrain, _TERRAIN_PALETTE["plains"])


def _ink_line(
    surface: pygame.Surface,
    color: tuple[int, int, int],
    start: tuple[float, float],
    end: tuple[float, float],
    width: int = 1,
) -> None:
    pygame.draw.line(surface, color, start, end, width)


def draw_mountain(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    half = size // 2
    base_y = y + size // 3
    apex = (x, y - size // 2)
    left = (x - half, base_y)
    right = (x + half, base_y)
    pygame.draw.polygon(surface, palette["mid"], [left, apex, right])
    pygame.draw.polygon(surface, palette["dark"], [left, apex, right], width=2)
    ridge_left = (x - half // 3, y - size // 6)
    ridge_right = (x + half // 3, y - size // 8)
    _ink_line(surface, palette["dark"], apex, ridge_left, 1)
    _ink_line(surface, palette["dark"], apex, ridge_right, 1)
    snow = [
        apex,
        (apex[0] - size // 5, apex[1] + size // 4),
        (apex[0], apex[1] + size // 6),
        (apex[0] + size // 6, apex[1] + size // 4),
    ]
    pygame.draw.polygon(surface, palette["light"], snow)


def draw_tree(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    half = max(2, size // 2)
    crown = [
        (x - half, y + half // 2),
        (x, y - size),
        (x + half, y + half // 2),
    ]
    pygame.draw.polygon(surface, palette["mid"], crown)
    highlight = [
        (x - half // 2, y),
        (x, y - size // 2),
        (x, y + half // 2),
    ]
    pygame.draw.polygon(surface, palette["light"], highlight)
    pygame.draw.polygon(surface, palette["dark"], crown, width=1)
    trunk_top = (x, y + half // 2)
    trunk_bot = (x, y + half // 2 + max(2, size // 4))
    _ink_line(surface, palette["dark"], trunk_top, trunk_bot, 2)


def draw_hill(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    rect = pygame.Rect(x - size, y - size // 2, size * 2, size)
    pygame.draw.arc(surface, palette["dark"], rect, math.radians(20), math.radians(160), 2)
    inner = pygame.Rect(x - size + 4, y - size // 2 + 3, size * 2 - 8, size - 6)
    pygame.draw.arc(surface, palette["mid"], inner, math.radians(35), math.radians(145), 1)


def draw_wave(
    surface: pygame.Surface,
    center: tuple[int, int],
    length: int,
    color: tuple[int, int, int],
    width: int = 1,
) -> None:
    cx, cy = center
    half = length // 2
    steps = 16
    pts: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = i / steps
        x = cx - half + t * length
        y = cy + math.sin(t * math.tau) * 2.2
        pts.append((x, y))
    if len(pts) >= 2:
        pygame.draw.aalines(surface, color, False, pts, width)


def draw_lake(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    rect = pygame.Rect(x - size, y - size // 2, size * 2, size)
    pygame.draw.ellipse(surface, palette["mid"], rect)
    pygame.draw.ellipse(surface, palette["dark"], rect, width=1)
    inner = rect.inflate(-size // 2, -size // 3)
    pygame.draw.ellipse(surface, palette["light"], inner, width=1)


def draw_swamp_tuft(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    rect = pygame.Rect(x - size, y - size // 3, size * 2, max(4, size * 2 // 3))
    pygame.draw.ellipse(surface, palette["mid"], rect)
    pygame.draw.ellipse(surface, palette["dark"], rect, width=1)
    for dx in (-size // 2, 0, size // 2):
        _ink_line(
            surface,
            palette["dark"],
            (x + dx, y - size // 3 - 1),
            (x + dx, y - size // 3 - max(3, size // 2)),
            1,
        )


def draw_wheat(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    x, y = pos
    stem_top = (x, y - size)
    stem_bot = (x, y)
    _ink_line(surface, palette["dark"], stem_top, stem_bot, 1)
    for i, frac in enumerate((0.25, 0.5, 0.75)):
        ty = y - int(size * frac)
        offset = max(2, size // 5)
        _ink_line(surface, palette["mid"], (x, ty), (x - offset, ty - offset), 1)
        _ink_line(surface, palette["mid"], (x, ty), (x + offset, ty - offset), 1)


def draw_castle(
    surface: pygame.Surface,
    pos: tuple[int, int],
    size: int,
    ink: tuple[int, int, int],
    fill: tuple[int, int, int],
    banner_color: tuple[int, int, int] | None = None,
) -> None:
    x, y = pos
    half = size // 2
    body = pygame.Rect(x - half, y - size, size, size)
    pygame.draw.rect(surface, fill, body)
    pygame.draw.rect(surface, ink, body, width=2)
    crenel_w = max(2, size // 5)
    for i in range(3):
        cx = body.left + crenel_w + i * (crenel_w * 2)
        if cx + crenel_w > body.right:
            break
        c_rect = pygame.Rect(cx, body.top - crenel_w, crenel_w, crenel_w)
        pygame.draw.rect(surface, fill, c_rect)
        pygame.draw.rect(surface, ink, c_rect, width=2)
    door = pygame.Rect(x - max(2, size // 6), body.bottom - size // 2, max(4, size // 3), size // 2)
    pygame.draw.rect(surface, ink, door)
    if banner_color is not None:
        pole_top = (x, body.top - crenel_w - max(6, size // 2))
        pole_bot = (x, body.top - crenel_w)
        _ink_line(surface, ink, pole_top, pole_bot, 2)
        flag = [
            pole_top,
            (pole_top[0] + max(6, size // 2), pole_top[1] + max(2, size // 6)),
            (pole_top[0], pole_top[1] + max(4, size // 3)),
        ]
        pygame.draw.polygon(surface, banner_color, flag)
        pygame.draw.polygon(surface, ink, flag, width=1)


_compass_letter_font: pygame.font.Font | None = None


def _get_compass_font() -> pygame.font.Font:
    global _compass_letter_font
    if _compass_letter_font is None:
        _compass_letter_font = pygame.font.SysFont("microsoftyahei", 18, bold=True)
    return _compass_letter_font


def draw_compass(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    ink: tuple[int, int, int],
    accent: tuple[int, int, int],
    paper: tuple[int, int, int],
) -> None:
    cx, cy = center
    pygame.draw.circle(surface, paper, center, radius)
    pygame.draw.circle(surface, ink, center, radius, width=2)
    pygame.draw.circle(surface, ink, center, radius - 6, width=1)
    pygame.draw.circle(surface, accent, center, radius // 4)
    pygame.draw.circle(surface, ink, center, radius // 4, width=1)
    main_tip = radius - 4
    side = max(4, radius // 5)
    for angle_deg, fill in (
        (-90, accent),
        (90, ink),
        (0, ink),
        (180, ink),
    ):
        rad = math.radians(angle_deg)
        tip = (cx + math.cos(rad) * main_tip, cy + math.sin(rad) * main_tip)
        perp = rad + math.pi / 2
        base_l = (cx + math.cos(perp) * side / 2, cy + math.sin(perp) * side / 2)
        base_r = (cx - math.cos(perp) * side / 2, cy - math.sin(perp) * side / 2)
        pygame.draw.polygon(surface, fill, [tip, base_l, base_r])
        pygame.draw.polygon(surface, ink, [tip, base_l, base_r], width=1)
    diag = radius - 10
    diag_side = max(3, radius // 8)
    for angle_deg in (-45, 45, 135, -135):
        rad = math.radians(angle_deg)
        tip = (cx + math.cos(rad) * diag, cy + math.sin(rad) * diag)
        perp = rad + math.pi / 2
        base_l = (cx + math.cos(perp) * diag_side / 2, cy + math.sin(perp) * diag_side / 2)
        base_r = (cx - math.cos(perp) * diag_side / 2, cy - math.sin(perp) * diag_side / 2)
        pygame.draw.polygon(surface, ink, [tip, base_l, base_r], width=1)
    font = _get_compass_font()
    for letter, angle_deg in (("N", -90), ("E", 0), ("S", 90), ("W", 180)):
        rad = math.radians(angle_deg)
        lx = cx + math.cos(rad) * (radius + 12)
        ly = cy + math.sin(rad) * (radius + 12)
        text = font.render(letter, True, ink)
        rect = text.get_rect(center=(int(lx), int(ly)))
        surface.blit(text, rect)


def draw_scroll_label(
    surface: pygame.Surface,
    rect: pygame.Rect,
    paper: tuple[int, int, int],
    ink: tuple[int, int, int],
    shadow: tuple[int, int, int],
) -> None:
    body = rect.inflate(-rect.height, 0)
    if body.width <= 0:
        body = rect.copy()
    shadow_rect = body.move(2, 3)
    pygame.draw.rect(surface, shadow, shadow_rect, border_radius=6)
    pygame.draw.rect(surface, paper, body, border_radius=6)
    pygame.draw.rect(surface, ink, body, width=2, border_radius=6)
    end_radius = rect.height // 2
    left_center = (body.left, rect.centery)
    right_center = (body.right, rect.centery)
    pygame.draw.circle(surface, paper, left_center, end_radius)
    pygame.draw.circle(surface, ink, left_center, end_radius, width=2)
    pygame.draw.circle(surface, paper, right_center, end_radius)
    pygame.draw.circle(surface, ink, right_center, end_radius, width=2)
    pygame.draw.circle(surface, ink, left_center, max(2, end_radius // 3), width=1)
    pygame.draw.circle(surface, ink, right_center, max(2, end_radius // 3), width=1)


def draw_scroll_title(
    surface: pygame.Surface,
    center: tuple[int, int],
    text: str,
    font: pygame.font.Font,
    paper: tuple[int, int, int],
    ink: tuple[int, int, int],
    shadow: tuple[int, int, int],
) -> pygame.Rect:
    text_surf = font.render(text, True, ink)
    pad_x = 56
    pad_y = 20
    rect = text_surf.get_rect()
    bg_rect = pygame.Rect(0, 0, rect.width + pad_x, rect.height + pad_y)
    bg_rect.center = center
    draw_scroll_label(surface, bg_rect, paper, ink, shadow)
    text_rect = text_surf.get_rect(center=center)
    surface.blit(text_surf, text_rect)
    return bg_rect


def _scatter(
    surface: pygame.Surface,
    polygon: list[tuple[int, int]],
    rng: random.Random,
    count: int,
    inset: int,
    drawer: Callable[[tuple[int, int]], None],
) -> None:
    placed = 0
    attempts = 0
    while placed < count and attempts < count * 10:
        attempts += 1
        pos = random_point_in_polygon(polygon, rng, inset=inset)
        if pos is None:
            return
        drawer(pos)
        placed += 1


def scatter_terrain(
    surface: pygame.Surface,
    polygon: list[tuple[int, int]],
    terrain: str,
    seed: int,
) -> None:
    if len(polygon) < 3:
        return
    rng = random.Random(seed)
    palette = terrain_palette(terrain)
    min_x, min_y, max_x, max_y = polygon_bbox(polygon)
    area_factor = max(1, ((max_x - min_x) * (max_y - min_y)) // 12000)

    if terrain == "mountain":
        count = 9 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=20,
            drawer=lambda p: draw_mountain(surface, p, rng.randint(22, 34), palette),
        )
    elif terrain == "hills":
        count = 8 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=14,
            drawer=lambda p: draw_hill(surface, p, rng.randint(14, 22), palette),
        )
    elif terrain == "forest":
        count = 18 + area_factor * 2
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=12,
            drawer=lambda p: draw_tree(surface, p, rng.randint(12, 18), palette),
        )
    elif terrain == "plains":
        count = 6 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=18,
            drawer=lambda p: draw_wheat(surface, p, rng.randint(10, 16), palette),
        )
        for _ in range(40 + area_factor * 3):
            pos = random_point_in_polygon(polygon, rng, inset=10)
            if pos is None:
                break
            pygame.draw.circle(surface, palette["dark"], pos, 1)
    elif terrain == "swamp":
        count = 7 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=14,
            drawer=lambda p: draw_swamp_tuft(surface, p, rng.randint(10, 16), palette),
        )
        for _ in range(8 + area_factor):
            pos = random_point_in_polygon(polygon, rng, inset=12)
            if pos is None:
                break
            draw_wave(surface, pos, rng.randint(20, 32), palette["dark"], 1)
    elif terrain == "lakes":
        count = 4 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=20,
            drawer=lambda p: draw_lake(surface, p, rng.randint(18, 28), palette),
        )
        for _ in range(10 + area_factor):
            pos = random_point_in_polygon(polygon, rng, inset=12)
            if pos is None:
                break
            draw_wave(surface, pos, rng.randint(18, 28), palette["mid"], 1)
    elif terrain == "coast":
        for _ in range(14 + area_factor * 2):
            pos = random_point_in_polygon(polygon, rng, inset=10)
            if pos is None:
                break
            draw_wave(surface, pos, rng.randint(20, 36), palette["mid"], 1)
        count = 3 + area_factor
        _scatter(
            surface,
            polygon,
            rng,
            count,
            inset=20,
            drawer=lambda p: draw_lake(surface, p, rng.randint(12, 20), palette),
        )
    elif terrain == "city":
        for _ in range(6 + area_factor):
            pos = random_point_in_polygon(polygon, rng, inset=24)
            if pos is None:
                break
            draw_wheat(surface, pos, rng.randint(8, 12), palette)
