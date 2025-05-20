import pygame
import os

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.width = 288
        self.height = 160
        self.scale = 2
        self.pos = pos
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 2
        # Reduced health
        self.max_health = 10
        self.health = self.max_health
        self.damage = 50
        self.facing_right = True
        
        # Add sound effects
        self.laugh_sound = pygame.mixer.Sound(r"E:\Python\Proiect Python V\Projects\Assets\Sounds\evil-laugh-boss.mp3")  # Changed from cleaver-sound
        self.attack_sound = pygame.mixer.Sound(r"E:\Python\Proiect Python V\Projects\Assets\Sounds\cleaver-sound.mp3")  # Changed from evil-laugh-boss
        self.laugh_sound.play()  # Play initial laugh when boss spawns
        
        # Add sound control variable
        self.attack_sound_played = False
        
        # Rest of the initialization...
        self.current_animation = "idle"
        self.animation_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        self.gravity = 0.8
        self.on_ground = False
        self.hit_timer = 0
        self.hit_duration = 20
        
        self.animations = self._load_animations()
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect(topleft=pos)
        
        self.attack_cooldown = 0
        self.attack_range = 100
        self.is_attacking = False

    def update(self, player, platforms):
        if self.health <= 0:
            self.current_animation = "death"
            if self.animation_timer >= 1:
                self.animation_timer = 0
                if self.animation_index < len(self.animations["death"]) - 1:
                    self.animation_index += 1
                else:
                    self.kill()
                    return
            self.animation_timer += self.animation_speed
            # Update current frame for death animation
            self.image = self.animations[self.current_animation][self.animation_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
            return  # Stop processing other updates when dying

        # Rest of the update method remains the same...
    
        # Apply gravity
        if not self.on_ground:
            self.velocity_y += self.gravity

        # Handle hit animation
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.current_animation = "idle"
                self.animation_index = 0

        # Only process movement and attacks if not being hit
        if self.hit_timer <= 0:
            player_center = player.rect.center
            boss_center = self.rect.center
            
            # Calculate direction to player
            dx = player_center[0] - boss_center[0]
            
            # Update facing direction
            if dx > 0:
                self.facing_right = False
            else:
                self.facing_right = True
            
            # Movement and attack logic
            if not self.is_attacking:
                distance = abs(dx)
                if distance > self.attack_range:
                    self.velocity_x = self.speed if dx > 0 else -self.speed
                    self.current_animation = "walk"
                    self.attack_sound_played = False  # Reset sound flag when walking
                else:
                    self.velocity_x = 0
                    if self.attack_cooldown <= 0:
                        # Start attack
                        self.current_animation = "cleave"
                        self.is_attacking = True
                        self.attack_cooldown = 60
                        # Play attack sound
                        if not self.attack_sound_played:
                            self.attack_sound.play()
                            self.attack_sound_played = True
                    else:
                        self.current_animation = "idle"
                        self.attack_sound_played = False  # Reset sound flag when idle

        # Update position and handle collisions
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # Platform collisions
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

        # Update cooldowns and animation
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Modify the animation update section to not use modulo for death animation
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            if self.current_animation == "death":
                if self.animation_index < len(self.animations["death"]) - 1:
                    self.animation_index += 1
            else:
                self.animation_index = (self.animation_index + 1) % len(self.animations[self.current_animation])
            
            if self.is_attacking and self.animation_index >= len(self.animations["cleave"]) - 1:
                self.is_attacking = False
                self.current_animation = "idle"
                self.animation_index = 0

        # Update current frame
        self.image = self.animations[self.current_animation][self.animation_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def take_damage(self, amount):
        self.health -= amount
        if self.health > 0:
            self.current_animation = "hit"
            self.animation_index = 0
            self.hit_timer = self.hit_duration
            self.is_attacking = False
            # Random chance to laugh when hit (e.g., 30% chance)
            if pygame.time.get_ticks() % 3 == 0:  # Simple way to get a 1/3 chance
                self.laugh_sound.play()
    def _load_animations(self):
        animations = {}
        base_path = r"E:\Python\Proiect Python V\Projects\Assets\Images\Boss"
        
        animation_data = {
            "idle": ("demon_idle", 6),
            "walk": ("demon_walk", 12),
            "cleave": ("demon_cleave", 15),
            "hit": ("demon_take_hit", 5),
            "death": ("demon_death", 22)
        }
        
        for anim_name, (folder_name, frame_count) in animation_data.items():
            frames = []
            for i in range(1, frame_count + 1):
                frame_path = os.path.join(base_path, f"{folder_name}_{i}.png")
                frame = pygame.image.load(frame_path).convert_alpha()
                frame = pygame.transform.scale(frame, 
                                            (self.width * self.scale, 
                                             self.height * self.scale))
                if not self.facing_right:
                    frame = pygame.transform.flip(frame, True, False)
                frames.append(frame)
            animations[anim_name] = frames
        
        return animations

    def draw_health_bar(self, screen):
        # Health bar background
        bar_width = 200
        bar_height = 20
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 30
        
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        
        # Current health
        health_width = (self.health / self.max_health) * bar_width
        pygame.draw.rect(screen, (0, 255, 0), (x, y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, (0, 0, 0), (x, y, bar_width, bar_height), 2)