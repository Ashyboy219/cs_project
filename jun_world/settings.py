"""Global constants and the colour palette for jun-world: Act One.

Everything visual in the game is generated procedurally from these values,
so the game runs with nothing but pygame installed.
"""

# ---- Window / timing -------------------------------------------------------
TITLE = "JUN-WORLD  -  Act One: The Ruined Gate"
TILE = 32
VIEW_TILES_W = 26
VIEW_TILES_H = 16
SCREEN_W = VIEW_TILES_W * TILE   # 832
SCREEN_H = VIEW_TILES_H * TILE   # 512
FPS = 60

# ---- Gameplay tuning -------------------------------------------------------
PLAYER_SPEED = 2.4
GUARD_PATROL_SPEED = 1.4
GUARD_CHASE_SPEED = 2.55     # faster than you when sprinting straight — you must use cover
INTERACT_RANGE = 40

VISION_RANGE = 200          # how far a guard can see (pixels)
VISION_HALF_ANGLE = 37      # half field-of-view, degrees
DETECT_RATE = 118           # detection meter points gained per second when seen
DETECT_DECAY = 42           # points lost per second when not seen
BUSH_DETECT_MULT = 0.42     # detection while hiding in a bush (less of a free pass now)

# ---- Survival --------------------------------------------------------------
PLAYER_MAX_HP = 5           # hearts
INVULN_TIME = 1.05          # i-frames after a hit (seconds)
GUARD_TOUCH_DAMAGE = 1
KNOCKBACK = 26.0

# ---- Dash (dodge) ----------------------------------------------------------
DASH_SPEED = 6.6
DASH_TIME = 0.15            # i-frames last the whole dash
DASH_COOLDOWN = 0.42
DASH_STAMINA_COST = 34
STAMINA_MAX = 100
STAMINA_REGEN = 40          # per second

# ---- The Sling (first weapon: stun, not kill) ------------------------------
PEBBLE_SPEED = 6.4
PEBBLE_LIFE = 0.85          # seconds before it drops
PEBBLE_MAX = 8              # pebbles per zone (refilled on entry)
FIRE_COOLDOWN = 0.40
GUARD_STUN_TIME = 3.2       # a direct hit staggers a guard this long
PEBBLE_DAMAGE = 1          # damage a pebble does to a combat enemy

# ---- the Captain: Act One pursuit boss ------------------------------------
# He can't be killed — only out-paced and staggered. The numbers below are the
# whole fight's fairness budget, so keep them honest:
CAPTAIN_CHASE_SPEED  = 2.18   # a hair under your 2.4 — straight sprints SLOWLY gain ground
CAPTAIN_STAGGER_TIME = 1.20   # a sling hit freezes him this long (your opening)
CAPTAIN_STAGGER_LOCK = 1.40   # ...then he shrugs off slings this long (no perma-lock)
CAPTAIN_TOUCH_STUN   = 0.45   # he recoils briefly right after he lands a hit on you
CAPTAIN_TOUCH_RECOIL = 34.0   # ...and is shoved back, so a hit never juggles you in place
WHIPCORD_DAMAGE = 2        # a charged Whipcord shot
WHIPCORD_CHARGE = 0.5      # hold time for a full charge (Whipcord upgrade)

# ---- Act Two combat --------------------------------------------------------
ENEMY_BULLET_SPEED = 3.1
ENEMY_BULLET_R = 6
ENEMY_TELEGRAPH = 0.55     # honest wind-up before an enemy fires
KO_CHITS = 3               # chits earned per enemy knocked out

# ---- Moral path keys -------------------------------------------------------
MERCY = "mercy"
SURVIVAL = "survival"
CRUELTY = "cruelty"

# ---- Colour palette --------------------------------------------------------
# A muted, dusty world with warm hope-accents and a cold castle red.
BLACK      = (12, 11, 16)
NEAR_BLACK = (20, 18, 26)
INK        = (28, 25, 36)
DARK       = (40, 36, 50)
SLATE      = (58, 54, 72)
STONE      = (92, 86, 104)
STONE_LT   = (120, 112, 130)
DUST       = (158, 138, 110)
DUST_DK    = (120, 100, 78)
SAND       = (190, 168, 132)
GRASS      = (96, 116, 72)
GRASS_DK   = (74, 92, 56)
GRASS_LT   = (124, 146, 92)
WATER      = (58, 92, 120)
WATER_DK   = (44, 72, 98)
WOOD       = (116, 84, 56)
WOOD_DK    = (86, 60, 40)
ROOF       = (138, 78, 66)
ROOF_DK    = (104, 56, 48)

WHITE      = (236, 232, 224)
BONE       = (214, 206, 192)
GREY       = (150, 146, 156)

HEART         = (216, 64, 72)
HEART_DK      = (60, 30, 36)
STAMINA_COL   = (120, 196, 210)
STAMINA_LOW   = (210, 150, 90)
PEBBLE_COL    = (206, 196, 168)
SUFFLOK_RED   = (176, 44, 52)
SUFFLOK_RED_D = (120, 28, 36)
GOLD          = (214, 178, 92)
GOLD_DK       = (150, 120, 56)
EERIE         = (122, 198, 188)   # checkpoint hum / portal glow
EERIE_DK      = (70, 132, 132)
WARN          = (236, 188, 86)
ALARM         = (228, 96, 84)
CHIT_COL      = (224, 196, 120)   # currency
BULLET_COL    = (236, 150, 90)    # enemy projectiles
BULLET_CORE   = (255, 224, 180)
SPOTLIGHT     = (244, 226, 150)   # stage kill-zone

# ---- Twisted Castle Kingdom palette (Act Two) ------------------------------
COURT_STONE   = (74, 66, 92)
COURT_STONE_L = (104, 94, 126)
COURT_FLOOR   = (96, 70, 86)      # red-purple marble
COURT_FLOOR_L = (124, 92, 110)
COURT_CARPET  = (132, 40, 52)
COURT_CARPET_D= (96, 26, 38)
COURT_GOLD    = (210, 172, 84)
STAGE_WOOD    = (120, 78, 60)
STAGE_WOOD_D  = (88, 54, 42)
VELVET        = (88, 36, 70)

# Path-flavoured accent (used for checkpoint glow + UI tint).
PATH_TINT = {
    MERCY:    (122, 198, 188),
    SURVIVAL: (150, 176, 210),
    CRUELTY:  (190, 96, 120),
}

# Character body colours.
PLAYER_BODY   = (96, 150, 176)
PLAYER_BODY_D = (66, 112, 138)
PLAYER_SKIN   = (228, 188, 156)
ROOK_BODY     = (170, 96, 72)
ROOK_BODY_D   = (132, 70, 52)
ROOK_SKIN     = (210, 168, 138)
ANKAM_BODY     = (92, 80, 120)
ANKAM_BODY_D   = (66, 56, 92)
ANKAM_SKIN     = (198, 178, 156)
GUARD_BODY    = (96, 92, 108)
GUARD_BODY_D  = (66, 62, 80)
VILLAGER_COLS = [
    (120, 120, 96), (108, 96, 116), (96, 112, 110),
    (132, 108, 96), (104, 116, 124),
]

# Act Two characters / enemies
PIKEMAN_BODY   = (60, 72, 120)    # court guard — navy + gold
PIKEMAN_BODY_D = (40, 50, 92)
CHARGER_BODY   = (150, 70, 60)    # red brute
CHARGER_BODY_D = (112, 48, 44)
CONDUCTOR_BODY = (120, 92, 150)   # purple support
CONDUCTOR_BODY_D = (90, 66, 116)
HERALD_BODY    = (170, 120, 60)   # gaudy gold
HERALD_BODY_D  = (128, 88, 42)
SHOPKEEP_BODY  = (96, 116, 90)    # mottled green-brown
SHOPKEEP_BODY_D = (70, 88, 66)
SHOPKEEP_SKIN  = (200, 176, 150)
