import pygame
from arrow import Arrow


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.scale = 2
        self.animations = {}
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 5
        self.facing_right = True
        self.is_firing = False

        self._load_animations()
        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-20, -10)  # collider mai precis

        self.speed = 4
        self.velocity_y = 0
        self.on_ground = False

        # Stats
        self.health = 5  # Start with 5 hearts
        self.max_health = 5
        self.lives = 1
        self.spawn_point = pos
        self.coins = 0

        # Combat
        self.weapon = 2  # 1 = melee, 2 = ranged
        self.damage = 1
        self.attack_cooldown = 0
        self.projectiles = pygame.sprite.Group()
        self.arrow_sound = pygame.mixer.Sound("assets/sounds/arrow.mp3")

        # Abilities
        self.dash_cooldown = 0
        self.shield = False
        self.shield_timer = 0
        self.shield_cooldown = 0

    def _load_animations(self):
        sheet = pygame.image.load("assets/images/player/archer/GandalfHardcore Archer red sheet.png").convert_alpha()

        def extract_frames(start_x, start_y, count):
            frames = []
            for i in range(count):
                frame = sheet.subsurface(pygame.Rect(start_x + i * 64, start_y, 64, 64))
                frame = pygame.transform.scale(frame, (64 * self.scale, 64 * self.scale))
                frames.append(frame)
            return frames

        self.animations = {
            "idle": extract_frames(0, 0, 5),
            "fire": extract_frames(0, 64, 8),
            "run": extract_frames(0, 128, 11),
            "hit": extract_frames(0, 192, 5),
            "death": extract_frames(0, 256, 6),
        }

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        dx = 0

        # Firing
        if mouse_pressed and self.attack_cooldown == 0 and not self.is_firing:
            self.is_firing = True
            self.attack()

        # Movement + animation
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -self.speed
            self._rotate_player(-1)
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = self.speed
            self._rotate_player(1)
            moving = True

        # Dash
        if keys[pygame.K_LSHIFT] and self.dash_cooldown == 0:
            dx *= 3.5
            self.dash_cooldown = 60

        # Apply X movement
        self.rect.x += dx
        self.hitbox.x += dx

        # Gravity
        self.velocity_y += 0.5
        self.velocity_y = min(self.velocity_y, 10)
        self.rect.y += self.velocity_y
        self.hitbox.y += self.velocity_y

        # Collision with platforms
        self.on_ground = False
        for platform in platforms:
            if self.hitbox.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.hitbox.bottom = platform.rect.top
                    self.rect.bottom = self.hitbox.bottom
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.hitbox.top = platform.rect.bottom
                    self.rect.top = self.hitbox.top
                    self.velocity_y = 0

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = -10

        # Shield activation
        if keys[pygame.K_r] and self.shield_cooldown == 0:
            self.shield = True
            self.shield_timer = 120
            self.shield_cooldown = 300

        # Change weapon
        if keys[pygame.K_1]: self.weapon = 1
        if keys[pygame.K_2]: self.weapon = 2

        # Cooldowns
        self.attack_cooldown = max(0, self.attack_cooldown - 1)
        self.dash_cooldown = max(0, self.dash_cooldown - 1)
        self.shield_cooldown = max(0, self.shield_cooldown - 1)
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False

        # Animation logic
        self._handle_animation(moving)
        self._update_animation()

        # Update arrows
        self.projectiles.update()

    def _handle_animation(self, moving):
        if self.is_firing:
            self.current_animation = "fire"
            if self.current_frame >= len(self.animations["fire"]) - 1:
                self.is_firing = False
        elif moving:
            self.current_animation = "run"
        else:
            self.current_animation = "idle"

    def _update_animation(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame += 1

            # Loop or reset animation
            frames = self.animations[self.current_animation]
            if self.current_frame >= len(frames):
                self.current_frame = 0
                if self.current_animation == "fire":
                    self.is_firing = False

            # Set image
            img = frames[self.current_frame]
            if not self.facing_right:
                img = pygame.transform.flip(img, True, False)
            self.image = img

    def _rotate_player(self, direction):
        self.facing_right = direction == 1

    def attack(self):
        if self.weapon == 2:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            arrow = Arrow(self.rect.center, (mouse_x, mouse_y), self.damage)
            self.projectiles.add(arrow)
            self.arrow_sound.play()
            self.attack_cooldown = 25
        else:
            # Future melee attack here
            self.attack_cooldown = 15

    def take_damage(self, amount):
        if self.shield:
            print("Blocked with shield!")
            return
            
        self.health -= amount
        if self.health <= 0:
            print("GAME OVER")
            self.kill()
            return "game_over"

    # Remove the respawn method since we're not using lives system anymore
    def respawn(self):
        pass

class Test1:
    def __init__(self, screen):
        # ... (keep existing initialization code)
        
        # Add heart properties
        self.heart_size = 20  # Size of each heart triangle
        self.heart_spacing = 30  # Space between hearts
        self.heart_color = (255, 0, 0)  # Red color
        
    def draw_hearts(self):
        for i in range(self.player.health):
            # Calculate position for each heart
            x = 20 + (i * self.heart_spacing)
            y = 20
            
            # Draw triangle (heart)
            points = [
                (x, y + self.heart_size),  # Bottom point
                (x - self.heart_size//2, y),  # Top left
                (x + self.heart_size//2, y)   # Top right
            ]
            pygame.draw.polygon(self.screen, self.heart_color, points)

    def update(self):
        # ... (keep existing update code)
        
        # Update enemies and check collisions
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                result = self.player.take_damage(1)
                if result == "game_over":
                    return "back"

        # Replace text UI with heart triangles
        self.draw_hearts()
        
        # ... (keep rest of update code)