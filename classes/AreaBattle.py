import pygame
# import textwrap
from classes.Camera import Camera
from classes.MapGen import MapGen
from classes.Settings import *
from classes.Character import *
from classes.Crosshair import Crosshair
from classes.AI import BaseAI


class AreaBattle():
    def __init__(self,seed,screen,directory,clock,FPS,starting_gun):
        self.seed = seed
        self.screen = screen
        self.clock = clock
        self.FPS = FPS
        self.directory = directory
        self.starting_gun = starting_gun
        
    def play(self, gun_list, credits):
        moving_left = False
        moving_up = False
        moving_right = False
        moving_down = False
        jump = False
        weapon_up = weapon_down = False

        TILESIZE = 320
        TILESX = 100
        TILESY = 70
        map_width = TILESIZE * TILESX
        map_height = TILESIZE * TILESY
        
        camera = Camera(self.screen.get_width(), self.screen.get_height(), map_width, map_height)
        
        bullet_group = pygame.sprite.Group()
        splash_group = pygame.sprite.Group()
        explosion_group = pygame.sprite.Group()
        prop_group = pygame.sprite.Group()
        all_sprites = pygame.sprite.Group()
        
        map = MapGen(self.seed, self.screen, self.screen.get_width(), self.screen.get_height(), TILESIZE, TILESX, TILESY, self.directory, number_of_generations)
        start_x, start_y = map.get_tile_pixel_coords(map.start)

        # Player Spawns
        player = Character(self.seed, self.screen, map_width, map_height, self.directory, gun_list, "player", start_x, start_y, 0.3, 0, 13, 100, starting_gun=self.starting_gun) # Speed 10 is decent
        player.receiveCredits(credits)
        print("current balance: ",player.credits, "recently received: ",credits)
        crosshair = Crosshair(player.jsondata)
        pygame.mouse.set_visible(False)

        for sprite in player.get_sprites():
            all_sprites.add(sprite)

        # Enemy Spawns
        enemy_group = []
        for i, milestone in enumerate(map.milestones):
            if i > 0:
                enemy_x, enemy_y = map.get_tile_pixel_coords(milestone)
                enemy = BaseAI(self.seed + i, self.screen, map_width, map_height, self.directory, gun_list, "enemy", enemy_x, enemy_y, 0.3, 0, 8, 5 * i, image_set = i, aimAccuracy = 200 / i)
                for sprite in enemy.get_sprites():
                    all_sprites.add(sprite)
                enemy_group.append(enemy)
        
        run = True
        while run:
            self.clock.tick(self.FPS)
            camera.update(player)

            self.screen.fill((50, 20, 80))
            map.draw_grid(camera)

            for sprite in all_sprites:
                if hasattr(sprite, 'image'):
                    self.screen.blit(sprite.image, camera.apply(sprite))
                
                if isinstance(sprite, Face):  # Or check if it has a health bar
                    sprite.draw_health_bar(camera)

            player.move(moving_left, moving_up, moving_right, moving_down, jump, map, prop_group)
            player.update(player.action, bullet_group, prop_group, map, camera, player, gun_list, weapon_up=weapon_up, weapon_down=weapon_down)
            
            for enemy in enemy_group:
                enemy.update(enemy.action, bullet_group, prop_group, map, camera, player, gun_list)
            
            for bullet in bullet_group:
                splash = bullet.update()
                if splash:
                    splash_group.add(splash)
                if hasattr(bullet, 'image'):
                    self.screen.blit(bullet.image, camera.apply(bullet))
            for splash in splash_group:
                splash.update()
                if hasattr(splash, 'image'):
                    self.screen.blit(splash.image, camera.apply(splash))
            for prop in prop_group:
                prop.update(bullet_group)
                explosion = prop.update(explosion_group)
                if explosion:
                    explosion_group.add(explosion)
                if hasattr(prop, 'image'):
                    self.screen.blit(prop.image, camera.apply(prop))
            for explosion in explosion_group:
                explosion.update()
                if hasattr(explosion, 'image'):
                    self.screen.blit(explosion.image, camera.apply(explosion))
            if player.shoot:
                bullet = player.fire(player.aim_direction)
                if bullet:
                    bullet_group.add(bullet)

            world_mouse_pos = pygame.Vector2(pygame.mouse.get_pos()) - camera.camera.topleft
            player.aim_direction = world_mouse_pos - pygame.Vector2(player.body.rect.center)
            player.cameraAim(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) 
            crosshair.draw(self.screen, pygame.mouse.get_pos())

            pygame.display.flip()

            # EVENT HANDLING
            for event in pygame.event.get():        
                if event.type == pygame.QUIT:
                    run = False
                    #self.state = "menu"
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        return "common_area", player.credits, gun_list
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
                        player.alive = False
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
                        player.shoot = True
                    if event.button == 3:
                        print("RMB: ", pygame.mouse.get_pos())
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        player.shoot = False
                    if event.button == 3:
                        print("RMB: ", pygame.mouse.get_pos())
            pygame.display.update()