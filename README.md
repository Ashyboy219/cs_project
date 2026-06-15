# Year End Project — Frogger

**IB Computer Science SL** · Skyline High School  
**Team:** Ashish Naik ([Ashyboy219](https://github.com/Ashyboy219)) · Kruthik Ankam ([KiwiHazards](https://github.com/KiwiHazards))

A Frogger-style arcade game built in Python and pygame. Guide a frog across roads and rivers to reach lily pads at the top. Grid movement, log slots, cars, scoring, and levels — all drawn with code (no image files).

---

## Repository structure

```
documentation/          Required project docs (norms, spec, Gantt, testing)
  templates/            Teacher-provided blank templates (.docx / .pdf)
  group-norms.md
  project-specification.md
  record-of-tasks.md
  testing.md
product/                Source code
  frogger.py
  requirements.txt
  README.md
```

---

## Quick start

```bash
cd product
pip install -r requirements.txt
python3 frogger.py
```

**Controls:** Arrow keys or WASD to hop · Space/Enter to start or continue

---

## Assignment deliverables

| Deliverable | Location |
|-------------|----------|
| Group norms | `documentation/group-norms.md` |
| Project specification | `documentation/project-specification.md` |
| Gantt / record of tasks | `documentation/record-of-tasks.md` |
| Test plan | `documentation/testing.md` |
| Working product | `product/frogger.py` |

---

## Success criteria (summary)

1. Grid-based hopping with keyboard controls  
2. Cars and water collisions work; frog rides log slots  
3. Lily pads, score, lives, levels, and game over  
4. Modular OOP design (Frog, Car, Log, Lanes)  
5. Runs with pygame only  

Full details in `documentation/project-specification.md`.

---

## Presentation

Live slides for class demo: [cs-project-smoky.vercel.app](https://cs-project-smoky.vercel.app/)

Files: `index.html` and `vercel.json` at repo root (Vercel deployment).
