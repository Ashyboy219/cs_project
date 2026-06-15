# Test Plan — Frogger

**Project:** Frogger  
**Group:** Ashish Naik · Kruthik Ankam  
**Method:** Manual testing (positive and negative cases per module)  
**Last tested:** June 2026

---

## How to run before testing

```bash
cd product
pip install pygame
python3 frogger.py
```

---

## 1. Frog class (`tryHop`, `update`)

| ID | Type | Test | Steps | Expected result | Pass? |
|----|------|------|-------|-----------------|-------|
| F-01 | Positive | Hop up | Press Up from start | Frog moves one row up | Yes |
| F-02 | Positive | Hop all directions | WASD / arrows | One tile per direction | Yes |
| F-03 | Negative | Hop off top/bottom/side | Move toward edge until blocked | Frog stays in bounds | Yes |
| F-04 | Negative | Spam keys | Hold key during cooldown | Only one hop per cooldown | Yes |
| F-05 | Positive | Reach lily pad | Hop onto empty goal | Score increases, frog resets to bottom | Yes |
| F-06 | Negative | Revisit filled pad | Hop to same pad again | No extra score | Yes |

---

## 2. River / Log system

| ID | Type | Test | Steps | Expected result | Pass? |
|----|------|------|-------|-----------------|-------|
| L-01 | Positive | Land on log slot | Hop from safe row onto visible log slot | Frog rides with log | Yes |
| L-02 | Negative | Hop into open water | Hop to river row with no log under column | Instant drown, lose life | Yes |
| L-03 | Negative | Ride off screen | Stay on log until slot leaves screen | Drown, lose life | Yes |
| L-04 | Positive | Hop between slots on same log | Move left/right on log | Stays on log if slot exists | Yes |
| L-05 | Positive | Slot dividers visible | Look at logs in river | 1–3 slots shown per log | Yes |

---

## 3. Car / Road system

| ID | Type | Test | Steps | Expected result | Pass? |
|----|------|------|-------|-----------------|-------|
| C-01 | Positive | Cars move | Watch road rows | Cars scroll left/right | Yes |
| C-02 | Positive | Cars wrap | Wait for car to leave screen | Car re-enters from other side | Yes |
| C-03 | Negative | Hit by car | Hop into car on road row | Squash, lose life, dead screen | Yes |
| C-04 | Negative | Dash through cars | Try timing (no dash feature) | N/A — grid hop only | N/A |

---

## 4. Lanes / Goals / Levels

| ID | Type | Test | Steps | Expected result | Pass? |
|----|------|------|-------|-----------------|-------|
| G-01 | Positive | Fill all goals | Reach every lily pad | Win screen, level +1 | Yes |
| G-02 | Positive | Level speed up | Complete level 1 | Cars/logs faster on level 2 | Yes |
| G-03 | Positive | HUD updates | Play game | Score, lives, level visible | Yes |
| G-04 | Negative | Three deaths | Lose all lives | Game over screen | Yes |

---

## 5. Game states / UI

| ID | Type | Test | Steps | Expected result | Pass? |
|----|------|------|-------|-----------------|-------|
| U-01 | Positive | Title screen | Launch game | "FROGGER" + Space to start | Yes |
| U-02 | Positive | Start game | Press Space | Gameplay begins | Yes |
| U-03 | Positive | Continue after death | Press Space on SPLAT | Frog resets, play continues | Yes |
| U-04 | Positive | Restart after game over | Press Space on GAME OVER | Back to title, score reset | Yes |
| U-05 | Negative | pygame missing | Run without pygame installed | Clear error message | Yes |

---

## 6. Integration (full play-through)

| ID | Type | Test | Expected result | Pass? |
|----|------|------|-----------------|-------|
| I-01 | Positive | Complete one full level | All pads filled, level 2 starts | Yes |
| I-02 | Positive | Partner machine clone test | `git clone` + run instructions work | Yes |
| I-03 | Negative | Quit window | Close window | Game exits cleanly | Yes |

---

## Notes from demos

- **5/22:** Basic hop and road collision demonstrated in class.  
- **5/28:** Log slots and scoring demonstrated; fixed riding glitch after demo.  
- **6/9:** Final demo — full level clear + game over flow.

---

## Known limitations (not bugs)

- No sound effects  
- No high-score save file  
- Testing is manual only (no pytest suite)
