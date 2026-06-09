"""Actors: player, villagers, guards, checkpoints and supply pickups."""
import math
import pygame

from . import settings as S
from .assets import CELL_W, CELL_H, FOOT_Y

WALK_SEQ = [1, 0, 2, 0]
WALK_FRAME_T = 0.13


def _facing(dx, dy):
    if abs(dx) > abs(dy):
        return "right" if dx > 0 else "left"
    return "down" if dy >= 0 else "up"


class Character:
    """Base sprite actor with shadow + walk animation, foot-anchored."""

    def __init__(self, frames, x, y, name="?"):
        self.frames = frames
        self.x = float(x)
        self.y = float(y)
        self.name = name
        self.dir = "down"
        self.anim_t = 0.0
        self.moving = False
        self.w = 16
        self.h = 12
        self.overlay = None  # e.g. Ankam's hat

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w / 2), int(self.y - self.h), self.w, self.h)

    def feet(self):
        return (self.x, self.y)

    def _anim_frame(self):
        if not self.moving:
            return 0
        i = int(self.anim_t / WALK_FRAME_T) % len(WALK_SEQ)
        return WALK_SEQ[i]

    def update_anim(self, dt):
        if self.moving:
            self.anim_t += dt
        else:
            self.anim_t = 0.0

    def draw(self, surf, cam):
        frame = self._anim_frame()
        spr = self.frames[(self.dir, frame)]
        sx = int(self.x - CELL_W / 2 - cam[0])
        sy = int(self.y - FOOT_Y - cam[1])
        # shadow
        sh = pygame.Surface((22, 9), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), (0, 0, 22, 9))
        surf.blit(sh, (int(self.x - 11 - cam[0]), int(self.y - 5 - cam[1])))
        surf.blit(spr, (sx, sy))
        if self.overlay:
            surf.blit(self.overlay, (sx, sy))


class Player(Character):
    def __init__(self, frames, x, y):
        super().__init__(frames, x, y, "You")
        self.speed = S.PLAYER_SPEED
        self.w = 16
        self.h = 12
        self.stamina = S.STAMINA_MAX
        self.dash_t = 0.0
        self.dash_cd = 0.0
        self.dash_dir = (1.0, 0.0)
        self.trail = []         # recent positions for the dash streak

    @property
    def dashing(self):
        return self.dash_t > 0

    def can_dash(self):
        return self.dash_cd <= 0 and self.stamina >= S.DASH_STAMINA_COST and self.dash_t <= 0

    def start_dash(self, dx, dy):
        if not self.can_dash():
            return False
        if dx == 0 and dy == 0:
            vx, vy = {"left": (-1, 0), "right": (1, 0),
                      "up": (0, -1), "down": (0, 1)}[self.dir]
        else:
            m = math.hypot(dx, dy)
            vx, vy = dx / m, dy / m
        self.dash_dir = (vx, vy)
        self.dash_t = S.DASH_TIME
        self.dash_cd = S.DASH_COOLDOWN
        self.stamina -= S.DASH_STAMINA_COST
        self.dir = _facing(vx, vy)
        return True

    def tick(self, dt):
        if self.dash_cd > 0:
            self.dash_cd -= dt
        if self.dash_t > 0:
            self.dash_t -= dt
            self.trail.append((self.x, self.y))
            if len(self.trail) > 6:
                self.trail.pop(0)
        else:
            if self.trail:
                self.trail.pop(0)
            if self.stamina < S.STAMINA_MAX:
                self.stamina = min(S.STAMINA_MAX, self.stamina + S.STAMINA_REGEN * dt)

    def dash_step(self, tmap, blockers=None):
        vx, vy = self.dash_dir
        self._axis(vx * S.DASH_SPEED, 0, tmap, blockers)
        self._axis(0, vy * S.DASH_SPEED, tmap, blockers)
        self.moving = True

    def move(self, dx, dy, tmap, blockers=None):
        self.moving = dx != 0 or dy != 0
        if self.moving:
            self.dir = _facing(dx, dy)
            mag = math.hypot(dx, dy) or 1
            vx = dx / mag * self.speed
            vy = dy / mag * self.speed
            self._axis(vx, 0, tmap, blockers)
            self._axis(0, vy, tmap, blockers)

    def _axis(self, vx, vy, tmap, blockers):
        nx = self.x + vx
        ny = self.y + vy
        r = pygame.Rect(int(nx - self.w / 2), int(ny - self.h), self.w, self.h)
        if tmap.rect_blocked(r):
            return
        if blockers:
            for b in blockers:
                if b is not self and r.colliderect(b.rect):
                    return
        self.x, self.y = nx, ny
        # clamp to map
        self.x = max(self.w, min(tmap.pixw - self.w, self.x))
        self.y = max(self.h + 4, min(tmap.pixh - 2, self.y))


class Pebble:
    """A sling pebble: stuns a guard on a direct hit, makes a luring noise where
    it lands.  This merges the old 'throw a noise' into the weapon itself."""

    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.life = S.PEBBLE_LIFE
        self.dead = False
        self.hit_wall = False
        self.trail = []

    def update(self, dt, tmap):
        self.life -= dt
        steps = 3
        for _ in range(steps):
            nx = self.x + self.vx / steps
            ny = self.y + self.vy / steps
            if tmap.is_solid_px(nx, ny - 6):
                self.dead = True
                self.hit_wall = True
                return
            self.x, self.y = nx, ny
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
        if self.life <= 0:
            self.dead = True
            self.hit_wall = True

    def draw(self, surf, cam):
        for i, (tx, ty) in enumerate(self.trail):
            a = int(40 + i * 24)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*S.PEBBLE_COL, a), (3, 3), 2)
            surf.blit(s, (int(tx - cam[0] - 3), int(ty - 6 - cam[1] - 3)))
        pygame.draw.circle(surf, S.PEBBLE_COL,
                           (int(self.x - cam[0]), int(self.y - 6 - cam[1])), 3)
        pygame.draw.circle(surf, S.WOOD_DK,
                           (int(self.x - cam[0]), int(self.y - 6 - cam[1])), 3, 1)


class NPC(Character):
    def __init__(self, frames, x, y, name, wander=False, face="down"):
        super().__init__(frames, x, y, name)
        self.dir = face
        self.home = (x, y)
        self.wander = wander
        self.t = 0.0
        self.vx = self.vy = 0.0
        self.retarget = 0.0
        self.talk_lock = False  # face player & stop while talking

    def update(self, dt, tmap):
        if self.talk_lock:
            self.moving = False
            self.update_anim(dt)
            return
        if not self.wander:
            self.moving = False
            self.update_anim(dt)
            return
        self.retarget -= dt
        if self.retarget <= 0:
            self.retarget = 1.4 + (hash((int(self.x), int(self.y), int(self.t))) % 100) / 60.0
            import random
            if random.random() < 0.45:
                self.vx = random.choice([-1, 0, 1]) * 0.5
                self.vy = random.choice([-1, 0, 1]) * 0.5
            else:
                self.vx = self.vy = 0.0
        self.t += dt
        moved = False
        if self.vx or self.vy:
            # stay near home
            if abs(self.x + self.vx - self.home[0]) < 48 and abs(self.y + self.vy - self.home[1]) < 48:
                r = pygame.Rect(int(self.x + self.vx - self.w / 2),
                                int(self.y + self.vy - self.h), self.w, self.h)
                if not tmap.rect_blocked(r):
                    self.x += self.vx
                    self.y += self.vy
                    self.dir = _facing(self.vx, self.vy)
                    moved = True
        self.moving = moved
        self.update_anim(dt)

    def face_to(self, tx, ty):
        self.dir = _facing(tx - self.x, ty - self.y)


def ray_hit(tmap, x0, y0, ang, maxd):
    """March a ray until it hits a cover tile; return endpoint."""
    step = 7.0
    d = 0.0
    ca, sa = math.cos(ang), math.sin(ang)
    while d < maxd:
        d += step
        px = x0 + ca * d
        py = y0 + sa * d
        tx, ty = int(px // S.TILE), int(py // S.TILE)
        if tx < 0 or ty < 0 or tx >= tmap.w or ty >= tmap.h:
            return x0 + ca * d, y0 + sa * d
        if tmap.cover[ty][tx]:
            return px, py
    return x0 + ca * maxd, y0 + sa * maxd


class Guard(NPC):
    def __init__(self, frames, x, y, waypoints=None, name="Guard"):
        super().__init__(frames, x, y, name)
        self.waypoints = waypoints or [(x, y)]
        self.wp = 0
        self.face_angle = math.pi / 2  # radians, pointing down
        self.mode = "patrol"           # patrol | look | chase | stunned
        self.look_t = 0.0
        self.sweep = 0.0
        self.target = None
        self.stun_t = 0.0
        self.speed = S.GUARD_PATROL_SPEED
        self.lost_t = 0.0
        self.captain = False
        self.chase_speed = None      # override for elites like the Captain

    def sees(self, px, py, tmap, in_bush):
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        rng = S.VISION_RANGE
        if dist > rng or dist < 1:
            return 0.0
        ang = math.atan2(dy, dx)
        diff = abs((ang - self.face_angle + math.pi) % (2 * math.pi) - math.pi)
        if math.degrees(diff) > S.VISION_HALF_ANGLE:
            return 0.0
        if tmap.line_blocked(self.x, self.y, px, py):
            return 0.0
        factor = 1.0 - dist / rng
        if in_bush:
            factor *= S.BUSH_DETECT_MULT
        return factor

    def update(self, dt, tmap):
        if self.mode == "stunned":
            self.stun_t -= dt
            self.moving = False
            if self.stun_t <= 0:
                self.mode = "patrol"
            self.update_anim(dt)
            return

        if self.mode == "chase" and self.target:
            self.speed = self.chase_speed or S.GUARD_CHASE_SPEED
            self._step_to(self.target[0], self.target[1], tmap)
        elif self.mode == "investigate" and self.target:
            self.speed = S.GUARD_PATROL_SPEED
            self._step_to(self.target[0], self.target[1], tmap)
            if abs(self.x - self.target[0]) < 5 and abs(self.y - self.target[1]) < 5:
                self.mode = "look"
                self.look_t = 1.2
                self.target = None
        elif self.mode == "look":
            self.moving = False
            self.look_t -= dt
            self.sweep += dt
            self.face_angle += math.sin(self.sweep * 3.0) * dt * 1.6
            if self.look_t <= 0:
                self.mode = "patrol"
        else:  # patrol
            self.speed = S.GUARD_PATROL_SPEED
            tx, ty = self.waypoints[self.wp]
            if abs(self.x - tx) < 3 and abs(self.y - ty) < 3:
                self.wp = (self.wp + 1) % len(self.waypoints)
                self.mode = "look"
                self.look_t = 0.7
            else:
                self._step_to(tx, ty, tmap)
        self.update_anim(dt)

    def _step_to(self, tx, ty, tmap):
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy) or 1
        vx, vy = dx / dist * self.speed, dy / dist * self.speed
        self.face_angle = math.atan2(vy, vx)
        self.dir = _facing(vx, vy)
        r = pygame.Rect(int(self.x + vx - self.w / 2), int(self.y + vy - self.h), self.w, self.h)
        if not tmap.rect_blocked(r):
            self.x += vx
            self.y += vy
            self.moving = True
        else:
            # simple wall-slide
            r2 = pygame.Rect(int(self.x + vx - self.w / 2), int(self.y - self.h), self.w, self.h)
            if not tmap.rect_blocked(r2):
                self.x += vx
            else:
                self.y += vy
            self.moving = True

    def draw_cone(self, surf, cam, tmap, color):
        pts = [(self.x - cam[0], self.y - cam[1])]
        half = math.radians(S.VISION_HALF_ANGLE)
        rays = 13
        for i in range(rays + 1):
            a = self.face_angle - half + (2 * half) * i / rays
            hx, hy = ray_hit(tmap, self.x, self.y, a, S.VISION_RANGE)
            pts.append((hx - cam[0], hy - cam[1]))
        cone = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(cone, (*color, 46), pts)
        pygame.draw.polygon(cone, (*color, 90), pts, 1)
        surf.blit(cone, (0, 0))


class Checkpoint:
    """A 'music note' save point. Hums, glows, remembers you."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.t = 0.0
        self.activated = False
        self.pulse = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 14), int(self.y - 30), 28, 36)

    def update(self, dt):
        self.t += dt
        if self.pulse > 0:
            self.pulse -= dt

    def ping(self):
        self.pulse = 1.0
        self.activated = True

    def draw(self, surf, cam, tint):
        bob = math.sin(self.t * 2.2) * 4
        cx = self.x - cam[0]
        cy = self.y - 18 - cam[1] + bob
        # glow
        glow_r = 22 + math.sin(self.t * 3.0) * 3 + (self.pulse * 18)
        glow = pygame.Surface((int(glow_r * 2), int(glow_r * 2)), pygame.SRCALPHA)
        for rr in range(int(glow_r), 0, -3):
            a = int(60 * (1 - rr / glow_r))
            pygame.draw.circle(glow, (*tint, a), (int(glow_r), int(glow_r)), rr)
        surf.blit(glow, (cx - glow_r, cy - glow_r))
        # base shadow
        sh = pygame.Surface((24, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), (0, 0, 24, 8))
        surf.blit(sh, (cx - 12, self.y - 4 - cam[1]))
        # the note glyph: stem + head + flag
        col = tint
        pygame.draw.line(surf, col, (cx + 5, cy - 14), (cx + 5, cy + 6), 3)
        pygame.draw.ellipse(surf, col, (cx - 4, cy + 2, 12, 9))
        pygame.draw.ellipse(surf, S.WHITE, (cx - 1, cy + 4, 4, 4))
        pygame.draw.line(surf, col, (cx + 5, cy - 14), (cx + 12, cy - 9), 3)
        # faint staff lines drifting up
        for i in range(3):
            yy = cy - 18 - i * 7 - (self.t * 10) % 7
            a = max(0, 90 - i * 30)
            pygame.draw.line(surf, (*tint, a), (cx - 8, yy), (cx + 10, yy), 1)


class Supply:
    """A crate of stolen food/medicine to recover during the mission."""

    def __init__(self, x, y, kind="food"):
        self.x = float(x)
        self.y = float(y)
        self.kind = kind
        self.taken = False
        self.t = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - 13), int(self.y - 24), 26, 28)

    def update(self, dt):
        self.t += dt

    def draw(self, surf, cam):
        if self.taken:
            return
        cx = int(self.x - cam[0])
        cy = int(self.y - cam[1])
        sh = pygame.Surface((26, 9), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 80), (0, 0, 26, 9))
        surf.blit(sh, (cx - 13, cy - 3))
        # crate
        pygame.draw.rect(surf, S.WOOD, (cx - 11, cy - 22, 22, 22), border_radius=2)
        pygame.draw.rect(surf, S.WOOD_DK, (cx - 11, cy - 22, 22, 22), 2, border_radius=2)
        pygame.draw.line(surf, S.WOOD_DK, (cx - 11, cy - 11), (cx + 11, cy - 11), 1)
        # contents glint
        mark = S.WARN if self.kind == "food" else S.EERIE
        pygame.draw.circle(surf, mark, (cx, cy - 11), 4)
        if self.kind == "medicine":
            pygame.draw.line(surf, S.WHITE, (cx, cy - 14), (cx, cy - 8), 2)
            pygame.draw.line(surf, S.WHITE, (cx - 3, cy - 11), (cx + 3, cy - 11), 2)
        else:
            pygame.draw.circle(surf, S.WOOD_DK, (cx, cy - 11), 4, 1)
        # gentle float arrow when reachable
        a = int(120 + 80 * math.sin(self.t * 4))
        pygame.draw.polygon(surf, (*S.GOLD, a),
                            [(cx, cy - 30), (cx - 4, cy - 35), (cx + 4, cy - 35)])
