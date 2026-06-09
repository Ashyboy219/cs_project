"""jun-world - Act One: The Ruined Gate.  Core game loop and Act One script."""
import math
import os
import random
import pygame

from . import settings as S
from . import assets
from . import ui
from .world import TileMap
from .entities import Player, NPC, Guard, Supply, Pebble
from .scenes import all_scenes
from .save import SaveManager

# human-readable location labels for the save menu
LOCATIONS = {"fall": "The Broken Road", "village": "Ruined Village",
             "depot": "Guard Depot", "escape": "The East Road"}


class _Barrier:
    """A static collision rect (e.g. the escape gate) the player can't pass."""
    def __init__(self, rect):
        self.rect = rect

# speaker name -> (actor sprite key, accent colour)
SPEAKERS = {
    "You":        ("player", S.PLAYER_BODY),
    "Rook":       ("rook", S.ROOK_BODY),
    "Mr. Ankam":   ("ankam", S.ANKAM_BODY),
    "Villager":   ("villager0", S.GREY),
    "Nervous Villager": ("villager2", (150, 160, 150)),
    "???":        (None, S.EERIE),
    "The Note":   (None, S.EERIE),
}


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(S.TITLE)
        self.screen = pygame.display.set_mode((S.SCREEN_W, S.SCREEN_H))
        self.clock = pygame.time.Clock()
        self.fonts = assets.Fonts()
        self.audio = assets.Audio()
        self.actors = assets.build_all_actors()
        self.ankam_hat = assets.hat_overlay()
        self.vignette = ui.vignette((S.SCREEN_W, S.SCREEN_H))
        self.portraits = self._build_portraits()

        self.dialogue = ui.DialogueBox(self.fonts, self.audio)
        self.choice = ui.ChoiceBox(self.fonts, self.audio)
        self.toast = ui.Toast(self.fonts)

        self.scene_data = all_scenes()
        self.running = True
        self.mode = "title"

        # persistent run state
        self.moral = {S.MERCY: 0, S.SURVIVAL: 0, S.CRUELTY: 0}
        self.flags = set()
        self.quest = "intro"
        self.objective = ""
        self.collected = 0
        self.depot_taken = [False, False, False]
        self.respawn = ("fall", 12 * S.TILE + 16, 9 * S.TILE + 26)

        # live scene objects
        self.scene = None
        self.tmap = None
        self.player = None
        self.npcs = []
        self.guards = []
        self.supplies = []
        self.checkpoints = []
        self.signs = []
        self.cam = (0, 0)
        self.tint = S.EERIE

        # stealth
        self.detection = 0.0
        self.alerted = False
        self.alert_timer = 0.0
        self.noise_pings = []
        self.noise_cd = 0.0

        # cutscene / scripting
        self.cutscene = False
        self.movers = []
        self.fade = 0.0           # 0..1 black overlay
        self.fade_dir = 0
        self.fade_then = None

        # title / narration
        self.cards = []
        self.card_i = 0
        self.card_t = 0.0
        self.fall_t = 0.0
        self.motes = self._make_motes()
        self.t = 0.0
        self.interact_target = None
        self.sneaking = False

        # survival / health
        self.act = 1
        self.hp = S.PLAYER_MAX_HP
        self.max_hp = S.PLAYER_MAX_HP
        self.invuln = 0.0
        self.shake = 0.0
        self.hit_flash = 0.0
        self.playtime = 0.0
        self.dead = False

        # weapon (the Sling)
        self.pebbles = []
        self.ammo = S.PEBBLE_MAX
        self.fire_cd = 0.0

        # escape / pursuit-boss state
        self.extra_blockers = []
        self.captain = None
        self.caged = None
        self.gate_barrier = None
        self.gate_open = True
        self.exit_x = 0

        # menus + saves
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.saves = SaveManager(base)
        self.menu = None          # dict(title, items, sel, on_cancel, note)
        self.start_title()        # build the title menu

    # ------------------------------------------------------------------ setup
    def _build_portraits(self):
        out = {}
        for name, (key, col) in SPEAKERS.items():
            surf = pygame.Surface((84, 108), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*col, 40), (0, 0, 84, 108), border_radius=6)
            if key:
                spr = self.actors[key][("down", 0)]
                big = pygame.transform.scale(spr, (assets.CELL_W * 3, assets.CELL_H * 3))
                surf.blit(big, (84 // 2 - big.get_width() // 2, 108 - big.get_height() + 6))
            else:
                # mysterious silhouette for ??? / The Note
                pygame.draw.circle(surf, col, (42, 44), 16)
                pygame.draw.line(surf, col, (42, 30), (42, 78), 4)
                pygame.draw.ellipse(surf, col, (32, 70, 20, 14))
            out[name] = surf
        return out

    def _make_motes(self):
        m = []
        for _ in range(46):
            m.append([random.uniform(0, S.SCREEN_W), random.uniform(0, S.SCREEN_H),
                      random.uniform(-6, 6), random.uniform(-14, -4),
                      random.uniform(0.4, 1.0)])
        return m

    def L(self, name, text):
        key, col = SPEAKERS.get(name, ("player", S.WHITE))
        return dict(name=name, text=text, color=col, portrait=self.portraits.get(name))

    # ---------------------------------------------------------------- scenes
    def load_scene(self, name, spawn):
        data = self.scene_data[name]
        self.scene = name
        self.tmap = TileMap(data["tiles"], data.get("buildings"), data.get("decos"))
        self.tmap.render()
        self.tint = data.get("tint", S.EERIE)

        sx, sy = data["spawns"][spawn]
        px = sx * S.TILE + S.TILE // 2
        py = sy * S.TILE + S.TILE - 6
        if self.player is None:
            self.player = Player(self.actors["player"], px, py)
        else:
            self.player.x, self.player.y = px, py
            self.player.moving = False

        self.checkpoints = []
        self.signs = [(d[1] * S.TILE + S.TILE // 2, d[2] * S.TILE + S.TILE - 6)
                      for d in data.get("decos", []) if d[0] == "sign"]
        self.npcs = []
        self.guards = []
        self.supplies = []
        self.detection = 0.0
        self.alerted = False
        self.alert_timer = 0.0
        self.noise_pings = []
        self.pebbles = []
        self.ammo = S.PEBBLE_MAX          # a fresh handful of pebbles each zone
        self.fire_cd = 0.0
        if self.player is not None:
            self.player.stamina = S.STAMINA_MAX
            self.player.dash_t = 0.0
            self.player.dash_cd = 0.0
            self.player.trail = []
        # escape state resets to a benign default for every scene
        self.extra_blockers = []
        self.captain = None
        self.caged = None
        self.gate_barrier = None
        self.gate_open = True
        self.exit_x = 0

        if name == "village":
            self._populate_village()
        elif name == "depot":
            self._populate_depot(data)
        elif name == "escape":
            self._populate_escape(data)

        self._update_camera(snap=True)

    def _tile_feet(self, tx, ty):
        return (tx * S.TILE + S.TILE // 2, ty * S.TILE + S.TILE - 6)

    def _populate_village(self):
        # ambient villagers
        spots = [(7, 13), (24, 14), (12, 15), (29, 16), (6, 17)]
        for i, (tx, ty) in enumerate(spots):
            n = NPC(self.actors["villager%d" % (i % 5)], *self._tile_feet(tx, ty),
                    name="Villager", wander=True)
            n.lines = self._villager_lines(i)
            n.line_i = 0
            n.kind = "villager"
            self.npcs.append(n)
        # nervous villager (optional moral beat)
        nv = NPC(self.actors["villager2"], *self._tile_feet(27, 15), name="Nervous Villager")
        nv.kind = "nervous"
        nv.line_i = 0
        self.npcs.append(nv)
        # Rook
        if "met_rook" in self.flags:
            rook = NPC(self.actors["rook"], *self._tile_feet(16, 11), name="Rook")
        else:
            rook = NPC(self.actors["rook"], *self._tile_feet(23, 11), name="Rook")
        rook.kind = "rook"
        self.rook = rook
        self.npcs.append(rook)

    def _populate_depot(self, data):
        for i, (tx, ty, kind) in enumerate(data["supplies"]):
            s = Supply(*self._tile_feet(tx, ty), kind=kind)
            s.taken = self.depot_taken[i]
            self.supplies.append(s)
        for gdef in data["guards"]:
            wpts = [self._tile_feet(x, y) for (x, y) in gdef["path"]]
            gx, gy = self._tile_feet(gdef["x"], gdef["y"])
            self.guards.append(Guard(self.actors["guard"], gx, gy, wpts, "Guard"))

    def _populate_escape(self, data):
        self.gate_open = False
        self.exit_x = data["exit_x"] * S.TILE
        gc = data["gate"]["col"]
        r0, r1 = data["gate"]["rows"]
        rect = pygame.Rect(gc * S.TILE, r0 * S.TILE, S.TILE, (r1 - r0 + 1) * S.TILE)
        self.gate_barrier = _Barrier(rect)
        self.extra_blockers = [self.gate_barrier]
        # the Captain: an un-killable elite pursuer
        cx, cy = self._tile_feet(*data["captain"])
        cap = Guard(self.actors["guard"], cx, cy, [(cx, cy)], "Captain")
        cap.captain = True
        cap.chase_speed = 2.34
        cap.mode = "chase"
        cap.target = (cx, cy)
        self.captain = cap
        self.guards.append(cap)
        for gdef in data["guards"]:
            wpts = [self._tile_feet(x, y) for (x, y) in gdef["path"]]
            gx, gy = self._tile_feet(gdef["x"], gdef["y"])
            self.guards.append(Guard(self.actors["guard"], gx, gy, wpts, "Guard"))
        vx, vy = self._tile_feet(*data["caged"])
        cv = NPC(self.actors["villager1"], vx, vy, "Caged Villager")
        cv.kind = "caged"
        self.caged = cv
        self.npcs.append(cv)

    def _villager_lines(self, i):
        pool = [
            ["They took the grain cart at first light. Said it was a 'tax.'",
             "We do not say his name out loud. You learn that fast here."],
            ["My boy is sick. The medicine went up the road to the castle.",
             "If you are kind, stranger... be kind quietly."],
            ["You fell out of the sky? The old folk say the sky used to be a door.",
             "Doors let things in. That is why he sealed it, they say."],
            ["Mr. Ankam stamps a paper and a family disappears. That is law now.",
             "He shakes when he does it. Did you know that? He shakes."],
            ["Careful past the depot. The guards there don't warn you twice.",
             "Last fellow who got caught? We don't see him in the bread line anymore."],
        ]
        return pool[i % len(pool)]

    # ------------------------------------------------------------------- run
    def run(self):
        self.start_title()
        while self.running:
            dt = min(0.05, self.clock.tick(S.FPS) / 1000.0)
            self.t += dt
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    self.on_key(e.key)
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    self.on_click(e.pos)
            self.update(dt)
            self.draw()
            pygame.display.flip()
        pygame.quit()

    # --------------------------------------------------------------- input
    def on_key(self, key):
        confirm = key in (pygame.K_z, pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)

        # menus capture all input
        if self.menu is not None:
            self._menu_key(key, confirm)
            return

        if key == pygame.K_ESCAPE:
            if (self.mode == "play" and not self.cutscene and not self.dialogue.active
                    and not self.choice.active and self.fade_dir == 0):
                self._open_pause()
            return

        if self.mode == "title":
            return          # title is driven by its menu
        if self.mode in ("opening", "ending"):
            if confirm:
                self.next_card()
            return
        if self.mode != "play":
            return

        # in-play overlays take priority
        if self.choice.active:
            if key in (pygame.K_UP, pygame.K_w):
                self.choice.move(-1)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.choice.move(1)
            elif confirm:
                self.choice.confirm()
            return
        if self.dialogue.active:
            if confirm:
                self.dialogue.advance()
            return
        if self.cutscene:
            return
        # world actions
        if key in (pygame.K_z, pygame.K_RETURN, pygame.K_e):
            self.try_interact()
        elif key == pygame.K_SPACE:
            self._try_dash()
        elif key in (pygame.K_f, pygame.K_j):
            self._fire(None)

    # --------------------------------------------------------------- update
    def update(self, dt):
        self.toast.update(dt)
        self._update_motes(dt)
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt * 36)
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt * 2.4)
        if self.menu is not None:
            return                      # menus freeze the world
        if self.mode == "title":
            return
        if self.mode == "opening":
            self.card_t += dt
            return
        if self.mode == "ending":
            self.card_t += dt
            return
        if self.mode == "falling":
            self.fall_t += dt
            if self.fall_t > 1.3:
                self.mode = "play"
                self.audio.play("hurt", 0.5)
                self.toast.push("You hit the dirt hard. The sky above you is already healing shut.",
                                S.EERIE, 3.6)
                self._autosave()
            return

        # ---- play ----
        self.dialogue.update(dt)
        self._update_fade(dt)
        for s in self.supplies:
            s.update(dt)
        for n in self.npcs:
            n.update(dt, self.tmap)
        self._update_movers(dt)
        self._update_pebbles(dt)
        for p in self.noise_pings:
            p[2] += dt
        self.noise_pings = [p for p in self.noise_pings if p[2] < 0.8]
        if self.noise_cd > 0:
            self.noise_cd -= dt

        if self.invuln > 0:
            self.invuln = max(0.0, self.invuln - dt)
        controllable = (not self.cutscene and not self.dialogue.active
                        and not self.choice.active and self.fade_dir == 0)
        if controllable:
            self.playtime += dt
            self._handle_movement(dt)
            self._check_transitions()
        # guards & stealth always tick during depot (even mid-dialogue rare)
        if self.scene == "depot":
            for g in self.guards:
                g.update(dt, self.tmap)
            if controllable:
                self._check_supply_pickup()
                self._update_stealth(dt)
        elif self.scene == "escape":
            if controllable:
                for g in self.guards:
                    g.update(dt, self.tmap)
                self._update_escape(dt)
        self._update_camera()
        self._update_interact_target()

    def _handle_movement(self, dt):
        self.player.tick(dt)
        blockers = [n for n in self.npcs] + [g for g in self.guards] + self.extra_blockers
        if self.player.dashing:
            self.player.dash_step(self.tmap, blockers)
            self.player.update_anim(dt)
            return
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        sneaking = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.sneaking = sneaking
        old_speed = self.player.speed
        self.player.speed = S.PLAYER_SPEED * (0.55 if sneaking else 1.0)
        self.player.move(dx, dy, self.tmap, blockers)
        self.player.update_anim(dt)
        self.player.speed = old_speed
        if self.player.moving and int(self.t * 8) % 2 == 0:
            self.audio.play("step", 0.22)

    def _try_dash(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        if self.player.start_dash(dx, dy):
            self.audio.play("ui_move", 0.5)

    def _fire(self, target):
        if self.player is None or self.scene is None or self.dead:
            return
        if "has_sling" not in self.flags or self.fire_cd > 0:
            return
        if self.ammo <= 0:
            self.audio.play("ui_move", 0.3)
            self.toast.push("Out of pebbles. They refill when you reach somewhere new.",
                            S.GREY, 1.6)
            return
        if target is None:
            vx, vy = {"left": (-1, 0), "right": (1, 0),
                      "up": (0, -1), "down": (0, 1)}[self.player.dir]
        else:
            dx, dy = target[0] - self.player.x, target[1] - self.player.y
            m = math.hypot(dx, dy) or 1
            vx, vy = dx / m, dy / m
            self.player.dir = ("right" if abs(vx) > abs(vy) and vx > 0 else
                               "left" if abs(vx) > abs(vy) else
                               "down" if vy > 0 else "up")
        self.pebbles.append(Pebble(self.player.x, self.player.y,
                                   vx * S.PEBBLE_SPEED, vy * S.PEBBLE_SPEED))
        self.ammo -= 1
        self.fire_cd = S.FIRE_COOLDOWN
        self.audio.play("ui_ok", 0.35)

    def on_click(self, pos):
        if self.menu is not None or self.mode != "play":
            return
        if self.cutscene or self.dialogue.active or self.choice.active:
            return
        world = (pos[0] + self.cam[0], pos[1] + self.cam[1])
        self._fire(world)

    def _update_pebbles(self, dt):
        if self.fire_cd > 0:
            self.fire_cd -= dt
        for p in self.pebbles:
            p.update(dt, self.tmap)
            if p.dead:
                continue
            for g in self.guards:
                if g.mode == "stunned":
                    continue
                if math.hypot(g.x - p.x, g.y - p.y) < 17:
                    g.mode = "stunned"
                    g.stun_t = S.GUARD_STUN_TIME
                    p.dead = True
                    self.shake = max(self.shake, 4.0)
                    self.audio.play("hurt", 0.45)
                    self.toast.push("Stunned a guard. Slip past while it reels.", S.EERIE, 1.4)
                    break
        for p in self.pebbles:
            if p.dead and p.hit_wall:
                self.noise_pings.append([p.x, p.y, 0.0])
                if not self.alerted:
                    best, bestd = None, 240
                    for g in self.guards:
                        if g.mode in ("chase", "stunned"):
                            continue
                        d = math.hypot(g.x - p.x, g.y - p.y)
                        if d < bestd:
                            bestd, best = d, g
                    if best:
                        best.mode = "investigate"
                        best.target = (p.x, p.y)
        self.pebbles = [p for p in self.pebbles if not p.dead]

    # --------------------------------------------------------------- camera
    def _update_camera(self, snap=False):
        if not self.player:
            return
        tx = self.player.x - S.SCREEN_W / 2
        ty = self.player.y - S.SCREEN_H / 2
        tx = max(0, min(max(0, self.tmap.pixw - S.SCREEN_W), tx))
        ty = max(0, min(max(0, self.tmap.pixh - S.SCREEN_H), ty))
        if snap:
            self.cam = (tx, ty)
        else:
            cx = self.cam[0] + (tx - self.cam[0]) * 0.16
            cy = self.cam[1] + (ty - self.cam[1]) * 0.16
            self.cam = (cx, cy)

    # ----------------------------------------------------------- transitions
    def _check_transitions(self):
        pr = self.player.rect
        for tr in self.scene_data[self.scene].get("transitions", []):
            rect = pygame.Rect(tr["x"] * S.TILE, tr["y"] * S.TILE,
                               tr["w"] * S.TILE, tr["h"] * S.TILE)
            if pr.colliderect(rect):
                if tr.get("needs_brief") and "mission_briefed" not in self.flags:
                    self.toast.push("Not yet. Rook is waiting for you.", S.ROOK_BODY)
                    self.player.x -= 6  # nudge back
                    return
                self._do_transition(tr["to"], tr["spawn"])
                return

    def _do_transition(self, to, spawn):
        prev = self.scene

        def after():
            self.load_scene(to, spawn)
            self._on_enter_scene(prev, to)
        self.start_fade(after)

    def _on_enter_scene(self, prev, to):
        if to == "village" and self.quest == "intro":
            self.quest = "meet"
            self._begin_meet_rook()
        elif to == "village" and self.collected >= 3 and self.quest in ("briefed", "stealing"):
            self.quest = "returning"
            self._begin_return()
        elif to == "depot":
            if self.quest in ("briefed",):
                self.quest = "stealing"
            if self.collected >= 3:
                self.objective = "Got it all. Slip back out the south gate."
            else:
                self.objective = "Recover %d more supplies. Stay out of sightlines." % (
                    3 - self.collected)
            self.toast.push("Shift sneak   ·   Space dash   ·   F / click = Sling (stun)",
                            S.BONE, 4.4)
        elif to == "village" and self.quest == "stealing" and self.collected < 3:
            self.objective = "Go back for the rest. Rook is waiting."
        elif to == "village" and self.quest == "briefed":
            self.objective = "Find the guard depot. Take the east gate."
        elif to == "fall":
            self.objective = "Head east. The road leads to the village."
        elif to == "escape":
            self.quest = "escape"
            self.objective = "RUN east. Reach the far gate. Open the road. Don't let the Captain reach you."
            self.toast.push("You can't kill the Captain. Outrun him — dash through the gaps.",
                            S.ALARM, 4.2)
        self._autosave()

    def tint_path(self):
        dom = self.dominant()
        return S.PATH_TINT.get(dom, S.EERIE)

    # ----------------------------------------------------------- interaction
    def _update_interact_target(self):
        self.interact_target = None
        if self.cutscene or self.dialogue.active or self.choice.active:
            return
        best = None
        bestd = S.INTERACT_RANGE
        cands = []
        for n in self.npcs:
            cands.append(("npc", n, n.x, n.y))
        for (sx, sy) in self.signs:
            cands.append(("sign", (sx, sy), sx, sy))
        for kind, obj, ox, oy in cands:
            d = math.hypot(ox - self.player.x, oy - self.player.y)
            if d < bestd:
                bestd = d
                best = (kind, obj, ox, oy)
        self.interact_target = best

    def try_interact(self):
        if not self.interact_target:
            return
        kind, obj, ox, oy = self.interact_target
        if kind == "sign":
            self.say([self.L("???", "A faded notice, half scorched: 'ALL JOY BY PERMIT ONLY. "
                             "BY ORDER OF LORD SUFFLOK.' Someone scratched 'liar' beneath it.")])
        elif kind == "npc":
            self._talk_npc(obj)

    def _talk_npc(self, npc):
        npc.face_to(self.player.x, self.player.y)
        if npc.kind == "rook":
            if self.quest in ("meet",) and "met_rook" not in self.flags:
                self._begin_meet_rook()
            elif self.quest == "briefed":
                self.say([self.L("Rook", "Quit stalling. East gate. Get the food and medicine "
                                  "back before someone starves waiting on your nerves.")])
            else:
                self.say([self.L("Rook", "You came from the wrong side of the sky. "
                                  "But you're still standing. That's something.")])
        elif npc.kind == "nervous":
            self._talk_nervous(npc)
        elif npc.kind == "caged":
            self._talk_caged(npc)
        else:
            lines = getattr(npc, "lines", [["..."]])
            block = lines[npc.line_i % len(lines)]
            npc.line_i += 1
            self.say([self.L("Villager", t) for t in block])

    def _talk_nervous(self, npc):
        if "nervous_done" in self.flags:
            self.say([self.L("Nervous Villager", "Please... whatever you do, do it quiet. "
                             "They are always listening.")])
            return
        self.say(
            [self.L("Nervous Villager", "You're new. I saw where the guards hid the medicine "
                    "before they hauled it off. I could tell you. But if they trace it to me..."),
             self.L("Nervous Villager", "...what kind of person are you going to be here?")],
            then=self._nervous_choice)

    def _nervous_choice(self):
        def mercy():
            self.flags.add("nervous_done")
            self.add_moral(S.MERCY)
            self.flags.add("hint_medicine")
            self.say([self.L("You", "Your name stays out of it. I promise. Thank you."),
                      self.L("Nervous Villager", "...East stash. Behind the right-hand crates. "
                             "Go gentle. And thank you for not making me afraid of you too.")])

        def survival():
            self.flags.add("nervous_done")
            self.add_moral(S.SURVIVAL)
            self.flags.add("hint_medicine")
            self.say([self.L("You", "Tell me, and no one ever knows we talked. Clean trade."),
                      self.L("Nervous Villager", "...Right-hand crates, east side. You're practical. "
                             "Out here, practical keeps people breathing. Mostly.")])

        def cruelty():
            self.flags.add("nervous_done")
            self.add_moral(S.CRUELTY)
            self.say([self.L("You", "You'll tell me. You don't want to be a problem."),
                      self.L("Nervous Villager", "...Okay! Okay. East crates. Please don't look at me "
                             "like that. You looked at me like he does.")])
        self.choose("How do you get the location out of them?", [
            dict(label="\"Your name stays out of it. I promise.\"", tag=S.MERCY, cb=mercy),
            dict(label="\"No one will ever know we talked.\"", tag=S.SURVIVAL, cb=survival),
            dict(label="\"You'll tell me. Don't be a problem.\"", tag=S.CRUELTY, cb=cruelty),
        ])

    # ------------------------------------------------------------- stealth
    def make_noise(self):
        if self.scene != "depot" or self.alerted or self.noise_cd > 0:
            return
        self.noise_cd = 1.4
        self.audio.play("ui_move", 0.5)
        nx, ny = self.player.x, self.player.y
        self.noise_pings.append([nx, ny, 0.0])
        best = None
        bestd = 260
        for g in self.guards:
            if g.mode in ("chase",):
                continue
            d = math.hypot(g.x - nx, g.y - ny)
            if d < bestd:
                bestd = d
                best = g
        if best:
            best.mode = "investigate"
            best.target = (nx, ny)

    def _update_stealth(self, dt):
        in_bush = self.tmap.in_bush(self.player.x, self.player.y)
        best = 0.0
        seer = None
        for g in self.guards:
            if g.mode == "stunned":
                continue
            f = g.sees(self.player.x, self.player.y, self.tmap, in_bush)
            if f > best:
                best = f
                seer = g
        sneak_mult = 0.62 if getattr(self, "sneaking", False) else 1.0
        if best > 0:
            self.detection += S.DETECT_RATE * best * sneak_mult * dt
            if seer and seer.mode == "patrol":
                seer.mode = "look"
                seer.look_t = 0.5
        else:
            self.detection -= S.DETECT_DECAY * dt
        self.detection = max(0.0, min(100.0, self.detection))

        if self.detection >= 100 and not self.alerted:
            self._raise_alarm()

        if self.alerted:
            still_seen = best > 0
            if still_seen:
                self.alert_timer = 3.0
            else:
                self.alert_timer -= dt
            for g in self.guards:
                if g.mode != "stunned":
                    g.mode = "chase"
                    g.target = (self.player.x, self.player.y)
                if math.hypot(g.x - self.player.x, g.y - self.player.y) < 18:
                    self._hit_player(S.GUARD_TOUCH_DAMAGE, g.x, g.y)
                    if self.dead:
                        return
            if self.alert_timer <= 0:
                self.alerted = False
                self.detection = 25
                for g in self.guards:
                    g.mode = "patrol"
                self.toast.push("You slipped their sight. Keep moving.", S.EERIE)

    def _raise_alarm(self):
        self.alerted = True
        self.alert_timer = 3.0
        self.audio.play("alert", 0.8)
        self.toast.push("SPOTTED! Break their line of sight!", S.ALARM, 2.4)
        for g in self.guards:
            g.mode = "chase"
            g.target = (self.player.x, self.player.y)

    # ----------------------------------------------------- combat / death
    def _hit_player(self, dmg, fromx, fromy):
        if self.invuln > 0 or self.dead or (self.player and self.player.dashing):
            return
        self.hp -= dmg
        self.invuln = S.INVULN_TIME
        self.shake = 9.0
        self.hit_flash = 1.0
        self.audio.play("hurt", 0.8)
        self._knockback(fromx, fromy, S.KNOCKBACK)
        if self.hp <= 0:
            self.hp = 0
            self._game_over()

    def _knockback(self, fromx, fromy, dist):
        dx, dy = self.player.x - fromx, self.player.y - fromy
        m = math.hypot(dx, dy) or 1
        ux, uy = dx / m * 4, dy / m * 4
        for _ in range(int(dist // 4)):
            r = pygame.Rect(int(self.player.x + ux - self.player.w / 2),
                            int(self.player.y + uy - self.player.h),
                            self.player.w, self.player.h)
            if self.tmap.rect_blocked(r):
                break
            self.player.x += ux
            self.player.y += uy

    def _game_over(self):
        self.dead = True
        self.audio.play("caught", 0.9)
        self.shake = 14.0
        self.alerted = False
        for g in self.guards:
            g.mode = "patrol"
        latest = self.saves.latest()
        items = []
        if latest:
            items.append(("Reload last save", lambda: self._do_load(latest)))
        items.append(("Load a save...", self._open_load))
        items.append(("Quit to title", self._to_title))
        self.menu = dict(title="YOU WERE CAUGHT", items=items, sel=0, on_cancel=None,
                         note="Out here, a mistake costs more than a song. Reload and try again.",
                         danger=True)

    # ----------------------------------------------------- saves / menus
    def _autosave(self):
        if self.cutscene or self.dialogue.active or self.choice.active or self.dead:
            return
        if self.player is None or self.scene is None:
            return
        self.saves.save("auto", self.build_save_state())

    def build_save_state(self):
        return dict(
            version=1, act=self.act, scene=self.scene,
            location=LOCATIONS.get(self.scene, self.scene),
            px=self.player.x, py=self.player.y, dir=self.player.dir,
            moral=dict(self.moral), flags=sorted(self.flags),
            quest=self.quest, objective=self.objective,
            collected=self.collected, depot_taken=list(self.depot_taken),
            hp=self.hp, max_hp=self.max_hp, playtime=self.playtime)

    def apply_save_state(self, s):
        self.act = s.get("act", 1)
        self.moral = {S.MERCY: 0, S.SURVIVAL: 0, S.CRUELTY: 0}
        self.moral.update({k: int(v) for k, v in s.get("moral", {}).items()
                           if k in self.moral})
        self.flags = set(s.get("flags", []))
        self.quest = s.get("quest", "intro")
        self.objective = s.get("objective", "")
        self.collected = s.get("collected", 0)
        self.depot_taken = list(s.get("depot_taken", [False, False, False]))
        self.hp = s.get("hp", self.max_hp)
        self.max_hp = s.get("max_hp", S.PLAYER_MAX_HP)
        self.playtime = s.get("playtime", 0.0)
        self.cutscene = False
        self.dialogue.active = False
        self.choice.active = False
        self.movers = []
        self.dead = False
        self.menu = None
        self.detection = 0.0
        self.alerted = False
        self.invuln = 0.0
        self.fade = 0.0
        self.fade_dir = 0
        scene = s.get("scene", "fall")
        spawn0 = list(self.scene_data[scene]["spawns"].keys())[0]
        self.load_scene(scene, spawn0)
        self.player.x = s.get("px", self.player.x)
        self.player.y = s.get("py", self.player.y)
        self.player.dir = s.get("dir", "down")
        self.mode = "play"
        self._update_camera(snap=True)

    def _do_save(self, slot):
        ok = self.saves.save(slot, self.build_save_state())
        self.menu = None
        self.audio.play("ui_ok", 0.7)
        self.toast.push("Saved to slot %s." % slot if ok else "Save failed.",
                        S.EERIE if ok else S.ALARM)

    def _do_load(self, slot):
        state = self.saves.load(slot)
        if not state:
            self.audio.play("hurt", 0.6)
            return
        self.apply_save_state(state)
        self.audio.play("ui_ok", 0.7)
        self.toast.push("Loaded.", S.EERIE)

    def _to_title(self):
        self.menu = None
        self.dead = False
        self.start_title()

    # ----- menu construction -----
    def _open_pause(self):
        items = [
            ("Resume", self._close_menu),
            ("Save game", self._open_save),
            ("Load game", self._open_load),
            ("Quit to title", self._to_title),
        ]
        self.menu = dict(title="PAUSED", items=items, sel=0, on_cancel=self._close_menu,
                         note="Esc to resume", danger=False)

    def _open_save(self):
        rows = self.saves.list()
        items = []
        for slot in ("1", "2", "3"):
            label = "Slot %s   %s" % (slot, SaveManager.describe(rows.get(slot)))
            items.append((label, (lambda sl=slot: self._do_save(sl))))
        self.menu = dict(title="SAVE GAME", items=items, sel=0, on_cancel=self._open_pause,
                         note="Choose a slot to overwrite", danger=False)

    def _open_load(self):
        rows = self.saves.list()
        items = []
        for slot in SaveManager.SLOTS:
            st = rows.get(slot)
            name = "Auto" if slot == "auto" else ("Slot %s" % slot)
            label = "%s   %s" % (name, SaveManager.describe(st))
            if st:
                items.append((label, (lambda sl=slot: self._do_load(sl))))
            else:
                items.append((label, None))
        back = self._to_title if (self.dead or self.mode == "title") else self._open_pause
        self.menu = dict(title="LOAD GAME", items=items, sel=0, on_cancel=back,
                         note="", danger=False)

    def _close_menu(self):
        self.menu = None

    def _menu_key(self, key, confirm):
        m = self.menu
        if key in (pygame.K_UP, pygame.K_w):
            m["sel"] = (m["sel"] - 1) % len(m["items"])
            self.audio.play("ui_move", 0.5)
        elif key in (pygame.K_DOWN, pygame.K_s):
            m["sel"] = (m["sel"] + 1) % len(m["items"])
            self.audio.play("ui_move", 0.5)
        elif key == pygame.K_ESCAPE:
            if m.get("on_cancel"):
                self.audio.play("ui_move", 0.5)
                m["on_cancel"]()
        elif confirm:
            label, cb = m["items"][m["sel"]]
            if cb:
                self.audio.play("ui_ok", 0.7)
                cb()
            else:
                self.audio.play("hurt", 0.4)

    # --------------------------------------------------- supply pickup check
    def _check_supply_pickup(self):
        for i, s in enumerate(self.supplies):
            if s.taken:
                continue
            if math.hypot(s.x - self.player.x, s.y - self.player.y) < 26:
                s.taken = True
                self.depot_taken[i] = True
                self.collected += 1
                self.audio.play("pickup", 0.8)
                label = "medicine" if s.kind == "medicine" else "food"
                self.toast.push("Recovered %s.  (%d/3)" % (label, self.collected),
                                S.WARN if s.kind == "food" else S.EERIE)
                if self.collected >= 3:
                    self.objective = "Got it all. Slip back out the south gate."
                    self.toast.push("That's everything. Get out clean.", S.ROOK_BODY, 3.0)

    # ------------------------------------------------- escape / pursuit boss
    def _update_escape(self, dt):
        cap = self.captain
        if cap:
            cap.mode = "chase"
            cap.target = (self.player.x, self.player.y)
        for g in self.guards:
            if g is cap or g.mode == "stunned":
                continue
            d = math.hypot(g.x - self.player.x, g.y - self.player.y)
            if d < 150 and not self.tmap.line_blocked(g.x, g.y, self.player.x, self.player.y):
                g.mode = "chase"
                g.target = (self.player.x, self.player.y)
            elif g.mode == "chase" and d > 260:
                g.mode = "patrol"
        for g in self.guards:
            if g.mode == "stunned":
                continue
            if math.hypot(g.x - self.player.x, g.y - self.player.y) < 18:
                self._hit_player(S.GUARD_TOUCH_DAMAGE, g.x, g.y)
                if self.dead:
                    return
        if "escape_done" not in self.flags and self.player.x > self.exit_x:
            self.flags.add("escape_done")
            self._finish_act_one()

    def _finish_act_one(self):
        self.flags.add("act_one_done")
        self.quest = "done"
        self.cutscene = True
        self.toast.push("Through the gate. It crashes down behind you.", S.EERIE, 3.0)
        self.audio.play("save", 0.6)
        self.start_fade(self.start_ending)

    def _talk_caged(self, npc):
        npc.face_to(self.player.x, self.player.y)
        self.choose("A villager is locked in a haul-cage by the gate. The Captain is closing.", [
            dict(label="Free them — costs precious seconds, but they'll help.",
                 tag=S.MERCY, cb=self._caged_free),
            dict(label="No time. Shove the barrel onto the plank yourself.",
                 tag=S.SURVIVAL, cb=self._caged_barrel),
            dict(label="Tip the cage at the guards. Let them have the easy catch.",
                 tag=S.CRUELTY, cb=self._caged_cruel),
        ])

    def _open_escape_gate(self):
        self.gate_open = True
        if self.gate_barrier in self.extra_blockers:
            self.extra_blockers.remove(self.gate_barrier)
        self.audio.play("ui_ok", 0.5)

    def _remove_caged(self):
        if self.caged in self.npcs:
            self.npcs.remove(self.caged)
        self.caged = None

    def _caged_free(self):
        self.add_moral(S.MERCY, 2)
        self.flags.add("escape_mercy")
        self._open_escape_gate()
        self.hp = self.max_hp
        self.invuln = max(self.invuln, 1.2)
        self._remove_caged()
        self.say([
            self.L("Caged Villager", "You came back for— here, take this, it's all the salve I've "
                   "got. GO. The side bars are loose — I'll slow them. GO!"),
            self.L("???", "(A full heart again, right when you'll need every one. A stranger spent "
                   "their last kindness on you.)"),
        ])

    def _caged_barrel(self):
        self.add_moral(S.SURVIVAL, 1)
        self.flags.add("escape_survival")
        self._open_escape_gate()
        self._remove_caged()
        self.say([self.L("You", "(One shove. The plank groans down, the gate lifts. No time for "
                         "anything — or anyone — else.)")])

    def _caged_cruel(self):
        self.add_moral(S.CRUELTY, 2)
        self.flags.add("escape_cruel")
        self._open_escape_gate()
        self._remove_caged()
        if self.captain:
            self.captain.chase_speed = (self.captain.chase_speed or 2.34) + 0.5
        self.say([
            self.L("You", "(You kick the cage toward the guards. They lunge for the easy prize. "
                   "The road clears.)"),
            self.L("???", "(You don't let yourself hear the sound behind you. But the Captain "
                   "hears it — and something in him recognizes you. He runs faster now.)"),
        ])

    # ------------------------------------------------------------- movers
    def move_actor(self, actor, tile, speed=1.6, then=None):
        tx, ty = self._tile_feet(*tile)
        self.movers.append(dict(a=actor, tx=tx, ty=ty, sp=speed, then=then, done=False))

    def _update_movers(self, dt):
        for m in self.movers:
            a = m["a"]
            dx, dy = m["tx"] - a.x, m["ty"] - a.y
            dist = math.hypot(dx, dy)
            if dist < 2.5:
                a.moving = False
                a.update_anim(dt)
                if not m["done"]:
                    m["done"] = True
                    if m["then"]:
                        m["then"]()
                continue
            step = m["sp"]
            a.x += dx / dist * step
            a.y += dy / dist * step
            a.dir = ("right" if abs(dx) > abs(dy) and dx > 0 else
                     "left" if abs(dx) > abs(dy) else
                     "down" if dy > 0 else "up")
            a.moving = True
            a.update_anim(dt)
        self.movers = [m for m in self.movers if not m["done"]]

    # --------------------------------------------------------- cutscene API
    def say(self, lines, then=None):
        self.dialogue.start(lines, on_done=then)

    def choose(self, prompt, options):
        self.choice.start(prompt, options)

    def add_moral(self, tag, n=1):
        self.moral[tag] += n
        names = {S.MERCY: "mercy", S.SURVIVAL: "survival", S.CRUELTY: "cruelty"}
        self.toast.push("Your path leans toward %s." % names[tag], S.PATH_TINT[tag], 2.2)

    def dominant(self):
        if not any(self.moral.values()):
            return None
        return max(self.moral, key=lambda k: self.moral[k])

    # ----------------------------------------------------------- fade
    def start_fade(self, then):
        self.fade = 0.0
        self.fade_dir = 1
        self.fade_then = then

    def _update_fade(self, dt):
        if self.fade_dir == 1:
            self.fade += dt * 2.6
            if self.fade >= 1:
                self.fade = 1
                self.fade_dir = -1
                if self.fade_then:
                    cb, self.fade_then = self.fade_then, None
                    cb()
        elif self.fade_dir == -1:
            self.fade -= dt * 2.6
            if self.fade <= 0:
                self.fade = 0
                self.fade_dir = 0

    # ===================================================================
    #  ACT ONE SCRIPT
    # ===================================================================
    def start_title(self):
        self.mode = "title"
        self.dead = False
        self.cutscene = False
        items = [("New game", self._new_game)]
        if self.saves.has_any():
            latest = self.saves.latest()
            items.append(("Continue", (lambda sl=latest: self._do_load(sl))))
        items.append(("Load game", self._open_load))
        items.append(("Quit", self._quit))
        self.menu = dict(title="", items=items, sel=0, on_cancel=None, is_title=True,
                         note="WASD/Arrows move  ·  Z/Enter interact  ·  Shift sneak  ·  "
                              "Space dash  ·  F / click Sling  ·  Esc pause", danger=False)

    def _new_game(self):
        self._reset_run()
        self.hp = self.max_hp = S.PLAYER_MAX_HP
        self.act = 1
        self.playtime = 0.0
        self.invuln = 0.0
        self.menu = None
        self.start_opening()

    def _quit(self):
        self.running = False

    def start_opening(self):
        self.menu = None
        self.mode = "opening"
        self.card_i = 0
        self.card_t = 0.0
        self.audio.play("portal", 0.8)
        self.cards = [
            ("A sound like a torn song opens above the broken road.", S.EERIE),
            ("You fall through light, and dust, and something that feels "
             "like a forgotten memory.", S.BONE),
            ("When you wake, the world is cracked. The sky is the wrong colour. "
             "A little glowing note hums beside you.", S.EERIE),
            ("You did not choose to come here.  Something chose for you.", S.SUFFLOK_RED),
            ("Far off, a black castle watches the road like it owns the morning.", S.GOLD),
        ]

    def start_ending(self):
        self.mode = "ending"
        self.card_i = 0
        self.card_t = 0.0
        dom = self.dominant()
        close = {
            S.MERCY: ("You were scared, and you helped anyway. The village will "
                      "remember the shape of that. So will the note.", S.PATH_TINT[S.MERCY]),
            S.SURVIVAL: ("You moved smart and quiet, and people are still breathing "
                         "because of it. The note keeps your time, exactly.", S.PATH_TINT[S.SURVIVAL]),
            S.CRUELTY: ("You got results. People obeyed. And a few of them looked at "
                        "you the way they look at HIM. The note hums colder now.", S.PATH_TINT[S.CRUELTY]),
            None: ("You are still afraid. But you are still here. That is its "
                   "own small mercy.", S.EERIE),
        }
        if "escape_mercy" in self.flags:
            esc = ("You carried a stranger's mercy out of that village — and a full heart. "
                   "You will need both.", S.PATH_TINT[S.MERCY])
        elif "escape_cruel" in self.flags:
            esc = ("You bought your way out with someone else's body. The east road is quiet "
                   "now. It will not stay quiet.", S.PATH_TINT[S.CRUELTY])
        elif "escape_survival" in self.flags:
            esc = ("You ran clean and fast and left the gate shut behind you. Alive is alive, "
                   "out here.", S.PATH_TINT[S.SURVIVAL])
        else:
            esc = ("Somehow you made the far gate with the Captain's breath on your neck. "
                   "It crashed down an inch behind you.", S.EERIE)
        self.cards = [
            esc,
            ("Patrols double. Rook's name is on a list now. And the Captain has seen your face.",
             S.ALARM),
            close.get(dom, close[None]),
            ("Somewhere above the castle, the torn-song sound flickers again — "
             "as if the portal is listening for you.", S.EERIE),
            ("Why did it open?  Why you?  And why is a tyrant so afraid "
             "of an outsider who only wanted to go home?", S.BONE),
            ("END OF ACT ONE", S.GOLD),
            ("The Ruined Gate", S.GREY),
        ]

    def next_card(self):
        self.card_i += 1
        self.card_t = 0.0
        if self.mode == "opening" and self.card_i >= len(self.cards):
            self.mode = "falling"
            self.fall_t = 0.0
            self.load_scene("fall", "start")
            self.objective = "Head east. The road leads somewhere."
            self.quest = "intro"
        elif self.mode == "ending" and self.card_i >= len(self.cards):
            self._reset_run()
            self.start_title()

    def _reset_run(self):
        self.moral = {S.MERCY: 0, S.SURVIVAL: 0, S.CRUELTY: 0}
        self.flags = set()
        self.quest = "intro"
        self.collected = 0
        self.depot_taken = [False, False, False]
        self.player = None
        self.hp = self.max_hp = S.PLAYER_MAX_HP
        self.dead = False
        self.detection = 0.0
        self.alerted = False

    # ---- meeting Rook -------------------------------------------------
    def _begin_meet_rook(self):
        self.cutscene = True
        self.quest = "meet"
        rook = self.rook
        # Rook rushes over and pulls you into cover
        self.move_actor(rook, (6, 11), speed=2.4, then=self._meet_rook_talk)

    def _meet_rook_talk(self):
        self.rook.face_to(self.player.x, self.player.y)
        self.player.dir = "right"
        self.say([
            self.L("Rook", "Down! Get DOWN. You walked the open road like you wanted "
                   "an audience with him."),
            self.L("Rook", "You came from the wrong side of the sky. If you're one of "
                   "Sufflok's tricks, you picked a bad face for it — you look terrified."),
            self.L("Rook", "Good. Scared people run fast. I'm Rook. This was my village "
                   "before his collectors decided we owed them everything."),
            self.L("Rook", "They hauled off our food. Our medicine. There's a sick kid two "
                   "doors down who can't wait for a brave speech. Will you help me take it back?"),
        ], then=self._meet_rook_choice)

    def _meet_rook_choice(self):
        def mercy():
            self.add_moral(S.MERCY)
            self.say([self.L("You", "Those people need that medicine. I'm scared... but "
                             "yes. Let's get it back."),
                      self.L("Rook", "Scared and still in. I can work with that. Maybe you're "
                             "not from one of his nightmares after all.")],
                     then=self._mission_brief)

        def survival():
            self.add_moral(S.SURVIVAL)
            self.say([self.L("You", "If helping you gets me closer to a way home, I'm in. "
                             "Tell me how we do this without dying."),
                      self.L("Rook", "Ha. A planner. Fine. I need someone who thinks before "
                             "they bleed. Stick close.")],
                     then=self._mission_brief)

        def cruelty():
            self.add_moral(S.CRUELTY)
            self.say([self.L("You", "Fine. Let's go scare some guards off their own loot."),
                      self.L("Rook", "...Heh. Bold. Just — don't enjoy it too much. I've seen "
                             "where enjoying it leads. It wears a crown.")],
                     then=self._mission_brief)
        self.choose("How do you answer Rook?", [
            dict(label="\"Those people need it. I'll help.\"", tag=S.MERCY, cb=mercy),
            dict(label="\"If it gets me home, I'm in.\"", tag=S.SURVIVAL, cb=survival),
            dict(label="\"Let's scare those guards off.\"", tag=S.CRUELTY, cb=cruelty),
        ])

    def _mission_brief(self):
        self.say([
            self.L("Rook", "The depot's through the east gate. Low-level guards — mean, not "
                   "clever. They patrol in little loops. Watch their eyes — those cones of "
                   "sight. Step into one and they WILL come, and you've only so much blood to give."),
            self.L("Rook", "Here. My old sling and a fistful of pebbles. Aim with the mouse, or "
                   "tap F to throw the way you're facing. A pebble to the back of the skull drops "
                   "a guard cold for a few seconds — doesn't kill, just buys a gap. Miss, and the "
                   "CLACK pulls them toward the noise instead. Either way it's a tool, not a body count."),
            self.L("Rook", "And if it goes bad — SPACE to dash. Quick roll, you'll shrug off a hit "
                   "mid-dodge, but it burns your wind, so don't lean on it. Get the three crates "
                   "and slip out. Quiet keeps people alive out here."),
        ], then=self._mission_briefed)

    def _mission_briefed(self):
        self.flags.add("met_rook")
        self.flags.add("mission_briefed")
        self.flags.add("has_sling")
        self.quest = "briefed"
        self.objective = "Find the guard depot. Take the EAST gate."
        self.cutscene = False
        self.move_actor(self.rook, (16, 11), speed=1.4)
        self._autosave()

    # ---- returning the supplies + Mr. Ankam ----------------------------
    def _begin_return(self):
        self.cutscene = True
        self.objective = "Return the supplies to Rook."
        self.player.dir = "left"
        rook = self.rook
        # bring Rook in close from the plaza so the reunion reads quickly
        rook.x, rook.y = self._tile_feet(26, 11)
        rook.face_to(self.player.x, self.player.y)
        self.move_actor(rook, (self.player.x / S.TILE - 1.0, self.player.y / S.TILE),
                        speed=2.6, then=self._return_talk)

    def _return_talk(self):
        self.rook.x = self.player.x + 26
        self.rook.y = self.player.y
        self.rook.face_to(self.player.x, self.player.y)
        rep = self._return_rook_line()
        self.say([
            self.L("Rook", "You actually did it. Three crates. The kid eats tonight."),
            self.L("Rook", rep),
            self.L("Villager", "Bless you, stranger. We won't forget who carried it back."),
        ], then=self._ankam_entrance)

    def _return_rook_line(self):
        dom = self.dominant()
        return {
            S.MERCY: "You were scared the whole time. I watched it. And you still chose them. "
                     "That... that matters more than brave.",
            S.SURVIVAL: "Clean. Quiet. Smart. You think fast under pressure — I need that. "
                        "Stick with me and we both might survive this.",
            S.CRUELTY: "You got results. Can't argue with results. But something about how you "
                       "got them sat wrong in my gut. Watch yourself.",
            None: "You came back in one piece, and so did the medicine. Good enough. Good enough.",
        }.get(dom, "Good work.")

    def _ankam_entrance(self):
        # Mr. Ankam marches in from the east gate with guards
        gx, gy = self._tile_feet(31, 11)
        ankam = NPC(self.actors["ankam"], gx, gy, name="Mr. Ankam")
        ankam.kind = "ankam"
        ankam.overlay = self.ankam_hat
        self.ankam = ankam
        self.npcs.append(ankam)
        g1 = NPC(self.actors["guard"], *self._tile_feet(32, 10), name="Guard")
        g2 = NPC(self.actors["guard"], *self._tile_feet(32, 12), name="Guard")
        g1.kind = g2.kind = "guard"
        self.npcs.extend([g1, g2])
        self.move_actor(g1, (self.player.x / S.TILE + 2.4, self.player.y / S.TILE - 0.6), 2.0)
        self.move_actor(g2, (self.player.x / S.TILE + 2.4, self.player.y / S.TILE + 0.6), 2.0)
        self.move_actor(ankam, (self.player.x / S.TILE + 3.2, self.player.y / S.TILE),
                        speed=1.8, then=self._ankam_talk)
        self.audio.play("alert", 0.5)

    def _ankam_talk(self):
        self.ankam.face_to(self.player.x, self.player.y)
        self.say([
            self.L("Mr. Ankam", "NOBODY MOVE. By order of the magnificent, merciful, extremely "
                   "not-disappointed Lord Sufflok, this village is under corrective silence!"),
            self.L("Mr. Ankam", "Patrols are doubled. Rations are revoked. And the rebel called "
                   "Rook is to be captured, boxed, labelled, and delivered — before anyone asks "
                   "why this happened on MY watch."),
            self.L("Mr. Ankam", "And YOU. You're not on any list. You're not in any file. You came "
                   "through the — the SKY thing. Do you know how much paperwork a sky thing is?"),
            self.L("Mr. Ankam", "S-stay back. I have guards. I have a HAT. I have the full and "
                   "trembling authority of the castle, and I will absolutely use one of those things."),
        ], then=self._ankam_choice)

    def _ankam_choice(self):
        self.choose("Mr. Ankam is shaking. What do you do?", [
            dict(label="\"Why are you so afraid?\"", tag=S.MERCY, cb=self._ankam_mercy),
            dict(label="\"Sufflok will blame YOU for this.\"", tag=S.SURVIVAL, cb=self._ankam_survival),
            dict(label="\"Leave. Now. Or I make you.\"", tag=S.CRUELTY, cb=self._ankam_cruel),
        ])

    def _ankam_mercy(self):
        self.add_moral(S.MERCY, 2)
        self.flags.add("ankam_mercy")
        self.say([
            self.L("You", "You're shaking, Mr. Ankam. Look at your hands. Who taught you to be "
                   "this afraid?"),
            self.L("Mr. Ankam", "I— that's— you don't get to— ...He counts mistakes. He keeps a "
                   "LEDGER. A theft on my road is a mark by my name, and marks by your name is how "
                   "people stop having names."),
            self.L("Mr. Ankam", "Don't look at me like that. Like I'm a person. It's very "
                   "unprofessional of you. ...Take your rebel and your medicine and GO, before I "
                   "remember I'm supposed to be terrifying."),
            self.L("???", "(He marched in to crush you. He's leaving you a head start. "
                   "Mercy noticed his fear — and the fear answered.)"),
        ], then=self._act_end)

    def _ankam_survival(self):
        self.add_moral(S.SURVIVAL, 2)
        self.flags.add("ankam_survival")
        self.say([
            self.L("You", "Think it through. You report a theft AND an outsider AND a rebel you "
                   "didn't catch? Sufflok won't punish me. I'm not in his ledger. You are."),
            self.L("Mr. Ankam", "...That's— no. That's— ...that's actually a very good point and I "
                   "hate it enormously."),
            self.L("Mr. Ankam", "So here is what didn't happen today. There was no theft. There was "
                   "no sky thing. There was certainly no me, failing to capture anyone. We are "
                   "AGREED on the things that didn't happen?"),
            self.L("???", "(You didn't beat him. You made the truth more expensive than the lie. "
                   "Out here, that is a kind of winning.)"),
        ], then=self._act_end)

    def _ankam_cruel(self):
        self.add_moral(S.CRUELTY, 2)
        self.flags.add("ankam_cruel")
        self.say([
            self.L("You", "Here's the offer. Leave. Now. Or I show this whole village exactly how "
                   "much your guards are worth when I stop being polite."),
            self.L("Mr. Ankam", "Y-you can't just— the HAT means— ...guards. Guards? Why are you "
                   "stepping BACK, that's MY direction to step—"),
            self.L("Mr. Ankam", "Fine! FINE. We're going. Note that I'm leaving by CHOICE, as a "
                   "tactical— stop looking at me like he looks at me. STOP IT."),
            self.L("???", "(They scattered. It worked. It worked fast. And Rook is staring at you "
                   "now the way you'd stare at something that might bite.)"),
        ], then=self._act_end_cruel)

    def _act_end_cruel(self):
        self.say([
            self.L("Rook", "...Remind me to never be on the wrong end of that. You scared a man "
                   "with a hat and an army into the dirt."),
            self.L("Rook", "Just — that's how HE started. Sufflok. Scaring people because it's "
                   "faster than asking. Don't get a taste for it. Please."),
        ], then=self._act_end)

    def _act_end(self):
        # Ankam is resolved — now the raid hits. The escape (pursuit boss) begins.
        self.flags.add("ankam_resolved")
        self.say([
            self.L("???", "A horn tears across the rooftops — one long note, then two short, "
                   "then long. Then more horns answer it, from the castle road."),
            self.L("Rook", "That's the garrison call. He's not sending a patrol — he's sending the "
                   "whole fist. We can't hold this. EAST ROAD, now, RUN — I'm right behind you. GO!"),
        ], then=self._goto_escape)

    def _goto_escape(self):
        self.cutscene = False
        self._do_transition("escape", "start")

    # ===================================================================
    #  RENDER
    # ===================================================================
    def draw(self):
        if self.mode == "title":
            self._draw_title()
        elif self.mode in ("opening", "ending"):
            self._draw_cards()
        elif self.mode == "falling":
            self._draw_falling()
        else:
            self._draw_world()
        # red hit flash
        if self.hit_flash > 0 and self.menu is None and self.mode == "play":
            fl = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
            fl.fill((200, 40, 40, int(70 * self.hit_flash)))
            self.screen.blit(fl, (0, 0))
        # fade overlay
        if self.fade > 0:
            ov = pygame.Surface((S.SCREEN_W, S.SCREEN_H))
            ov.fill(S.BLACK)
            ov.set_alpha(int(self.fade * 255))
            self.screen.blit(ov, (0, 0))
        # menu overlay (pause / save / load / game over / title)
        if self.menu is not None:
            self._draw_menu()

    def _draw_world(self):
        ox = oy = 0.0
        if self.shake > 0:
            ox = random.uniform(-self.shake, self.shake)
            oy = random.uniform(-self.shake, self.shake)
        camx = max(0, min(max(0, self.tmap.pixw - S.SCREEN_W), self.cam[0] + ox))
        camy = max(0, min(max(0, self.tmap.pixh - S.SCREEN_H), self.cam[1] + oy))
        cam = (int(camx), int(camy))
        self.screen.fill(S.BLACK)
        # background sub-region
        view = pygame.Rect(cam[0], cam[1], S.SCREEN_W, S.SCREEN_H)
        self.screen.blit(self.tmap.bg, (0, 0), view)

        # escape gate, drawn as a barred wall while shut
        if self.scene == "escape" and not self.gate_open and self.gate_barrier:
            r = self.gate_barrier.rect.move(-cam[0], -cam[1])
            pygame.draw.rect(self.screen, S.WOOD_DK, r)
            for bx in range(r.x + 4, r.right - 2, 8):
                pygame.draw.line(self.screen, S.WOOD, (bx, r.y + 2), (bx, r.bottom - 2), 3)
            pygame.draw.rect(self.screen, S.INK, r, 2)
            lk = self.fonts.tiny.render("locked", True, S.WARN)
            self.screen.blit(lk, (r.centerx - lk.get_width() // 2, r.y - 14))

        # vision cones (under sprites)
        if self.scene == "depot":
            for g in self.guards:
                col = S.ALARM if (self.alerted or g.mode == "chase") else (
                    S.WARN if g.mode in ("look", "investigate") else S.EERIE)
                g.draw_cone(self.screen, cam, self.tmap, col)
            for p in self.noise_pings:
                r = int(p[2] * 50)
                a = max(0, int(160 * (1 - p[2] / 0.8)))
                pygame.draw.circle(self.screen, (*S.WARN, a),
                                   (int(p[0] - cam[0]), int(p[1] - cam[1])), r, 2)

        # y-sorted actors + supplies
        draw_list = []
        for s in self.supplies:
            if not s.taken:
                draw_list.append((s.y, lambda s=s: s.draw(self.screen, cam)))
        for n in self.npcs:
            draw_list.append((n.y, lambda n=n: n.draw(self.screen, cam)))
        for g in self.guards:
            draw_list.append((g.y, lambda g=g: self._draw_guard(g, cam)))
        draw_list.append((self.player.y, lambda: self._draw_player(cam)))
        draw_list.sort(key=lambda t: t[0])
        for _, fn in draw_list:
            fn()

        # pebbles fly above the actors
        for p in self.pebbles:
            p.draw(self.screen, cam)

        # interact prompt
        self._draw_interact_prompt(cam)

        # ambient motes + vignette
        self._draw_motes()
        self.screen.blit(self.vignette, (0, 0))

        # HUD
        ui.draw_objective(self.screen, self.fonts, self.objective)
        self._draw_hearts()
        self._draw_combat_hud()
        if self.scene == "depot":
            ui.draw_detection(self.screen, self.fonts, self.detection, self.alerted)
        if self.collected and self.scene == "depot":
            cs = self.fonts.small.render("Supplies %d/3" % self.collected, True, S.WARN)
            self.screen.blit(cs, (18, 134))
        ui.draw_moral(self.screen, self.fonts, self.moral)

        # overlays
        self.dialogue.draw(self.screen)
        self.choice.draw(self.screen)
        self.toast.draw(self.screen)

    def _draw_combat_hud(self):
        if "has_sling" not in self.flags or self.player is None:
            return
        x, y = 18, 96
        # stamina (dash) bar
        bar = pygame.Rect(x, y, 118, 7)
        pygame.draw.rect(self.screen, S.INK, bar, border_radius=3)
        frac = self.player.stamina / S.STAMINA_MAX
        col = S.STAMINA_COL if self.player.can_dash() else S.STAMINA_LOW
        pygame.draw.rect(self.screen, col, (x, y, int(118 * frac), 7), border_radius=3)
        self.screen.blit(self.fonts.tiny.render("DASH", True, S.GREY), (x + 124, y - 3))
        # pebbles (Sling ammo)
        py = y + 14
        for i in range(S.PEBBLE_MAX):
            cx = x + i * 13
            full = i < self.ammo
            pygame.draw.circle(self.screen, S.PEBBLE_COL if full else S.INK, (cx + 4, py + 4), 3)
            if full:
                pygame.draw.circle(self.screen, S.WOOD_DK, (cx + 4, py + 4), 3, 1)
        self.screen.blit(self.fonts.tiny.render("SLING", True, S.GREY),
                         (x + S.PEBBLE_MAX * 13 + 8, py - 1))

    # ---- HUD / player / menu drawing ----------------------------------
    def _draw_player(self, cam):
        # dash after-images
        for i, (tx, ty) in enumerate(self.player.trail):
            ghost = self.player.frames[(self.player.dir, 0)].copy()
            ghost.set_alpha(28 + i * 16)
            self.screen.blit(ghost, (int(tx - assets.CELL_W / 2 - cam[0]),
                                     int(ty - assets.FOOT_Y - cam[1])))
        # blink during invulnerability (but not during the dash itself)
        if self.invuln > 0 and not self.player.dashing and int(self.t * 22) % 2 == 0:
            sh = pygame.Surface((22, 9), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 90), (0, 0, 22, 9))
            self.screen.blit(sh, (int(self.player.x - 11 - cam[0]),
                                  int(self.player.y - 5 - cam[1])))
            return
        self.player.draw(self.screen, cam)

    def _draw_hearts(self):
        x0, y = 18, 72
        for i in range(self.max_hp):
            cx = x0 + i * 22
            full = i < self.hp
            col = S.HEART if full else S.HEART_DK
            pygame.draw.circle(self.screen, col, (cx + 4, y + 4), 4)
            pygame.draw.circle(self.screen, col, (cx + 11, y + 4), 4)
            pygame.draw.polygon(self.screen, col,
                                [(cx + 1, y + 6), (cx + 14, y + 6), (cx + 7, y + 15)])
            if full:
                pygame.draw.circle(self.screen, (255, 200, 200), (cx + 4, y + 3), 1)

    def _draw_menu(self):
        m = self.menu
        items = m["items"]
        n = len(items)

        if m.get("is_title"):
            # compact list low on the title art (no heavy panel over the logo)
            cx = S.SCREEN_W // 2
            y0 = 388
            for i, (label, cb) in enumerate(items):
                sel = i == m["sel"]
                if sel:
                    ls = self.fonts.mid.render("> %s <" % label, True, S.EERIE)
                else:
                    ls = self.fonts.body.render(label, True, S.GREY)
                self.screen.blit(ls, (cx - ls.get_width() // 2, y0 + i * 28))
            if m.get("note"):
                ns = self.fonts.tiny.render(m["note"], True, S.SLATE)
                self.screen.blit(ns, (cx - ns.get_width() // 2, S.SCREEN_H - 22))
            return

        dim = pygame.Surface((S.SCREEN_W, S.SCREEN_H), pygame.SRCALPHA)
        if m.get("danger"):
            dim.fill((50, 6, 10, 170))
        else:
            dim.fill((0, 0, 0, 165))
        self.screen.blit(dim, (0, 0))

        pw = 620
        ph = 70 + n * 44 + (34 if m.get("note") else 0)
        px = (S.SCREEN_W - pw) // 2
        py = (S.SCREEN_H - ph) // 2
        border = S.ALARM if m.get("danger") else S.GOLD
        ui.rounded_panel(self.screen, pygame.Rect(px, py, pw, ph), S.NEAR_BLACK, border,
                         radius=14, border_w=3, alpha=242)
        yy = py + 18
        if m.get("title"):
            ts = self.fonts.big.render(m["title"], True, border)
            self.screen.blit(ts, (S.SCREEN_W // 2 - ts.get_width() // 2, yy))
            yy += 46
        for i, (label, cb) in enumerate(items):
            sel = i == m["sel"]
            disabled = cb is None
            row = pygame.Rect(px + 16, yy - 4, pw - 32, 38)
            if sel:
                pygame.draw.rect(self.screen, (*border, 55), row, border_radius=8)
                pygame.draw.rect(self.screen, border, row, 2, border_radius=8)
                pygame.draw.polygon(self.screen, border,
                                    [(px + 26, yy + 14), (px + 36, yy + 8), (px + 36, yy + 20)])
            col = S.SLATE if disabled else (S.WHITE if sel else S.GREY)
            ls = self.fonts.body.render(label, True, col)
            self.screen.blit(ls, (px + 48, yy))
            yy += 44
        if m.get("note"):
            ns = self.fonts.tiny.render(m["note"], True, S.GREY)
            self.screen.blit(ns, (S.SCREEN_W // 2 - ns.get_width() // 2, yy + 4))

    def _draw_guard(self, g, cam):
        g.draw(self.screen, cam)
        if getattr(g, "captain", False):
            cx = int(g.x - cam[0])
            cy = int(g.y - 46 - cam[1])
            pygame.draw.polygon(self.screen, S.SUFFLOK_RED,
                                [(cx, cy - 7), (cx - 4, cy + 2), (cx + 4, cy + 2)])
            pygame.draw.circle(self.screen, S.GOLD, (cx, cy + 1), 2)
        # alert mark
        if g.mode == "chase" or self.alerted:
            mark = self.fonts.mid.render("!", True, S.ALARM)
            self.screen.blit(mark, (int(g.x - cam[0] - 3), int(g.y - 56 - cam[1])))
        elif g.mode in ("look", "investigate"):
            mark = self.fonts.mid.render("?", True, S.WARN)
            self.screen.blit(mark, (int(g.x - cam[0] - 4), int(g.y - 54 - cam[1])))

    def _draw_interact_prompt(self, cam):
        if not self.interact_target:
            return
        kind, obj, ox, oy = self.interact_target
        bob = math.sin(self.t * 5) * 2
        x = int(ox - cam[0])
        y = int(oy - 56 - cam[1] + bob)
        if kind == "checkpoint":
            y += 14
        pygame.draw.circle(self.screen, S.NEAR_BLACK, (x, y), 11)
        pygame.draw.circle(self.screen, S.GOLD, (x, y), 11, 2)
        zs = self.fonts.tiny.render("Z", True, S.GOLD)
        self.screen.blit(zs, (x - zs.get_width() // 2, y - zs.get_height() // 2))

    # ---- title / cards / falling --------------------------------------
    def _draw_title(self):
        self.screen.fill(S.BLACK)
        # soft portal swirl
        cx, cy = S.SCREEN_W // 2, 180
        for i in range(70):
            a = self.t * 0.8 + i * 0.4
            rad = 20 + i * 1.6
            x = cx + math.cos(a) * rad
            y = cy + math.sin(a) * rad * 0.55
            col = S.EERIE if i % 2 == 0 else S.EERIE_DK
            r = max(1, 4 - i // 24)
            s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*col, 150), (r + 1, r + 1), r)
            self.screen.blit(s, (x - r, y - r))
        self._draw_motes()
        title = self.fonts.huge.render("JUN-WORLD", True, S.BONE)
        self.screen.blit(title, (cx - title.get_width() // 2, 250))
        sub = self.fonts.mid.render("Act One  -  The Ruined Gate", True, S.GOLD)
        self.screen.blit(sub, (cx - sub.get_width() // 2, 318))
        tag = self.fonts.small.render(
            "A scared, kind stranger.  A stolen world.  A choice in how you survive it.",
            True, S.GREY)
        self.screen.blit(tag, (cx - tag.get_width() // 2, 356))
        self.screen.blit(self.vignette, (0, 0))

    def _draw_cards(self):
        self.screen.fill(S.BLACK)
        # drifting portal light behind the words
        cx, cy = S.SCREEN_W // 2, S.SCREEN_H // 2
        for i in range(40):
            a = self.t * 0.6 + i * 0.5
            rad = 30 + i * 4
            x = cx + math.cos(a) * rad
            y = cy + math.sin(a) * rad * 0.4
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*S.EERIE_DK, 60), (3, 3), 2)
            self.screen.blit(s, (x, y))
        if self.card_i < len(self.cards):
            text, col = self.cards[self.card_i]
            # fade in/out
            a = min(1.0, self.card_t / 0.8)
            lines = ui.wrap_text(self.fonts.mid, text, S.SCREEN_W - 200)
            big = (text.isupper() and len(text) < 24)
            font = self.fonts.big if big else self.fonts.mid
            lines = ui.wrap_text(font, text, S.SCREEN_W - 200)
            total_h = len(lines) * (font.get_height() + 6)
            y = cy - total_h // 2
            for ln in lines:
                ts = font.render(ln, True, col)
                ts.set_alpha(int(a * 255))
                self.screen.blit(ts, (cx - ts.get_width() // 2, y))
                y += font.get_height() + 6
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            p = self.fonts.tiny.render("Z  >", True, S.GREY)
            self.screen.blit(p, (S.SCREEN_W - 70, S.SCREEN_H - 40))
        self.screen.blit(self.vignette, (0, 0))

    def _draw_falling(self):
        self.screen.fill(S.BLACK)
        # bright portal at top, player streaking down
        cx = S.SCREEN_W // 2
        prog = min(1.0, self.fall_t / 1.3)
        py = int(-40 + prog * (S.SCREEN_H * 0.6 + 40))
        # light beam
        beam = pygame.Surface((160, S.SCREEN_H), pygame.SRCALPHA)
        for i in range(80):
            a = int(80 * (1 - i / 80))
            pygame.draw.rect(beam, (*S.EERIE, a), (80 - i, 0, i * 2, S.SCREEN_H))
        self.screen.blit(beam, (cx - 80, 0))
        # swirling portal mouth
        for i in range(50):
            a = self.t * 2 + i * 0.5
            rad = 10 + i * 1.4
            x = cx + math.cos(a) * rad
            y = 40 + math.sin(a) * rad * 0.5
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*S.EERIE, 180), (3, 3), 2)
            self.screen.blit(s, (x, y))
        # falling player sprite
        spr = self.actors["player"][("down", 0)]
        spr = pygame.transform.rotozoom(spr, prog * 40, 1.0 + prog * 0.4)
        self.screen.blit(spr, (cx - spr.get_width() // 2, py))
        # dust at landing
        if prog > 0.85:
            for i in range(14):
                ang = i / 14 * math.tau
                d = (prog - 0.85) * 300
                x = cx + math.cos(ang) * d
                y = py + 30 + math.sin(ang) * d * 0.4
                pygame.draw.circle(self.screen, S.DUST, (int(x), int(y)), 3)
        self.screen.blit(self.vignette, (0, 0))

    # ---- ambient motes ------------------------------------------------
    def _update_motes(self, dt):
        for m in self.motes:
            m[0] += m[2] * dt
            m[1] += m[3] * dt
            if m[1] < -4:
                m[1] = S.SCREEN_H + 4
                m[0] = random.uniform(0, S.SCREEN_W)
            if m[0] < -4:
                m[0] = S.SCREEN_W + 4
            elif m[0] > S.SCREEN_W + 4:
                m[0] = -4

    def _draw_motes(self):
        for m in self.motes:
            a = int(70 * m[4])
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 214, 200, a), (2, 2), 1)
            self.screen.blit(s, (m[0], m[1]))


def main():
    Game().run()
