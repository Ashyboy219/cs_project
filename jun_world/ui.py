"""On-screen UI: typewriter dialogue, branching choice menu, HUD and effects."""
import math
import pygame

from . import settings as S


def wrap_text(font, text, max_w):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if font.size(trial)[0] <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rounded_panel(surf, rect, fill, border, radius=10, border_w=2, alpha=235):
    panel = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*fill, alpha), (0, 0, rect.w, rect.h), border_radius=radius)
    pygame.draw.rect(panel, (*border, 255), (0, 0, rect.w, rect.h), border_w, border_radius=radius)
    surf.blit(panel, rect.topleft)


class DialogueBox:
    """Plays a list of lines. Each line: dict(name, text, color, portrait)."""

    def __init__(self, fonts, audio):
        self.f = fonts
        self.audio = audio
        self.active = False
        self.lines = []
        self.idx = 0
        self.reveal = 0.0
        self.on_done = None
        self.speed = 38.0  # chars per second
        self._wrapped = []
        self._t = 0.0

    def start(self, lines, on_done=None):
        self.lines = lines
        self.idx = 0
        self.reveal = 0.0
        self.active = True
        self.on_done = on_done
        self._t = 0.0
        self._rewrap()

    def _rewrap(self):
        line = self.lines[self.idx]
        self._wrapped = wrap_text(self.f.body, line["text"], S.SCREEN_W - 240)

    @property
    def _full_len(self):
        return sum(len(w) + 1 for w in self._wrapped)

    def advance(self):
        if not self.active:
            return
        if self.reveal < self._full_len:
            self.reveal = self._full_len  # reveal all instantly
            return
        self.idx += 1
        if self.idx >= len(self.lines):
            self.active = False
            cb, self.on_done = self.on_done, None
            if cb:
                cb()
        else:
            self.reveal = 0.0
            self._rewrap()

    def update(self, dt):
        if not self.active:
            return
        prev = int(self.reveal)
        self.reveal = min(self._full_len, self.reveal + self.speed * dt)
        if int(self.reveal) != prev and int(self.reveal) % 2 == 0:
            self.audio.play("talk", 0.5)

    def draw(self, surf):
        if not self.active:
            return
        line = self.lines[self.idx]
        col = line.get("color", S.WHITE)
        box = pygame.Rect(24, S.SCREEN_H - 168, S.SCREEN_W - 48, 144)
        rounded_panel(surf, box, S.INK, col, radius=12, border_w=3, alpha=242)

        # portrait
        port = line.get("portrait")
        px = box.x + 16
        if port:
            pr = pygame.Rect(px, box.y + 16, 96, 112)
            pygame.draw.rect(surf, S.NEAR_BLACK, pr, border_radius=8)
            pygame.draw.rect(surf, col, pr, 2, border_radius=8)
            surf.blit(port, (pr.centerx - port.get_width() // 2,
                             pr.bottom - port.get_height() - 6))
            text_x = pr.right + 18
        else:
            text_x = px + 6

        # name plate
        name = line.get("name", "")
        if name:
            ns = self.f.name.render(name, True, col)
            np_rect = pygame.Rect(text_x - 6, box.y - 18, ns.get_width() + 20, 28)
            rounded_panel(surf, np_rect, S.NEAR_BLACK, col, radius=8, border_w=2, alpha=242)
            surf.blit(ns, (text_x + 4, box.y - 14))

        # typewriter body
        shown = int(self.reveal)
        y = box.y + 22
        used = 0
        for w in self._wrapped:
            seg = w
            if used + len(w) + 1 > shown:
                take = max(0, shown - used)
                seg = w[:take]
            ts = self.f.body.render(seg, True, S.BONE)
            surf.blit(ts, (text_x, y))
            y += 28
            used += len(w) + 1
            if used >= shown:
                break

        if self.reveal >= self._full_len:
            blink = (pygame.time.get_ticks() // 400) % 2 == 0
            if blink:
                tip = "Z / Enter"
                ts = self.f.tiny.render(tip + "  >", True, col)
                surf.blit(ts, (box.right - ts.get_width() - 16, box.bottom - 22))


class ChoiceBox:
    """A small menu of branching options with moral colour cues."""

    def __init__(self, fonts, audio):
        self.f = fonts
        self.audio = audio
        self.active = False
        self.prompt = ""
        self.options = []   # list of dict(label, tag, cb, sub)
        self.sel = 0
        self.on_pick = None

    def start(self, prompt, options):
        self.prompt = prompt
        self.options = options
        self.sel = 0
        self.active = True

    def move(self, d):
        if not self.active:
            return
        self.sel = (self.sel + d) % len(self.options)
        self.audio.play("ui_move", 0.6)

    def confirm(self):
        if not self.active:
            return
        self.active = False
        self.audio.play("ui_ok", 0.7)
        opt = self.options[self.sel]
        if opt.get("cb"):
            opt["cb"]()

    def draw(self, surf):
        if not self.active:
            return
        tag_col = {S.MERCY: S.PATH_TINT[S.MERCY], S.SURVIVAL: S.PATH_TINT[S.SURVIVAL],
                   S.CRUELTY: S.PATH_TINT[S.CRUELTY], None: S.BONE}
        w = S.SCREEN_W - 120
        h = 56 + len(self.options) * 40
        box = pygame.Rect((S.SCREEN_W - w) // 2, S.SCREEN_H - h - 28, w, h)
        rounded_panel(surf, box, S.NEAR_BLACK, S.GOLD, radius=12, border_w=3, alpha=246)

        ps = self.f.small.render(self.prompt, True, S.GREY)
        surf.blit(ps, (box.x + 18, box.y + 12))

        for i, opt in enumerate(self.options):
            oy = box.y + 42 + i * 40
            selected = i == self.sel
            col = tag_col.get(opt.get("tag"))
            if selected:
                hl = pygame.Rect(box.x + 12, oy - 6, box.w - 24, 36)
                pygame.draw.rect(surf, (*col, 60), hl, border_radius=8)
                pygame.draw.rect(surf, col, hl, 2, border_radius=8)
                pygame.draw.polygon(surf, col,
                                    [(box.x + 22, oy + 12), (box.x + 32, oy + 6), (box.x + 32, oy + 18)])
            label = opt["label"]
            ls = self.f.body.render(label, True, S.WHITE if selected else S.GREY)
            surf.blit(ls, (box.x + 44, oy))
            tag = opt.get("tag")
            if tag:
                tname = {S.MERCY: "mercy", S.SURVIVAL: "survival", S.CRUELTY: "cruelty"}[tag]
                ts = self.f.tiny.render(tname, True, col)
                surf.blit(ts, (box.right - ts.get_width() - 18, oy + 4))


class Toast:
    """Fading top-of-screen notifications (path shifts, items, etc.)."""

    def __init__(self, fonts):
        self.f = fonts
        self.items = []  # list of [text, color, ttl, age]

    def push(self, text, color=S.BONE, ttl=2.6):
        self.items.append([text, color, ttl, 0.0])

    def update(self, dt):
        for it in self.items:
            it[3] += dt
        self.items = [it for it in self.items if it[3] < it[2]]

    def draw(self, surf):
        y = 14
        for text, color, ttl, age in self.items:
            a = 255
            if age < 0.2:
                a = int(255 * age / 0.2)
            elif age > ttl - 0.6:
                a = int(255 * (ttl - age) / 0.6)
            a = max(0, min(255, a))
            ts = self.f.small.render(text, True, color)
            bg = pygame.Surface((ts.get_width() + 24, 28), pygame.SRCALPHA)
            pygame.draw.rect(bg, (*S.NEAR_BLACK, int(a * 0.8)), (0, 0, bg.get_width(), 28), border_radius=8)
            pygame.draw.rect(bg, (*color, a), (0, 0, bg.get_width(), 28), 1, border_radius=8)
            ts.set_alpha(a)
            x = S.SCREEN_W // 2 - bg.get_width() // 2
            surf.blit(bg, (x, y))
            surf.blit(ts, (x + 12, y + 4))
            y += 34


def draw_objective(surf, fonts, text):
    if not text:
        return
    label = fonts.tiny.render("OBJECTIVE", True, S.GOLD)
    ts = fonts.small.render(text, True, S.BONE)
    w = max(label.get_width(), ts.get_width()) + 28
    box = pygame.Rect(14, 14, w, 50)
    rounded_panel(surf, box, S.NEAR_BLACK, S.SLATE, radius=8, border_w=2, alpha=200)
    surf.blit(label, (box.x + 14, box.y + 6))
    surf.blit(ts, (box.x + 14, box.y + 24))


def draw_detection(surf, fonts, value, alerted):
    if value <= 1 and not alerted:
        return
    w = 220
    box = pygame.Rect(S.SCREEN_W - w - 16, 16, w, 24)
    rounded_panel(surf, box, S.NEAR_BLACK, S.SLATE, radius=6, border_w=2, alpha=210)
    frac = max(0.0, min(1.0, value / 100.0))
    col = S.ALARM if alerted else (S.WARN if frac > 0.45 else S.EERIE)
    pygame.draw.rect(surf, col, (box.x + 4, box.y + 4, int((box.w - 8) * frac), box.h - 8), border_radius=4)
    label = "SPOTTED!" if alerted else "alert"
    ls = fonts.tiny.render(label, True, col)
    surf.blit(ls, (box.x + 6, box.y + 5))


def draw_moral(surf, fonts, moral):
    """Small three-bar readout of the player's leaning, bottom-right."""
    order = [(S.MERCY, "MERCY"), (S.SURVIVAL, "SURVIVAL"), (S.CRUELTY, "CRUELTY")]
    total = sum(moral.values()) or 1
    x = S.SCREEN_W - 156
    y = S.SCREEN_H - 64
    for i, (key, name) in enumerate(order):
        col = S.PATH_TINT[key]
        ls = fonts.tiny.render(name, True, col)
        surf.blit(ls, (x, y + i * 16))
        bar = pygame.Rect(x + 78, y + i * 16 + 2, 64, 8)
        pygame.draw.rect(surf, S.INK, bar, border_radius=3)
        frac = moral[key] / total
        pygame.draw.rect(surf, col, (bar.x, bar.y, int(bar.w * frac), bar.h), border_radius=3)


def vignette(size):
    """Pre-rendered soft dark vignette overlay."""
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w / 2, h / 2
    maxd = math.hypot(cx, cy)
    step = 8
    for ry in range(0, h, step):
        for rx in range(0, w, step):
            d = math.hypot(rx - cx, ry - cy) / maxd
            a = int(max(0, (d - 0.55)) * 230)
            if a > 0:
                pygame.draw.rect(surf, (0, 0, 0, a), (rx, ry, step, step))
    return surf
