import socket
import os
import logging
import time
import datetime
import threading
import yaml
import base64
import sqlite3

logging.root.setLevel(logging.DEBUG)

gameid = 0

## ToDo ##
#
# Clean up the game networking protocol
# Find all "None" commands
#
# Make it possible to drop from a game and handle Bad file descriptor errors as a drop
#
# Currently, another player can login at the same time as he's online
#

## Done ##
#
# Remove the playerlist and player dict and object
#
# Make a initial find of user in MessageHandler and Game instead of throwing around the username
# so we use the object instead of finding the user for each function needing it
#
# Remove get.game.ball and make it automatic for each server frame
#
# Make only one sendData for consistencies sake
#
# Make some UDP connections to TCP for reliability, and structure it up!
#


class Main():
    def __init__(self):
        self.running = True
        self.cwd = os.getcwd()
        self.loadSettings()

    def start(self):
        tcp.start()
        udp.start()
        while self.running:
            time.sleep(1)

    def loadSettings(self):
        settings_file = file(self.cwd + "/settings.yaml", 'r')
        self.settings = yaml.load(settings_file)['server']


class Database():
    def __init__(self):
        self.cursor = sqlite3.connect('database.db', check_same_thread=False)
        #self.cursor = self.conn.cursor
        #self.createTable()
        #self.addUser('Johan2', "asdasd")
        #self.getUser("Johan2")
        #logging.info(self.getUser("Johan2")[1])

    def createTable(self):
        self.cursor.execute('''CREATE TABLE users
             (username text, password text, created text, lastseen text, wins int, losses int, PRIMARY KEY (username))''')

    def createUser(self, username, password):
        self.cursor.execute(
            "INSERT INTO users VALUES ('{username}','{password}','{created}','{lastseen}',0,0)".format(
                username=username,
                password=password,
                created=datetime.datetime.now(),
                lastseen=datetime.datetime.now(),
            ))
        self.cursor.commit()

    def getUser(self, username):
        response = self.cursor.execute("SELECT * FROM users WHERE username='{}'".format(username)).fetchone()
        if response:
            return response

    def closeConnection(self):
        self.conn.close()


class Games(dict):
    def __init__(self):
        pass

    def pprint(self):
        string = "Game list"
        for game in self:
            string += "\nGameID:{id} | P1:{P1} | P2:{P2}".format(id=str(games[game].id),
                                                                 P1=games[game].player1.username,
                                                                 P2=games[game].player2.username)
        logging.info(string)

    def newGame(self, game_id):
        self[str(game_id)] = Game()

    def removeGame(self, game_id):
        self[str(game_id)] = None
        del self[str(game_id)]
        logging.info("Game {id} removed".format(id=game_id))


class Clients(dict):
    def __init__(self):
        pass

    def addClient(self, client):
        self[client.username] = client

    def hashPassword(self, password):
        return password


class Client(threading.Thread):
    def __init__(self, conn, address):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.connected = True
        self.loggedin = False

        self.start()

    def run(self):
        # Listen for TCP connections
        self.sendTcpData("lobby.userinfo", "")
        # Authenticate user
        while self.connected and not self.loggedin:
            data = self.conn.recv(2048)
            if data:
                for msg in data.split(';'):
                    if msg:
                        logging.debug('TCP: Client:Unathenticated - Got:{}'.format(data))
                        self.username, action, value = str(data).split('|')
                        action = action.split('.')
                        msghandler.authentication(self.username, action, value, self)
        # The rest
        while self.connected and self.loggedin:
            data = self.conn.recv(2048)
            if data:
                response = msghandler.handle(data, self.address)
                if response:
                    self.conn.send(response)
        self.conn.close()

    def joinGame(self, username, game, playernum):
        self.game = game
        self.username = username
        self.playernum = playernum
        clients[username] = self

    def login(self, password):
        clients.addClient(self)
        self.password = password
        self.loggedin = True
        logging.info("{} logged in".format(self.username))

    def sendTcpData(self, action, value="None"):
        message = "{}|{};".format("tcp." + action, value)
        try:
            self.conn.send(message)
        except Exception as e:
            logging.error(e, exc_info=True)

        try:
            logging.debug('TCP: Client:{} - Sent:{}'.format(self.username, message))
        except AttributeError:
            logging.debug('TCP: Client:{} - Sent:{}'.format(self.address, message))

    def sendUdpData(self, action, value="None"):
        address = clients[self.username].udp_address
        message = "{}|{};".format("udp." + action, value)
        udp.sock.sendto(message, address)
        logging.debug('UDP: Client:{} - sent:{}'.format(self.username, message))


class TcpHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        self.server_address = (main.settings['ip'], main.settings['port'])
        logging.info('starting up on %s port %s' % self.server_address)
        self.sock.bind(self.server_address)

    def run(self):
        # Listening for new connections
        self.sock.listen(5)
        while True:
            # Accepting new connections
            conn, address = self.sock.accept()
            logging.info('Client {} connected!'.format(address))
            Client(conn, address)


class UdpHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        self.server_address = (main.settings['ip'], main.settings['port'])
        logging.info('starting up on %s port %s' % self.server_address)
        self.sock.bind(self.server_address)

    def run(self):
        while True:
            data, address = self.sock.recvfrom(4096)
            logging.debug(str(data) + ", " + str(address))

            logging.debug('UDP: Client:{} - Got:{}'.format(address, data))

            message = msghandler.handle(data, address)
            logging.debug(message)


class MessageHandler():
    def handle(self, data, address):
        try:
            for data in data.split(';'):
                user, action, data = data.split('|')
                action = action.split('.')
                logging.debug("{}|{}|{}".format(user, action, data))
                try:
                    if action[1] == "general":
                        return self.general(user, action, data, address)
                    elif action[1] == "game":
                        return self.game(user, action, data, address)
                    elif action[1] == "lobby":
                        return self.lobby(user, action, data, address)
                    else:
                        logging.debug("invalid request: {}|{}|{}".format(user, action, data))
                except Exception as e:
                    logging.error("{error} \n From: {adress}".format(error=e, adress=str(address)), exc_info=True)
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    def general(self, user, action, data, address):
        if action[2] == "ping":
            return "|Ping sucessfull!"

    def game(self, username, action, data, address):

        if action[2] == "padY":
            game = clients[username].game
            if clients[username].playernum == 1:
                game.brick1Y = int(data)
                try:
                    game.player2.sendUdpData("game.pad2", str(game.brick1Y))
                except AttributeError:
                    pass
            elif clients[username].playernum == 2:
                game.brick2Y = int(data)
                game.player1.sendUdpData("game.pad2", str(game.brick2Y))

        if action[2] == "initUdp":
            clients[username].udp_address = address

    def lobby(self, username, action, data, address):
        if action[2] == "logout":
            clients[username].connected = False
            logging.info("{} logged out".format(username))
        if action[2] == "quickFind":
            global gameid, playerlist, games
            try:
                # Try to join game
                game = games[str(gameid)]
                logging.info("{user} just joined a game!")
                # Cleanup needed here
                clients[username].joinGame(username, game, 2)
                game.player2 = clients[username]
                gameid += 1

            except KeyError:
                # Initialize game
                games[str(gameid)] = Game()
                game = games[str(gameid)]
                try:
                    # Define player
                    clients[username].joinGame(username, game, 1)
                    game.player1 = clients[username]
                    # Start game
                    game.start()

                    logging.info("{user} with address {address} just created a game!".format(user=username, address=address))
                except Exception as e:
                    logging.error("Could not create game :( \n{error}".format(error=e), exc_info=True)

            else:
                game = None
            #return "get.game.msg|hejhej"

    def authentication(self, username, action, data, client):
        if action[2] == "login":
            try:
                userinfo = db.getUser(username)
                if userinfo:
                    password = base64.b64decode(data)
                    hashed_password = clients.hashPassword(password)
                    correct_password = userinfo[1]
                    logging.info(correct_password)
                    if hashed_password == correct_password:
                        client.login(hashed_password)
                        client.sendTcpData("lobby.login", "True,{}".format(hashed_password))
                        logging.info("{} logged in!".format(username))
                    else:
                        client.sendTcpData("lobby.login", "False,{}".format("Invalid password"))
            except KeyError:
                client.sendTcpData("lobby.login", "False,{}".format("Invalid username"))
        if action[2] == "register":
            # Password section
            password = base64.b64decode(data)
            hashed_password = clients.hashPassword(password)
            client.password = hashed_password
            # return registration
            client.sendTcpData("lobby.register", "True")
            db.createUser(username, hashed_password)
            logging.info("{} just got registered!")
            client.sendTcpData("lobby.login", "True,{}".format(hashed_password))
            client.login(hashed_password)
        if action[2] == "logout":
            client.connected = False
            logging.info("{} closed the connection".format(client.username))


class Game(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True

        self.id = gameid

        self.ballX = 500
        self.ballY = 500
        self.ballGoingUp = False
        self.ballGoingRight = False

        self.brick1Y = 300
        self.brick2Y = 300

        self.player1 = None
        self.player2 = None

        self.pointsP1 = 0
        self.pointsP2 = 0

        self.brick2X = 1150
        self.brick2Y = 300
        self.ballFrame = 0

        self.baseSpeed = 3
        self.speed = self.baseSpeed

    def run(self):
        # First player joined!
        self.player1.sendTcpData("game.msg", "Searching for player")
        self.player1.sendTcpData("game.playerslot", "1")
        # Searching for second player
        while not self.player2:
            time.sleep(0.5)
        # Player found!
        self.player2.sendTcpData("game.playerslot", "2")
        logging.info(games.pprint())
        for s in range(5):
            # Countdown
            self.player1.sendTcpData("game.msg", "Player found! Game starts in {} seconds".format(str(5-s)))
            self.player2.sendTcpData("game.msg", "Player found! Game starts in {} seconds".format(str(5-s)))
            time.sleep(1)
        self.player1.sendTcpData("game.msg", "")
        self.player2.sendTcpData("game.msg", "")
        # Game starts!
        while self.pointsP1 < 10 and self.pointsP2 < 10:
            self.eventList()
            self.sendPads()
            time.sleep(0.01)
        # Game over
        self.player1.sendTcpData("game.msg", "Game over!")
        self.player2.sendTcpData("game.msg", "Game over!")
        time.sleep(30)
        games.removeGame(self.id)

    def sendPads(self):
        # Ball
        self.player1.sendUdpData("game.ball", str(self.ballX) + "," + str(self.ballY))
        self.player2.sendUdpData("game.ball", str(self.ballX) + "," + str(self.ballY))

    def eventList(self):
        # Speedup the ball!
        self.ballFrame += 1
        if self.ballFrame > 240:
            self.speed += 1
            self.ballFrame = 0

        # Reaches top or borrom
        if self.ballY < 1 or self.ballY > 674:
            self.ballGoingUp = not self.ballGoingUp

        # Moves ball left or right
        if self.ballGoingRight:
            self.ballX = self.ballX + self.speed*2
        else:
            self.ballX = self.ballX - self.speed*2

        # Moves ball up or down
        if self.ballGoingUp:
            self.ballY = self.ballY + self.speed
        else:
            self.ballY = self.ballY - self.speed

        # Collision detection with ball and brick

        # Right pad collision detection
        if self.ballX >= 1150 and self.ballY >= self.brick2Y and self.ballY <= self.brick2Y+100:
            self.ballGoingRight = not self.ballGoingRight
            self.player1.sendUdpData("game.collision")
            self.player2.sendUdpData("game.collision")

        # Left pad collision detection
        elif self.ballX <= 50 and self.ballY >= self.brick1Y and self.ballY <= self.brick1Y+100:
            self.ballGoingRight = not self.ballGoingRight
            self.player1.sendUdpData("game.collision")
            self.player2.sendUdpData("game.collision")

        # Score!
        if self.ballX < 0:
            self.ballX = 600
            self.ballY = 335
            self.speed = 5
            self.pointsP2 += 1
            self.player1.sendTcpData("game.score", "{},{}".format(str(self.pointsP1), str(self.pointsP2)))
            self.player2.sendTcpData("game.score", "{},{}".format(str(self.pointsP1), str(self.pointsP2)))
            logging.info("Score! Going right: " + str(self.ballGoingRight))
        elif self.ballX > 1200:
            self.ballX = 600
            self.ballY = 335
            self.speed = 5
            self.pointsP1 += 1
            self.player1.sendTcpData("game.score", "{},{}".format(str(self.pointsP1), str(self.pointsP2)))
            self.player2.sendTcpData("game.score", "{},{}".format(str(self.pointsP1), str(self.pointsP2)))
            logging.info("Score! Going right: " + str(self.ballGoingRight))

if __name__ == '__main__':
    db = Database()
    clients = Clients()
    games = Games()
    msghandler = MessageHandler()

    main = Main()
    tcp = TcpHandler()
    udp = UdpHandler()
    main.start()
