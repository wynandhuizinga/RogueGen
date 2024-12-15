import pygame
import os
import re
import random
import json
import base64
import io

from Explosion import Explosion

class Prop(pygame.sprite.Sprite):
    def __init__(self, x, y, prop, explosions):
        pygame.sprite.Sprite.__init__(self)
        self.image = prop
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
        self.health = random.randint(1,40)
        self.lifetime = 1000
        self.explosions = explosions
    
    def update(self,bullet_group):
        self.counter += 1
        if self.counter >= self.lifetime or self.health < 1:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5,self.explosions)
            return explosion
            
        for bullet in bullet_group:
            if self.rect.colliderect(bullet.rect): 
                if self.alive:
                    self.health -= 10
                    bullet.hit = True