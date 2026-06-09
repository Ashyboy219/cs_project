# JUN-WORLD — Act One: The Ruined Gate

A top-down, choice-driven story game built with **Python + pygame**. A scared but
kind stranger falls through a portal into a dimension ruled by the tyrant
**Sufflok**. Outside his castle lie ruined villages, frightened people, and a
reckless rebel teen named **Rook**. You want to get home — but how you survive
cruelty becomes who you are. Play with **mercy**, **survival cunning**, or
**cruelty**, and the world reacts.

This is the **complete, playable Act One**, built as a polished vertical slice with
combat, stealth, a boss, save files, and three full moral branches. The full
six-act design (story, systems, bosses, puzzles, art, and a senior design review)
lives in **[DESIGN.md](DESIGN.md)** as the roadmap for the rest of the game.

## Run it

```bash
pip install pygame      # numpy is optional but enables sound
python3 play.py
```

(or `python3 -m jun_world`)  ·  Tested on Python 3.9+ with pygame 2.6.

## Controls

| Action | Keys |
|---|---|
| Move | **WASD** / **Arrow keys** |
| Interact · talk · advance · confirm | **Z**, **Enter**, **E** |
| **Sneak** (slower, harder to spot) | **Shift** (hold) |
| **Dash / dodge** (i-frames, costs stamina) | **Spacebar** |
| **Sling** (stun a guard / make a lure) | **F**, or **left-click** to aim with the mouse |
| Pause · Save · Load · Quit | **Esc** |

## Systems

- **No more checkpoints.** Death matters: lose all your hearts and it's **Game
  Over → reload your last save**.
- **Save files** — 3 manual slots + an autosave on every zone entry. Save/Load from
  the pause menu (Esc) or the title screen. "Continue" picks up your latest save.
- **Health** — five hearts, i-frames after a hit, knockback, screenshake. A dash's
  i-frames let you roll *through* danger if you time it.
- **The Sling** — your first weapon, given by Rook. A pebble to the head **stuns a
  guard** (it doesn't kill); a *miss* clatters and **lures** guards to the noise.
  Pebbles are scarce and refill each zone — restraint is a tool, not a body count.
- **Stealth** — patrolling guards with real vision cones, hide-in-bushes,
  detection meter, alarms, and a chase if you're spotted. Tuned to be tense.
- **Three moral paths** — Mercy / Survival / Cruelty, tracked and shown bottom-right,
  shaping dialogue, NPC trust, the world's fear of you, and the ending.

## Act One, beat by beat

1. **The Fall** — you drop through a torn-song portal onto a cracked road.
2. **The Ruined Village** — frightened people under Sufflok's "taxes." Read the
   scorched notices, help the **Nervous Villager** (an optional moral fork), and
   meet **Rook**, who hands you the Sling and pulls you into a job.
3. **The Guard Depot (stealth)** — slip past vision cones, stun guards with the
   Sling, dash out of trouble, and recover **3 supply crates**. Get caught and the
   guards swarm you — and now that can kill you.
4. **Mr. Ankam** — Sufflok's cowardly, theatrical assistant locks the village down,
   shaking the whole time. **You choose how to face him** — *mercy* (see his fear),
   *survival* (make the truth cost more than the lie), or *cruelty* (make him flee).
5. **The Raid — boss escape** — the garrison horn sounds. You **flee the East Road**
   ahead of an **un-killable elite Captain** (you can only outrun or briefly stun
   him). A locked gate blocks the way, and a **caged villager** offers a fork with an
   *immediate* payoff: **free them** (a full heart for the run — mercy), **shove the
   barrel** (fastest — survival), or **tip the cage at the guards** (clears the path,
   but the world turns colder — cruelty). Reach the far gate to clear Act One.
6. **End of Act One** — closing cards reflect the path you leaned toward and the
   choices you made, and seed the portal mystery: *why did it open, and why you?*

## Design

Inspired by Undertale's emotional weirdness and choice-driven conflict, but with its
own world, its own stealth-and-Sling conflict system, and its own identity — no
heart-in-a-box battles, no copied characters. Core themes: *fear can become many
things*, *power changes people*, *mercy is active not passive*, *survival is morally
messy*, and *cruelty works too fast*.

The expansion was designed by a multi-agent workflow (narrative, systems, boss,
puzzle, and art directors + a senior design-review critic) and then pressure-tested
with a formal **game-design review**. The headline finding shaped the build: *a
player who can win by force must be given a reason to choose restraint — an immediate,
legible reward, not a deferred one.* That's why Act One teaches "you can win without
killing" (the un-killable Captain) **before** the gun matters, the Sling **stuns**
instead of kills, and the escape's mercy choice hands you a heart right when you need
it. See **[DESIGN.md](DESIGN.md)** for the full six-act roadmap, boss/puzzle designs,
and the review.

## Project layout

```
play.py            launcher
DESIGN.md          full six-act design bible + design review (roadmap)
jun_world/
  settings.py      constants, tuning, colour palette
  assets.py        procedural sprites, fonts, synthesised sound
  world.py         tilemap: terrain, buildings, collision, line-of-sight
  entities.py      player (dash/stamina), guards (vision), Sling pebbles, pickups
  scenes.py        Act One maps (built programmatically)
  save.py          save-slot file management
  ui.py            dialogue, branching choices, HUD, menus, effects
  game.py          game loop + the full Act One script
```

All art and audio are generated in code — no external asset files required.
