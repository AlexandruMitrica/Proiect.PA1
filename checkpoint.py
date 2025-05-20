import pygame

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((30, 60))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(topleft=pos)
