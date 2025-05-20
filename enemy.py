import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.animations = {}
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 8

        self.scale = 2  # ⚠️ Mărime dublă
        self.width = 80
        self.height = 64

        self._load_animations()

        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=pos)

        self.speed = 2
        self.velocity_y = 0
        self.on_ground = False
        self.health = 3
        self.state = "idle"

        self.direction = 1
        self.attack_range = 50
        self.attack_cooldown = 0

    def _load_animations(self):
        def load_animation(name):
            sheet = pygame.image.load(f"assets/images/enemy/ciuperca/{name}.png").convert_alpha()
            sheet_width = sheet.get_width()
            frame_count = sheet_width // self.width
            frames = []
            for i in range(frame_count):
                frame = sheet.subsurface(pygame.Rect(i * self.width, 0, self.width, self.height))
                # 🔥 Dublează dimensiunea
                frame = pygame.transform.scale(frame, (self.width * self.scale, self.height * self.scale))
                frames.append(frame)
            return frames

        for anim in ["idle", "run", "attack", "hit", "die"]:
            self.animations[anim] = load_animation(anim)

    def update(self, player, platforms):
        if self.state == "die":
            self._update_animation()
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance < self.attack_range and self.attack_cooldown == 0:
            self.state = "attack"
            player.take_damage(1)
            self.attack_cooldown = 60
        elif abs(dx) < 300:
            self.state = "run"
            self.direction = 1 if dx > 0 else -1
            self.rect.x += self.direction * self.speed
        else:
            self.state = "idle"

        self.velocity_y += 0.5
        if self.velocity_y > 10:
            self.velocity_y = 10
        self.rect.y += self.velocity_y

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self._update_animation()

    def _update_animation(self):
        if self.state in self.animations:
            if self.current_animation != self.state:
                self.current_animation = self.state
                self.current_frame = 0
                self.frame_timer = 0

            self.frame_timer += 1
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.animations[self.current_animation]):
                    if self.state == "attack":
                        self.state = "idle"
                    elif self.state == "die":
                        self.kill()
                        return
                    self.current_frame = 0

            self.image = self.animations[self.current_animation][self.current_frame]
            if self.direction == -1:
                self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, amount):
        if self.state != "die":
            self.health -= amount
            self.state = "hit"
            self.current_frame = 0
            if self.health <= 0:
                self.state = "die"
