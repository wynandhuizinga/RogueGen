import pygame
import textwrap
from classes.Camera import Camera
from classes.MapGen import MapGen
from classes.Settings import *
from classes.Character import Character
from classes.Crosshair import Crosshair


class AreaCommon():
    def __init__(self,seed,screen,directory,gun_list,clock,FPS,starting_gun):
        TILESIZE = 320
        TILESX = 20
        TILESY = 10
        map_width = TILESIZE * TILESX
        map_height = TILESIZE * TILESY
        self.screen = screen
        self.seed = seed

        self.clock = clock
        self.FPS = FPS
        self.camera = Camera(screen.get_width(), screen.get_height(), map_width, map_height)

        self.bullet_group = pygame.sprite.Group()
        self.splash_group = pygame.sprite.Group()
        self.explosion_group = pygame.sprite.Group()
        self.prop_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.map = MapGen(self.seed, screen, screen.get_width(), screen.get_height(), TILESIZE, TILESX, TILESY, directory, number_of_generations,2,set_traps=False) # TODO - add all enemies
        start_x, start_y = self.map.get_tile_pixel_coords(self.map.start)
        self.player = Character(self.seed, screen, map_width, map_height, directory, gun_list, "player", start_x, start_y, 0.3, 0, 13, 100, starting_gun=starting_gun)
        self.crosshair = Crosshair(self.player.jsondata)
        for sprite in self.player.get_sprites():
            self.all_sprites.add(sprite)
        pygame.mouse.set_visible(False)
            
        # Enemy Spawns
        self.enemy_group = []
        for i, milestone in enumerate(self.map.milestones):
            if i > 0:
                enemy_x, enemy_y = self.map.get_tile_pixel_coords(milestone)
                enemy = Character(self.seed + i, self.screen, map_width, map_height, directory, gun_list, "enemy", enemy_x, enemy_y, 0.3, 0, 8, i*10000, image_set = i, aimAccuracy = 200 / i)
                for sprite in enemy.get_sprites():
                    self.all_sprites.add(sprite)
                self.enemy_group.append(enemy)
                
    def play(self, gun_list, credits=None,player=None):
        moving_left = False
        moving_up = False
        moving_right = False
        moving_down = False
        jump = False
        weapon_up = weapon_down = False
        
        if not player == None:
            self.player = player
        if not credits == None:
            self.player.credits = credits

        run = True
        while run:
            self.screen.fill((50, 140, 100))
            self.camera.update(self.player)

            self.map.draw_grid(self.camera)
            self.draw_text('Common Area', 100, self.screen.get_width() / 2, self.screen.get_height() / 4)
            self.clock.tick(self.FPS)
            for sprite in self.all_sprites:
                if hasattr(sprite, 'image'):
                    self.screen.blit(sprite.image, self.camera.apply(sprite))
            self.player.move(moving_left, moving_up, moving_right, moving_down, jump, self.map, self.prop_group)
            self.player.update(self.player.action, self.bullet_group, self.prop_group, self.map, self.camera, player, gun_list, weapon_up=weapon_up, weapon_down=weapon_down)
            
            for i, enemy in enumerate(self.enemy_group):
                enemy.update(enemy.action, self.bullet_group, self.prop_group, self.map, self.camera, self.player, gun_list)
                if self.player.proximity_circle.rect.colliderect(enemy.proximity_circle.rect):
                    self.draw_text('Hit [E] to interact', 50, self.screen.get_width() / 2, self.screen.get_height() / 5)
                    enemy.move(False, False, False, False, True, self.map, self.prop_group)
                else:
                    enemy.move(False, False, False, False, False, self.map, self.prop_group)
                
            for bullet in self.bullet_group:
                splash = bullet.update()
                if splash:
                    self.splash_group.add(splash)
                if hasattr(bullet, 'image'):
                    self.screen.blit(bullet.image, self.camera.apply(bullet))
            for splash in self.splash_group:
                splash.update()
                if hasattr(splash, 'image'):
                    self.screen.blit(splash.image, self.camera.apply(splash))
            for prop in self.prop_group:
                prop.update(self.bullet_group)
                explosion = prop.update(self.explosion_group)
                if explosion:
                    self.explosion_group.add(explosion)
                if hasattr(prop, 'image'):
                    self.screen.blit(prop.image, self.camera.apply(prop))
            for explosion in self.explosion_group:
                explosion.update()
                if hasattr(explosion, 'image'):
                    self.screen.blit(explosion.image, self.camera.apply(explosion))
            if self.player.shoot:
                bullet = self.player.fire(self.player.aim_direction)
                if bullet:
                    self.bullet_group.add(bullet)
                    
            world_mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - self.camera.camera.topleft
            self.player.aim_direction = world_mouse_pos - pygame.Vector2(self.player.body.rect.center)
            self.player.cameraAim(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) 
            self.crosshair.draw(self.screen, pygame.mouse.get_pos())
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    return "menu", None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        return "menu", None, self.player, gun_list
                    if event.key == pygame.K_a:
                        moving_left = True
                        moving_right = False
                    if event.key == pygame.K_w:
                        moving_up = True
                        moving_down = False
                    if event.key == pygame.K_d:
                        moving_right = True
                        moving_left = False
                    if event.key == pygame.K_s:
                        moving_down = True
                        moving_up = False
                    if event.key == pygame.K_SPACE:
                        jump = True
                    if event.key == pygame.K_k:
                        self.player.alive = False
                    if event.key == pygame.K_e:
                        for enemy in self.enemy_group:
                            if self.player.proximity_circle.rect.colliderect(enemy.proximity_circle.rect):
                                run = False
                                return "dialogue", enemy, self.player, gun_list
                    if event.key == pygame.K_f:
                        weapon_up = True
                    if event.key == pygame.K_g:
                        weapon_down = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        moving_left = False
                    if event.key == pygame.K_w:
                        moving_up = False
                    if event.key == pygame.K_d:
                        moving_right = False
                    if event.key == pygame.K_s:
                        moving_down = False
                    if event.key == pygame.K_SPACE:
                        jump = False
                    if event.key == pygame.K_f:
                        weapon_up = False
                    if event.key == pygame.K_g:
                        weapon_down = False
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.shoot = True
                    if event.button == 3:
                        print("RMB: ", pygame.mouse.get_pos())
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        self.player.shoot = False
                    if event.button == 3:
                        print("RMB: ", pygame.mouse.get_pos())
            pygame.display.update()

    def draw_text(self, text, size, x, y):
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)
        