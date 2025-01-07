import pygame
import os
import re
import math
import cProfile
import pstats
import io
import textwrap

from classes.Settings import *
from classes.Character import *
from classes.AreaCommon import AreaCommon
from classes.AreaBattle import AreaBattle
from classes.AI import BaseAI
from classes.MapGen import MapGen
from classes.Camera import Camera
from classes.Crosshair import Crosshair
from classes.Dialogue import Dialogue
from classes.APICallHandler import APICallHandler

api_handler = APICallHandler(API_SETTINGS)

class Arena():
    def __init__(self, seed, charGenDir, profiling=False):
        pygame.init()
        pygame.display.set_caption("tryout pygame")
        self.seed = seed
        self.directory = playDirectory if playDirectory != "" else charGenDir
        self.profiling = profiling
        self.SCREENX = 1536
        self.SCREENY = 768
        self.screen = pygame.display.set_mode((self.SCREENX, self.SCREENY))
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.state = "menu"
        self.message_number = 1
        self.conversingEnemy = None
        self.starting_gun = None # TODO - Dynamic
        self.gun_list = []
        self.load_guns()
        self.areaCommon = AreaCommon(self.seed,self.screen,self.directory,self.gun_list,self.clock,self.FPS,self.starting_gun)
        self.playerCredits = 0
        self.player = None
        
                
    def load_guns(self):
        pattern = re.compile(rf'^.*[0-9]{{8}}.*\.json$')
        total_count = 0
        players_gun_number = random.randint(0, 3)

        for file_name in os.listdir(self.directory):
            match = pattern.match(file_name)
            if match:
                with open(os.path.join(self.directory, file_name), 'r', encoding='utf-8') as f:
                    jsondata = json.load(f)

                gun_data = jsondata.get('Gun_Data', {})

                for category, gun_list in gun_data.items():
                    for gun in gun_list:
                        base_gun_data = gun.get('base_gun_data', {})
                        upgraded_gun_data = gun.get('upgraded_gun_data', {})

                        base_gun_image_data = base_gun_data.get('gun_image_data')
                        base_projectile_data = base_gun_data.get('projectile_data', [])
                        base_splash_data = base_gun_data.get('splash_data', [])

                        upgraded_gun_image_data = upgraded_gun_data.get('gun_image_data')
                        upgraded_projectile_data = upgraded_gun_data.get('projectile_data', [])
                        upgraded_splash_data = upgraded_gun_data.get('splash_data', [])

                        rate_of_fire = random.randint(4, 30)
                        damage = random.randint(4, 20)

                        if total_count == players_gun_number or total_count == players_gun_number+1 or total_count == players_gun_number+2  : # TODO - remove second part
                            owned = True
                            price = 0
                            self.starting_gun = total_count
                        else:
                            owned = False
                            price = random.randint(40, 1000)

                        upgraded = False

                        gun_entry = {
                            "category": category,
                            "idx": total_count,  # Use total_count as a unique index
                            "base_gun_image_data": base_gun_image_data,
                            "rate_of_fire": rate_of_fire,
                            "damage": damage,
                            "upgraded_gun_image_data": upgraded_gun_image_data,
                            "owned": owned,
                            "upgraded": upgraded,
                            "price": price,
                            "base_projectile_data": base_projectile_data,
                            "base_splash_data": base_splash_data,
                            "upgraded_projectile_data": upgraded_projectile_data,
                            "upgraded_splash_data": upgraded_splash_data
                        }

                        self.gun_list.append(gun_entry)
                        total_count += 1
            

    def play(self):
        if self.profiling:
            pr = cProfile.Profile()
            pr.enable()

        while True:
            if self.state == "menu":
                self.main_menu()
            elif self.state == "common_area":
                self.commonArea()
            elif self.state == "game":
                self.run_game()
            elif self.state == "dialogue":
                self.dialogue(self.conversingEnemy)
            elif self.state == "settings":
                self.settings_menu()
            elif self.state == "quit":
                break

        pygame.quit()
        if self.profiling:
            pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()
            print(s.getvalue())

    def main_menu(self):
        run = True
        while run:
            self.screen.fill((0, 0, 0))
            self.draw_menu_text('Main Menu', 100, self.SCREENX / 2, self.SCREENY / 4)
            self.draw_menu_text('1. Common Area', 50, self.SCREENX / 2, self.SCREENY / 2)
            self.draw_menu_text('2. Start New Game', 50, self.SCREENX / 2, self.SCREENY / 2 + 50)
            self.draw_menu_text('3. Edit Audio Settings', 50, self.SCREENX / 2, self.SCREENY / 2 + 100)
            self.draw_menu_text('4. Quit Game', 50, self.SCREENX / 2, self.SCREENY / 2 + 150)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.state = "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        run = False
                        self.state = "common_area"
                    if event.key == pygame.K_2:
                        run = False
                        self.state = "game"
                    if event.key == pygame.K_3:
                        run = False
                        self.state = "settings"
                    if event.key == pygame.K_4:
                        run = False
                        self.state = "quit"

    def settings_menu(self):
        run = True
        while run:
            self.screen.fill((0, 0, 0))
            self.draw_menu_text('Settings Menu', 100, self.SCREENX / 2, self.SCREENY / 4)
            self.draw_menu_text('Press any key to go back', 50, self.SCREENX / 2, self.SCREENY / 2)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    self.state = "quit"
                if event.type == pygame.KEYDOWN:
                    run = False
                    self.state = "menu"

    def draw_menu_text(self, text, size, x, y):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def commonArea(self):
        if self.player == None:
            self.state, self.conversingEnemy, self.player, gun_list = self.areaCommon.play(self.gun_list, credits=self.playerCredits)
            self.player.credits = self.playerCredits
        else:
            self.state, self.conversingEnemy, self.player, self.gun_list = self.areaCommon.play(self.gun_list, player=self.player)
            self.playerCredits = self.player.credits
        # print("end of commonarea - ",self.player.credits)

    def dialogue(self, conversingEnemy):
        dialogue = Dialogue(self.seed,self.screen,self.FPS,self.clock)
        self.state, self.player, self.gun_list = dialogue.dialogue(conversingEnemy,self.player, self.gun_list)
        # print("end of dialogue - ",self.player.credits)

    def run_game(self):
        areaBattle = AreaBattle(self.seed,self.screen,self.directory,self.clock,self.FPS,self.starting_gun)
        if not self.player == None:
            self.playerCredits = self.player.credits
            # print("mid battle - ",self.player.credits)
        self.state, self.playerCredits, self.gun_list = areaBattle.play(self.gun_list, self.playerCredits)
        if not self.player == None:
            self.player.credits = self.playerCredits
        # print("player's credits end of battle: ",self.playerCredits)
            
