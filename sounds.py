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


             # def collect(self, grain):
    #     ''''collect a sugar grain only when it falls into the bucket'''
    #     if self.grain_in_bucket(grain):
    #         self.count += 1
    #         if self.count >= self.needed_sugar and not self.exploded:
    #             self.explode()
    #         return True
    #     return False
    
    # def grain_in_bucket(self,grain):
    #     '''''is grain inside the bucket area?'''
    #     return grain.position[0] in range(self.position[0], self.position[0] + self.width) and \
    #            grain.position[1] in range(self.position[1] + self.height)
    
    # def grains_left(self):
    #     return self.needed_sugar - self.count
    
    # def explode (self):
    #     '''handle bucket's explosion'''
    #     self.exploded = True
    #     #remove grains from this bucket
    #     for grain in self.sugar_grains:
    #         grain.delete()
    


     # y_offset = 50
        # for bucket in self.buckets:
        #     remaining_grains = bucket.grains_left()
        #     bucket_text = self.font.render (f'{remaining_grains}', True, (255, 255, 255))
        #     self.screen.blit(bucket_text, (WIDTH - 200, y_offset))
        #     y_offset +=40
