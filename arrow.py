import pygame
import math

class Arrow(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, damage):
        super().__init__()
        self.image = pygame.image.load("assets/images/player/archer/arrow.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 10))

        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=start_pos)

        self.velocity = 10
        dist = math.hypot(dx, dy)
        self.dir_x = dx / dist
        self.dir_y = dy / dist
        self.damage = damage

    def update(self):
        self.rect.x += self.dir_x * self.velocity
        self.rect.y += self.dir_y * self.velocity

        if self.rect.right < 0 or self.rect.left > 1920 or self.rect.bottom < 0 or self.rect.top > 1080:
            self.kill()
