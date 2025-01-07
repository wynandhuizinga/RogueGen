import pygame
import os
import re
import random
import json
import base64
import io

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, explosions):
        pygame.sprite.Sprite.__init__(self)
        self.images = explosions
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 3
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]