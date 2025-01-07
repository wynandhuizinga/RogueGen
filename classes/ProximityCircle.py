import pygame

class ProximityCircle(pygame.sprite.Sprite):
    def __init__(self, character, radius=70):
        super().__init__()
        self.character = character
        self.radius = radius
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(character.x, character.y))
        self.update_position()

    def update_position(self):
        self.rect.center = (self.character.x, self.character.y)

    def update(self):
        self.update_position()