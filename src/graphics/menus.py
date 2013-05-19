import widgets
import pygame
import os
import yaml
#import logging

global cwd, font
cwd = os.getcwd()
pygame.font.init()
font = pygame.font.Font(cwd+"/font/CALIBRI.TTF", 50)
settings_file = file(cwd + "/settings.yaml", 'r')
settings = yaml.load(settings_file)['client']
screensize = settings['screen']['resolution']
#screensize = (1200, 700)


class Menu():
    def __init__(self, screen, parent=False, username=False):
        self.screen = screen
        self.parent = parent
        self.username = username
        self.load()
        if self.parent:
            self.backButton = widgets.Button(25, screensize[1]-75, 100, 50, (255, 255, 255), text="Back")
        if self.username:
            self.loggedinText = widgets.Text(800, 650, "Logged in as "+self.username, 30)
        self.update()

    def load(self):
        pass

    def drawGeneral(self):
        if self.parent:
            self.screen.blit(self.backButton, (self.backButton.X, self.backButton.Y))
        if self.username:
            self.screen.blit(self.loggedinText, self.loggedinText.XY)

    def draw(self):
        pass

    def update(self):
        if self.parent:
            self.drawGeneral()
        self.draw()


class MainMenu(Menu):
    def load(self):
        self.startButton = widgets.Button((screensize[0]/2)-(300/2), 200, 300, 100, (255, 255, 255), text="Singleplayer")
        self.multiplayerButton = widgets.Button((screensize[0]/2)-(300/2), 350, 300, 100, (255, 255, 255), text="Multiplayer")
        self.backButton = widgets.Button(25, screensize[1]-75, 100, 50, (255, 255, 255), text="Quit")

    def draw(self):
        # Blit to screen
        self.screen.blit(self.startButton, (self.startButton.X, self.startButton.Y))
        self.screen.blit(self.multiplayerButton, (self.multiplayerButton.X, self.multiplayerButton.Y))
        self.screen.blit(self.backButton, (self.backButton.X, self.backButton.Y))


class MultiplayerMenu(Menu):
    def load(self):
        # Initialize items
        self.quickFindButton = widgets.Button((screensize[0]/2)-(300/2), 200, 300, 100, (255, 255, 255), text="Quick find")

    def draw(self):
        # Blit to screen
        self.screen.blit(self.quickFindButton, (self.quickFindButton.X, self.quickFindButton.Y))


class LoginMenu(Menu):
    def load(self):
        # Initialize items
        self.loginButton = widgets.Entity((screensize[0]/2)-(200+50), 400, 200, 100, (255, 255, 255))
        self.registerButton = widgets.Button((screensize[0]/2)-(-50), 400, 200, 100, (255, 255, 255), text="Signup")
        self.usernameBox = widgets.TextBox((screensize[0]/2)-(500/2), 200, 500, 40, question="Username: ")
        self.passwordBox = widgets.PasswordBox((screensize[0]/2)-(500/2), self.usernameBox.Y + self.usernameBox.H + 20, 500, 40, question="Password: ")

        # Give items attributes and sub items
        self.loginButtonText = font.render("Login", True, pygame.color.Color(0, 0, 0))
        self.loginButton.blit(self.loginButtonText, (25, 25))

    def draw(self):
        # Blit to screen
        self.screen.blit(self.loginButton, (self.loginButton.X, self.loginButton.Y))
        self.screen.blit(self.registerButton, (self.registerButton.X, self.registerButton.Y))
        self.screen.blit(self.usernameBox, (self.usernameBox.X, self.usernameBox.Y))
        self.screen.blit(self.passwordBox, (self.passwordBox.X, self.passwordBox.Y))


class LoadingMenu(Menu):
    def load(self):
        self.messageXY = (300, 300)
        self.setMessage("Connecting to server...")

    def setMessage(self, message):
        self.message = message
        self.loadingMessage = font.render(self.message, True, pygame.color.Color(255, 255, 255))
        self.screen.blit(self.loadingMessage, self.messageXY)

    def draw(self):
        # Blit to screen
        self.screen.blit(self.loadingMessage, self.messageXY)
