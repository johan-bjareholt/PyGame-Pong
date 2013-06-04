import pygame
import os

cwd = os.getcwd()


class Entity(pygame.Surface):
    def __init__(self, x, y, w, h, color=(255, 255, 255)):
        pygame.Surface.__init__(self, (w, h))
        self.X = x
        self.Y = y
        self.XY = (x, y)
        self.W = w
        self.H = h
        self.color = color
        if color:
            self.fill(color)

    def rect(self):
        return self.get_rect(topleft=(self.X, self.Y))


class Button(Entity):
    def __init__(self, x, y, w, h, color=(255, 255, 255), text=""):
        Entity.__init__(self, x, y, w, h, color)
        self.text = text
        self.loadFont()
        self.drawText()

    def loadFont(self):
        self.fontSize = int(self.H*0.5)
        self.XY_textStart = int((self.H/2)-(self.fontSize/2))
        self.font = pygame.font.Font(cwd+"/font/CALIBRI.TTF", self.fontSize)

    def drawText(self):
        rendered_text = self.font.render(self.text, True, pygame.color.Color(0, 0, 0))
        self.blit(rendered_text, (self.XY_textStart, self.XY_textStart))


class TextBox(Entity):
    def __init__(self, x, y, w, h, question="",
                 fg_color=(255, 255, 255), bg_color=(0, 0, 0), border=1):
        Entity.__init__(self, x, y, w, h, bg_color)
        self.border = border
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.question = question
        self.inputText = ""
        self.focus = False
        self.loadFont()
        self.draw()

    def draw(self):
        self.drawFrame()
        self.drawText()

    def loadFont(self):
        self.fontSize = int(self.H-4-(self.border*2))
        self.XY_textStart = self.border + 2
        self.font = pygame.font.Font(cwd+"/font/CALIBRI.TTF", self.fontSize)

    def drawText(self):
        text = self.question + self.inputText
        rendered_text = self.font.render(text, True, pygame.color.Color(255, 255, 255))
        #"Singleplayer", True, pygame.color.Color(0, 0, 0)
        self.blit(rendered_text, (self.XY_textStart, self.XY_textStart))

    def drawFrame(self):
        # Makes a frame
        self.fill(self.fg_color)
        bg = pygame.Surface((self.W-(self.border*2), self.H-(self.border*2)))
        bg.fill(self.bg_color)
        self.blit(bg, (self.border, self.border))

    def getKey(self, events, keys_pressed):
        for event in events:
            if event.type == pygame.KEYDOWN:
                inkey = event.key
                if inkey == pygame.K_BACKSPACE:
                    self.inputText = self.inputText[0:-1]
                elif inkey == pygame.K_RETURN:
                    self.focus = False
                elif inkey <= 127:
                    if keys_pressed[pygame.K_LSHIFT] or keys_pressed[pygame.K_RSHIFT]:
                        self.inputText += chr(inkey).capitalize()
                    else:
                        self.inputText += chr(inkey)


class PasswordBox(TextBox):
    def __init__(self, x, y, w, h, question="",
                 fg_color=(255, 255, 255), bg_color=(0, 0, 0), border=1):
        TextBox.__init__(self, x, y, w, h, question,
                         fg_color, bg_color, border)

    def drawText(self):
        asterixes = ''
        for letter in range(len(self.inputText)):
            asterixes += '*'
        text = self.question + asterixes
        rendered_text = self.font.render(text, True, pygame.color.Color(255, 255, 255))
        #"Singleplayer", True, pygame.color.Color(0, 0, 0)
        self.blit(rendered_text, (self.XY_textStart, self.XY_textStart))


class Text(pygame.Surface):
    def __init__(self, x, y, text, fontSize, color=(255, 255, 255)):
        self.X = x
        self.Y = y
        self.XY = (x, y)
        self.text = text
        self.fontColor = pygame.color.Color(color[0], color[1], color[2])
        self.fontSize = fontSize
        self.loadSurface()
        pygame.Surface.__init__(self, self.WH)
        self.draw()

    def loadSurface(self):
        self.font = pygame.font.Font(cwd+"/font/CALIBRI.TTF", self.fontSize)
        self.rendered = self.font.render(self.text, True, self.fontColor)
        self.W = self.rendered.get_size()[0]
        self.H = self.rendered.get_size()[1]
        self.WH = self.rendered.get_size()

    def draw(self):
        self.blit(self.rendered, (0, 0))

    def changeText(self, text):
        self.text = text
        self.fill((0, 0, 0))
        self.loadSurface()
        pygame.Surface.__init__(self, self.WH)
        self.draw()


class PauseMenu(Entity):
    def __init__(self):
        Entity.__init__(self, 450, 200, 300, 500, color=(100, 100, 100))
        self.loadSurface()
        self.draw()

    def loadSurface(self):
        self.leaveButton = Button(50, 100, 200, 100, (255, 255, 255), text="Leave")

    def draw(self):
        self.blit(self.leaveButton, (self.leaveButton.X, self.leaveButton.Y))
