# Frogger

A simple Frogger-style game I made with Python and pygame. You play as a frog trying to cross roads and rivers to reach the lily pads at the top. It's one file (`frogger.py`) and everything is drawn with basic shapes — no image files needed.

## How to run

Make sure you have Python 3.9+ and pygame:

```bash
pip install pygame
python3 frogger.py
```

That's it. A window should pop up. Press **Space** or **Enter** on the title screen to start.

## Controls

| What | Keys |
|------|------|
| Hop up / down / left / right | **Arrow keys** or **WASD** |
| Start / continue after dying | **Space** or **Enter** |

The frog moves one tile at a time (not smooth walking). There's a short cooldown between hops so you can't spam keys.

## How to play

1. Start at the bottom on the green safe zone.
2. Hop through the **road** lanes — don't get hit by cars.
3. Cross the **river** by landing on **logs**. Each log has 1–3 slots (the little dividers show where you can stand). If you hop into open water, you drown.
4. While on a log, you ride with it. If the log carries you off the screen, you drown.
5. Reach the **lily pads** at the top. Fill all of them to beat the level.
6. You get **3 lives**. Cars squash you, water drowns you.

Score goes up when you reach a lily pad. Each new level makes the cars and logs a bit faster.

## What's in the code

Everything lives in `frogger.py` (~480 lines):

- **Frog** — player position, hopping, riding logs
- **Car** — moves left or right on road lanes
- **Log** — river platform with 1–3 frog slots
- **Lanes** — spawns all cars/logs and tracks lily pads
- **main()** — game loop, input, drawing, score/lives

The game uses a grid (columns and rows). On land you're snapped to the grid. On logs you're locked to a slot and move with the log — similar to the original arcade Frogger.

## Other stuff in this repo

There's also a bigger pygame story game in `jun_world/` from an earlier version of the project. That's separate from Frogger. To run that one: `pip install pygame` then `python3 play.py`.

## Requirements

- Python 3.9+
- pygame 2.x

See `requirements.txt` for the dependency list (mostly for the other game; Frogger only needs pygame).
