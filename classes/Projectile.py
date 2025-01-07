import pygame
import os
import re
import random
import json
import base64
import io

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction,scale,aim_direction,projectiles,damage,char_type,splashes,speed=15):
        bullet_img = pygame.image.load('./templates/Balloon-1.png').convert_alpha() # todo Replace to logical location so that it stays in memory.

        pygame.sprite.Sprite.__init__(self)
        self.speed = speed
        self.timer = 60
        self.scale = scale
        self.image = bullet_img
        self.owner = char_type
        self.damage = damage
        self.splashes = splashes
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width()) * self.scale, int(self.image.get_height() * self.scale)))
        self.rect  = self.image.get_rect()
        self.rect.center = (x,y)
        if aim_direction.length() != 0:
            self.aim_direction = aim_direction.normalize() * self.speed
        else:
            self.aim_direction = pygame.math.Vector2(0, 0) # null-safe?
        self.projectiles = projectiles
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.hit = False
        
    def update(self):
        self.rect.x += self.aim_direction.x
        self.rect.y += self.aim_direction.y
        self.update_animation()
        
        self.timer -= 1
        if self.timer <= 0 or self.hit:
            self.kill()
            splash = Splash(self.rect.x, self.rect.y, 0.5,self.splashes)
            return splash
        
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.projectiles[self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.projectiles):
            self.frame_index = 0

class Splash(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, splashes):
        pygame.sprite.Sprite.__init__(self)
        self.images = splashes
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]