"""Tile map: parsing, procedural terrain rendering, collision and line-of-sight."""
import math
import pygame

from . import settings as S

TILE = S.TILE


def _noise(x, y, salt=0):
    h = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    h &= 0xFFFFFFFF
    return (h % 1000) / 1000.0


# Tile property table: solid (blocks walk), cover (blocks sight), bush (hides).
PROPS = {
    ".": dict(solid=False, cover=False, bush=False),  # dust ground
    ",": dict(solid=False, cover=False, bush=False),  # grass
    "P": dict(solid=False, cover=False, bush=False),  # road / path
    "f": dict(solid=False, cover=False, bush=False),  # interior floor
    "g": dict(solid=False, cover=False, bush=False),  # gate threshold
    "b": dict(solid=False, cover=False, bush=True),   # bush (hiding)
    "w": dict(solid=True,  cover=False, bush=False),  # water
    "#": dict(solid=True,  cover=True,  bush=False),  # stone wall
    "r": dict(solid=True,  cover=True,  bush=False),  # rubble
    "T": dict(solid=True,  cover=True,  bush=False),  # tree
    "C": dict(solid=True,  cover=True,  bush=False),  # crate stack (cover)
    "=": dict(solid=True,  cover=False, bush=False),  # low fence
    # ---- Act Two: the Twisted Castle Kingdom ----
    "m": dict(solid=False, cover=False, bush=False),  # court marble floor
    "c": dict(solid=False, cover=False, bush=False),  # red carpet
    "s": dict(solid=False, cover=False, bush=False),  # stage planks
    "k": dict(solid=True,  cover=True,  bush=False),  # castle wall
    "p": dict(solid=True,  cover=True,  bush=False),  # pillar / cover
}


class TileMap:
    def __init__(self, rows, buildings=None, decos=None):
        self.grid = [list(r) for r in rows]
        self.h = len(self.grid)
        self.w = max(len(r) for r in self.grid)
        for r in self.grid:
            while len(r) < self.w:
                r.append(".")
        self.pixw = self.w * TILE
        self.pixh = self.h * TILE
        self.buildings = buildings or []
        self.decos = decos or []
        self.solid = [[False] * self.w for _ in range(self.h)]
        self.cover = [[False] * self.w for _ in range(self.h)]
        self.bush = [[False] * self.w for _ in range(self.h)]
        self._build_flags()
        self.bg = None  # rendered lazily

    def _build_flags(self):
        for y in range(self.h):
            for x in range(self.w):
                p = PROPS.get(self.grid[y][x], PROPS["."])
                self.solid[y][x] = p["solid"]
                self.cover[y][x] = p["cover"]
                self.bush[y][x] = p["bush"]
        # stamp buildings (solid walls + cover) leaving the door cell open
        for b in self.buildings:
            for yy in range(b["y"], b["y"] + b["h"]):
                for xx in range(b["x"], b["x"] + b["w"]):
                    if 0 <= xx < self.w and 0 <= yy < self.h:
                        self.solid[yy][xx] = True
                        self.cover[yy][xx] = True
            dx, dy = b.get("door", (b["w"] // 2, b["h"] - 1))
            ddx, ddy = b["x"] + dx, b["y"] + dy
            if 0 <= ddx < self.w and 0 <= ddy < self.h:
                self.solid[ddy][ddx] = False
                self.cover[ddy][ddx] = False
        # crate-style decos add cover/solid
        for d in self.decos:
            if d[0] in ("crate", "barrel", "well", "cart"):
                tx, ty = d[1], d[2]
                if 0 <= tx < self.w and 0 <= ty < self.h:
                    self.solid[ty][tx] = True
                    if d[0] in ("crate", "cart"):
                        self.cover[ty][tx] = True

    # ---- queries ----------------------------------------------------------
    def is_solid_px(self, x, y):
        tx, ty = int(x // TILE), int(y // TILE)
        if tx < 0 or ty < 0 or tx >= self.w or ty >= self.h:
            return True
        return self.solid[ty][tx]

    def rect_blocked(self, rect):
        x0 = int(rect.left // TILE)
        x1 = int((rect.right - 1) // TILE)
        y0 = int(rect.top // TILE)
        y1 = int((rect.bottom - 1) // TILE)
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if tx < 0 or ty < 0 or tx >= self.w or ty >= self.h:
                    return True
                if self.solid[ty][tx]:
                    return True
        return False

    def in_bush(self, x, y):
        tx, ty = int(x // TILE), int(y // TILE)
        if 0 <= tx < self.w and 0 <= ty < self.h:
            return self.bush[ty][tx]
        return False

    def line_blocked(self, x0, y0, x1, y1):
        """True if a wall/cover tile lies on the segment (for vision)."""
        dist = math.hypot(x1 - x0, y1 - y0)
        steps = int(dist // 8) + 1
        for i in range(1, steps):
            t = i / steps
            px = x0 + (x1 - x0) * t
            py = y0 + (y1 - y0) * t
            tx, ty = int(px // TILE), int(py // TILE)
            if 0 <= tx < self.w and 0 <= ty < self.h and self.cover[ty][tx]:
                return True
        return False

    # ---- rendering --------------------------------------------------------
    def render(self):
        if self.bg is not None:
            return self.bg
        surf = pygame.Surface((self.pixw, self.pixh)).convert()
        for y in range(self.h):
            for x in range(self.w):
                self._draw_tile(surf, x, y)
        for b in self.buildings:
            self._draw_building(surf, b)
        for d in self.decos:
            self._draw_deco(surf, d)
        self.bg = surf
        return surf

    def _draw_tile(self, surf, x, y):
        ch = self.grid[y][x]
        px, py = x * TILE, y * TILE
        r = pygame.Rect(px, py, TILE, TILE)

        if ch in (".", "g", "P", "f", "r", "=", "T", "b", "C"):
            base = S.DUST if ch != "f" else S.SLATE
            pygame.draw.rect(surf, base, r)
            self._speckle(surf, x, y, base, S.DUST_DK, S.SAND)
        elif ch == ",":
            pygame.draw.rect(surf, S.GRASS, r)
            self._grass(surf, x, y)
        elif ch == "w":
            pygame.draw.rect(surf, S.WATER, r)
            for i in range(3):
                yy = py + 6 + i * 9 + int(2 * _noise(x, y, i))
                pygame.draw.line(surf, S.WATER_DK, (px + 3, yy), (px + TILE - 4, yy), 1)
        elif ch in ("m", "k", "p"):
            pygame.draw.rect(surf, S.COURT_FLOOR, r)
            pygame.draw.rect(surf, S.COURT_FLOOR_L, (px, py, TILE, 1))
            for i in range(2):
                vy = py + 9 + i * 13
                pygame.draw.line(surf, S.COURT_FLOOR_L,
                                 (px + 3, vy), (px + TILE - 4, vy - 3 + int(4 * _noise(x, y, i))), 1)
        elif ch == "c":
            pygame.draw.rect(surf, S.COURT_CARPET, r)
            pygame.draw.rect(surf, S.COURT_CARPET_D, r, 1)
            pygame.draw.line(surf, S.COURT_GOLD, (px, py + 2), (px + TILE, py + 2), 1)
            pygame.draw.line(surf, S.COURT_GOLD, (px, py + TILE - 3), (px + TILE, py + TILE - 3), 1)
        elif ch == "s":
            pygame.draw.rect(surf, S.STAGE_WOOD, r)
            for yy in range(py + 4, py + TILE, 7):
                pygame.draw.line(surf, S.STAGE_WOOD_D, (px, yy), (px + TILE, yy), 1)

        # path / road
        if ch in ("P", "g"):
            pygame.draw.rect(surf, S.STONE, r)
            pygame.draw.rect(surf, S.STONE_LT, (px + 1, py + 1, TILE - 2, 2))
            for i in range(2):
                for j in range(2):
                    cx = px + 6 + i * 14 + int(3 * _noise(x, y, i * 2 + j))
                    cy = py + 6 + j * 14
                    pygame.draw.rect(surf, S.SLATE, (cx, cy, 9, 9), 1)
        if ch == "f":
            pygame.draw.rect(surf, S.DARK, r, 1)
            pygame.draw.rect(surf, S.STONE, (px + 2, py + 2, 3, 3))

        # rubble
        if ch == "r":
            for i in range(4):
                rx = px + 4 + int(20 * _noise(x, y, i))
                ry = py + 6 + int(18 * _noise(x, y, i + 9))
                sz = 4 + int(5 * _noise(x, y, i + 3))
                pygame.draw.rect(surf, S.STONE, (rx, ry, sz, sz), border_radius=2)
                pygame.draw.rect(surf, S.SLATE, (rx, ry, sz, sz), 1, border_radius=2)
        # fence
        if ch == "=":
            pygame.draw.line(surf, S.WOOD_DK, (px, py + 12), (px + TILE, py + 12), 3)
            pygame.draw.line(surf, S.WOOD_DK, (px, py + 22), (px + TILE, py + 22), 3)
            for fx in (px + 6, px + 22):
                pygame.draw.rect(surf, S.WOOD, (fx, py + 6, 4, 22))
        # bush
        if ch == "b":
            pygame.draw.rect(surf, S.GRASS_DK, r)
            for i in range(5):
                bx = px + 5 + int(18 * _noise(x, y, i))
                by = py + 8 + int(16 * _noise(x, y, i + 5))
                pygame.draw.circle(surf, S.GRASS, (bx, by), 6)
                pygame.draw.circle(surf, S.GRASS_LT, (bx - 1, by - 1), 3)
        # tree
        if ch == "T":
            pygame.draw.rect(surf, S.GRASS_DK, r)
            pygame.draw.rect(surf, S.WOOD_DK, (px + TILE // 2 - 3, py + TILE - 12, 6, 12))
            pygame.draw.circle(surf, S.GRASS_DK, (px + TILE // 2, py + 12), 13)
            pygame.draw.circle(surf, S.GRASS, (px + TILE // 2, py + 11), 11)
            pygame.draw.circle(surf, S.GRASS_LT, (px + TILE // 2 - 3, py + 8), 5)
        # crate stack
        if ch == "C":
            self._crate(surf, px + 2, py + 2, TILE - 4, TILE - 4)

        # subtle depth grid line
        if not PROPS.get(ch, PROPS["."])["solid"] and ch != "w":
            pygame.draw.line(surf, (0, 0, 0, 30), (px, py + TILE - 1), (px + TILE, py + TILE - 1))

        # wall (drawn last so it sits crisp)
        if ch == "#":
            self._wall(surf, px, py)
        if ch == "k":
            self._court_wall(surf, px, py)
        if ch == "p":
            self._pillar(surf, px, py)

    def _court_wall(self, surf, px, py):
        r = pygame.Rect(px, py, TILE, TILE)
        pygame.draw.rect(surf, S.COURT_STONE, r)
        pygame.draw.rect(surf, S.COURT_STONE_L, (px, py, TILE, 4))
        pygame.draw.rect(surf, S.NEAR_BLACK, (px, py + TILE - 4, TILE, 4))
        pygame.draw.line(surf, S.COURT_GOLD, (px, py + 14), (px + TILE, py + 14), 1)
        pygame.draw.line(surf, S.NEAR_BLACK, (px + 16, py), (px + 16, py + 14), 1)
        pygame.draw.line(surf, S.NEAR_BLACK, (px + 8, py + 14), (px + 8, py + TILE), 1)
        pygame.draw.line(surf, S.NEAR_BLACK, (px + 24, py + 14), (px + 24, py + TILE), 1)

    def _pillar(self, surf, px, py):
        cx = px + TILE // 2
        pygame.draw.rect(surf, S.COURT_STONE_L, (cx - 8, py + 2, 16, TILE - 4), border_radius=4)
        pygame.draw.rect(surf, S.COURT_STONE, (cx - 8, py + 2, 6, TILE - 4), border_radius=4)
        pygame.draw.rect(surf, S.COURT_GOLD, (cx - 9, py + 1, 18, 3), border_radius=2)
        pygame.draw.rect(surf, S.COURT_GOLD, (cx - 9, py + TILE - 5, 18, 3), border_radius=2)

    def _speckle(self, surf, x, y, base, dk, lt):
        px, py = x * TILE, y * TILE
        for i in range(5):
            n = _noise(x, y, i)
            sx = px + int(n * (TILE - 4))
            sy = py + int(_noise(x, y, i + 11) * (TILE - 4))
            col = dk if i % 2 == 0 else lt
            pygame.draw.rect(surf, col, (sx, sy, 2, 2))

    def _grass(self, surf, x, y):
        px, py = x * TILE, y * TILE
        for i in range(6):
            bx = px + int(_noise(x, y, i) * TILE)
            by = py + int(_noise(x, y, i + 7) * TILE)
            col = S.GRASS_LT if i % 2 == 0 else S.GRASS_DK
            pygame.draw.line(surf, col, (bx, by), (bx, by - 3), 1)

    def _wall(self, surf, px, py):
        r = pygame.Rect(px, py, TILE, TILE)
        pygame.draw.rect(surf, S.STONE, r)
        pygame.draw.rect(surf, S.STONE_LT, (px, py, TILE, 4))
        pygame.draw.rect(surf, S.SLATE, (px, py + TILE - 5, TILE, 5))
        pygame.draw.line(surf, S.DARK, (px, py + 15), (px + TILE, py + 15), 1)
        pygame.draw.line(surf, S.DARK, (px + 15, py), (px + 15, py + 15), 1)
        pygame.draw.line(surf, S.DARK, (px + 8, py + 15), (px + 8, py + TILE), 1)
        pygame.draw.line(surf, S.DARK, (px + 23, py + 15), (px + 23, py + TILE), 1)

    def _crate(self, surf, x, y, w, h):
        pygame.draw.rect(surf, S.WOOD, (x, y, w, h), border_radius=2)
        pygame.draw.rect(surf, S.WOOD_DK, (x, y, w, h), 2, border_radius=2)
        pygame.draw.line(surf, S.WOOD_DK, (x, y), (x + w, y + h), 2)
        pygame.draw.line(surf, S.WOOD_DK, (x + w, y), (x, y + h), 2)

    def _draw_building(self, surf, b):
        px, py = b["x"] * TILE, b["y"] * TILE
        w, h = b["w"] * TILE, b["h"] * TILE
        roof = b.get("roof", S.ROOF)
        roof_d = b.get("roof_d", S.ROOF_DK)
        ruined = b.get("ruined", False)
        # wall body
        pygame.draw.rect(surf, S.DUST_DK, (px, py + 10, w, h - 10))
        pygame.draw.rect(surf, S.WOOD_DK, (px, py + 10, w, h - 10), 2)
        # plank texture
        for yy in range(py + 16, py + h - 4, 8):
            pygame.draw.line(surf, S.WOOD_DK, (px + 2, yy), (px + w - 2, yy), 1)
        # roof
        pygame.draw.rect(surf, roof, (px - 3, py, w + 6, 16), border_radius=3)
        pygame.draw.rect(surf, roof_d, (px - 3, py + 11, w + 6, 5))
        for xx in range(px, px + w, 8):
            pygame.draw.line(surf, roof_d, (xx, py + 1), (xx, py + 14), 1)
        # door
        dx, dy = b.get("door", (b["w"] // 2, b["h"] - 1))
        dpx, dpy = (b["x"] + dx) * TILE, (b["y"] + dy) * TILE
        pygame.draw.rect(surf, S.NEAR_BLACK, (dpx + 6, dpy + 2, TILE - 12, TILE - 2), border_radius=3)
        pygame.draw.rect(surf, S.WOOD, (dpx + 6, dpy + 2, TILE - 12, TILE - 2), 2, border_radius=3)
        # window
        if b["w"] >= 3:
            wx, wy = px + w // 2 - 6, py + 20
            pygame.draw.rect(surf, S.NEAR_BLACK, (wx, wy, 12, 12), border_radius=2)
            pygame.draw.line(surf, S.WOOD, (wx + 6, wy), (wx + 6, wy + 12))
            pygame.draw.line(surf, S.WOOD, (wx, wy + 6), (wx + 12, wy + 6))
        if ruined:
            # break the roofline and scorch a corner
            pygame.draw.polygon(surf, S.NEAR_BLACK,
                                [(px + w - 14, py), (px + w + 3, py), (px + w + 3, py + 16),
                                 (px + w - 4, py + 8)])
            for i in range(6):
                rx = px + 6 + int(_noise(b["x"], b["y"], i) * (w - 12))
                ry = py + h - 10 + int(_noise(b["x"], b["y"], i + 4) * 8)
                pygame.draw.rect(surf, S.STONE, (rx, ry, 4, 4))

    def _draw_deco(self, surf, d):
        kind = d[0]
        px, py = d[1] * TILE, d[2] * TILE
        if kind == "crate":
            self._crate(surf, px + 3, py + 4, TILE - 6, TILE - 6)
        elif kind == "barrel":
            pygame.draw.ellipse(surf, S.WOOD, (px + 6, py + 4, TILE - 12, TILE - 6))
            pygame.draw.ellipse(surf, S.WOOD_DK, (px + 6, py + 4, TILE - 12, TILE - 6), 2)
            pygame.draw.line(surf, S.WOOD_DK, (px + 6, py + 14), (px + TILE - 6, py + 14), 2)
        elif kind == "cart":
            pygame.draw.rect(surf, S.WOOD_DK, (px + 2, py + 6, TILE - 4, TILE - 12), border_radius=2)
            pygame.draw.circle(surf, S.INK, (px + 8, py + TILE - 6), 5)
            pygame.draw.circle(surf, S.INK, (px + TILE - 8, py + TILE - 6), 5)
        elif kind == "well":
            pygame.draw.circle(surf, S.STONE, (px + TILE // 2, py + TILE // 2), 12)
            pygame.draw.circle(surf, S.NEAR_BLACK, (px + TILE // 2, py + TILE // 2), 7)
            pygame.draw.rect(surf, S.WOOD, (px + 4, py - 4, 3, 12))
            pygame.draw.rect(surf, S.WOOD, (px + TILE - 7, py - 4, 3, 12))
        elif kind == "flower":
            for i in range(3):
                fx = px + 8 + i * 7
                fy = py + 14 + int(4 * _noise(d[1], d[2], i))
                pygame.draw.line(surf, S.GRASS_DK, (fx, fy), (fx, fy + 6))
                pygame.draw.circle(surf, [S.WARN, S.EERIE, S.ALARM][i % 3], (fx, fy), 2)
        elif kind == "sign":
            pygame.draw.rect(surf, S.WOOD, (px + 6, py + 4, TILE - 12, 14), border_radius=2)
            pygame.draw.rect(surf, S.WOOD_DK, (px + 6, py + 4, TILE - 12, 14), 1, border_radius=2)
            pygame.draw.rect(surf, S.WOOD_DK, (px + TILE // 2 - 2, py + 18, 4, 12))
            pygame.draw.line(surf, S.INK, (px + 9, py + 9), (px + TILE - 9, py + 9), 1)
            pygame.draw.line(surf, S.INK, (px + 9, py + 13), (px + TILE - 11, py + 13), 1)
        elif kind == "banner":
            # Sufflok's banner: red drape with a harsh gold mark
            pygame.draw.rect(surf, S.SUFFLOK_RED_D, (px + 8, py, 16, TILE + 6))
            pygame.draw.rect(surf, S.SUFFLOK_RED, (px + 10, py + 2, 12, TILE))
            pygame.draw.polygon(surf, S.SUFFLOK_RED, [(px + 10, py + TILE + 2),
                                (px + 16, py + TILE - 4), (px + 22, py + TILE + 2)])
            cx, cy = px + 16, py + 14
            pygame.draw.circle(surf, S.GOLD, (cx, cy), 5, 1)
            pygame.draw.line(surf, S.GOLD, (cx, cy - 6), (cx, cy + 6), 1)
            pygame.draw.line(surf, S.GOLD, (cx - 5, cy + 5), (cx + 5, cy + 5), 1)
        elif kind == "mark":
            # Sufflok's symbol sprayed on the ground/wall
            cx, cy = px + TILE // 2, py + TILE // 2
            pygame.draw.circle(surf, S.SUFFLOK_RED_D, (cx, cy), 11, 2)
            pygame.draw.line(surf, S.SUFFLOK_RED_D, (cx, cy - 9), (cx, cy + 9), 2)
            pygame.draw.line(surf, S.SUFFLOK_RED_D, (cx - 8, cy + 7), (cx + 8, cy + 7), 2)
        elif kind == "rubblepile":
            for i in range(7):
                rx = px + int(_noise(d[1], d[2], i) * (TILE - 6))
                ry = py + int(_noise(d[1], d[2], i + 3) * (TILE - 6))
                pygame.draw.rect(surf, S.STONE, (rx, ry, 5, 5), border_radius=1)
