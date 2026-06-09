#!/usr/bin/env python3
# frogger game for class project
# run with: python3 frogger.py
# you need pygame installed first (pip install pygame)

import random
import sys

try:
    import pygame
except ImportError:
    sys.exit("need pygame - run: pip install pygame")

# ----- screen setup -----
tileSize = 40
colCount = 16
rowCount = 17
hudHeight = 44
screenWidth = colCount * tileSize
screenHeight = hudHeight + rowCount * tileSize
frameRate = 60

# colors i picked for the different lanes
colorBg = (24, 32, 48)
colorSafe = (34, 90, 54)
colorWater = (30, 70, 120)
colorRoad = (48, 48, 56)
colorGoal = (70, 140, 90)
colorFrog = (60, 200, 80)
colorFrogEye = (240, 250, 255)
carColorList = [(200, 60, 60), (220, 160, 40), (90, 120, 220), (180, 80, 180)]
colorLog = (120, 80, 40)
colorText = (235, 240, 245)

# gameplay numbers
startLives = 3
hopCooldownTime = 0.14
startRow = rowCount - 2
goalRows = {1, 2}
safeRows = {0, 3, 6, 9, 12, 15, startRow}
waterRows = {4, 5, 7, 8, 10, 11}
roadRows = {13, 14}


def rowY(row):
    # push rows down so the hud bar doesn't cover the top lane
    return hudHeight + row * tileSize


def colX(col):
    # center of a grid column in pixels
    return col * tileSize + tileSize // 2


class Frog:
    # the player frog - moves on a grid and rides logs in the river

    def __init__(self):
        self.reset()
        self.cooldown = 0.0

    def reset(self):
        self.col = colCount // 2
        self.row = startRow
        self.rideLog = None
        self.rideSlot = None

    @property
    def centerX(self):
        # if we're on a log, stick to that log's slot (like real frogger)
        if self.rideLog is not None:
            return self.rideLog.slotCenterX(self.rideSlot)
        return colX(self.col)

    @property
    def rect(self):
        spriteSize = tileSize - 14
        half = spriteSize // 2
        centerY = rowY(self.row) + tileSize // 2
        centerX = self.centerX
        return pygame.Rect(int(centerX - half), int(centerY - half), spriteSize, spriteSize)

    def detachFromLog(self):
        self.rideLog = None
        self.rideSlot = None

    def tryHop(self, deltaCol, deltaRow, lanes):
        # one hop at a time, frogger style
        if self.cooldown > 0:
            return None
        newCol, newRow = self.col + deltaCol, self.row + deltaRow
        if not (0 <= newCol < colCount and 0 <= newRow < rowCount):
            return None
        self.col, self.row = newCol, newRow
        self.detachFromLog()
        self.cooldown = hopCooldownTime

        # made it to a lily pad at the top
        if newRow in goalRows and lanes.markGoal(newRow, newCol):
            return "goal"

        # river rows - you HAVE to land on a log slot or you die
        if newRow in waterRows:
            if not lanes.attachFrogToLog(self, newCol, newRow):
                return "drown"
        return None

    def update(self, deltaTime, lanes):
        self.cooldown = max(0.0, self.cooldown - deltaTime)

        if self.row in waterRows:
            if self.rideLog is None:
                return "drown"
            log = self.rideLog
            centerX = log.slotCenterX(self.rideSlot)
            # fell off the side of the screen while riding
            if centerX < -tileSize or centerX > screenWidth + tileSize:
                return "drown"
            if not log.slotOnScreen(self.rideSlot):
                return "drown"
            self.col = max(0, min(colCount - 1, round((centerX - tileSize / 2) / tileSize)))
        else:
            self.detachFromLog()

        # cars run you over on the road
        if self.row in roadRows:
            for car in lanes.carsInRow(self.row):
                if self.rect.colliderect(car.rect):
                    return "squash"
        return None


class Car:
    # cars driving left or right on the road lanes

    def __init__(self, row, startX, speed, color):
        self.row = row
        self.x = startX
        self.baseSpeed = speed
        self.speed = speed
        self.color = color
        self.carWidth = random.choice([tileSize * 1.6, tileSize * 2.2, tileSize * 2.8])

    @property
    def rect(self):
        topY = rowY(self.row) + 5
        return pygame.Rect(int(self.x), topY, int(self.carWidth), tileSize - 10)

    def update(self, deltaTime):
        self.x += self.speed * deltaTime
        # wrap around when they drive off screen
        if self.speed > 0 and self.x > screenWidth + 20:
            self.x = -self.carWidth - 20
        elif self.speed < 0 and self.x < -self.carWidth - 20:
            self.x = screenWidth + 20


class Log:
    # logs in the river - each one has 1 to 3 slots the frog can stand on

    def __init__(self, row, startX, speed, slotCount):
        self.row = row
        self.x = float(startX)
        self.baseVx = speed
        self.vx = speed
        self.slots = max(1, min(3, slotCount))

    @property
    def length(self):
        return self.slots * tileSize

    @property
    def rect(self):
        return pygame.Rect(int(self.x), rowY(self.row) + 5, int(self.length), tileSize - 10)

    def slotCenterX(self, slotIndex):
        return self.x + slotIndex * tileSize + tileSize / 2

    def slotOnScreen(self, slotIndex):
        leftEdge = self.x + slotIndex * tileSize
        return leftEdge + tileSize > 0 and leftEdge < screenWidth

    def slotForCol(self, col):
        # checks if the frog's grid column lines up with a slot on this log
        pixelX = colX(col)
        for slotIndex in range(self.slots):
            leftEdge = self.x + slotIndex * tileSize
            if leftEdge <= pixelX < leftEdge + tileSize:
                return slotIndex
        return None

    def update(self, deltaTime):
        self.x += self.vx * deltaTime
        if self.vx > 0 and self.x > screenWidth + 30:
            self.x = -self.length - 30
        elif self.vx < 0 and self.x < -self.length - 30:
            self.x = screenWidth + 30


class Lanes:
    # holds all the cars and logs and keeps track of goals

    def __init__(self):
        self.cars = []
        self.logs = []
        self.goals = {(r, c): False for r in goalRows for c in range(2, colCount - 2, 2)}
        self.spawnTraffic()

    def spawnTraffic(self):
        # road lanes at the bottom
        for row in roadRows:
            carCount = 3 + (row % 2)
            laneSpeed = 95 if row == 13 else -110
            spacing = screenWidth / carCount
            for i in range(carCount):
                self.cars.append(Car(
                    row, i * spacing + random.uniform(0, 40), laneSpeed,
                    random.choice(carColorList),
                ))

        # river lanes in the middle - logs with random slot counts
        riverSpecs = [
            (4, 70), (5, -85), (7, 95), (8, -75), (10, 80), (11, -100),
        ]
        for row, laneSpeed in riverSpecs:
            logCount = 2
            spacing = screenWidth / logCount
            for i in range(logCount):
                slotCount = random.choice([1, 2, 3])
                self.logs.append(Log(row, i * spacing, laneSpeed, slotCount))

    def resetGoals(self):
        for key in self.goals:
            self.goals[key] = False

    def markGoal(self, row, col):
        # goals take up 2 columns, snap to even col
        snappedCol = col if col % 2 == 0 else col - 1
        key = (row, snappedCol)
        if key in self.goals and not self.goals[key]:
            self.goals[key] = True
            return True
        return False

    def allGoalsFilled(self):
        return all(self.goals.values())

    def carsInRow(self, row):
        return [car for car in self.cars if car.row == row]

    def logsOnRow(self, row):
        return [log for log in self.logs if log.row == row]

    def attachFrogToLog(self, frog, col, row):
        # find a log under the frog and lock them to a slot
        for log in self.logsOnRow(row):
            slotIndex = log.slotForCol(col)
            if slotIndex is not None:
                frog.rideLog = log
                frog.rideSlot = slotIndex
                return True
        return False

    def update(self, deltaTime):
        for car in self.cars:
            car.update(deltaTime)
        for log in self.logs:
            log.update(deltaTime)


def drawHudBar(screen, font, score, lives, level):
    pygame.draw.rect(screen, (18, 22, 32), (0, 0, screenWidth, hudHeight))
    pygame.draw.line(screen, (60, 68, 88), (0, hudHeight - 1), (screenWidth, hudHeight - 1))
    hudText = font.render(f"Score {score}   Lives {lives}   Level {level}", True, colorText)
    screen.blit(hudText, (12, (hudHeight - hudText.get_height()) // 2))


def drawBackground(screen):
    for row in range(rowCount):
        topY = rowY(row)
        if row in goalRows:
            laneColor = colorGoal
        elif row in waterRows:
            laneColor = colorWater
        elif row in roadRows:
            laneColor = colorRoad
        elif row in safeRows:
            laneColor = colorSafe
        else:
            laneColor = colorBg
        pygame.draw.rect(screen, laneColor, (0, topY, screenWidth, tileSize))
        # dashed line down the middle of road lanes
        if row in roadRows:
            for x in range(0, screenWidth, tileSize * 2):
                pygame.draw.rect(screen, (70, 70, 78), (x, topY + tileSize // 2 - 2, tileSize, 4))


def drawCar(screen, car):
    carRect = car.rect
    goingRight = car.speed > 0
    bodyRect = carRect.inflate(-2, -6)
    pygame.draw.rect(screen, car.color, bodyRect, border_radius=4)
    pygame.draw.rect(screen, (20, 20, 24), bodyRect, 2, border_radius=4)
    # just headlights, kept it simple
    if goingRight:
        headlightX = bodyRect.right - 4
    else:
        headlightX = bodyRect.x + 4
    pygame.draw.circle(screen, (255, 245, 180), (headlightX, bodyRect.centery - 4), 3)
    pygame.draw.circle(screen, (255, 245, 180), (headlightX, bodyRect.centery + 4), 3)


def drawLog(screen, log):
    pygame.draw.rect(screen, colorLog, log.rect, border_radius=6)
    pygame.draw.rect(screen, (90, 60, 30), log.rect, 2, border_radius=6)
    # little lines so you can see the frog slots
    for slotIndex in range(1, log.slots):
        lineX = int(log.x + slotIndex * tileSize)
        pygame.draw.line(screen, (70, 48, 24), (lineX, log.rect.top + 3), (lineX, log.rect.bottom - 3), 2)


def drawGoals(screen, lanes):
    for (row, col), isFilled in lanes.goals.items():
        padX, padY = col * tileSize + 4, rowY(row) + 4
        padRect = pygame.Rect(padX, padY, tileSize * 2 - 8, tileSize - 8)
        if isFilled:
            pygame.draw.ellipse(screen, (100, 220, 130), padRect)
        else:
            pygame.draw.ellipse(screen, (50, 110, 70), padRect, 2)


def drawFrog(screen, frog):
    frogRect = frog.rect
    centerX = frogRect.centerx
    pygame.draw.ellipse(screen, colorFrog, frogRect)
    pygame.draw.ellipse(screen, (40, 120, 55), frogRect, 2)
    # frog faces up toward the goals
    pygame.draw.circle(screen, colorFrogEye, (centerX - 7, frogRect.top + 9), 4)
    pygame.draw.circle(screen, colorFrogEye, (centerX + 7, frogRect.top + 9), 4)
    pygame.draw.circle(screen, (20, 40, 30), (centerX - 7, frogRect.top + 10), 2)
    pygame.draw.circle(screen, (20, 40, 30), (centerX + 7, frogRect.top + 10), 2)
    pygame.draw.ellipse(screen, (45, 130, 60), (centerX - 4, frogRect.top + 14, 8, 5))


def drawCenterText(screen, bigFont, smallFont, title, subtitle=""):
    titleSurf = bigFont.render(title, True, colorText)
    screen.blit(titleSurf, titleSurf.get_rect(center=(screenWidth // 2, screenHeight // 2 - 20)))
    if subtitle:
        subSurf = smallFont.render(subtitle, True, (180, 190, 200))
        screen.blit(subSurf, subSurf.get_rect(center=(screenWidth // 2, screenHeight // 2 + 28)))


def levelSpeedMult(level):
    # cars and logs get faster each level
    return 1.0 + (level - 1) * 0.12


def main():
    pygame.init()
    pygame.display.set_caption("Frogger")
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()
    uiFont = pygame.font.SysFont("menlo,consolas,monospace", 20)
    titleFont = pygame.font.SysFont("menlo,consolas,monospace", 42, bold=True)

    frog = Frog()
    lanes = Lanes()
    score = 0
    lives = startLives
    level = 1
    gameState = "title"  # title, play, dead, win, or gameover
    deadTimer = 0.0

    # ----- main loop -----
    while True:
        deltaTime = clock.tick(frameRate) / 1000.0
        speedMult = levelSpeedMult(level)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if gameState == "title" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    gameState = "play"

                elif gameState == "dead" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    gameState = "play"
                    frog.reset()

                elif gameState == "win" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    gameState = "play"
                    frog.reset()

                elif gameState == "gameover" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    score, lives, level = 0, startLives, 1
                    frog = Frog()
                    lanes = Lanes()
                    gameState = "title"

                elif gameState == "play":
                    hopResult = None
                    if event.key in (pygame.K_UP, pygame.K_w):
                        hopResult = frog.tryHop(0, -1, lanes)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        hopResult = frog.tryHop(0, 1, lanes)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        hopResult = frog.tryHop(-1, 0, lanes)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        hopResult = frog.tryHop(1, 0, lanes)

                    if hopResult in ("goal", "drown"):
                        if hopResult == "goal":
                            score += 100 + frog.row * 10
                            frog.reset()
                            if lanes.allGoalsFilled():
                                level += 1
                                lanes.resetGoals()
                                for car in lanes.cars:
                                    car.baseSpeed *= 1.08
                                for log in lanes.logs:
                                    log.baseVx *= 1.08
                                gameState = "win"
                        else:
                            lives -= 1
                            frog.reset()
                            if lives <= 0:
                                gameState = "gameover"
                            else:
                                gameState = "dead"
                                deadTimer = 1.2

        if gameState == "play":
            for car in lanes.cars:
                car.speed = car.baseSpeed * speedMult
            for log in lanes.logs:
                log.vx = log.baseVx * speedMult

            lanes.update(deltaTime)
            deathReason = frog.update(deltaTime, lanes)
            if deathReason:
                lives -= 1
                frog.reset()
                if lives <= 0:
                    gameState = "gameover"
                else:
                    gameState = "dead"
                    deadTimer = 1.2

        elif gameState == "dead":
            deadTimer -= deltaTime
            if deadTimer <= 0:
                gameState = "play"

        # ----- drawing -----
        drawBackground(screen)
        drawGoals(screen, lanes)
        for log in lanes.logs:
            drawLog(screen, log)
        for car in lanes.cars:
            drawCar(screen, car)

        if gameState in ("play", "dead", "win"):
            drawFrog(screen, frog)
            drawHudBar(screen, uiFont, score, lives, level)
        elif gameState != "title":
            drawHudBar(screen, uiFont, score, lives, level)

        if gameState == "title":
            drawCenterText(screen, titleFont, uiFont, "FROGGER",
                           "Arrow keys / WASD to hop  ·  Space to start")
        elif gameState == "dead":
            drawCenterText(screen, titleFont, uiFont, "SPLAT!", "Press Space")
        elif gameState == "win":
            drawCenterText(screen, titleFont, uiFont, f"Level {level - 1} clear!",
                           "Press Space for next level")
        elif gameState == "gameover":
            drawCenterText(screen, titleFont, uiFont, "GAME OVER",
                           f"Score {score}  ·  Space to retry")

        pygame.display.flip()


if __name__ == "__main__":
    main()
