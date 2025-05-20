import pygame
import os
import math

class Enemy1(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.scale = 2
        self.animations = {}
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 6
        self.load_animations()

        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)

        self.speed = 2
        self.health = 3

    def load_animations(self):
        animation_names = ["idle", "run", "attack", "die", "hurt"]
        frame_width, frame_height = 64, 64

        for name in animation_names:
            path = f"assets/images/enemy/liliac/{name}.png"
            if not os.path.exists(path):
                print(f"Animation file not found: {path}")
                continue
            sheet = pygame.image.load(path).convert_alpha()
            frames = []

            sheet_width = sheet.get_width()
            num_frames = sheet_width // frame_width

            for i in range(num_frames):
                frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (frame_width * self.scale, frame_height * self.scale))
                frames.append(frame)

            self.animations[name] = frames

    def update(self, player, platforms=None):
        if self.health <= 0:
            return

        # Mișcare spre jucător
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            self.rect.x += int(self.speed * dx)
            self.rect.y += int(self.speed * dy)

        # Schimbă animația
        if self.rect.colliderect(player.rect):
            self.current_animation = "attack"
            player.take_damage(1)
        else:
            self.current_animation = "run"

        # Actualizare frame
        self.frame_timer += 1
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.animations[self.current_animation]):
                self.current_frame = 0

        self.image = self.animations[self.current_animation][self.current_frame]

    def take_damage(self, amount):
        self.health -= amount
        self.current_animation = "hurt"
        self.current_frame = 0
        if self.health <= 0:
            self.die()

    def die(self):
        self.current_animation = "die"
        self.current_frame = 0
        # Poți adăuga efecte, sunete etc.
        self.kill()
