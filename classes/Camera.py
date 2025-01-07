import pygame

class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.panningspeed = 1

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, player):
        target_x = -player.face.rect.centerx + int(self.width / 2)
        target_y = -player.face.rect.centery + int(self.height / 2)

        offset_x = int(player.mouseAim.x * (self.width/3))
        offset_y = int(player.mouseAim.y * (self.height/3))

        target_x -= offset_x
        target_y -= offset_y

        # Clamp the target position to map boundaries
        target_x = max(min(target_x, 0), -(self.map_width - self.width))
        target_y = max(min(target_y, 0), -(self.map_height - self.height))

        self.target = pygame.math.Vector2(target_x, target_y)

        # Smoothly move the camera towards the target position
        self.camera.x += (self.target.x - self.camera.x) * 0.1
        self.camera.y += (self.target.y - self.camera.y) * 0.1