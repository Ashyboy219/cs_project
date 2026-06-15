# Project Specification

**Name of Project:** Frogger (Python / pygame arcade game)

**Name of student(s):** Ashish Naik (Ashyboy219) · Kruthik Ankam (KiwiHazards)

*Filled-in version of the teacher template (`templates/Year_End_Project_Specification.docx.pdf`).*

---

## PROJECT PROBLEM STATEMENT

Arcade games are a practical way to learn programming because they combine input handling, graphics, timing, and collision detection in one program. Our problem is to build a **working Frogger-style game** where the player guides a frog across busy roads and a river to reach lily pads at the top of the screen.

Many students have never built a graphical game before. We need a project that runs on school laptops without paid software or image files, demonstrates **object-oriented design** (separate classes for the frog, cars, logs, and lane manager), and can be finished and tested within the year-end project timeline.

The opportunity is to recreate core mechanics from the classic 1981 game: grid movement, riding moving logs with fixed slots, avoiding cars, scoring, lives, and increasing difficulty — while learning **Python and pygame**.

---

## CONCISE DESIGN OVERVIEW

After researching pygame tutorials and Frogger clones, we chose a **single-file modular OOP design** in `product/frogger.py`.

| Component | Role |
|-----------|------|
| **Frog** | Player on a grid; hops one tile per key press; rides log slots on river rows |
| **Car** | Enemy on road rows; moves horizontally and wraps off-screen |
| **Log** | River platform with 1–3 discrete slots (one tile wide each) |
| **Lanes** | Spawns all cars/logs, tracks lily pad goals, attaches frog to logs |
| **main()** | pygame loop: events → update → draw; manages game states |

**Prototype / model:** the running game window is the prototype. Lanes are color-coded rows (safe, water, road, goal). The frog is drawn with ellipses and circles; cars are rectangles with headlights; logs are brown bars with slot divider lines. No external assets.

**Abstract flow:**

```
Title screen → Play → (reach goals / die) → Win or Dead or Game Over → restart
```

Grid: 16 columns × 17 rows, 40px tiles, HUD bar at top for score / lives / level.

---

## SCOPE STATEMENT

### SMART objectives

| Objective | Specific | Measurable | Achievable | Relevant | Time-bound |
|-----------|----------|------------|------------|----------|------------|
| Playable Frogger core | Hop, roads, river, goals | Demo + test cases pass | pygame on school Mac | CS SL OOP project | By 5/28 demo |
| Documentation complete | Norms, spec, Gantt, testing | All files in `documentation/` | Templates provided | Grading rubric | By 6/9 submission |
| Partner collaboration | PRs and shared tasks | Record of tasks shows 50/50 | Two-person team | Group project requirement | Ongoing through June |

### Success criteria (minimum 3 required)

1. **SC1 — Movement:** Player starts game and hops on a grid with arrow keys or WASD (one tile per press).
2. **SC2 — Collisions:** Cars kill on road rows; open water kills; frog rides log slots on river rows.
3. **SC3 — Win condition:** All lily pads can be filled, score increases, levels get faster, game over after 3 lives.
4. **SC4 — OOP design:** Separate Frog, Car, Log, and Lanes classes with a clear game loop.
5. **SC5 — Deployable:** Runs with `pip install pygame` and `python3 frogger.py` from the repo.

### In scope

- Title / play / dead / win / game over screens  
- Score, lives, level HUD  
- Manual testing with documented positive and negative cases  
- GitHub repo with `documentation/` and `product/` folders  

### Out of scope

- Sound and music  
- Online multiplayer  
- Mobile touch controls  
- Saved high-score file  

---

## TIMELINE

See **`record-of-tasks.md`** for the full Gantt chart / record of tasks with owners and status.

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| Repo + folders + group norms | 5/8 | GitHub structure, `group-norms.md` |
| Problem statement in OneNote | 5/13 | Collaboration section |
| Project specification | 5/15 | This document |
| Planning complete | 5/20 | Record of tasks |
| Interim demo 1 | 5/22 | Playable hop + roads |
| Interim demo 2 | 5/28 | Logs, goals, scoring |
| Final submission + live demo | 6/9 (11th grade) | Full repo + class presentation |

---

## TEST PLAN

See **`testing.md`** for full module-level cases.

### Whole solution (integration)

| Test | Type | Steps | Expected |
|------|------|-------|----------|
| Full level clear | Positive | Reach every lily pad | Level increases, win screen |
| Full game over | Negative | Lose 3 lives | Game over screen, score shown |
| Fresh install | Positive | `pip install pygame`, run game | Window opens, title screen |

### Component testing (manual)

| Module | Positive test | Negative test |
|--------|---------------|---------------|
| Frog.tryHop | Hop up from start row | Hop off grid edge — no move |
| Frog + water | Land on log slot | Hop into open water — drown |
| Car | Car wraps when leaving screen | N/A |
| Log.slotForCol | Column on log returns slot index | Column in gap returns None |
| Lanes.markGoal | First visit to pad scores | Second visit same pad — no duplicate score |

**Method:** Manual testing during class demos and before each commit to `main`. No automated test framework (out of scope); we use a written test table with pass/fail notes.

---

## RISKS AND CONTINGENCY PLANS

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Partner absent on demo day | Medium | Medium | Other partner can run full demo; README has run steps |
| pygame not installed on demo laptop | Low | High | Test on classroom machine day before; bring `requirements.txt` |
| Log riding bugs (frog glitches off log) | Medium | High | Use slot-based position from log.x; retest after each change |
| Scope creep (adding sounds, menus, etc.) | Medium | Medium | Stick to spec; extras only if core criteria done |
| Unequal work split | Low | High | Record of tasks + PR reviews; talk to teacher if norms broken |
| GitHub / merge conflicts | Medium | Low | Small commits; communicate before editing same file |

---

## Technology

- Python 3.9+, pygame 2.x, Git/GitHub (Skyline Classroom repo)

## How to run

```bash
cd product
pip install pygame
python3 frogger.py
```
