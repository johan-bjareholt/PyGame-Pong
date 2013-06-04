import os
import logging
import threading

import pygame
# Import this when building for mac
#import pygame._view

import random

from socket import *
import base64

try:
    import android
except ImportError:
    android = None

if not android:
    import yaml

from sound import Sound
from graphics import widgets, menus, game

netlog = logging.getLogger('netlog')
inputlog = logging.getLogger('inputlog')
soundlog = logging.getLogger('soundlog')

logging.root.setLevel(logging.DEBUG)
netlog.setLevel(logging.DEBUG)
inputlog.setLevel(logging.INFO)
soundlog.setLevel(logging.INFO)

#
# Multiplayer Pong!
#
# Made by Johan Bjareholt
#


class Main():
    def __init__(self):
        self.running = True
        self.inMenu = True
        self.inGame = False
        self.loggedin = False
        self.mode = "singleplayer"
        self.cwd = os.getcwd()
        logging.info(self.cwd)
        self.loadSettings()

    def run(self):
        pygame.init()
        self.load()
        self.gameinput = {"singleplayer": input.playerSplitScreen, "multiplayer": input.playerOnline}

        self.loadMenu()
        gfx.menu.draw()
        while self.running:
            if android:
                if android.check_pause():
                    android.wait_for_resume()
            input.general()
            if not self.inGame:
                input.inMenu(gfx.menu.location)
                gfx.menu.draw()
            else:
                input.inGame()
                self.gameinput[self.mode]()
                if self.settings['game']['hippie']:
                    gfx.game.ball.hippie()
                if gfx.game.playing:
                    if self.mode == "singleplayer":
                        gfx.game.ball.ballEvent()
                gfx.game.draw()

            gfx.newFrame()

        self.quit()

    def quit(self):
        if self.loggedin:
            net.lobby.sendData("lobby.logout")
        pygame.quit()

    def loadSettings(self):
        if android:
            self.settings = {'screen': {'fullscreen': True, 'resolution': [1200, 700]},
                             'host': {'ip': 'ngenia.net', 'port': 10000},
                             'audio': {'volume': 7, 'enabled': True},
                             'game': {'sensitivity': 12, 'hippie': False},
                             'user': {'password': '', 'name': ''}}
        else:
            settings_file = file(self.cwd + "/settings.yaml", 'r')
            self.settings = yaml.load(settings_file)['client']
            logging.info(self.settings)
        if self.settings['game']['hippie']:
            logging.info("HIPPIE!")

    def load(self):
        if android:
            android.init()
            android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
        self.clock = pygame.time.Clock()
        gfx.fontSmall = pygame.font.Font(main.cwd+"/font/CALIBRI.TTF", 30)
        gfx.font = pygame.font.Font(main.cwd+"/font/CALIBRI.TTF", 50)
        gfx.fontBig = pygame.font.Font(main.cwd+"/font/CALIBRI.TTF", 75)

    def loadMenu(self):
        gfx.menu = gfx.Menu(gfx.screen)
        gfx.menu.surfaceLoad()

    def loadGame(self):
        gfx.game = game.Game(gfx.screen,
                             sound.effects,
                             sensitivity=int(main.settings['game']['sensitivity']),
                             screensize=(gfx.X, gfx.Y),
                             loggedin=main.loggedin)
        gfx.game.surfaceLoad()


class Graphics():
    def __init__(self):
        self.X, self.Y = main.settings['screen']['resolution']
        if main.settings['screen']['fullscreen']:
            self.screen = pygame.display.set_mode((self.X, self.Y), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.X, self.Y))

    class Menu:
        def __init__(self, parent):
            gfx.screen = parent

            self.menus = {}
            for menu in ["main", "multiplayer", "login", "loginConnect"]:
                self.menus[menu] = {'loaded': False}

            self.location = "main"

        def surfaceLoad(self):
            self.pongText = gfx.font.render("Pong!", True,
                                            pygame.color.Color(255, 255, 255))

        def draw(self):
            gfx.screen.fill((0, 0, 0))
            gfx.screen.blit(self.pongText, ((gfx.X/2)-75, 50))

            # Main menu
            if self.location == "main":
                if self.menus[self.location]['loaded']:
                    self.mainmenu.update()
                else:
                    self.mainmenu = menus.MainMenu(gfx.screen, username=user)
                    self.menus[self.location]['loaded'] = True

            # Multiplayer logged in screen for joining games
            elif self.location == "multiplayer":
                if self.menus[self.location]['loaded']:
                    self.multiplayermenu.update()
                else:
                    self.multiplayermenu = menus.MultiplayerMenu(gfx.screen, "main", username=user)
                    self.menus[self.location]['loaded'] = True

            # Login prompt
            elif self.location == "login":
                if self.menus[self.location]['loaded']:
                    self.loginmenu.update()
                else:
                    self.loginmenu = menus.LoginMenu(gfx.screen, "main", username=user)
                    self.menus[self.location]['loaded'] = True

            # Logging in and connecting to server load menu
            elif self.location == "loginConnect":
                if self.menus[self.location]['loaded']:
                    self.loginconnectmenu.update()
                else:
                    self.loginconnectmenu = menus.LoadingMenu(gfx.screen, "main", username=user)
                    self.menus[self.location]['loaded'] = True

    def newFrame(self):
        main.clock.tick(60)
        pygame.display.flip()


class Input():
    def __init__(self):
        self.newly_pressed = {}

    def general(self):
        pygame.event.pump()
        self.events = pygame.event.get()
        inputlog.debug(self.events)
        self.pressed = pygame.key.get_pressed()
        #logging.info(events)
        for event in self.events:
            if event.type == pygame.QUIT:
                main.running = False

    def inMenu(self, location):
        if location == "main":
            menu = gfx.menu.mainmenu
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu.startButton.rect().collidepoint(pygame.mouse.get_pos()):
                        logging.info("You started singleplayer! ")
                        main.loadGame()
                        main.inGame = True
                        main.inMenu = False
                        sound.music.fadeout(3000)
                    # Start multiplayer
                    if menu.multiplayerButton.rect().collidepoint(pygame.mouse.get_pos()):
                        if main.loggedin:
                            gfx.menu.location = "multiplayer"
                            gfx.menu.draw()
                        else:
                            gfx.menu.location = "login"
                            gfx.menu.draw()
                    # Quitbutton
                    if menu.backButton.rect().collidepoint(pygame.mouse.get_pos()):
                        main.running = False

        elif location == "multiplayer":
            menu = gfx.menu.multiplayermenu
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Start multiplayer
                    if menu.quickFindButton.rect().collidepoint(pygame.mouse.get_pos()):
                        logging.info("You started multiplayer! ")
                        net.game.start()
                        net.game.sendData("game.initUdp", "")
                        net.lobby.sendData("lobby.quickFind", "")
                        main.loadGame()
                        main.inGame = True
                        game.playing = True
                        main.inMenu = False
                        sound.music.fadeout(3000)

                    # Backbutton
                    if menu.backButton.rect().collidepoint(pygame.mouse.get_pos()):
                        gfx.menu.location = menu.parent
                        gfx.menu.draw()

        elif location == "login":
            menu = gfx.menu.loginmenu
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Start multiplayer
                    global user, password
                    if menu.loginButton.rect().collidepoint(pygame.mouse.get_pos()):
                        if not menu.usernameBox.inputText or not menu.passwordBox.inputText:
                            pass
                        else:
                            gfx.menu.location = "loginConnect"
                            gfx.menu.draw()
                            password = menu.passwordBox.inputText
                            b64ed_passwd = base64.b64encode(password)
                            # Final variables
                            user = menu.usernameBox.inputText
                            password = b64ed_passwd
                            net.lobby.register = False
                            net.lobby.start()
                    elif menu.registerButton.rect().collidepoint(pygame.mouse.get_pos()):
                            gfx.menu.location = "loginConnect"
                            gfx.menu.draw()
                            password = menu.passwordBox.inputText
                            b64ed_passwd = base64.b64encode(password)
                            # Final variables
                            user = menu.usernameBox.inputText
                            password = b64ed_passwd
                            net.lobby.register = True
                            net.lobby.start()
                    # Focus username textbox
                    if menu.usernameBox.rect().collidepoint(pygame.mouse.get_pos()):
                        menu.usernameBox.focus = True
                        menu.passwordBox.focus = False
                    if menu.passwordBox.rect().collidepoint(pygame.mouse.get_pos()):
                        menu.passwordBox.focus = True
                        menu.usernameBox.focus = False
                    # Backbutton
                    if menu.backButton.rect().collidepoint(pygame.mouse.get_pos()):
                        gfx.menu.location = menu.parent
                        gfx.menu.draw()
            # Handle username textbox input
            if menu.usernameBox.focus:
                menu.usernameBox.getKey(input.events, self.pressed)
                menu.usernameBox.draw()
                gfx.menu.draw()
            elif menu.passwordBox.focus:
                menu.passwordBox.getKey(input.events, self.pressed)
                menu.passwordBox.draw()
                gfx.menu.draw()

        elif location == "loginConnect":
            menu = gfx.menu.loginconnectmenu
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu.backButton.rect().collidepoint(pygame.mouse.get_pos()):
                        # Killing thread
                        net.lobby.running = False
                        del net.lobby
                        net.lobby = net.TcpHandler()
                        # Going back to main menu
                        gfx.menu.location = menu.parent
                        gfx.menu.draw()

    def inGame(self):
        for event in self.events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gfx.game.playing = not gfx.game.playing
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not gfx.game.playing:
                    if gfx.game.pauseMenu.leaveButton.rect().collidepoint((pygame.mouse.get_pos()[0]-gfx.game.pauseMenu.X,
                                                                           pygame.mouse.get_pos()[1]-gfx.game.pauseMenu.Y)):
                        gfx.menu.draw()
                        main.inGame = False

    def player1(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_w] and gfx.game.leftBrick.Y > 0:
            gfx.game.leftBrick.Y -= gfx.game.sensitivity
        if key[pygame.K_s] and gfx.game.leftBrick.Y < gfx.Y-gfx.game.leftBrick.H:
            gfx.game.leftBrick.Y += gfx.game.sensitivity

    def player2(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_o] and gfx.game.rightBrick.Y > 0:
            gfx.game.rightBrick.Y -= gfx.game.sensitivity
        if key[pygame.K_l] and gfx.game.rightBrick.Y < gfx.Y-gfx.game.rightBrick.H:
            gfx.game.rightBrick.Y += gfx.game.sensitivity

    def playerSplitScreen(self):
        if gfx.game.playing:
            self.player1()
            self.player2()

    def playerOnline(self):
        key = pygame.key.get_pressed()
        if net.game.playerslot == 1:
            if key[pygame.K_w] and gfx.game.leftBrick.Y > 0:
                gfx.game.leftBrick.Y -= gfx.game.sensitivity
                net.game.sendData("game.padY", gfx.game.leftBrick.Y)
            elif key[pygame.K_s] and gfx.game.leftBrick.Y < 600:
                gfx.game.leftBrick.Y += gfx.game.sensitivity
                net.game.sendData("game.padY", gfx.game.leftBrick.Y)
        else:
            if key[pygame.K_w] and gfx.game.rightBrick.Y > 0:
                gfx.game.rightBrick.Y -= gfx.game.sensitivity
                net.game.sendData("game.padY", gfx.game.rightBrick.Y)
            elif key[pygame.K_s] and gfx.game.rightBrick.Y < 600:
                gfx.game.rightBrick.Y += gfx.game.sensitivity
                net.game.sendData("game.padY", gfx.game.rightBrick.Y)


class Networking():
    #
    # userinfo|action|data
    #
    # Userinfo
    # name,dahash
    #
    # Actions
    # "method"."category"."value"
    #

    def __init__(self):
        self.msghandler = self.MessageHandler()
        self.game = self.UdpHandler()
        self.lobby = self.TcpHandler()
        global user, address
        user = None
        address = (main.settings['host']['ip'],
                   main.settings['host']['port'])

    class TcpHandler(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = "TcpConnection"
            self.daemon = True
            self.running = True
            self.register = False
            self.socket = socket(AF_INET, SOCK_STREAM)
            #self.user = "Johan" + str(random.randint(0, 100))

        def run(self):
            netlog.info("Starting tcp socket!")
            self.socket.connect(address)

            # Login section
            if not self.register:
                net.lobby.sendData("lobby.login", password)
            elif self.register:
                net.lobby.sendData("lobby.register", password)
                self.register = False
            while not main.loggedin and main.running and self.running:
                # Recv action
                recv_data = self.socket.recv(2048)
                data = recv_data.split('|')
                netlog.debug("TCP:Got: " + recv_data)
                # Message Handler
                response = net.msghandler.handleAuthentication(data)
                if response:
                    self.sendData(response)

            # Lobby and game section
            while main.loggedin and main.running and self.running:
                # Recv action
                recv_data = self.socket.recv(2048)
                if recv_data:
                    netlog.debug("TCP:Got: " + recv_data)

                    # Message Handler
                    for message in recv_data.split(';'):
                        data = message.split('|')
                        response = net.msghandler.handle(data)
                        if response:
                            self.sendData(response)

            self.socket.close()

        def sendData(self, action, data=None):
            data = "{user}|{action}|{data};".format(user=user, action="tcp."+action, data=data)
            self.socket.send(data)
            netlog.debug("TCP:Sent: " + data)

    class UdpHandler(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.name = "Connection"
            self.daemon = True
            self.running = True

            self.socket = socket(AF_INET, SOCK_DGRAM)

            #user = "Johan" + str(random.randint(0, 100))
            self.playerslot = None

        def run(self):
            netlog.info("Starting udp socket!")
            main.mode = "multiplayer"
            while main.running:
                recv_data, addr = self.socket.recvfrom(2048)
                if recv_data:
                    netlog.debug("UDP:Got: " + recv_data)

                    # Message Handler
                    for message in recv_data.split(';'):
                        data = message.split('|')
                        response = net.msghandler.handle(data)
                        if response:
                            self.sendData(response)

        def sendData(self, action, data=" "):
            data = "{user}|{action}|{data};".format(user=user, action="udp."+action, data=data)
            self.socket.sendto(data, address)
            netlog.debug("UDP:Sent: " + data)

    class MessageHandler():
        def handle(self, data):
            try:
                action = data[0]
                protocol, category, variable = action.split('.')
                value = data[1]
                if category == "game":
                    self.game(protocol, variable, value)
                elif category == "lobby":
                    self.lobby(protocol, variable, value)
            except Exception as e:
                netlog.error("Could not parse: {} \nError: {}".format(data, e), exc_info=True)

        def game(self, protocol, variable, value):
            # UDP
            if protocol == "udp":
                if variable == "ball":
                    value = str(value).split(',')
                    gfx.game.ball.X = int(value[0])
                    gfx.game.ball.Y = int(value[1])
                elif variable == "pad2":
                    if net.game.playerslot == 1:
                        gfx.game.rightBrick.Y = int(value)
                    elif net.game.playerslot == 2:
                        gfx.game.leftBrick.Y = int(value)
            # TCP
            elif protocol == "tcp":
                if variable == "msg":
                    gfx.game.statusMessage = str(value)
                elif variable == "score":
                    value = value.split(',')
                    gfx.game.player1 = value[0]
                    gfx.game.player2 = value[1]
                elif variable == "playerslot":
                    net.game.playerslot = int(value)
            if variable == "collision":
                sound.playSound('boing')

        def lobby(self, protocol, variable, value):
            if variable == "userinfo":
                if not register:
                    net.lobby.sendData("lobby.login", b64ed_passwd)
                elif register:
                    net.lobby.sendData("lobby.register", b64ed_passwd)
            if variable == "login":
                netlog.debug(value.split(',')[0])
                if value.split(',')[0] == "True":
                    gfx.menu.location = "multiplayer"
                    gfx.menu.draw()
                    main.loggedin = True
                else:
                    gfx.menu.loginconnectmenu.setMessage(value.split(',')[1])
                    gfx.menu.draw()

        def handleAuthentication(self, data):
            try:
                action = data[0]
                protocol, category, variable = action.split('.')
                value = data[1]
                self.authentication(protocol, variable, value)
            except Exception as e:
                netlog.error("Could not parse: {} \nError: {}".format(data, e), exc_info=True)

        def authentication(self, protocol, variable, value):
            if variable == "login":
                netlog.debug(value.split(',')[0])
                if value.split(',')[0] == "True":
                    gfx.menu.location = "multiplayer"
                    gfx.menu.draw()
                    main.loggedin = True
                else:
                    gfx.menu.loginconnectmenu.setMessage(value.split(',')[1])
                    gfx.menu.draw()


if __name__ == '__main__' or __name__ == 'client':
    main = Main()
    gfx = Graphics()
    input = Input()
    sound = Sound(soundlog, main.settings)
    net = Networking()
    main.run()
