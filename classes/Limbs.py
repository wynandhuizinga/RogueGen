import pygame
import os
import re
import random
import json
import base64
import io

class Face(pygame.sprite.Sprite):
    def __init__(self, screen, directory, image_set, char_type, x, y, scale, flip, translation, jsondata):
        super().__init__()   

        self.screen = screen
        self.directory = directory
        self.char_type = char_type
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0
        self.flip = flip
        self.image_set = image_set
        self.health = 1
        self.maxhealth = 1
        self.nodNo = 0

        animation_types = ['idle','move','shoot','death','jump','dead']
        face_data = jsondata['CharGen_data']['PlayerSprites']['face_data']
        for animation in animation_types:
            temp_list = []
            if animation in face_data:
                for image_data in face_data[animation]:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
                    image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                    temp_list.append(image)
            self.animation_list.append(temp_list) 

        self.image = self.animation_list[0][0] # Defines dimensions
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.translation = translation # 0 # translation+self.height
        self.rect.midbottom = (x,y)
        self.reset_y = 0

    def update(self,action,flip,health,maxhealth,alive):
        self.flip = flip
        self.update_action(action)
        self.update_animation()
        self.health = health
        self.maxhealth = maxhealth
        self.alive = alive
    
    def draw_health_bar(self, camera):
        screen_position = camera.apply(self)
        health_bar_position = (screen_position.x, screen_position.y - 10)
        health_bar_width = self.width
        health_bar_height = 5
        health_bar_rect = pygame.Rect(health_bar_position, (health_bar_width, health_bar_height))
            
        if self.char_type == 'enemy' and self.alive:
            pygame.draw.rect(self.screen, (0, 150, 150), health_bar_rect)
            if self.health != 0:
                health_bar_rect2 = pygame.Rect(health_bar_position, (health_bar_width*self.health/self.maxhealth, health_bar_height))
                pygame.draw.rect(self.screen, (0, 0, 200), health_bar_rect2)
                    
    def update_action(self,new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if len(self.animation_list[self.action]) > 0:
            self.image = self.animation_list[self.action][self.frame_index]
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width()), int(self.image.get_height())))
        self.image = pygame.transform.flip(self.image,self.flip,False)
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            
    def loser(self,player):
        self.nodNo-=1
        if self.char_type != 'player' and self.nodNo <= 0:
            self.flip = not self.flip
            self.nodNo = random.randint(15,30)
            self.update(0,self.flip,self.health,self.maxhealth,self.alive)
        
class Body(pygame.sprite.Sprite):
    def __init__(self, screen, directory, image_set, char_type, x, y, scale, flip, translation, jsondata):
        super().__init__()
        
        self.screen = screen
        self.directory = directory
        self.char_type = char_type
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0
        self.flip = flip
        self.image_set = image_set

        animation_types = ['idle','move','shoot','death','jump','dead']
        body_data = jsondata['CharGen_data']['PlayerSprites']['body_data']
        for animation in animation_types:
            temp_list = []
            if animation in body_data:
                for image_data in body_data[animation]:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
                    image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                    temp_list.append(image)
            self.animation_list.append(temp_list) 

        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.translation = translation # 0 #translation+self.height

        self.width = self.image.get_width()
        self.rect.midbottom = (x,y)
        self.reset_y = 0
        
    def update(self,action,flip):
        self.flip = flip
        self.update_action(action)
        self.update_animation()
                    
    def update_action(self,new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if len(self.animation_list[self.action]) > 0:
            self.image = self.animation_list[self.action][self.frame_index]
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width()), int(self.image.get_height())))
        self.image = pygame.transform.flip(self.image,self.flip,False)
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            

class Legs(pygame.sprite.Sprite):
    def __init__(self, screen, directory, image_set, char_type, x, y, scale, flip, translation, jsondata):
        super().__init__()
        self.rect = pygame.Rect(x, y, 30, 10)  # Non-visual, only a rect
        
        self.action = 0
        self.flip = flip
        self.frame_index = 0
        self.animation_list = []
        self.char_type = char_type
        self.screen = screen
        self.directory = directory
        self.update_time = pygame.time.get_ticks()
        self.image_set = image_set

        animation_types = ['idle','move','shoot','death','jump','dead']
        legs_data = jsondata['CharGen_data']['PlayerSprites']['legs_data']
        for animation in animation_types:
            temp_list = []
            if animation in legs_data:
                for image_data in legs_data[animation]:
                    image_bytes = base64.b64decode(image_data)
                    image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
                    image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                    temp_list.append(image)
            self.animation_list.append(temp_list) 

        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.translation = translation #translation+self.height
        self.rect.midbottom = (x,y)
        self.reset_y = 0
        
    def update(self,action,flip):
        self.flip = flip
        self.update_action(action)
        self.update_animation()
                    
    def update_action(self,new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
        
    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        if len(self.animation_list[self.action]) > 0:
            self.image = self.animation_list[self.action][self.frame_index]
        self.image = pygame.transform.scale(self.image,(int(self.image.get_width()), int(self.image.get_height())))
        self.image = pygame.transform.flip(self.image,self.flip,False)
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

class Shadow(pygame.sprite.Sprite):
    def __init__(self, screen, directory, char_type, x, y, scale, flip, translation):
        super().__init__()
        self.rect = pygame.Rect(x, y, 30, 10)  # Non-visual, only a rect
        self.action = 0
        self.char_type = char_type
        self.screen = screen
        self.directory = directory
        self.scale=scale

        img = pygame.image.load('./templates/shadow.png').convert_alpha()
        img = pygame.transform.scale(img,(int(img.get_width()) * scale * 1.5, int(img.get_height() * scale)))
        self.img2 = pygame.transform.scale(img,(int(img.get_width()) * scale * 7, int(img.get_height() * scale * 4.5)))

        self.image = img
        self.rect = self.image.get_rect()
        self.height = self.image.get_height()
        self.width = self.image.get_width()
        self.translation = translation
        self.rect.midbottom = (x,y)
        self.reset_y = 0
        
    def update(self,alive,flip):
        self.flip = flip
        
        if not alive:
            self.image = self.img2

