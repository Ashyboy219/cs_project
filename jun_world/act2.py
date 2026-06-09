"""Act Two: The Theatrical Crown.

Scene population, projectile-combat flow, the Weird Shopkeeper economy, the
rigged-decree puzzle, and the multi-phase Court Herald boss.  All functions take
the live Game instance `g` and lean on its helpers (say, choose, add_moral, L,
_tile_feet, _fire_bullet, _update_enemies, toast, audio, flags, ...).

Dialogue here is intentionally swappable: a background design-agent team is
authoring richer voiced lines that drop into these same beats.
"""
import math
import random
import pygame

from . import settings as S
from .entities import Enemy, NPC


# ---------------------------------------------------------------------------
class _Bar:
    """A static collision rect (the arena portcullis)."""
    def __init__(self, rect):
        self.rect = rect


def L(g, pairs):
    return [g.L(s, t) for (s, t) in pairs]


# ---------------------------------------------------------------------------
# Enemy factory
# ---------------------------------------------------------------------------
def make_enemy(g, kind, tx, ty):
    fx, fy = g._tile_feet(tx, ty)
    if kind == "charger":
        e = Enemy(g.actors["charger"], fx, fy, role="charger", hp=3, speed=1.7, name="Brute")
        e.contact_dmg = 1
    elif kind == "turret":
        e = Enemy(g.actors["pikeman"], fx, fy, role="turret", hp=3, speed=0.0, name="Crossbow Nest")
        e.pattern = "spread3"
        e.fire_interval = 2.3
    elif kind == "conductor":
        e = Enemy(g.actors["conductor"], fx, fy, role="conductor", hp=4, speed=0.9, name="Stagehand")
    else:  # pikeman
        e = Enemy(g.actors["pikeman"], fx, fy, role="shooter", hp=2, speed=1.15, name="Court Pikeman")
        e.pattern = "aimed"
        e.fire_interval = 1.9
    return e


def _spawn_wave(g, wave):
    for (kind, tx, ty) in wave:
        g.enemies.append(make_enemy(g, kind, tx, ty))


def _live(g):
    return [e for e in g.enemies if not e.ko]


# ---------------------------------------------------------------------------
# Act Two entry
# ---------------------------------------------------------------------------
def start(g):
    g.act = 2
    g.mode = "play"
    g.cutscene = False
    g.menu = None
    g._do_transition("k_gate", "from_escape")


def gate_message(g, needs):
    if needs == "act2_ankam":
        return "Mr. Ankam is still mid-speech. Best not to bolt for the wings yet."
    if needs == "arena_cleared":
        return "The portcullis is down. Clear the floor first."
    return "The way is barred."


# ---------------------------------------------------------------------------
# Populate
# ---------------------------------------------------------------------------
def populate(g, name, data):
    g.act2_state = {"points": []}
    st = g.act2_state
    if name == "k_gate":
        for (kind, tx, ty) in data.get("skirmish", []):
            g.enemies.append(make_enemy(g, kind, tx, ty))
        st["spawned"] = True
    elif name == "k_town":
        _populate_town(g, data)
    elif name == "k_arena":
        eg = data["exit_gate"]
        r0, r1 = eg["rows"]
        rect = pygame.Rect(eg["col"] * S.TILE, r0 * S.TILE, S.TILE, (r1 - r0 + 1) * S.TILE)
        bar = _Bar(rect)
        g.extra_blockers = [bar]
        st["arena_gate"] = bar
        st["arena"] = dict(waves=data["arena_waves"], i=1, done=False, inter=0.0)
        _spawn_wave(g, data["arena_waves"][0])
        g.objective = "Survive the arena. Wave 1/%d." % len(data["arena_waves"])
    elif name == "k_stage":
        bx, by = g._tile_feet(*data["boss_at"])
        g.boss = CourtHerald(g, bx, by)
        cx, cy = g._tile_feet(*data["captive_at"])
        cap = NPC(g.actors["villager3"], cx, cy, "Captive")
        cap.act2 = True
        cap.kind = "captive_stage"
        g.npcs.append(cap)
        st["spots"] = []


def _populate_town(g, data):
    st = g.act2_state
    sx, sy = g._tile_feet(*data["shop_at"])
    shop = NPC(g.actors["shopkeep"], sx, sy, "Shopkeeper")
    shop.act2 = True
    shop.kind = "shopkeep"
    g.npcs.append(shop)
    st["shop_pos"] = (sx, sy)
    # captured villager paraded on the stage
    vx, vy = g._tile_feet(*data["villager_at"])
    cap = NPC(g.actors["villager3"], vx, vy, "Captive")
    cap.act2 = True
    cap.kind = "captive_town"
    g.npcs.append(cap)
    # a couple of frightened courtfolk
    for i, (tx, ty) in enumerate([(7, 14), (33, 8), (16, 16)]):
        n = NPC(g.actors["villager%d" % (i % 5)], *g._tile_feet(tx, ty),
                name="Villager", wander=True)
        n.act2 = True
        n.kind = "court"
        n.line_i = 0
        g.npcs.append(n)
    # the rigged decree board
    dx, dy = g._tile_feet(*data["decree_at"])
    st["points"].append(dict(kind="decree", x=dx, y=dy))


# ---------------------------------------------------------------------------
# Per-scene entry beats
# ---------------------------------------------------------------------------
def enter(g, prev, to):
    g.act2_state.setdefault("points", [])
    if to == "k_gate":
        g.objective = "Cross into the kingdom."
        g.say(L(g, [
            ("Rook", "There it is. The Twisted Castle Kingdom. Looks like someone gilded a corpse "
             "and called it a celebration."),
            ("Rook", "See the gold leaf? It's peeling. The whole place is gold paint over wet "
             "wood. Lean on the wrong wall and your hand comes away shining AND rotten. Remember that."),
            ("Loudspeaker Cart", "GRA-TI-TUDE IS MAN-DA-TORY. SMILE AT INTERVALS. UN-GRATEFUL "
             "CITIZENS WILL BE NOTED. ENJOY THE FESTIVAL OF GRATITUDE. SMILE AT INTERVALS."),
            ("Rook", "Festival of Gratitude. Every soul in there is grateful at gunpoint. And "
             "they've taken someone — a girl from up our valley. They mean to 'award' her to "
             "Sufflok on the main stage, like a ribbon, in front of a crowd too scared to look away."),
            ("Rook", "I can't walk in — my face is on every other post. But you came out of the "
             "SKY. There's no poster for that yet. So you go in the front, I work the cracks, and "
             "somewhere in the middle we steal her back."),
            ("Rook", "One thing first. These aren't village guards — Court Pikemen, and they "
             "SHOOT. Everything flashes before it fires. When it flashes, you dash THROUGH the "
             "line, not away from it. Away is where the next one lands. Sling still drops them cold."),
        ]), then=lambda: _gate_goal(g))
    elif to == "k_town":
        g.objective = "The court town. Find a way backstage."
        _ankam_return(g)
    elif to == "k_arena":
        g.objective = "Survive the arena. Wave 1."
        g.toast.push("They're funnelling you onto the floor. Dash the shots, KO them, advance.",
                     S.WARN, 4.0)
    elif to == "k_stage":
        g.objective = "The Festival stage."
        _boss_intro(g)


def _after(g, objective):
    g.objective = objective
    g._autosave()


def _gate_goal(g):
    g.choose("Why are you really going in there?", [
        dict(label="\"To get her out. Nobody gets 'awarded' to anyone.\"", tag=S.MERCY,
             cb=lambda: _gate_goal_pick(g, S.MERCY, "goal_rescue", [
                 ("You", "Nobody gets handed to a tyrant like a prize. I don't care how the crowd "
                  "claps. We get her out, and we get her home."),
                 ("Rook", "Say it quiet, mean it loud. Come on — let's go steal a person back "
                  "from a party.")])),
        dict(label="\"A festival this loud is the best cover to slip out alive.\"", tag=S.SURVIVAL,
             cb=lambda: _gate_goal_pick(g, S.SURVIVAL, "goal_survive", [
                 ("You", "Everyone's watching the stage. That's the only time a place like this "
                  "stops watching the exits. We use the noise. Grab her in the gap, gone before "
                  "the applause stops."),
                 ("Rook", "Cold. Smart-cold, the kind I like. The crowd's loudest the second "
                  "before Sufflok's name. That's our window.")])),
        dict(label="\"By the time I leave, this castle is going to be afraid of me.\"", tag=S.CRUELTY,
             cb=lambda: _gate_goal_pick(g, S.CRUELTY, "goal_fear", [
                 ("You", "They run on fear. Fine. I'll give them something newer to be afraid of "
                  "than him. By the time I'm done, the wardens flinch when I walk."),
                 ("Rook", "...Hey. HEY. The girl. We're here for the GIRL. Fear's a tool — but you "
                  "keep reaching for the same one, one day it's the only one in your hand. Just go.")])),
    ])


def _gate_goal_pick(g, tag, flag, lines):
    g.add_moral(tag, 1)
    g.flags.add(flag)
    g.say(L(g, lines),
           then=lambda: _after(g, "Knock them out. Dash the volleys (Space). Then take the east gate."))


# ---------------------------------------------------------------------------
# Mr. Ankam returns (branches on his Act One disposition)
# ---------------------------------------------------------------------------
def _ankam_return(g):
    gx, gy = g._tile_feet(20, 4)
    ankam = NPC(g.actors["ankam"], gx, gy, "Mr. Ankam")
    ankam.overlay = g.ankam_hat
    ankam.act2 = True
    ankam.kind = "ankam2"
    g.ankam2 = ankam
    g.npcs.append(ankam)
    g.cutscene = True
    g.move_actor(ankam, (g.player.x / S.TILE + 2.0, g.player.y / S.TILE), speed=1.8,
                 then=lambda: _ankam_talk(g))


def _ankam_talk(g):
    g.ankam2.face_to(g.player.x, g.player.y)
    if "ankam_mercy" in g.flags:
        block = [
            ("Mr. Ankam", "YOU. Of course it's you. Do you have any idea how much paperwork a "
             "person like you generates simply by EXISTING in a kingdom?"),
            ("Mr. Ankam", "...Listen. Quietly. The festival's a snare. Sufflok's 'awarding' a "
             "villager to himself on that stage to remind everyone he can. I am NOT telling you "
             "this. I was never here. But the rigging beneath the stage — it's flammable, and "
             "the Herald is a coward. That's all. That's all I said, which was nothing."),
            ("???", "(He's helping. Badly. Furtively. Because once, you looked at him like he "
             "was a person — and the fear answered with a small, terrified kindness.)"),
        ]
    elif "ankam_cruel" in g.flags:
        block = [
            ("Mr. Ankam", "Oh. Oh no. It's the— the one who— guards, the— where are the— why do I "
             "never have guards when I— "),
            ("Mr. Ankam", "Please don't do the thing. The thing you did. I'll just— I'll stand "
             "over here and pretend to file something. The stage. Go to the stage. Anything to get "
             "you AWAY from m— I mean, glory to Lord Sufflok, etcetera, AAH—"),
            ("???", "(He's so frightened of you he's useless to himself. He scuttles off, knocking "
             "over a tribute urn. Somewhere, that costs a villager a ration. Power is fast. It is "
             "rarely clean.)"),
        ]
    else:
        block = [
            ("Mr. Ankam", "The outsider. With no file, no permit, and an alarming habit of being "
             "RIGHT. I checked. There is no lawful way for you to be here, which means officially "
             "you are not, which means I am not SEEING you."),
            ("Mr. Ankam", "Since I'm not seeing you, I can't stop you walking backstage. And I "
             "certainly can't mention that the Herald's whole act runs off one script he'd die "
             "before improvising. Now if you'll excuse me, I have a great deal of not-noticing to do."),
            ("???", "(You didn't beat him in the village. You made the lie cost more than the "
             "truth. He's still paying it off — in tips.)"),
        ]
    g.say(L(g, block), then=lambda: _ankam_done(g))


def _ankam_done(g):
    g.flags.add("act2_ankam")
    g.cutscene = False
    g.objective = "Browse the Shopkeeper, read the decree, then take the east door backstage."
    g.move_actor(g.ankam2, (20, 3), speed=1.6)
    g.toast.push("Tab = inventory · the green stall sells gear for chits · east door = backstage",
                 S.BONE, 4.6)
    g._autosave()


# ---------------------------------------------------------------------------
# Interactions
# ---------------------------------------------------------------------------
SHOP_ITEMS = [
    dict(id="bandage", name="Bandage", cost=6, effect="bandage", flavor="heals 2 hearts"),
    dict(id="smoke", name="Smokebead", cost=8, effect="smokebead", flavor="vanish 3s"),
    dict(id="pouch", name="Pebble Pouch", cost=10, effect="pebble_pouch", flavor="+4 sling capacity"),
    dict(id="whip", name="Whipcord Sling", cost=18, effect="whipcord", flavor="pebbles hit twice as hard"),
]


def talk(g, npc):
    if npc.kind == "shopkeep":
        _shop_greet(g)
    elif npc.kind in ("captive_town", "captive_stage"):
        _captive_talk(g, npc)
    elif npc.kind == "ankam2":
        g.say(L(g, [("Mr. Ankam", "I'm not here. You're not here. Beautiful weather for it.")]))
    else:  # court folk
        pool = [
            [("Villager", "Clap when the lights go red. Don't clap and the lights find YOU."),
             ("Villager", "We've all got sore hands and dry eyes. That's the Festival of Gratitude.")],
            [("Villager", "They took my neighbour to 'award' her to him. Like she's a ribbon."),
             ("Villager", "If you're going backstage... the Herald can't fight. He can only "
              "ANNOUNCE. Take away his script and he's just a loud man in gold.")],
            [("Villager", "That shopkeep? Sells you a lie and a cure in the same breath. "
              "Both work, somehow.")],
        ]
        block = pool[npc.line_i % len(pool)]
        npc.line_i += 1
        g.say(L(g, block))


def _captive_talk(g, npc):
    g.say(L(g, [
        ("Captive", "Don't. Don't make a scene for me — they'll only— ...you're not from here, "
         "are you. You don't have the flinch yet."),
        ("Captive", "If you really mean to help: it's not the guards that hold this place. It's "
         "the SHOW. Break the show and the rest is just frightened people remembering they're "
         "many and he's one."),
    ]))


def _shop_greet(g):
    if "met_shop" not in g.flags:
        g.flags.add("met_shop")
        lore = [
            ("Shopkeeper", "Ah-ah-ah. New face. Faces are inventory, you know — I keep a few. "
             "Don't worry, yours is cheap."),
            ("Shopkeeper", "You came through the SKY. Mm. Old word for that. 'Door.' They outlawed "
             "doors that open both ways, you know — long before your boots. A door that only lets "
             "things IN... that's a mouth, dear. Wonder what's hungry."),
            ("Shopkeeper", "But! Commerce. I sell bandages, smoke, pebbles, and one very good "
             "string for that sad little sling. Chits only. Knock heads, find chits. Off you go — "
             "browse."),
        ]
        g.say(L(g, lore), then=lambda: _open_shop(g))
    else:
        g.say(L(g, [("Shopkeeper", random.choice([
            "Back already? The smell of chits, I knew it.",
            "Buy something or admire something. The admiring is free. Once.",
            "Whipcord's the smart buy. Or be sentimental and heal. Your funeral, dear.",
        ]))]), then=lambda: _open_shop(g))


def _open_shop(g):
    disc = "mercy" if g.dominant() == S.MERCY else None
    items = []
    for it in SHOP_ITEMS:
        c = it["cost"]
        if disc and it["effect"] != "whipcord":
            c = max(1, c - 2)
        items.append(dict(it, cost=c))
    g.open_shop(items)


def talk_point(g, pt):
    if pt["kind"] == "decree":
        _decree(g)


def _decree(g):
    if "decree_won" in g.flags:
        g.say(L(g, [("???", "The decree board, now with your amendment nailed over it. A small "
                     "guard keeps re-reading it and getting angrier.")]))
        return
    g.say(L(g, [
        ("???", "A brass DECREE, bolted to the board, gilt and absolute:"),
        ("???", "'BY FESTIVAL LAW: NO PERSON MAY LEAVE THE COURT UNTIL THEY HAVE GIVEN A TRIBUTE "
         "OF EQUAL WORTH TO THE ONE AWARDED ON STAGE. A LIFE FOR A LIFE. SO ORDERS THE CROWN.'"),
        ("Rook", "...They want you to trade YOURSELF to free her. Or trade someone. That's the "
         "trap — it's built so any answer feeds him a body."),
        ("Rook", "Unless. You read it like HE does. To the letter. What does the law actually SAY?"),
    ]), then=lambda: _decree_choice(g))


def _decree_choice(g):
    g.choose("How do you beat the decree?", [
        dict(label="\"A LIFE of EQUAL WORTH. His own crown values HIM most — so I tribute HIM.\"",
             tag=S.SURVIVAL, cb=lambda: _decree_win(g, S.SURVIVAL)),
        dict(label="\"It says a life. It never said a HUMAN one. I tribute the festival's prize goat.\"",
             tag=S.MERCY, cb=lambda: _decree_win(g, S.MERCY)),
        dict(label="\"Equal worth? Then I'll make MY worth a threat no tribute can match.\"",
             tag=S.CRUELTY, cb=lambda: _decree_win(g, S.CRUELTY)),
    ])


def _decree_win(g, path):
    g.add_moral(path, 1)
    g.flags.add("decree_won")
    g.chits += 6
    if path == S.SURVIVAL:
        lines = [("You", "I nominate the most valuable life in this court, by the Crown's own "
                  "measure, as tribute: Lord Sufflok. The law's his. Let him argue with it."),
                 ("Rook", "Ha! The clerks are MELTING. They can't strike it without admitting "
                  "he's worth less than a villager. Beautiful. Cruel-clever, but beautiful.")]
    elif path == S.MERCY:
        lines = [("You", "The decree says 'a life,' not 'a person.' I tribute the festival goat. "
                  "Equal worth — your own auctioneer priced it at a fortune this morning."),
                 ("Rook", "They're checking the LEDGER. The goat's appraised higher than half the "
                  "town, because the town's worth was set to nothing. Their own cruelty just freed her.")]
    else:
        lines = [("You", "Equal worth. Fine. My worth is this: I walk out, and so does she, and "
                  "the first hand that stops us learns exactly what I cost to detain."),
                 ("Rook", "...They moved. They actually MOVED. You scared a whole court with one "
                  "sentence. Watch that doesn't start tasting good to you.")]
    g.say(L(g, lines + [("???", "(+6 chits 'reclaimed' from a tribute box in the confusion. The "
            "decree is broken. The stage is next.)")]))


# ---------------------------------------------------------------------------
# Per-frame update
# ---------------------------------------------------------------------------
def update(g, dt):
    st = g.act2_state
    name = g.scene
    if not st.get("autosaved"):
        st["autosaved"] = True
        g._autosave()
    if name in ("k_gate", "k_arena", "k_stage"):
        st["ammo_regen"] = st.get("ammo_regen", 0.0) + dt
        if st["ammo_regen"] >= 2.0 and g.ammo < g.ammo_max:
            g.ammo += 1
            st["ammo_regen"] = 0.0
        g._update_enemies(dt)
    if name == "k_gate":
        if st.get("spawned") and "k_gate_clear" not in g.flags and not _live(g):
            g.flags.add("k_gate_clear")
            g.objective = "Cleared. Take the east gate to the court."
            g.toast.push("Floor's clear. Go.", S.EERIE, 2.4)
    elif name == "k_arena":
        _update_arena(g, dt)
    elif name == "k_stage":
        _update_spots(g, dt)
        if g.boss is not None:
            g.boss.update(g, dt)


def _update_arena(g, dt):
    ar = g.act2_state.get("arena")
    if not ar or ar["done"]:
        return
    if _live(g):
        return
    if ar["inter"] > 0:
        ar["inter"] -= dt
        return
    ar["i"] += 1
    if ar["i"] > len(ar["waves"]):
        ar["done"] = True
        g.flags.add("arena_cleared")
        bar = g.act2_state.get("arena_gate")
        if bar in g.extra_blockers:
            g.extra_blockers.remove(bar)
        g.objective = "The portcullis grinds open. The stage waits, east."
        g.toast.push("Arena cleared. The way to the stage is open.", S.EERIE, 3.2)
        g.audio.play("save", 0.5)
    else:
        _spawn_wave(g, ar["waves"][ar["i"] - 1])
        ar["inter"] = 0.0
        g.objective = "Survive the arena. Wave %d/%d." % (ar["i"], len(ar["waves"]))
        g.toast.push("Wave %d." % ar["i"], S.WARN, 1.6)


def _add_spot(g, x, y):
    g.act2_state.setdefault("spots", []).append(
        dict(x=x, y=y, r=46, warn=0.75, strike=0.5, t=0.0, state="warn", hit=False))


def _update_spots(g, dt):
    spots = g.act2_state.get("spots", [])
    for sp in spots:
        sp["t"] += dt
        if sp["state"] == "warn":
            if sp["t"] >= sp["warn"]:
                sp["state"] = "strike"
                sp["t"] = 0.0
                g.audio.play("hurt", 0.25)
        elif sp["state"] == "strike":
            if (not sp["hit"] and g.invuln <= 0 and not g.player.dashing
                    and math.hypot(g.player.x - sp["x"], g.player.y - sp["y"]) < sp["r"]):
                sp["hit"] = True
                g._hit_player(1, sp["x"], sp["y"])
            if sp["t"] >= sp["strike"]:
                sp["state"] = "done"
    g.act2_state["spots"] = [s for s in spots if s["state"] != "done"]


def _boss_intro(g):
    g.objective = "Survive the Court Herald. Read his tells. Dash the light."
    g.say(L(g, [
        ("Court Herald", "AND NOW — the moment you've been CONDUCTED to feel grateful for! The "
         "ungrateful intruder, center stage, for your viewing obedience!"),
        ("Court Herald", "I don't FIGHT, you understand. I'm an ARTIST. I CONDUCT. The pikemen, "
         "the lights, the lovely lovely CONFETTI — they fight. I simply... cue them."),
        ("Court Herald", "Hit your marks, little guest. The spotlights are HUNGRY tonight and the "
         "crowd has been instructed to ADORE whatever's left. MAESTRO — from the top!"),
        ("Rook", "He hides behind the show — minions, spotlights, those bursts. Wear his composure "
         "down with the sling, dash everything that flashes. When his script finally breaks, "
         "that's when YOU choose how the curtain falls."),
    ]), then=lambda: g._autosave())


# ---------------------------------------------------------------------------
# The Court Herald boss
# ---------------------------------------------------------------------------
class CourtHerald:
    def __init__(self, g, x, y):
        self.x = float(x)
        self.y = float(y)
        self.r = 20
        self.max_hp = 12
        self.hp = 12
        self.phase = 1
        self.down = False
        self.t = 0.0
        self.tele = 0.0
        self.hit_flash = 0.0
        self.fire_t = 1.6
        self.min_t = 4.0
        self.spot_t = 3.0
        self.home = (x, y)
        self.spr = pygame.transform.rotozoom(g.actors["herald"][("down", 0)], 0, 1.5)
        # candidate minion spawn tiles on the stage
        self.spawn_pts = [(6, 4), (6, 13), (12, 3), (12, 14), (18, 4), (18, 13)]

    def taunt(self):
        return random.choice([
            "THE HERALD: 'A standing ovation for our DOOMED guest!'",
            "THE HERALD: 'LIGHTS! Give them the lights!'",
            "THE HERALD: 'This was NOT in the script— I mean— BEHOLD!'",
        ])

    def take_hit(self, g, dmg):
        if self.down:
            return
        self.hp -= dmg
        self.hit_flash = 1.0
        if self.hp <= 0:
            self.hp = 0
            self.down = True
            _boss_defeated(g)

    def update(self, g, dt):
        self.t += dt
        if self.hit_flash > 0:
            self.hit_flash = max(0.0, self.hit_flash - dt * 3)
        if self.down:
            return
        newp = 1 if self.hp > 8 else (2 if self.hp > 4 else 3)
        if newp != self.phase:
            self.phase = newp
            g.toast.push(self.taunt(), S.HERALD_BODY, 2.0)
            g.audio.play("alert", 0.4)
        # gentle pacing
        self.x = self.home[0] + math.sin(self.t * 0.8) * 18
        # firing
        if self.tele > 0:
            self.tele -= dt
            if self.tele <= 0:
                self._fire(g)
        else:
            self.fire_t -= dt
            if self.fire_t <= 0:
                self.tele = 0.5
                self.fire_t = max(1.0, 1.9 - 0.25 * self.phase)
        # minions
        self.min_t -= dt
        if self.min_t <= 0:
            cap = 1 + self.phase
            if len(_live(g)) < cap:
                tx, ty = random.choice(self.spawn_pts)
                g.enemies.append(make_enemy(g, "pikeman", tx, ty))
            self.min_t = max(2.6, 5.5 - self.phase)
        # spotlights from phase 2
        if self.phase >= 2:
            self.spot_t -= dt
            if self.spot_t <= 0:
                lead = 26
                tx = g.player.x + random.uniform(-lead, lead)
                ty = g.player.y + random.uniform(-lead, lead)
                _add_spot(g, tx, ty)
                self.spot_t = max(1.3, 3.4 - 0.5 * self.phase)

    def _fire(self, g):
        dx, dy = g.player.x - self.x, g.player.y - self.y
        a0 = math.atan2(dy, dx)
        if self.phase == 1:
            angs = [a0]
        elif self.phase == 2:
            angs = [a0 - 0.26, a0, a0 + 0.26]
        else:
            angs = [a0 + i * 2 * math.pi / 10 for i in range(10)]   # confetti ring
        for a in angs:
            g._fire_bullet(self.x, self.y, math.cos(a) * S.ENEMY_BULLET_SPEED,
                           math.sin(a) * S.ENEMY_BULLET_SPEED, color=S.HERALD_BODY)
        g.audio.play("ui_move", 0.3)

    def draw(self, surf, cam):
        x = int(self.x - cam[0])
        yb = int(self.y - cam[1])
        # shadow
        sh = pygame.Surface((40, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 110), (0, 0, 40, 12))
        surf.blit(sh, (x - 20, yb - 6))
        # podium
        pygame.draw.rect(surf, S.STAGE_WOOD_D, (x - 14, yb - 16, 28, 18), border_radius=3)
        pygame.draw.rect(surf, S.COURT_GOLD, (x - 14, yb - 16, 28, 3))
        # body (scaled herald sprite)
        spr = self.spr
        surf.blit(spr, (x - spr.get_width() // 2, yb - spr.get_height() + 4))
        # megaphone
        pygame.draw.polygon(surf, S.COURT_GOLD,
                            [(x + 10, yb - 40), (x + 24, yb - 46), (x + 24, yb - 34)])
        if self.tele > 0:
            r = int(8 + (1 - self.tele / 0.5) * 16)
            pygame.draw.circle(surf, S.WARN, (x, yb - 40), r, 2)
        if self.hit_flash > 0.4:
            fl = pygame.Surface((40, 56), pygame.SRCALPHA)
            pygame.draw.ellipse(fl, (255, 255, 255, 110), (0, 0, 40, 56))
            surf.blit(fl, (x - 20, yb - 56))


def _boss_defeated(g):
    g.bullets = []
    g.act2_state["spots"] = []
    g.say(L(g, [
        ("Court Herald", "No— no, that's not— where's my PAGE, someone fetch my— I don't KNOW "
         "what comes after this part, I've never— "),
        ("Rook", "His script's in pieces and the crowd's gone dead quiet. That silence? That's "
         "yours to spend. How do you end the show?"),
    ]), then=lambda: _boss_choice(g))


def _boss_choice(g):
    g.choose("The Herald has no lines left. End the show —", [
        dict(label="Hand him his own torn script. Read it back. Let them laugh.",
             tag=S.MERCY, cb=lambda: _end_boss(g, S.MERCY)),
        dict(label="Cut the stage rigging. Drop the lights. End it quietly.",
             tag=S.SURVIVAL, cb=lambda: _end_boss(g, S.SURVIVAL)),
        dict(label="Out-roar him. Turn the whole crowd's fear onto HIM.",
             tag=S.CRUELTY, cb=lambda: _end_boss(g, S.CRUELTY)),
    ])


def _end_boss(g, path):
    g.add_moral(path, 2)
    g.flags.add("herald_" + path)
    if path == S.MERCY:
        block = [
            ("You", "Here. Your script. Read the next line — go on, the real one, the one under "
             "the gold paint."),
            ("Court Herald", "...'I am afraid all the time. I make them clap so I can't hear it.' "
             "...I didn't write th— oh. Oh, they're LAUGHING. They're— they're laughing WITH— "),
            ("???", "(He flees the stage in tears and relief, un-knocked-out, un-broken. The crowd "
             "laughs, and for one minute the court forgets to be afraid. Mercy made a hole in the show.)"),
        ]
    elif path == S.SURVIVAL:
        block = [
            ("You", "Forget the man. Cut the show."),
            ("Rook", "Rigging's flammable — Ankam wasn't lying. One spark, the whole gilt backdrop "
             "comes down. No bodies. Just darkness, and an exit."),
            ("???", "(The stage goes black. In the dark, you and the captive are simply... gone. "
             "Clean. Efficient. Nobody's hero, nobody's monster. Alive.)"),
        ]
    else:
        block = [
            ("You", "You want a SHOW? I'll give them one they'll obey."),
            ("Court Herald", "Th-that's MY crowd, you can't just— why are they looking at me like— "
             "like they look at HIM— "),
            ("???", "(You out-perform him until the crowd's fear swings to you and turns on him. "
             "They drag the Herald off. It worked. It was fast. And Rook won't meet your eyes.)"),
        ]
    g.say(L(g, block), then=lambda: _free_captive(g))


def _free_captive(g):
    g.boss = None
    cap = next((n for n in g.npcs if getattr(n, "kind", "") == "captive_stage"), None)
    if cap:
        cap.face_to(g.player.x, g.player.y)
    if "herald_cruelty" in g.flags:
        line = ("Captive", "...You won. I'm free. So why do I still want to run from YOU? "
                "Get me out. Please. Just — get me out.")
    elif "herald_mercy" in g.flags:
        line = ("Captive", "You didn't hurt him. You didn't hurt anyone. You just... let them "
                "remember how to laugh. I didn't know that was a weapon. Thank you.")
    else:
        line = ("Captive", "Quiet, quick, gone. You're good at this. I'd ask what you are, but "
                "I think the answer's still being decided. Let's move.")
    g.say(L(g, [
        line,
        ("Rook", "Doors at the back lead DOWN — out of the kingdom, under it. That's where they "
         "keep the ones they don't parade. The Prison Zones."),
        ("Rook", "Sufflok knows your face now. He sent the Captain. He sent the Herald. Next time "
         "he won't send a SHOW. Come on. While the lights are still down."),
    ]), then=lambda: ending(g))


# ---------------------------------------------------------------------------
# Act Two ending -> teaser -> title
# ---------------------------------------------------------------------------
def ending(g):
    g.flags.add("act_two_done")
    g.cutscene = False
    g.mode = "ending"
    g.card_i = 0
    g.card_t = 0.0
    dom = g.dominant()
    close = {
        S.MERCY: ("You keep finding the gentlest blade in every room — and it keeps working. "
                  "The court will whisper about the day someone made them laugh instead of clap.",
                  S.PATH_TINT[S.MERCY]),
        S.SURVIVAL: ("Quiet, clever, alive. You're learning this place's grammar faster than it "
                     "can rewrite it. The shopkeeper would call that a bargain.", S.PATH_TINT[S.SURVIVAL]),
        S.CRUELTY: ("You're very good at fear now. It answers when you call. That's the part that "
                    "should scare you — and the part that's stopped.", S.PATH_TINT[S.CRUELTY]),
        None: ("Still scared. Still here. Still deciding what all this is making of you.", S.EERIE),
    }
    g.cards = [
        ("The gold-and-rot court goes dark behind you. The Festival of Gratitude is over. "
         "Nobody is grateful.", S.COURT_GOLD),
        close.get(dom, close[None]),
        ("Far above, in a black tower, the tyrant who fears doors finally says your name aloud — "
         "and orders it filed under 'PERSONAL'.", S.SUFFLOK_RED),
        ("Below the kingdom, the lamps run cold and bureaucratic, and the ones who 'disappeared' "
         "are still breathing, just barely, in numbered rooms.", S.STAMINA_COL),
        ("END OF ACT TWO", S.GOLD),
        ("The Theatrical Crown", S.GREY),
        ("Act Three — The Cold Ledger — awaits.", S.EERIE),
    ]


# ---------------------------------------------------------------------------
# Rendering helpers (called from Game._draw_world / HUD)
# ---------------------------------------------------------------------------
def draw_ground(g, cam):
    st = g.act2_state
    # decree board + shop stall + captive platform
    for pt in st.get("points", []):
        if pt["kind"] == "decree":
            _draw_board(g, cam, pt["x"], pt["y"])
    if "shop_pos" in st:
        _draw_stall(g, cam, *st["shop_pos"])
    # arena portcullis
    bar = st.get("arena_gate")
    if bar in g.extra_blockers and bar is not None:
        r = bar.rect.move(-int(cam[0]), -int(cam[1]))
        pygame.draw.rect(g.screen, S.COURT_STONE, r)
        for bx in range(r.x + 4, r.right - 2, 7):
            pygame.draw.line(g.screen, S.COURT_GOLD, (bx, r.y), (bx, r.bottom), 2)
        pygame.draw.rect(g.screen, S.NEAR_BLACK, r, 2)
    # boss spotlights
    for sp in st.get("spots", []):
        x = int(sp["x"] - cam[0])
        y = int(sp["y"] - cam[1])
        surf = pygame.Surface((sp["r"] * 2, sp["r"] * 2), pygame.SRCALPHA)
        if sp["state"] == "warn":
            a = int(60 + 50 * math.sin(g.t * 18))
            pygame.draw.circle(surf, (*S.SPOTLIGHT, max(30, a)), (sp["r"], sp["r"]), sp["r"], 3)
        else:
            pygame.draw.circle(surf, (*S.SPOTLIGHT, 150), (sp["r"], sp["r"]), sp["r"])
        g.screen.blit(surf, (x - sp["r"], y - sp["r"]))


def _draw_board(g, cam, x, y):
    bx = int(x - cam[0])
    by = int(y - cam[1])
    pygame.draw.rect(g.screen, S.WOOD_DK, (bx - 13, by - 30, 26, 22), border_radius=2)
    pygame.draw.rect(g.screen, S.COURT_GOLD, (bx - 13, by - 30, 26, 22), 2, border_radius=2)
    for i in range(4):
        pygame.draw.line(g.screen, S.GOLD_DK, (bx - 9, by - 26 + i * 5), (bx + 9, by - 26 + i * 5), 1)
    pygame.draw.rect(g.screen, S.WOOD, (bx - 2, by - 8, 4, 8))


def _draw_stall(g, cam, x, y):
    sx = int(x - cam[0])
    sy = int(y - cam[1])
    pygame.draw.rect(g.screen, S.SHOPKEEP_BODY_D, (sx - 18, sy - 4, 36, 8), border_radius=2)
    for i in range(5):
        col = S.COURT_CARPET if i % 2 == 0 else S.COURT_GOLD
        pygame.draw.rect(g.screen, col, (sx - 18 + i * 7, sy - 24, 7, 8))
    pygame.draw.rect(g.screen, S.WOOD_DK, (sx - 18, sy - 24, 3, 22))
    pygame.draw.rect(g.screen, S.WOOD_DK, (sx + 15, sy - 24, 3, 22))


def draw_hud(g):
    # chits
    cs = g.fonts.small.render("Chits %d" % g.chits, True, S.CHIT_COL)
    pygame.draw.circle(g.screen, S.CHIT_COL, (24, 122), 5)
    pygame.draw.circle(g.screen, S.GOLD_DK, (24, 122), 5, 1)
    g.screen.blit(cs, (34, 114))
    g.screen.blit(g.fonts.tiny.render("Tab: items", True, S.GREY), (34, 134))
    # boss HP bar
    if g.boss is not None and not g.boss.down:
        w = 320
        x = (S.SCREEN_W - w) // 2
        y = 22
        pygame.draw.rect(g.screen, S.NEAR_BLACK, (x - 3, y - 3, w + 6, 20), border_radius=6)
        pygame.draw.rect(g.screen, S.INK, (x, y, w, 14), border_radius=4)
        frac = g.boss.hp / g.boss.max_hp
        pygame.draw.rect(g.screen, S.HERALD_BODY, (x, y, int(w * frac), 14), border_radius=4)
        nm = g.fonts.tiny.render("THE COURT HERALD", True, S.GOLD)
        g.screen.blit(nm, (S.SCREEN_W // 2 - nm.get_width() // 2, y + 18))
