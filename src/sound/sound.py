import pygame
import logging
import os

cwd = os.getcwd()

class Sound:
    def __init__(self, soundlog, settings):
        pygame.mixer.init()
        self.channels = {}
        global volume, log
        log = soundlog
        if settings['audio']['enabled']:
            volume = float(settings['audio']['volume'])/10
        else:
            volume = 0
        self.effects = Effects()
        self.music = Music()
        try:
            self.music.load("menuMusic", "menu.ogg")
            self.music.play("menuMusic")
            self.effects.load("boing", "boing.ogg")
        except Exception as e:
            logging.info(e, exc_info=True)


class Music:
    def __init__(self):
        self.song = pygame.mixer.music

    def load(self, name, location):
        log.debug("Loading music song: {name}, from {location}".format(name=name, location=location))
        self.song.load(str(cwd + "/sound/music/" + location))

    def play(self, name):
        log.debug("Playing sound: {name}".format(name=name))
        self.song.set_volume(volume)
        self.song.play()

    def fadeout(self, time):
        log.debug("Fading out music song")
        self.song.fadeout(time)


class Effects(dict):
    def load(self, name, location):
        logging.debug("Loading sound: {name}, from {location}".format(name=name, location=location))
        self[name] = pygame.mixer.Sound(str(cwd + "/sound/effects/" + location))
        self[name].set_volume(volume)

    def play(self, name):
        logging.debug("Playing sound: {name}".format(name=name))
        self[name].play()