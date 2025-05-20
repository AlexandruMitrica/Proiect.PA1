import pygame

class Camera:
    def __init__(self, width, height):
        self.camera_rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, target):
        return target.rect.move(self.camera_rect.topleft)

    def update(self, target):
        # Urmărește playerul
        x = -target.rect.centerx + int(self.width / 2)
        y = -target.rect.centery + int(self.height / 2)

        # Limitează mișcarea camerei (dacă vrei)
        x = min(0, x)  # nu mergem mai la stânga decât marginea hărții
        y = min(0, y)

        self.camera_rect = pygame.Rect(x, y, self.width, self.height)


