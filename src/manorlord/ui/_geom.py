from __future__ import annotations

import random


Point = tuple[float, float]


def point_in_polygon(point: tuple[int, int], polygon: list[tuple[int, int]]) -> bool:
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


def chaikin(points: list[tuple[int, int]], iterations: int = 2) -> list[tuple[int, int]]:
    if len(points) < 3 or iterations <= 0:
        return [(int(round(x)), int(round(y))) for x, y in points]
    pts: list[tuple[float, float]] = [(float(x), float(y)) for x, y in points]
    for _ in range(iterations):
        new_pts: list[tuple[float, float]] = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            qx = 0.75 * x0 + 0.25 * x1
            qy = 0.75 * y0 + 0.25 * y1
            rx = 0.25 * x0 + 0.75 * x1
            ry = 0.25 * y0 + 0.75 * y1
            new_pts.append((qx, qy))
            new_pts.append((rx, ry))
        pts = new_pts
    return [(int(round(x)), int(round(y))) for x, y in pts]


def polygon_bbox(polygon: list[tuple[int, int]]) -> tuple[int, int, int, int]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return min(xs), min(ys), max(xs), max(ys)


def random_point_in_polygon(
    polygon: list[tuple[int, int]],
    rng: random.Random,
    inset: int = 0,
    max_attempts: int = 80,
) -> tuple[int, int] | None:
    min_x, min_y, max_x, max_y = polygon_bbox(polygon)
    min_x += inset
    min_y += inset
    max_x -= inset
    max_y -= inset
    if max_x <= min_x or max_y <= min_y:
        return None
    for _ in range(max_attempts):
        x = rng.randint(min_x, max_x)
        y = rng.randint(min_y, max_y)
        if point_in_polygon((x, y), polygon):
            return (x, y)
    return None


def polygon_centroid(polygon: list[tuple[int, int]]) -> tuple[int, int]:
    if not polygon:
        return (0, 0)
    a = 0.0
    cx = 0.0
    cy = 0.0
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a *= 0.5
    if abs(a) < 1e-6:
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        return (sum(xs) // n, sum(ys) // n)
    return (int(round(cx / (6 * a))), int(round(cy / (6 * a))))
