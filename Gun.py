import pygame
import random
import base64
import io
import json

class Gun(pygame.sprite.Sprite):
    def __init__(self, screen, gun_list, x, y, scale, starting_gun):
        super().__init__()
        self.screen = screen
        self.x = x
        self.y = y
        self.scale = scale * 0.5
        self.flipped1 = False
        self.flipped2 = False
        self.swap_countdown = 0
        self.random_selection = starting_gun # random.randint(0,3) # owned guns from player
        self.image, self.rate_of_fire, self.damage, self.projectile_images, self.splash_images = self.load_gun(gun_list)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.height = self.image.get_height()
        self.width = self.image.get_width()

    
    def load_gun(self, gun_list):
        # Gun_list contains dictionaries of gun data
        if self.random_selection > len(gun_list): # TODO - Remove
            gun = gun_list[random.randint(0,len(gun_list))]
            print("Remove this check, also remove it from Arena.py where player starts with extra guns, \"total_count == players_gun_number+1\" ")
        else:
            gun = gun_list[self.random_selection]
                
        gun_cat = gun['category']
        gun_image_data = gun['base_gun_image_data'] if not gun['upgraded'] else gun['upgraded_gun_image_data']
        rate_of_fire = gun['rate_of_fire']
        damage = gun['damage']
        owned = gun['owned']
        upgraded = gun['upgraded']
        projectile_images = gun['base_projectile_data'] if not gun['upgraded'] else gun['upgraded_projectile_data']
        projectile_images = self.imgLoader(projectile_images, 2)
        splash_images = gun['base_splash_data'] if not gun['upgraded'] else gun['upgraded_splash_data']
        splash_images = self.imgLoader(splash_images, 4)

        # Decode the image data
        gun_image_bytes = base64.b64decode(gun_image_data)
        gun_image = pygame.image.load(io.BytesIO(gun_image_bytes)).convert_alpha()
        gun_image = pygame.transform.scale(gun_image, (int(gun_image.get_width() * self.scale), int(gun_image.get_height() * self.scale)))

        return gun_image, rate_of_fire, damage, projectile_images, splash_images

    def update(self, angle, gunFlip, x ,y, weapon_up, weapon_down, gun_list, char_type):
        if weapon_up:
            self.swap_weapon(weapon_up, weapon_down, gun_list, x, y)
        if weapon_down:
            self.swap_weapon(weapon_up, weapon_down, gun_list, x, y)
        if self.swap_countdown < 30:
            self.swap_countdown += 1
            
        self.rect = self.image.get_rect(center=(x, y))
        if gunFlip:
            if char_type == 'player':
                self.image = pygame.transform.rotate(self.original_image, angle)
                self.image = pygame.transform.flip(self.image,False,False)
            else:
                self.image = pygame.transform.rotate(self.original_image, -angle)
                self.image = pygame.transform.flip(self.image,False,True)

        else:
            if char_type == 'player':
                self.image = pygame.transform.rotate(self.original_image, -angle)
                self.image = pygame.transform.flip(self.image,False,True)
            else:
                self.image = pygame.transform.rotate(self.original_image, angle)
                self.image = pygame.transform.flip(self.image,False,False)

    def swap_weapon(self, weapon_up, weapon_down, gun_list, x, y):
        if self.swap_countdown == 30:
            for i in range(len(gun_list)+1):
                if weapon_up:
                    if self.random_selection < len(gun_list)-1:
                        self.random_selection += 1
                    else:
                        self.random_selection = 0
                if weapon_down:
                    if self.random_selection > 0:
                        self.random_selection -= 1
                    else:
                        self.random_selection = len(gun_list)-1
                if gun_list[self.random_selection]['owned'] == True:
                    break
            self.swap_countdown = 0

        self.image, self.rate_of_fire, self.damage, self.projectile_images, self.splash_images = self.load_gun(gun_list)
        self.original_image = self.image
        self.rect = self.image.get_rect(center=(x, y))
        self.height = self.image.get_height()
        self.width = self.image.get_width()
            
    def imgLoader(self,img_data, scale_multiplier):
        temp_list = []

        for image_data in img_data:
            image_bytes = base64.b64decode(image_data)
            img = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
            img = pygame.transform.scale(img,(int(img.get_width()) * self.scale * scale_multiplier, int(img.get_height() * self.scale * scale_multiplier)))
            temp_list.append(img)

        return temp_list
        
