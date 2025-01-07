import pygame
import os
import re
import random
import json
import base64
import io
from classes.Limbs import Face, Body, Legs, Shadow
from classes.Projectile import Bullet, Splash
from classes.Explosion import Explosion
from classes.Prop import Prop
from classes.Character import Character 
from classes.Gun import Gun

class BaseAI(Character):
    def __init__(self, seed, screen, map_width, map_height, directory, gun_list, char_type, x, y, scale, action, speed, health, image_set=0,aimAccuracy=0):
        super().__init__(seed, screen, map_width, map_height, directory, gun_list, char_type, x, y, scale, action, speed,health,image_set=image_set,aimAccuracy=aimAccuracy)
        self.range = int(self.screen.get_width()/2)
        self.range_collider = pygame.Rect(self.x - self.range // 2, self.y - self.range // 2, self.range, self.range)
        self.playerDetected = False
        self.dodge_speed = 35 * self.speed  # Speed when dodging
        self.dodge_duration = 20  # Number of frames to dodge
        self.dodge_timer = 10
        self.dodge_direction = pygame.math.Vector2(0, 0)
        self.dodge_cooldown = 0  # Cooldown to prevent continuous dodging
        self.random_offset = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        self.diversive_cooldown = 10
        self.path = []  # to store the path to the player
        self.path_index = 0  # to keep track of the current position in the path
        self.recalculate_path_cooldown = 0  # cooldown to prevent constant path recalculation
        self.random_deviation = pygame.math.Vector2(0, 0)
        self.straightPath = True
        self.Redecide = 0
        self.aimAccuracy = self.aimAccuracy


    def update(self, action, bullet_group, prop_group, map_generator, camera, player, gun_list):
        super().update(action, bullet_group, prop_group, map_generator, camera, player, gun_list)
        self.applyEnemyAI(action, bullet_group, prop_group, map_generator, player)
        if not self.alive and self.time_of_death == None:
            self.time_of_death = pygame.time.get_ticks()
            player.receiveCredits(5)
        if not self.alive:
            self.draw_reward()
        
    def applyEnemyAI(self,action,bullet_group,prop_group,map_generator,player='player'):
        if self.char_type == 'enemy':
            self.range_collider.center = self.shadow.rect.center
            if self.dodge_timer > 0:
                self.dodge_timer -= 1
                self.move(self.dodge_direction.x < 0, self.dodge_direction.y < 0, self.dodge_direction.x > 0, self.dodge_direction.y > 0, self.jump, map_generator,prop_group)
            else:
                if player.alive and self.in_range(player) or self.playerDetected:
                    self.playerDetected = True
                    self.move_cautiously_towards_player(player, map_generator, prop_group)
                    self.shoot_at_player(player, bullet_group)
                    if self.dodge_cooldown == 0:
                        self.anticipate_and_dodge_bullets(bullet_group)
                    else:
                        self.dodge_cooldown -= 1
                if player.alive and self.playerDetected:
                    self.spawn_prop(player, prop_group, map_generator)
                        
    def in_range(self, player):
        return self.range_collider.colliderect(player.shadow.rect)
         
    def move_cautiously_towards_player(self, player, map_generator, prop_group):
        if not self.alive:
            return
        elif not player.alive:
            self.face.loser(player)
            if not self.playerDead:
                self.update_action(0)
                self.playerDead = True
            return

        self.Redecide -=1
        if self.Redecide <= 0:
            if random.random() < 0.2: 
                self.straightPath = True # Direct walk at player ignoring environment
            else:
                self.straightPath = False # Determine route to get to player taking walls into consideration
            self.Redecide = random.randint(40,100)
            
        if self.straightPath:
            if self.diversive_cooldown == 0:
                self.diversive_cooldown = random.randint(50,220) # define new length for 'evasive manouvres'
            else:
                self.diversive_cooldown -= 1
            # Randomly adjust direction slightly for organic movement
            self.direction = pygame.math.Vector2(player.shadow.rect.center) - pygame.math.Vector2(self.shadow.rect.center)
            if self.direction.length() > 0:
                self.direction.normalize_ip()
                # self.direction = direction # broken
                self.move(self.direction.x < 0, self.direction.y < 0, self.direction.x > 0, self.direction.y > 0, False, map_generator,prop_group)
            
        else:
            if self.recalculate_path_cooldown > 0:
                self.recalculate_path_cooldown -= 1
                
            if not self.path or self.path_index >= len(self.path) or self.recalculate_path_cooldown <= 0:
                self.path = map_generator.astar(self.get_grid_position(map_generator), player.get_grid_position(map_generator))
                self.path_index = 0
                self.recalculate_path_cooldown = random.randint(100,300)  # set cooldown for path recalculation

            if self.path and self.path_index < len(self.path):
                target = self.path[self.path_index]
                target_pos = pygame.math.Vector2(target[0] * map_generator.TILE_SIZE + map_generator.TILE_SIZE // 2,
                                                 target[1] * map_generator.TILE_SIZE + map_generator.TILE_SIZE // 2)

                # Add random deviation
                if random.random() < 0.03:  # occasionally adjust deviation
                    self.random_deviation = pygame.math.Vector2(random.uniform(-5, 5), random.uniform(-5, 5))
                elif random.random() < 0.1:
                    self.random_deviation = pygame.math.Vector2(0, 0)
                target_pos += self.random_deviation

                if random.random() <0.1:
                    self.direction = target_pos - pygame.math.Vector2(self.shadow.rect.center)
                    
                if self.direction.length() > 0:
                    self.direction.normalize_ip()

                    # Add slight randomness to movement direction
                    deviation = pygame.math.Vector2(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
                    self.direction += deviation
                    self.direction.normalize_ip()

                    self.move(self.direction.x < 0, self.direction.y < 0, self.direction.x > 0, self.direction.y > 0, False, map_generator, prop_group)

                if self.shadow.rect.collidepoint(target_pos):
                    self.path_index += 1

    def shoot_at_player(self, player, bullet_group):
        if self.alive and player.alive and self.shoot_cooldown == 0 and self.ammo > 0:            
            if self.char_type == 'player': # shouldn't ever happen
                self.shoot_cooldown = 20
            else: 
                self.shoot_cooldown = random.randint(5, 80)
            self.aim_direction = pygame.math.Vector2(player.shadow.rect.center) - pygame.math.Vector2(self.shadow.rect.center)
            self.aim_direction += pygame.math.Vector2(random.uniform(-self.aimAccuracy, self.aimAccuracy), random.uniform(-self.aimAccuracy, self.aimAccuracy))
            bullet = Bullet(self.body.rect.centerx, self.body.rect.centery, self.direction, 0.1, self.aim_direction, self.projectiles, self.gun.damage, self.char_type, self.splashes, speed=random.randint(10,20))
            self.ammo -= 1
            bullet_group.add(bullet)

    def anticipate_and_dodge_bullets(self, bullet_group):
        for bullet in bullet_group:
            if bullet.owner != self.char_type:
                # Predict future position
                bullet_future_rect = bullet.rect.move(bullet.aim_direction * 10)  # Predict 10 frames ahead
                if (self.shadow.rect.colliderect(bullet_future_rect) or self.legs.rect.colliderect(bullet_future_rect) or self.body.rect.colliderect(bullet_future_rect) or self.face.rect.colliderect(bullet_future_rect)):
                    dodge_direction = pygame.math.Vector2(bullet.aim_direction.y, -bullet.aim_direction.x)  # Dodge perpendicularly
                    if random.choice([True, False]):  # Randomly decide to dodge left or right
                        dodge_direction = -dodge_direction
                    self.jump = True
                    self.dodge_direction = dodge_direction.normalize() * self.dodge_speed
                    self.dodge_timer = self.dodge_duration
                    self.dodge_cooldown = random.randint(30, 60) # 60  # Cooldown to prevent continuous dodging
                    break
                    
    def draw_reward(self):
        #return # TODO - Remove
        if self.time_of_death != None:
            if (pygame.time.get_ticks() - self.time_of_death) < 4000 and not self.alive:
                # print("shown reward")
                return
                self.screen.blit(self.victory_image, self.victory_rect.topleft) # TODO - re-add

class CasualAI(BaseAI):
    def update(self, action, bullet_group, prop_group, map_generator, player='player'):
        # Define casual behavior here
        pass