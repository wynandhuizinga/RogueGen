import pygame
import os
import re
import random
import json
import base64
import io
from Limbs import Face, Body, Legs, Shadow
from Projectile import Bullet, Splash
from Explosion import Explosion
from Prop import Prop
from ProximityCircle import ProximityCircle
from Gun import Gun

class Character(pygame.sprite.Sprite):

    def __init__(self, seed, screen, map_width, map_height, directory, gun_list, char_type, x, y, scale, action, speed, health, image_set=0, aimAccuracy=0, starting_gun=None):
        random.seed(seed)
        self.char_type = char_type
        self.direction = pygame.math.Vector2(0, 0)
        self.mouseAim = pygame.math.Vector2(0, 0)
        self.mouse_pos = pygame.mouse.get_pos()
        self.x = x
        self.y = y

        self.speed = speed
        self.mobile = False
        self.screen = screen
        self.map_width = map_width
        self.map_height = map_height
        self.directory = directory
        self.image_set=image_set # 0 is player, rest is enemies -> hardcoded.
        
        self.flip = flip = False
        self.gunFlip = False
        self.shoot = False
        self.aim_direction = 0
        self.shoot_cooldown = 0
        self.prop_spawn_cooldown = 300
        self.trapDamageCountdown = 0
        self.ammo = 2000
        self.scale = scale
        self.translation = translation = 5
        self.vel_y = 0
        self.GRAVITY = 0.5

        self.health = self.maxhealth = health
        self.alive = True
        self.action = action
        self.aired = False
        self.jump = False
        self.update_time = pygame.time.get_ticks()
        self.time_of_death = None
        self.credits = 0

        pattern = re.compile(rf'^{self.image_set} - [0-9]{{8}}.*\.json$') # if failure here at startup, validate if all characters have been created
        for file_name in os.listdir(self.directory):
            match = pattern.match(file_name)
            if match:
                with open(os.path.join(self.directory, file_name), 'r', encoding='utf-8') as f:
                    jsondata = json.load(f)
        self.jsondata = jsondata

        self.face = Face(screen, directory, image_set, char_type, x, y, scale, flip, translation, jsondata)
        self.body = Body(screen, directory, image_set, char_type, x, y + 30, scale, flip, translation, jsondata)
        self.legs = Legs(screen, directory, image_set, char_type, x, y + 60, scale, flip, translation, jsondata)
        self.shadow = Shadow(screen, directory, char_type, x, y + 90, scale, flip, translation)
        if self.char_type == 'player':
            self.healthbar = Healthbar(self.health, self.maxhealth, self.jsondata)
            self.gun = Gun(screen, gun_list, self.body.rect.center[0], self.body.rect.center[1], scale, starting_gun)
        else:
            self.gun = Gun(screen, gun_list, self.body.rect.center[0], self.body.rect.center[1], scale, random.randint(0,len(gun_list)))

        self.proximity_circle = ProximityCircle(self)

        self.projectiles = self.gun.projectile_images
        self.splashes = self.gun.splash_images
        self.explosions = self.explosionLoader(jsondata)
        if char_type == 'enemy':
            self.props = self.propLoader(jsondata)

        # Victory
        if char_type == 'enemy':
            victory_image_data = self.jsondata['Image_data']['revealed']
            victory_image_bytes = base64.b64decode(victory_image_data)
            victory_image = pygame.image.load(io.BytesIO(victory_image_bytes)).convert_alpha()
            self.victory_image = pygame.transform.scale(victory_image, (int(victory_image.get_width()), int(victory_image.get_height())))
            self.victory_rect = self.victory_image.get_rect(center=(int(self.screen.get_width() - victory_image.get_width() / 2), int(self.screen.get_height() / 2)))
            
            regular_image_data = self.jsondata['Image_data']['regular']
            regular_image_bytes = base64.b64decode(regular_image_data)
            regular_image = pygame.image.load(io.BytesIO(regular_image_bytes)).convert_alpha()
            self.regular_image = pygame.transform.scale(regular_image, (int(regular_image.get_width()), int(regular_image.get_height())))
            self.regular_rect = self.regular_image.get_rect(center=(self.screen.get_width() - int(regular_image.get_width() / 2), int(self.screen.get_height() / 2)))
            
            wet_image_data = self.jsondata['Image_data']['wet']
            wet_image_bytes = base64.b64decode(wet_image_data)
            wet_image = pygame.image.load(io.BytesIO(wet_image_bytes)).convert_alpha()
            self.wet_image = pygame.transform.scale(wet_image, (int(wet_image.get_width()), int(wet_image.get_height())))
            self.wet_rect = self.wet_image.get_rect(center=(int(self.screen.get_width() - wet_image.get_width() / 2), int(self.screen.get_height() / 2)))

        # Enemy AI
        self.playerDead = False
        self.aimAccuracy = aimAccuracy
        
    def update(self, action, bullet_group, prop_group, map_generator, camera, player, gun_list, weapon_up=False, weapon_down=False):
        if self.char_type == 'player':
            self.healthbar.update(self.screen, self.health, self.maxhealth)
            
        if self.alive:
            self.getDamage(bullet_group, map_generator)

            self.mouse_pos = pygame.mouse.get_pos()
            world_mouse_pos = pygame.Vector2(self.mouse_pos) - camera.camera.topleft
            aim_direction = world_mouse_pos - pygame.Vector2(self.body.rect.center)
            angle = aim_direction.angle_to(pygame.Vector2(1, 0))
            if self.char_type == 'player':
                if self.mouse_pos[0] > self.screen.get_width() // 2:
                    self.gunFlip = True
                    self.gun.update(angle, self.gunFlip, self.body.rect.center[0], self.body.rect.center[1], weapon_up, weapon_down, gun_list, self.char_type)
                else:
                    self.gunFlip = False
                    self.gun.update(angle, self.gunFlip, self.body.rect.center[0], self.body.rect.center[1], weapon_up, weapon_down, gun_list, self.char_type)
                if weapon_up or weapon_down:
                    self.projectiles = self.gun.projectile_images
                    self.splashes = self.gun.splash_images
                    weapon_up = weapon_down = False
            elif self.char_type == 'enemy':
                player_pos = player.body.rect.center
                aim_direction = pygame.Vector2(player_pos) - pygame.Vector2(self.body.rect.center)
                angle = aim_direction.angle_to(pygame.Vector2(1, 0))
                self.gunFlip = player_pos[0] < self.body.rect.center[0]
                self.gun.update(angle, self.gunFlip, self.body.rect.center[0], self.body.rect.center[1], False, False, gun_list, self.char_type)

        if self.health < 1:
            self.alive = False
            if self.char_type == 'player' and self.credits > 0:
                self.loseCredits()

        self.legs.update(self.action, self.flip)
        self.body.update(self.action, self.flip)
        if not self.playerDead:
            self.face.update(self.action, self.flip, self.health, self.maxhealth, self.alive)

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.prop_spawn_cooldown > 0:
            self.prop_spawn_cooldown -= 1
        if not self.alive:
            self.playDead()

    def move(self, moving_left, moving_up, moving_right, moving_down, jump, map_generator, prop_group):
        self.direction = pygame.math.Vector2(0, 0)
        if self.alive:
            if moving_left:
                self.direction.x = -1
            if moving_right:
                self.direction.x = 1
            if moving_up:
                self.direction.y = -1
            if moving_down:
                self.direction.y = 1
            if moving_left:
                self.flip = True
            if moving_right:
                self.flip = False

            if self.direction.length() > 0:
                self.direction.normalize_ip()

            movement = self.direction * self.speed

            new_face_rect = self.face.rect.move(movement)
            new_body_rect = self.body.rect.move(movement)
            new_gun_rect = self.gun.rect.move(movement)
            new_legs_rect = self.legs.rect.move(movement)
            new_shadow_rect = self.shadow.rect.move(movement)
            new_proximity_circle_rect = self.proximity_circle.rect.move(movement)

            if not map_generator.is_collision(new_shadow_rect) and (self.aired or not self.is_prop_collision(new_shadow_rect, prop_group)):
                self.face.rect = new_face_rect
                self.body.rect = new_body_rect
                self.gun.rect = new_gun_rect
                self.legs.rect = new_legs_rect
                self.shadow.rect = new_shadow_rect
                self.proximity_circle.rect = new_proximity_circle_rect

            self.jump = jump
            self.jumping(self.jump, self.aired)

            # Reset & positioning limbs, shadows, guns etc.
            if self.alive and not self.aired:
                self.face.rect.center = self.shadow.rect.center
                self.face.rect.top = self.shadow.rect.top - self.legs.height * 0.6 - self.body.height * 0.8 - self.face.height * 0.7
                self.body.rect.center = self.face.rect.center
                self.body.rect.top = self.shadow.rect.top - self.legs.height * 0.6 - self.body.height * 0.8
                if self.char_type == 'player':
                    self.gun.rect.center = self.face.rect.center
                self.legs.rect.center = self.shadow.rect.center
                self.legs.rect.top = self.shadow.rect.top - self.legs.height * 0.6
                self.shadow.rect.left = max(0, min(self.shadow.rect.left, self.map_width - self.shadow.rect.width))
                self.shadow.rect.top = max(0, min(self.shadow.rect.top, self.map_height - self.shadow.rect.height))

            if self.aired:
                self.update_action(4)
            elif moving_left or moving_up or moving_right or moving_down:
                self.update_action(1)
            else:
                self.update_action(0)

    def cameraAim(self, mouseX, mouseY):
        self.mouseAim = pygame.math.Vector2(0, 0)
        self.mouseAim.x = (mouseX - self.screen.get_width() / 2) / (self.screen.get_width() / 2)
        self.mouseAim.y = (mouseY - self.screen.get_height() / 2) / (self.screen.get_height() / 2)

    def receiveCredits(self, amount):
        self.credits += amount

    def loseCredits(self):
        self.credits = 0

    def getDamage(self, bullet_group, map_generator):
        for bullet in bullet_group:
            if (self.face.rect.colliderect(bullet.rect) or self.body.rect.colliderect(bullet.rect) or self.legs.rect.colliderect(bullet.rect)) and bullet.owner != self.char_type and not self.aired:
                if self.alive:
                    self.health -= bullet.damage
                    bullet.hit = True
            if map_generator.is_collision(bullet.rect):
                bullet.hit = True

        current_position = self.get_grid_position(map_generator)
        if current_position in map_generator.traps and not self.aired:
            if not map_generator.trap_states[current_position]:  # Check if the trap is not revealed
                if self.trapDamageCountdown < 1:
                    self.health -= 20
                    self.trapDamageCountdown = 100
                    # Change trap image to a visible trap image when triggered
                    new_trap_image = random.choice(map_generator.all_traps[1:])  # Choose any image except the transparent one
                    map_generator.traps[current_position] = new_trap_image
                    map_generator.trap_states[current_position] = True  # Mark the trap as revealed
            else:
                if self.trapDamageCountdown < 1:
                    self.health -= 20
                    self.trapDamageCountdown = 100
        self.trapDamageCountdown -= 1

    def playDead(self):
        # Clamping camera
        self.shadow.update(self.alive, self.flip)
        self.flip = False
        self.face.rect.top = self.shadow.rect.top - self.shadow.rect.height * 0.3
        self.face.rect.left = self.shadow.rect.left + self.face.rect.width * 0.2

        self.body.rect.top = self.shadow.rect.top - self.shadow.rect.height * 0.3
        self.body.rect.left = self.face.rect.left + self.face.rect.width * 0.7

        if self.char_type == 'player':
            self.gun.rect.top = self.shadow.rect.top - self.shadow.rect.height * 0.3
            self.gun.rect.left = self.face.rect.left + self.face.rect.width * 0.7

        self.legs.rect.top = self.shadow.rect.top - self.shadow.rect.height * 0.3
        self.legs.rect.left = self.body.rect.left + self.body.rect.width * 0.8
        self.shadow.rect.left = max(0, min(self.shadow.rect.left, self.map_width - self.shadow.rect.width))
        self.shadow.rect.top = max(0, min(self.shadow.rect.top, self.map_height - self.shadow.rect.height))

        # Dead animation
        self.update_action(5)

    def get_grid_position(self, map_generator):
        return (self.shadow.rect.centerx // map_generator.TILE_SIZE, self.shadow.rect.centery // map_generator.TILE_SIZE)

    def jumping(self, jump, aired):
        if jump and not self.aired:
            self.vel_y = -10
            self.aired = True
            self.jump = False
        if self.aired:
            self.vel_y += self.GRAVITY
            self.face.rect.top += self.vel_y
            self.body.rect.top += self.vel_y
            if self.char_type == 'player':
                self.gun.rect.top += self.vel_y
            self.legs.rect.top += self.vel_y
        if self.vel_y > 9:
            self.vel_y = 0
            self.aired = False

    def fire(self, aim_direction):
        if self.alive and self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = self.gun.rate_of_fire
            bullet = Bullet(self.gun.rect.centerx, self.gun.rect.centery, self.direction, 0.5, aim_direction, self.projectiles, self.gun.damage, self.char_type, self.splashes)
            self.ammo -= 1
            return bullet

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    

    def propLoader(self,jsondata):
        props_data = jsondata['CharGen_data']['PropsList']
        temp_list = []

        for image_data in props_data:
            image_bytes = base64.b64decode(image_data[5])
            img = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
            img = pygame.transform.scale(img,(int(img.get_width()), int(img.get_height())))
            temp_list.append(img)

        return temp_list
        
    def explosionLoader(self, jsondata):
        explosion_data_sets = jsondata['CharGen_data']['PlayerSprites']['attack_data']['explosion_data']
        all_explosions = []

        for explosion_data in explosion_data_sets:
            temp_list = []
            for image_data in explosion_data:
                image_bytes = base64.b64decode(image_data)
                img = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()) * self.scale * 2, int(img.get_height()) * self.scale * 2))
                temp_list.append(img)
            all_explosions.append(temp_list)

        return all_explosions
        
    def draw_character(self):
        self.screen.blit(self.regular_image, self.regular_rect.topleft) # TODO - re-add

    def draw_character_won(self):
        self.screen.blit(self.victory_image, self.regular_rect.topleft) # TODO - re-add

    def draw_character_wet(self):
        self.screen.blit(self.wet_image, self.regular_rect.topleft) # TODO - re-add

    def get_sprites(self):
        if self.char_type == 'player':
            return [self.shadow, self.face, self.body, self.legs, self.gun, self.proximity_circle]
        else:
            return [self.shadow, self.face, self.body, self.legs, self.gun, self.proximity_circle]
    
    def spawn_prop(self, player, prop_group, map_generator):
        if player.alive and self.prop_spawn_cooldown == 0:            
            if self.char_type == 'player':
                pass
            else: 
                for _ in range(10):  # Try up to 10 times to find a valid position
                    x = self.body.rect.centerx + random.randint(-500, 500)
                    y = self.body.rect.centery + random.randint(-500, 500)
                    prop_rect = pygame.Rect(x, y, 50, 50)  # Adjust the size according to your prop size
                    
                    if not map_generator.is_collision(prop_rect):
                        random_number = random.randint(0,len(self.explosions)-1)
                        prop = Prop(x, y, self.props[random.randint(0, len(self.props)-1)],self.explosions[random_number])
                        prop_group.add(prop)
                        self.prop_spawn_cooldown = random.randint(100, 300)
                        break
                        
    def is_prop_collision(self, rect, prop_group):
        for prop in prop_group:
            if rect.colliderect(prop.rect):
                return True
        return False
    
class Healthbar(pygame.sprite.Sprite):
    def __init__(self, health, maxhealth, jsondata):
        pygame.sprite.Sprite.__init__(self)
        self.maxhealth = maxhealth
        jsondata = jsondata['CharGen_data']['PlayerSprites']['healthbar_data']
        image_bytes = base64.b64decode(jsondata)
        self.image = pygame.image.load(io.BytesIO(image_bytes)).convert_alpha()
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.topleft = (int(self.image.get_width()/20), int(self.image.get_height()/20))
    
    def update(self, screen, health, maxhealth):
        self.image2 = pygame.transform.chop(self.image, (self.width -  self.width * (health/maxhealth), self.height, self.width, self.height))
        screen.blit(self.image2, (screen.get_width()/30,screen.get_height()/25))
        pygame.draw.rect(screen, (0,0,200), (screen.get_width()/30, screen.get_height()/25, self.width, self.height), 1) # border