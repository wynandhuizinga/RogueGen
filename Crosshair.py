import pygame 
import base64
import io
import json

class Crosshair(pygame.sprite.Sprite):
    def __init__(self,jsondata):
        pygame.sprite.Sprite.__init__(self)
        jsondata = jsondata['CharGen_data']['PlayerSprites']['crosshair_data']
        image_bytes = base64.b64decode(jsondata)
        self.image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.image2 = pygame.transform.scale(self.image, (self.width//3, self.height//3))
        self.rect = self.image2.get_rect()
        self.width = self.image2.get_width()
        self.height = self.image2.get_height()
        self.rect.center = (0,0)
    
    def draw(self, screen, pos):
        screen.blit(self.image2, (pos[0]-self.width//2,pos[1]-self.height//2))
