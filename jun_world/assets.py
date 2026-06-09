"""Procedural art, fonts and audio.

No external files are used.  Character sprites are drawn from coloured shapes
in four facing directions with a small two-step walk animation.  Sound effects
are synthesised with numpy when available and degrade to silence otherwise.
"""
import math
import pygame

from . import settings as S

# Sprite cell: wider/taller than a tile so heads can rise above the feet.
CELL_W = 28
CELL_H = 40
FOOT_Y = 38  # y of the foot anchor inside the cell

DIRS = ("down", "up", "left", "right")


# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------
class Fonts:
    def __init__(self):
        pygame.font.init()
        self.tiny = pygame.font.Font(None, 16)
        self.small = pygame.font.Font(None, 20)
        self.body = pygame.font.Font(None, 24)
        self.mid = pygame.font.Font(None, 30)
        self.big = pygame.font.Font(None, 52)
        self.huge = pygame.font.Font(None, 84)
        self.name = pygame.font.Font(None, 26)
        self.name.set_bold(True)
        self.big.set_bold(True)
        self.huge.set_bold(True)


# ---------------------------------------------------------------------------
# Character sprite generation
# ---------------------------------------------------------------------------
def _lerp(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _draw_character(body, body_d, skin, hair, direction, frame, cape=None):
    """Return a CELL_W x CELL_H per-pixel-alpha surface of one pose."""
    surf = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
    cx = CELL_W // 2

    # Walk cycle: frame 0 idle, 1 left foot fwd, 2 right foot fwd.
    step = 0
    if frame == 1:
        step = -1
    elif frame == 2:
        step = 1

    # --- legs ---
    leg_w, leg_h = 5, 9
    ly = FOOT_Y - leg_h
    la = step
    lb = -step
    pygame.draw.rect(surf, body_d, (cx - 6, ly + max(0, la), leg_w, leg_h - abs(la)), border_radius=2)
    pygame.draw.rect(surf, body_d, (cx + 1, ly + max(0, lb), leg_w, leg_h - abs(lb)), border_radius=2)

    # --- optional cape behind body (for Ankam/Sufflok flair) ---
    if cape:
        pygame.draw.polygon(surf, cape, [(cx - 8, 16), (cx + 8, 16), (cx + 6, FOOT_Y - 6), (cx - 6, FOOT_Y - 6)])

    # --- torso ---
    torso = pygame.Rect(cx - 8, 16, 16, 15)
    pygame.draw.rect(surf, body, torso, border_radius=4)
    pygame.draw.rect(surf, body_d, (cx, 16, 8, 15), border_top_right_radius=4, border_bottom_right_radius=4)
    pygame.draw.rect(surf, _lerp(body, S.WHITE, 0.12), (cx - 8, 16, 16, 3), border_radius=3)

    # --- arms (swing opposite to legs) ---
    arm_w, arm_h = 4, 11
    ax = step
    pygame.draw.rect(surf, body_d, (cx - 11, 17 - ax, arm_w, arm_h), border_radius=2)
    pygame.draw.rect(surf, body_d, (cx + 7, 17 + ax, arm_w, arm_h), border_radius=2)

    # --- head ---
    hx, hy, hr = cx, 11, 7
    pygame.draw.circle(surf, skin, (hx, hy), hr)
    pygame.draw.circle(surf, _lerp(skin, S.BLACK, 0.18), (hx, hy), hr, 1)

    if direction == "down":
        # hair cap on the upper half of the head, face + eyes below
        pygame.draw.rect(surf, hair, (hx - hr, hy - hr, hr * 2, hr - 1), border_radius=3)
        pygame.draw.circle(surf, S.INK, (hx - 3, hy + 2), 1)
        pygame.draw.circle(surf, S.INK, (hx + 3, hy + 2), 1)
    elif direction == "up":
        # back of the head: mostly hair
        pygame.draw.circle(surf, hair, (hx, hy), hr)
        pygame.draw.circle(surf, _lerp(hair, S.BLACK, 0.2), (hx, hy), hr, 1)
    elif direction == "left":
        # facing left: face/eye on the left; hair caps the whole top and wraps the back (right)
        pygame.draw.rect(surf, hair, (hx - hr, hy - hr, hr * 2, hr), border_radius=3)
        pygame.draw.rect(surf, hair, (hx + 1, hy - hr, hr, hr + 3), border_radius=2)
        pygame.draw.circle(surf, _lerp(hair, S.BLACK, 0.2), (hx + 2, hy - 1), 1)
        pygame.draw.circle(surf, S.INK, (hx - 3, hy + 1), 1)
    elif direction == "right":
        pygame.draw.rect(surf, hair, (hx - hr, hy - hr, hr * 2, hr), border_radius=3)
        pygame.draw.rect(surf, hair, (hx - hr - 1, hy - hr, hr, hr + 3), border_radius=2)
        pygame.draw.circle(surf, _lerp(hair, S.BLACK, 0.2), (hx - 2, hy - 1), 1)
        pygame.draw.circle(surf, S.INK, (hx + 3, hy + 1), 1)

    return surf


def build_actor(body, body_d, skin, hair, cape=None):
    """Return {(direction, frame): Surface} for frames 0,1,2."""
    out = {}
    for d in DIRS:
        for f in range(3):
            out[(d, f)] = _draw_character(body, body_d, skin, hair, d, f, cape)
    return out


def build_all_actors():
    """All named character sprite sets used in Act One."""
    a = {}
    a["player"] = build_actor(S.PLAYER_BODY, S.PLAYER_BODY_D, S.PLAYER_SKIN, (54, 40, 36))
    a["rook"] = build_actor(S.ROOK_BODY, S.ROOK_BODY_D, S.ROOK_SKIN, (40, 30, 28))
    a["ankam"] = build_actor(S.ANKAM_BODY, S.ANKAM_BODY_D, S.ANKAM_SKIN, (32, 30, 30),
                            cape=S.SUFFLOK_RED_D)
    a["guard"] = build_actor(S.GUARD_BODY, S.GUARD_BODY_D, (190, 170, 150), (30, 28, 34))
    for i, col in enumerate(S.VILLAGER_COLS):
        d = tuple(max(0, c - 28) for c in col)
        a["villager%d" % i] = build_actor(col, d, (206, 178, 150), (48, 40, 36))
    return a


def hat_overlay():
    """A crooked little official hat drawn for Mr. Ankam (blitted over head)."""
    s = pygame.Surface((CELL_W, CELL_H), pygame.SRCALPHA)
    cx = CELL_W // 2
    pygame.draw.ellipse(s, S.INK, (cx - 8, 4, 16, 4))
    pygame.draw.rect(s, S.SUFFLOK_RED_D, (cx - 5, 0, 10, 5))
    pygame.draw.circle(s, S.GOLD, (cx, 2), 1)
    return s


# ---------------------------------------------------------------------------
# Audio (numpy synth, optional)
# ---------------------------------------------------------------------------
class Audio:
    def __init__(self):
        self.ok = False
        self.sounds = {}
        try:
            import numpy as np
            self.np = np
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self.ok = True
            self._build()
        except Exception:
            self.ok = False

    def _tone(self, freq, dur, vol=0.4, wave="sine", fade=0.6, detune=0.0):
        np = self.np
        n = int(44100 * dur)
        t = np.linspace(0, dur, n, endpoint=False)
        f = freq
        if wave == "sine":
            w = np.sin(2 * np.pi * f * t)
            if detune:
                w = 0.6 * w + 0.4 * np.sin(2 * np.pi * (f * (1 + detune)) * t)
        elif wave == "square":
            w = np.sign(np.sin(2 * np.pi * f * t))
        elif wave == "tri":
            w = 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1
        else:  # noise
            w = np.random.uniform(-1, 1, n)
        env = np.ones(n)
        a = int(n * 0.02)
        if a > 0:
            env[:a] = np.linspace(0, 1, a)
        d = int(n * fade)
        if d > 0:
            env[-d:] = np.linspace(1, 0, d)
        return w * env * vol

    def _make(self, samples):
        np = self.np
        s = np.clip(samples, -1, 1)
        s = (s * 32767).astype(np.int16)
        stereo = np.column_stack((s, s))
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

    def _build(self):
        np = self.np
        try:
            self.sounds["step"] = self._make(self._tone(140, 0.06, 0.16, "tri", 0.9))
            self.sounds["ui_move"] = self._make(self._tone(420, 0.05, 0.2, "square", 0.8))
            self.sounds["ui_ok"] = self._make(
                np.concatenate([self._tone(520, 0.05, 0.22, "square"),
                                self._tone(780, 0.08, 0.22, "square")]))
            self.sounds["talk"] = self._make(self._tone(300, 0.03, 0.13, "square", 0.9))
            self.sounds["pickup"] = self._make(
                np.concatenate([self._tone(660, 0.07, 0.25, "tri"),
                                self._tone(990, 0.10, 0.22, "tri")]))
            self.sounds["alert"] = self._make(
                np.concatenate([self._tone(880, 0.10, 0.3, "square", 0.4),
                                self._tone(880, 0.10, 0.3, "square", 0.4),
                                self._tone(660, 0.18, 0.3, "square")]))
            self.sounds["hum"] = self._make(
                self._tone(196, 0.55, 0.16, "sine", 0.5, detune=0.01))
            self.sounds["save"] = self._make(
                np.concatenate([self._tone(392, 0.08, 0.2, "sine"),
                                self._tone(587, 0.10, 0.2, "sine"),
                                self._tone(784, 0.16, 0.2, "sine")]))
            self.sounds["portal"] = self._make(
                self._tone(90, 0.9, 0.3, "noise", 0.85) * 0.4
                + self._tone(120, 0.9, 0.3, "sine", 0.85))
            self.sounds["hurt"] = self._make(
                np.concatenate([self._tone(220, 0.08, 0.3, "square"),
                                self._tone(150, 0.16, 0.3, "square")]))
            self.sounds["caught"] = self._make(
                np.concatenate([self._tone(300, 0.12, 0.3, "square", 0.3),
                                self._tone(240, 0.12, 0.3, "square", 0.3),
                                self._tone(160, 0.3, 0.3, "square")]))
        except Exception:
            self.ok = False

    def play(self, name, vol=1.0):
        if not self.ok:
            return
        s = self.sounds.get(name)
        if s:
            try:
                s.set_volume(vol)
                s.play()
            except Exception:
                pass
