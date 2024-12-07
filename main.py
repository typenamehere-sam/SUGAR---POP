#############################################################
# Module Name: Sugar Pop Main Module
# Project: Sugar Pop Program
# Date: Dec 3, 2024
# By: samwel O obiero
# Description: The main implementation of the sugar pop game
#############################################################


import pygame as pg
import pymunk  # Import Pymunk library
import sys
from settings import *
import random
import static_item
import dynamic_item
import sugar_grain
import bucket
import level
import message_display
from pathlib import Path
from sounds import Sound


class Game:
    def __init__(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.iter = 0
        
        # Initialize font for HUD
        self.font = pg.font.SysFont(None, 36)  # Default font, size 36

        # Create a Pymunk space with gravity
        self.current_level = 0 # Start game at 0
        self.level_complete = False
        self.space = pymunk.Space()
        self.space.gravity = (0, -9)  # Gravity pointing downwards in Pymunk's coordinate system
        # Iterations defaults to 10. Higher is more accurate collison detection
        self.space.iterations = 40 
        self.is_paused = False
        self.gravity_reversed = False

        self.drawing_lines = []
        self.sugar_grains = []
        self.buckets = []
        self.statics = []
        self.total_sugar_count = None
        self.level_spout_position = None
        self.level_grain_dropping = None
        self.mouse_down = False
        self.current_line = None
        self.message_display = message_display.MessageDisplay(font_size=72)

        #initializing sound manager
        pg.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sound = Sound()
        self.sound.channel1.play( pg.mixer.Sound ('./sounds/Game_background.mp3'))
        self.sound_playing = False
        
        # Load the intro image
        self.intro_image = pg.image.load("./images/SugarPop.png").convert()  # Load the intro image
        # Get new height based on correct scale
        scale_height = self.intro_image.get_height() * WIDTH / self.intro_image.get_width()
        self.intro_image = pg.transform.scale(self.intro_image, (WIDTH, int(scale_height)))  # Scale to screen resolution
        
        pg.time.set_timer(LOAD_NEW_LEVEL, 5000)  # Load in 5 seconds

    def load_level(self, levelnumber=0):
        # Destroy any current game objects
        for item in self.sugar_grains:
            item.delete()  # Delete all sugar grains
        for item in self.drawing_lines:
            item.delete() 
        for item in self.buckets:
            item.delete() 
        for item in self.statics:
            item.delete() 
        self.sugar_grains = []
        self.drawing_lines = []  # Clear the list
        self.buckets = []
        self.statics = []
 
        new_level = LEVEL_FILE_NAME.replace("X", str(levelnumber))
        self.level = level.Level(new_level)

        #play background sound for loaded level
        pg.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        self.sound = Sound()
        self.sound.channel1.play( pg.mixer.Sound ('./sounds/Game_bgd.mp3'))
        
        # Make sure the file was found
        if not self.level or not self.level.data:
            return False
        else:  # Do final steps to start the level
            self.level_grain_dropping = False
            self.level_spout_position = (self.level.data['spout_x'], self.level.data['spout_y'])
            self.build_main_walls()

            # Load buckets
            for nb in self.level.data['buckets']:
                self.buckets.append(bucket.Bucket(self.space, nb['x'], nb['y'], nb['width'], nb['height'], nb['needed_sugar']))
                
            # Load static items
            for nb in self.level.data['statics']:
                self.statics.append(static_item.StaticItem(self.space, nb['x1'], nb['y1'], nb['x2'], nb['y2'], nb['color'], nb['line_width'], nb['friction'], nb['restitution']))
            self.total_sugar_count = self.level.data['number_sugar_grains']
            pg.time.set_timer(START_FLOW, 5 * 1000)  # 5 seconds
            self.message_display.show_message("Level Up", 10)
            self.level_complete = False
            return True
        

    def build_main_walls(self):
        '''Build the walls, ceiling, and floor of the screen'''
        # Floor
        floor = static_item.StaticItem(self.space, 0, 0, WIDTH, 0, 'red', 5)
        self.statics.append(floor)
        # Left Wall
        left_wall = static_item.StaticItem(self.space, 0, 0, 0, HEIGHT, 'red')
        self.statics.append(left_wall)
        # Right Wall
        right_wall = static_item.StaticItem(self.space, WIDTH, 0, WIDTH, HEIGHT, 'red')
        self.statics.append(right_wall)
        # Ceiling
        ceiling = static_item.StaticItem(self.space, 0, HEIGHT, WIDTH, HEIGHT, 'red')
        self.statics.append(ceiling)
    
    def check_all_buckets_exploded(self):
        """
        Check if all buckets have exploded.
        """
        return all(bucket.exploded for bucket in self.buckets)

    def update(self):
        '''Update the program physics'''
        
        if self.is_paused:
            return
        
        # Keep an overall iterator
        self.iter += 1
        
        # Calculate time since last frame
        delta_time = self.clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds

        # Cap delta_time to prevent instability from large time steps
        time_step = min(delta_time, MAX_TIME_STEP)

        # Step the physics simulation forward with the calculated time_step
        self.space.step(time_step)
        
        # Update our game counter
        if self.iter == 60:
            self.iter = 0

        pg.display.set_caption(f'fps: {self.clock.get_fps():.1f}')
        
        # Only do the following every 20 frames for less system stress
        if self.iter % 20 == 0:
            # Update any messages
            self.message_display.update()
            
            # Calculate buckets count by counting each grain's position
          #loop through the buckets and check if sugar is entering
            for bucket in self.buckets:
           

                    #check if the bucket has exploded after attaining the required amount of sugar
                if bucket.count >= bucket.needed_sugar:
                    bucket.explode(self.sugar_grains)
                    #play sound for explosion
                    if hasattr (self, 'sound'):
                        self.sound.play ('Game_over')

                    if not self.level_complete and self.check_all_buckets_exploded():
                        self.level_complete =True
                        self.message_display.show_message("level complete!", 2)
                        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)
                else:
                    bucket.count_reset()
# count the grains in unexploded buckets
            for grain in self.sugar_grains:
                for bucket in self.buckets:
                    bucket.collect(grain)

                    
                    # If all the buckets are gone, level up!
                    if not self.level_complete and self.check_all_buckets_exploded():
                        self.level_complete = True
                        self.message_display.show_message("Level Complete!", 2)

                        #lets play the sound
                        if hasattr (self, 'sound'):
                            self.sound.play ('Level_complete')

                        # stop the current background sound
                        if hasattr(self.sound, 'channel1'):
                            self.sound.channel1.stop()
                        pg.time.set_timer(LOAD_NEW_LEVEL, 2000)  # Schedule next level load
                else:
                    bucket.count_reset()
            # Count the grains in the un-exploded buckets
            for grain in self.sugar_grains:
                for bucket in self.buckets:
                    #has sugar entered the bucket?
                    if bucket.collect(grain):
                        #play the sound
                        if hasattr (self, 'sound'):
                            self.sound.play ('bucket1')
                
            # Drop sugar if needed
            if self.level_grain_dropping:
                # Create new sugar to drop
                new_sugar = sugar_grain.sugar_grain(self.space, self.level_spout_position[0], self.level_spout_position[1], 0.1)
                self.sugar_grains.append(new_sugar)
                # Check if it's time to stop
                if len(self.sugar_grains) >= self.total_sugar_count:
                    self.level_grain_dropping = False

    def draw_hud(self):
        """Draw the HUD displaying the number of grains."""
        # Prepare the text surface
        if self.total_sugar_count:
            text_surface = self.font.render(f'{self.total_sugar_count - len(self.sugar_grains)}', True, (255, 255, 255))
            # Draw the text surface on the screen
            self.screen.blit(text_surface, (10, 10))  # Position at top-left corner



    def draw(self):
        '''Draw the overall game. Should call individual item draw() methods'''
        # Clear the screen
        self.screen.fill('darkgreen')

        # Only show the intro screen if we haven't loaded a level yet
        if self.intro_image:
            self.screen.blit(self.intro_image, (0, 0))  # Draw the intro image
    
        for bucket in self.buckets:
            bucket.draw(self.screen)

        # Draw each sugar grain
        for grain in self.sugar_grains:
            grain.draw(self.screen)

        # Draw the current dynamic line
        if self.current_line is not None:
            self.current_line.draw(self.screen)
        
        # Draw the user-drawn lines
        for line in self.drawing_lines:
            line.draw(self.screen)
            
        # Draw any static items
        for static in self.statics:
            static.draw(self.screen)

        # Draw the nozzle (Remember to subtract y from the height)
        if self.level_spout_position:
            pg.draw.line(
                self.screen, 
                (255, 165, 144), 
                (self.level_spout_position[0], HEIGHT - self.level_spout_position[1] - 10), 
                (self.level_spout_position[0], HEIGHT - self.level_spout_position[1]), 
                5
            )
        
        # Draw the heads-up display
        self.draw_hud()

        # Show any messages needed        
        self.message_display.draw(self.screen)

        #gravity reverse message
        if self.gravity_reversed:
            #prepare surface
            gravity_text = self.font.render("Gravity reversed", True, (255,0,0))
            #draw text on screen
            text_rect = gravity_text.get_rect (center=(WIDTH // 2, 50))
            self.screen.blit(gravity_text,text_rect)

        # Update the display
        pg.display.update()

    def reverse_gravity (self):
        x,y  = self.space.gravity
        self.space.gravity = (x, -y)
        self.gravity_reversed = not self.gravity_reversed

    def check_events(self):
        '''Check for keyboard and mouse events'''
        for event in pg.event.get():
            if event.type == EXIT_APP or event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

            # Implementing level restart
            elif event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.current_level -= 1
                pg.time.set_timer(LOAD_NEW_LEVEL, 100)  # Load level

            
            # Implementing a pause
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                if self.is_paused:
                    #when unpausing the game
                    self.is_paused = False  
                    self.sound.channel1.unpause()      
                else:
                    #when pausing
                    self.message_display.show_message("Paused", 2)  # Show Paused
                    self.is_paused = True
                    self.sound.channel1.pause()

                #reverse gravity
            elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                self.reverse_gravity()
                
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_down = True
                # Get mouse position and start a new dynamic line
                mouse_x, mouse_y = pg.mouse.get_pos()
                self.current_line = dynamic_item.DynamicItem(self.space, 'blue')
                self.current_line.add_vertex(mouse_x, mouse_y)
                
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_down = False
                if self.current_line:
                    self.drawing_lines.append(self.current_line)
                    self.current_line = None
                
            elif event.type == pg.MOUSEMOTION and self.mouse_down:
                # Get mouse position
                mouse_x, mouse_y = pg.mouse.get_pos()
                if mouse_x == 0 or mouse_x == WIDTH or mouse_y == 0 or mouse_y == HEIGHT:
                    self.mouse_down = False
                if self.current_line and self.iter % 10 == 0:
                    self.current_line.add_vertex(mouse_x, mouse_y)

            elif event.type == START_FLOW:
                self.level_grain_dropping = True
                # Disable the timer after the first trigger
                pg.time.set_timer(START_FLOW, 0)
                
            elif event.type == LOAD_NEW_LEVEL:
                pg.time.set_timer(LOAD_NEW_LEVEL, 0)  # Clear the timer
                self.intro_image = None
                self.current_level += 1
                if not self.load_level(self.current_level):
                    self.message_display.show_message("You Win!", 5)  # End of game message
                    pg.time.set_timer(EXIT_APP, 5000)  # Quit game after 5 seconds
                else:
                    self.message_display.show_message(f"Level {self.current_level} Start!", 2)

    
                    
    def run(self):
        '''Run the main game loop'''
        while True:
            self.check_events()
            self.update()
            self.draw()

    

def main():
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
