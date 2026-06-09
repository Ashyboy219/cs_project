#!/usr/bin/env python3
"""Builds FROGGER_PROJECT.pdf — run once: python3 generate_frogger_pdf.py"""

from fpdf import FPDF


class ProjectPdf(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Frogger Project Documentation", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 80, 50)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def body_text(self, text):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, text)
        self.ln(2)

    def bullet(self, text):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, f"- {text}")


def build():
    pdf = ProjectPdf()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # title page
    pdf.ln(50)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(40, 120, 60)
    pdf.cell(0, 14, "Frogger", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "CS Project Documentation", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 7,
        "This document explains my Frogger game: what it does, how to play it, "
        "and how the code is put together. The whole game is one Python file using pygame.",
        align="C")

    pdf.add_page()
    pdf.section_title("1. Introduction")
    pdf.body_text(
        "For this project I built a Frogger-style arcade game in Python. The player "
        "controls a frog that has to cross busy roads and a river full of moving logs "
        "to reach lily pads at the top of the screen. It is inspired by the classic "
        "1981 Konami arcade game, but I wrote everything from scratch with simple "
        "shapes instead of sprites."
    )
    pdf.body_text(
        "I chose this because it hits a good balance for a class project: the rules are "
        "easy to understand, but the movement on logs and collision with cars still "
        "makes you think about timing and positioning."
    )

    pdf.section_title("2. What you need to run it")
    pdf.bullet("Python 3.9 or newer")
    pdf.bullet("pygame library (install with: pip install pygame)")
    pdf.bullet("A computer with a screen (desktop window game, not a web game)")
    pdf.ln(2)
    pdf.body_text("From the project folder, run:")
    pdf.set_font("Courier", "", 10)
    pdf.multi_cell(0, 6, "    python3 frogger.py")
    pdf.ln(2)

    pdf.section_title("3. How to play")
    pdf.body_text(
        "The frog starts at the bottom on a safe green strip. The goal is to hop "
        "upward through different lanes and land on every lily pad at the top. "
        "You have 3 lives. Losing all lives ends the game."
    )
    pdf.body_text("Lane types from bottom to top:")
    pdf.bullet("Safe zones (green): no danger, catch your breath")
    pdf.bullet("Road (gray): cars drive left and right; touching one kills you")
    pdf.bullet("River (blue): you must stand on logs; open water drowns you")
    pdf.bullet("Goals (top green): lily pads; land on each one to clear the level")
    pdf.body_text(
        "Movement is grid-based. Each key press moves the frog exactly one tile. "
        "There is a short hop cooldown so you cannot move too fast."
    )

    pdf.section_title("4. Controls")
    pdf.bullet("Arrow keys or WASD: hop one tile")
    pdf.bullet("Space or Enter: start game / continue after dying")
    pdf.bullet("Close the window to quit")

    pdf.section_title("5. Scoring and levels")
    pdf.body_text(
        "You earn points every time you reach a lily pad (100 plus a small bonus "
        "based on how high up you are). When all lily pads on a level are filled, "
        "you advance to the next level. Cars and logs speed up a little each level, "
        "so it gets harder over time."
    )

    pdf.add_page()
    pdf.section_title("6. Log mechanics (important part)")
    pdf.body_text(
        "The trickiest part of Frogger is the river. I modeled it after the original "
        "game: each log has a fixed number of slots (1, 2, or 3) that are exactly "
        "one tile wide. You can only stand on those slots, not in the gap between "
        "logs or in the middle of a log where there is no slot."
    )
    pdf.body_text(
        "When you hop onto a river row, the game checks if your column lines up with "
        "a slot on any log in that row. If yes, the frog locks to that slot and rides "
        "the log as it moves. Your screen position is calculated from the log position "
        "plus the slot offset, so you move smoothly with the log instead of sliding "
        "around on your own."
    )
    pdf.body_text(
        "You die in the river if you hop into water with no log under you, or if "
        "the log carries your slot off the edge of the screen."
    )

    pdf.section_title("7. Code structure")
    pdf.body_text(
        "The game is in frogger.py as a single file (~480 lines). I used camelCase "
        "for variable names and left comments explaining what each section does."
    )
    pdf.body_text("Main classes:")
    pdf.bullet("Frog: player state, hop logic, riding logs, collision rect")
    pdf.bullet("Car: position, speed, width; wraps around when leaving the screen")
    pdf.bullet("Log: slot count, movement, slot position math")
    pdf.bullet("Lanes: creates all cars and logs, tracks lily pads, attaches frog to logs")

    pdf.section_title("8. Game loop")
    pdf.body_text(
        "The main() function runs a standard pygame loop at 60 FPS:"
    )
    pdf.bullet("1. Read keyboard events (hops, start, restart)")
    pdf.bullet("2. Update car and log positions")
    pdf.bullet("3. Update frog (check drowning, car hits)")
    pdf.bullet("4. Draw background lanes, logs, cars, frog, HUD, and overlay text")
    pdf.bullet("5. Flip the display and repeat")
    pdf.body_text(
        "Game state is tracked with a string: title, play, dead, win, or gameover. "
        "That controls what input is accepted and what gets drawn on screen."
    )

    pdf.section_title("9. Drawing")
    pdf.body_text(
        "There are no PNG or JPG files. Everything is drawn with pygame primitives: "
        "rectangles for roads, cars, and logs; ellipses for the frog and lily pads; "
        "circles for headlights and eyes. The HUD bar at the top shows score, lives, "
        "and level so it does not cover the goal row."
    )

    pdf.add_page()
    pdf.section_title("10. Project files")
    pdf.bullet("frogger.py: the entire Frogger game")
    pdf.bullet("README.md: quick start guide")
    pdf.bullet("FROGGER_PROJECT.pdf: this document")
    pdf.bullet("requirements.txt: Python dependencies")
    pdf.body_text(
        "Note: this repository also contains jun_world/, a larger story game from an "
        "earlier iteration of the project. That is separate from Frogger and is not "
        "required to run this game."
    )

    pdf.section_title("11. What I learned")
    pdf.body_text(
        "Building this taught me how to structure a game loop, handle collision detection "
        "with pygame.Rect, and attach a player to a moving platform without weird glitches. "
        "The log slot system was the hardest part. Free-floating pixel movement kept "
        "breaking until I snapped the frog to discrete slots on each log, like the "
        "real arcade game."
    )

    pdf.section_title("12. Possible improvements")
    pdf.bullet("Add sound effects and music")
    pdf.bullet("High score saved to a file")
    pdf.bullet("Turtles that dive underwater after a few seconds")
    pdf.bullet("A proper start menu with difficulty options")
    pdf.bullet("Sprite images instead of drawn shapes")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "End of document", align="C")

    out = "FROGGER_PROJECT.pdf"
    pdf.output(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    build()
