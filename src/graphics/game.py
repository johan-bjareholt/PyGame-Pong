import pygame
import widgets
import random
import logging


class Game:
    def __init__(self, screen, effects, screensize=[1200, 700],
                 loggedin=False, sensitivity=10):
        self.screen = screen
        self.effects = effects
        self.loggedin = loggedin
        self.sensitivity = sensitivity
        self.screensize = screensize

        self.player1 = 0
        self.player2 = 0

        self.playing = True

        if self.loggedin:
            self.statusMessage = "Connecting..."
        else:
            self.statusMessage = ""
        self.drawnStatusMessage = None

    class Brick(pygame.Surface):
        def __init__(self, x, size=(20, 100)):
            self.size = size
            self.W = self.size[0]
            self.H = self.size[1]
            pygame.Surface.__init__(self, size)
            self.fill((255, 255, 255))
            self.Y = 300
            self.X = x
            self.XY = (self.X, self.Y)

        def rect(self):
            return self.get_rect(topleft=(self.X, self.Y))

    class Ball(pygame.Surface):
        def __init__(self, game, size=25):
            self.ballsize = size
            pygame.Surface.__init__(self, [self.ballsize, self.ballsize])
            self.color = (254, 254, 254)
            self.fill((self.color))
            self.game = game

            self.ballDirectionVertical = 1
            self.ballDirectionHorizontal = 1

            self.goingUp = False
            self.goingRight = True

            self.c = 0

            self.X = 200
            self.Y = 332
            self.XY = (self.X, self.Y)

            self.speed = 5
            self.ballFrame = 0

        def hippie(self):
            self.color = list(self.color)
            for c in range(3):
                self.color[c] = random.randint(0, 255)
            self.color = tuple(self.color)
            #logging.debug(self.color)
            self.setColor()

        def setColor(self):
            self.fill((self.color))

        def rect(self):
            return self.get_rect(topleft=(self.X, self.Y))

        def ballEvent(self):
            self.ballFrame = self.ballFrame + 1

            # Speedup
            if self.ballFrame > 240:
                self.speed += 1
                self.ballFrame = 0

            # Reaches top or borrom
            if self.Y <= 1 or self.Y > self.game.screensize[1]-self.ballsize:
                self.goingUp = not self.goingUp

            # Moves ball left or right
            if self.goingRight:
                self.X = self.X + self.speed*2
            else:
                self.X = self.X - self.speed*2

            # Moves ball up or down
            if self.goingUp:
                self.Y = self.Y + self.speed
            else:
                self.Y = self.Y - self.speed

            # Collision detection with ball and brick
            for brick in self.game.brickRects:
                if self.rect().colliderect(brick.rect()):
                    self.goingRight = not self.goingRight
                    self.game.effects.play('boing')

            # Score!
            if self.X < 0:
                self.X = 600
                self.Y = 335
                self.speed = 5
                self.game.player2 += 1
                logging.info("Score! Going right: " + str(self.goingRight))
            elif self.X > self.game.screensize[0]:
                self.X = 600
                self.Y = 335
                self.speed = 5
                self.game.player1 += 1
                logging.info("Score! Going right: " + str(self.goingRight))

    def drawStatus(self):
        if self.drawnStatusMessage != self.statusMessage:
            self.drawnStatusMessage = self.statusMessage
            self.statusText.changeText(self.statusMessage)
        self.screen.blit(self.statusText, self.statusText.XY)

    def surfaceLoad(self):

        self.leftBrick = self.Brick(30)
        self.rightBrick = self.Brick(self.screensize[0]-50)
        self.brickRects = [self.rightBrick, self.leftBrick]
        self.pauseMenu = widgets.PauseMenu()

        self.statusText = widgets.Text(550, 600, str(self.statusMessage), 30)
        self.pointsTextP1 = widgets.Text(500, 50, str(self.player1), 50)
        self.pointsTextP2 = widgets.Text(700, 50, str(self.player2), 50)

        self.ball = self.Ball(self)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.rightBrick, (self.rightBrick.X, self.rightBrick.Y))
        self.screen.blit(self.leftBrick, (self.leftBrick.X, self.leftBrick.Y))
        self.screen.blit(self.ball, (self.ball.X, self.ball.Y))

        self.drawStatus()

        if self.pointsTextP1.text != str(self.player1):
            self.pointsTextP1.changeText(str(self.player1))
        if self.pointsTextP2.text != str(self.player2):
            self.pointsTextP2.changeText(str(self.player2))

        self.screen.blit(self.pointsTextP1, self.pointsTextP1.XY)
        self.screen.blit(self.pointsTextP2, self.pointsTextP2.XY)

        if not self.playing:
            self.screen.blit(self.pauseMenu, self.pauseMenu.XY)
