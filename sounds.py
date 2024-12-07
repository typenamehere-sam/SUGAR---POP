import pygame as pg
from pygame import mixer
class Sound:
    def __init__ (self):
        pg.init()
        pg.mixer.init()
        self.sounds = {
            'Game_background': pg.mixer.Sound ('./sounds/Game_background.mp3'),
            'Sugar_into_bucket': pg.mixer.Sound ('./sounds/Sugar_into_bucket.mp3'),
            'Level_complete': pg.mixer.Sound ('./sounds/Level_complete.mp3'),
            'Game_over': pg.mixer.Sound ('./sounds/Game_over.mp3'),
        
        }

        self.channel1 = pg.mixer.Channel(0) #background
        self.channel2 = pg.mixer.Channel(1)

    def background (self, value):
        background_sound = self.sounds.get(value)
        if background_sound:
            self.channel1.play(background_sound)

    def bucket_sound(self, value):
        sugar_into_bucket = self.sounds.get(value)
        if sugar_into_bucket:
            self.channel2.play(value)


    def play (self, sound_name):
        if sound_name in self.sounds:
            self.sounds [sound_name].play()


         