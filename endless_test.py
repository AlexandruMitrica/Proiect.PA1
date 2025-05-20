import pygame
from pytmx import load_pygame
from Tiles.Tile import Tile
from player import Player
from enemy1 import Enemy1
from camera import Camera
import random
import math


class EndlessLevel:
    def __init__(self, screen):
        self.screen = screen

        # Initialize sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.decor_tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        # Night background elements
        self.sky_color = (20, 24, 40)  # Dark blue night sky
        self.moon_pos = (100, 100)
        self.moon_radius = 40
        self.moon_color = (230, 230, 210)
        self.moon_glow = []
        self.stars = []
        self.clouds = []

        self.generate_moon_glow(12)
        self.generate_stars(100)
        self.generate_clouds(5)

        # Hills with night colors
        self.back_hills = [
            {"color": (40, 45, 55), "points": self.generate_hill_points(0, 500, 3)},
            {"color": (30, 35, 45), "points": self.generate_hill_points(200, 450, 2)},
        ]
        self.front_hills = [
            {"color": (20, 25, 35), "points": self.generate_hill_points(-100, 400, 1)}
        ]

        # Load the Tiled map
        tmx_data = load_pygame(r'E:\Python\Proiect Python V\level_endless.tmx')

        tile_size = tmx_data.tileheight
        map_pixel_height = tile_size * tmx_data.height
        vertical_offset = self.screen.get_height() - map_pixel_height
        self.camera = Camera(tmx_data.width * tile_size, tmx_data.height * tile_size)

        # Find player spawn point
        spawn_x, spawn_y = 0, 0
        for obj in tmx_data.objects:
            if obj.name == "Player sp" or obj.properties.get("player.type") == "sp":
                spawn_x = obj.x
                spawn_y = obj.y + vertical_offset
                break

        self.player = Player((spawn_x, spawn_y))
        self.all_sprites.add(self.player)

        # Load decorative layers
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data') and layer.name != "Collision":
                for x, y, surf in layer.tiles():
                    pos = (x * tile_size, y * tile_size + vertical_offset)
                    Tile(pos=pos, surf=surf, groups=[self.decor_tiles, self.all_sprites])

        # Load collision layers
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data') and layer.name == "Gnd":
                for x, y, surf in layer.tiles():
                    pos = (x * tile_size, y * tile_size + vertical_offset)
                    Tile(pos=pos, surf=surf, groups=[self.platforms])

        # Spawn enemies from map
        for obj in tmx_data.objects:
            if obj.properties.get("enemy_type") == "enemy":
                x = obj.x
                y = obj.y + vertical_offset
                enemy = Enemy1((x, y))
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        self.font = pygame.font.SysFont("Arial", 24)

        # Enemy spawning variables
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 2000  # Start with 2 seconds between spawns
        self.min_spawn_delay = 500  # Minimum delay of 0.5 seconds
        self.last_spawn_time = pygame.time.get_ticks()
        self.difficulty_increase_rate = 50  # Decrease delay by 50ms every spawn
        self.enemy_count = 0
        self.max_concurrent_enemies = 10  # Maximum number of enemies at once

        # Score trackingd"Arial", 24)
        self.score = 0
        self.game_over = False

    def generate_moon_glow(self, count):
        for i in range(count):
            angle = (2 * math.pi * i) / count
            length = random.randint(10, 20)
            self.moon_glow.append({"angle": angle, "length": length})

    def generate_stars(self, count):
        for _ in range(count):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(0, 300)
            size = random.uniform(1, 3)
            twinkle_speed = random.uniform(0.001, 0.005)
            self.stars.append({
                "x": x, "y": y,
                "size": size,
                "twinkle_speed": twinkle_speed
            })

    def generate_clouds(self, count):
        for _ in range(count):
            x = random.randint(-200, self.screen.get_width())
            y = random.randint(50, 250)
            size = random.uniform(0.8, 1.5)
            speed = random.uniform(0.2, 0.5)
            self.clouds.append({"x": x, "y": y, "size": size, "speed": speed})

    def generate_hill_points(self, start_x, base_y, variation):
        points = [(start_x, self.screen.get_height())]
        x = start_x
        while x < self.screen.get_width() + 100:
            x += random.randint(100, 200)
            y = base_y + random.randint(-20, 20) * variation
            points.append((x, y))
        points.append((x, self.screen.get_height()))
        return points

    def draw_star(self, x, y, size, current_time):
        brightness = abs(math.sin(current_time)) * 255
        color = (brightness, brightness, brightness)
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))

    def draw_cloud(self, x, y, size):
        cloud_color = (60, 60, 70)  # Dark clouds for night
        centers = [
            (x, y),
            (x + 20 * size, y - 10 * size),
            (x + 40 * size, y),
            (x + 20 * size, y + 10 * size),
            (x + 60 * size, y - 5 * size)
        ]
        for cx, cy in centers:
            pygame.draw.circle(self.screen, cloud_color, (int(cx), int(cy)), int(25 * size))

    def draw_background(self):
        self.screen.fill(self.sky_color)

        # Draw stars
        current_time = pygame.time.get_ticks() / 1000
        for star in self.stars:
            self.draw_star(star["x"], star["y"], star["size"],
                           current_time * star["twinkle_speed"])

        # Draw moon and glow
        pygame.draw.circle(self.screen, self.moon_color, self.moon_pos, self.moon_radius)
        for glow in self.moon_glow:
            end_x = self.moon_pos[0] + math.cos(glow["angle"]) * (self.moon_radius + glow["length"])
            end_y = self.moon_pos[1] + math.sin(glow["angle"]) * (self.moon_radius + glow["length"])
            pygame.draw.line(self.screen, (180, 180, 170), self.moon_pos, (end_x, end_y), 2)

        # Draw hills
        for hill in self.back_hills:
            pygame.draw.polygon(self.screen, hill["color"], hill["points"])

        # Update and draw clouds
        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > self.screen.get_width() + 100:
                cloud["x"] = -200
            self.draw_cloud(cloud["x"], cloud["y"], cloud["size"])

        for hill in self.front_hills:
            pygame.draw.polygon(self.screen, hill["color"], hill["points"])

    def spawn_enemy(self):
        if len(self.enemies) < self.max_concurrent_enemies:
            # Spawn positions relative to player's current position
            min_distance = 400  # Minimum spawn distance from player
            max_distance = 800  # Maximum spawn distance from player

            # Random position calculation
            spawn_side = random.choice([-1, 1])  # Left or right of player
            x = self.player.rect.x + (spawn_side * random.randint(min_distance, max_distance))
            y = random.randint(100, self.screen.get_height() - 200)

            # Create and add enemy
            enemy = Enemy1((x, y))
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.enemy_count += 1

            # Increase difficulty
            self.enemy_spawn_delay = max(
                self.min_spawn_delay,
                self.enemy_spawn_delay - self.difficulty_increase_rate
            )

    def update(self):
        if self.game_over:
            # Display game over screen
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 0))
            restart_text = self.font.render("Press ESC to return to menu", True, (255, 255, 255))

            text_rect = game_over_text.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
            score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            restart_rect = restart_text.get_rect(
                center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))

            self.screen.blit(game_over_text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)
            return "back"

        current_time = pygame.time.get_ticks()

        # Spawn enemies continuously
        if current_time - self.last_spawn_time > self.enemy_spawn_delay:
            self.spawn_enemy()
            self.last_spawn_time = current_time

        self.camera.update(self.player)
        self.draw_background()

        # Update player and check if dead
        self.player.update(self.platforms)
        if self.player.lives <= 0:
            self.game_over = True

        # Platform collisions
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            if self.player.velocity_y > 0:
                self.player.rect.bottom = hits[0].rect.top
                self.player.velocity_y = 0
                self.player.on_ground = True
        else:
            self.player.on_ground = False

        # Update and check enemy collisions
        for enemy in self.enemies:
            enemy.update(self.player, self.platforms)

            # Remove enemies that are too far behind
            if enemy.rect.right < self.camera.state.x - 200:
                enemy.kill()
                self.score += 1  # Score point for surviving past an enemy
        import pygame
        from pytmx import load_pygame
        from Tiles.Tile import Tile
        from player import Player
        from enemy1 import Enemy1
        from camera import Camera
        import random
        import math

        class EndlessLevel:
            def __init__(self, screen):
                self.screen = screen

                # Initialize sprite groups
                self.all_sprites = pygame.sprite.Group()
                self.platforms = pygame.sprite.Group()
                self.decor_tiles = pygame.sprite.Group()
                self.enemies = pygame.sprite.Group()
                self.coins = pygame.sprite.Group()

                # Night background elements
                self.sky_color = (20, 24, 40)  # Dark blue night sky
                self.moon_pos = (100, 100)
                self.moon_radius = 40
                self.moon_color = (230, 230, 210)
                self.moon_glow = []
                self.stars = []
                self.clouds = []

                self.generate_moon_glow(12)
                self.generate_stars(100)
                self.generate_clouds(5)

                # Hills with night colors
                self.back_hills = [
                    {"color": (40, 45, 55), "points": self.generate_hill_points(0, 500, 3)},
                    {"color": (30, 35, 45), "points": self.generate_hill_points(200, 450, 2)},
                ]
                self.front_hills = [
                    {"color": (20, 25, 35), "points": self.generate_hill_points(-100, 400, 1)}
                ]

                # Load the Tiled map
                tmx_data = load_pygame(r'E:\Python\Proiect Python V\level_endless.tmx')

                tile_size = tmx_data.tileheight
                map_pixel_height = tile_size * tmx_data.height
                vertical_offset = self.screen.get_height() - map_pixel_height
                self.camera = Camera(tmx_data.width * tile_size, tmx_data.height * tile_size)

                # Find player spawn point
                spawn_x, spawn_y = 0, 0
                for obj in tmx_data.objects:
                    if obj.name == "Player sp" or obj.properties.get("player.type") == "sp":
                        spawn_x = obj.x
                        spawn_y = obj.y + vertical_offset
                        break

                self.player = Player((spawn_x, spawn_y))
                self.all_sprites.add(self.player)

                # Load decorative layers
                for layer in tmx_data.visible_layers:
                    if hasattr(layer, 'data') and layer.name != "Collision":
                        for x, y, surf in layer.tiles():
                            pos = (x * tile_size, y * tile_size + vertical_offset)
                            Tile(pos=pos, surf=surf, groups=[self.decor_tiles, self.all_sprites])

                # Load collision layers
                for layer in tmx_data.visible_layers:
                    if hasattr(layer, 'data') and layer.name == "Gnd":
                        for x, y, surf in layer.tiles():
                            pos = (x * tile_size, y * tile_size + vertical_offset)
                            Tile(pos=pos, surf=surf, groups=[self.platforms])

                # Spawn enemies from map
                for obj in tmx_data.objects:
                    if obj.properties.get("enemy_type") == "enemy":
                        x = obj.x
                        y = obj.y + vertical_offset
                        enemy = Enemy1((x, y))
                        self.enemies.add(enemy)
                        self.all_sprites.add(enemy)

                self.font = pygame.font.SysFont("Arial", 24)

                # Enemy spawning variables
                self.enemy_spawn_timer = 0
                self.enemy_spawn_delay = 2000  # Start with 2 seconds between spawns
                self.min_spawn_delay = 500  # Minimum delay of 0.5 seconds
                self.last_spawn_time = pygame.time.get_ticks()
                self.difficulty_increase_rate = 50  # Decrease delay by 50ms every spawn
                self.enemy_count = 0
                self.max_concurrent_enemies = 10  # Maximum number of enemies at once

                # Score trackingd"Arial", 24)
                self.score = 0
                self.game_over = False

            def generate_moon_glow(self, count):
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    length = random.randint(10, 20)
                    self.moon_glow.append({"angle": angle, "length": length})

            def generate_stars(self, count):
                for _ in range(count):
                    x = random.randint(0, self.screen.get_width())
                    y = random.randint(0, 300)
                    size = random.uniform(1, 3)
                    twinkle_speed = random.uniform(0.001, 0.005)
                    self.stars.append({
                        "x": x, "y": y,
                        "size": size,
                        "twinkle_speed": twinkle_speed
                    })

            def generate_clouds(self, count):
                for _ in range(count):
                    x = random.randint(-200, self.screen.get_width())
                    y = random.randint(50, 250)
                    size = random.uniform(0.8, 1.5)
                    speed = random.uniform(0.2, 0.5)
                    self.clouds.append({"x": x, "y": y, "size": size, "speed": speed})

            def generate_hill_points(self, start_x, base_y, variation):
                points = [(start_x, self.screen.get_height())]
                x = start_x
                while x < self.screen.get_width() + 100:
                    x += random.randint(100, 200)
                    y = base_y + random.randint(-20, 20) * variation
                    points.append((x, y))
                points.append((x, self.screen.get_height()))
                return points

            def draw_star(self, x, y, size, current_time):
                brightness = abs(math.sin(current_time)) * 255
                color = (brightness, brightness, brightness)
                pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size))

            def draw_cloud(self, x, y, size):
                cloud_color = (60, 60, 70)  # Dark clouds for night
                centers = [
                    (x, y),
                    (x + 20 * size, y - 10 * size),
                    (x + 40 * size, y),
                    (x + 20 * size, y + 10 * size),
                    (x + 60 * size, y - 5 * size)
                ]
                for cx, cy in centers:
                    pygame.draw.circle(self.screen, cloud_color, (int(cx), int(cy)), int(25 * size))

            def draw_background(self):
                self.screen.fill(self.sky_color)

                # Draw stars
                current_time = pygame.time.get_ticks() / 1000
                for star in self.stars:
                    self.draw_star(star["x"], star["y"], star["size"],
                                   current_time * star["twinkle_speed"])

                # Draw moon and glow
                pygame.draw.circle(self.screen, self.moon_color, self.moon_pos, self.moon_radius)
                for glow in self.moon_glow:
                    end_x = self.moon_pos[0] + math.cos(glow["angle"]) * (self.moon_radius + glow["length"])
                    end_y = self.moon_pos[1] + math.sin(glow["angle"]) * (self.moon_radius + glow["length"])
                    pygame.draw.line(self.screen, (180, 180, 170), self.moon_pos, (end_x, end_y), 2)

                # Draw hills
                for hill in self.back_hills:
                    pygame.draw.polygon(self.screen, hill["color"], hill["points"])

                # Update and draw clouds
                for cloud in self.clouds:
                    cloud["x"] += cloud["speed"]
                    if cloud["x"] > self.screen.get_width() + 100:
                        cloud["x"] = -200
                    self.draw_cloud(cloud["x"], cloud["y"], cloud["size"])

                for hill in self.front_hills:
                    pygame.draw.polygon(self.screen, hill["color"], hill["points"])

            def spawn_enemy(self):
                if len(self.enemies) < self.max_concurrent_enemies:
                    # Spawn positions relative to player's current position
                    min_distance = 400  # Minimum spawn distance from player
                    max_distance = 800  # Maximum spawn distance from player

                    # Random position calculation
                    spawn_side = random.choice([-1, 1])  # Left or right of player
                    x = self.player.rect.x + (spawn_side * random.randint(min_distance, max_distance))
                    y = random.randint(100, self.screen.get_height() - 200)

                    # Create and add enemy
                    enemy = Enemy1((x, y))
                    self.enemies.add(enemy)
                    self.all_sprites.add(enemy)
                    self.enemy_count += 1

                    # Increase difficulty
                    self.enemy_spawn_delay = max(
                        self.min_spawn_delay,
                        self.enemy_spawn_delay - self.difficulty_increase_rate
                    )

            def update(self):
                if hasattr(self, 'game_over') and self.game_over:
                    # Game over display code...
                    return "back"

                current_time = pygame.time.get_ticks()

                # Spawn enemies continuously
                if hasattr(self, 'last_spawn_time') and current_time - self.last_spawn_time > self.enemy_spawn_delay:
                    self.spawn_enemy()
                    self.last_spawn_time = current_time

                self.camera.update(self.player)
                self.draw_background()

                # Update player and projectiles
                self.player.update(self.platforms)
                if hasattr(self.player, 'projectiles'):
                    self.player.projectiles.update()
                    # Handle projectile collisions with enemies
                    pygame.sprite.groupcollide(self.player.projectiles, self.enemies, True, True)

                # Platform collisions
                hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
                if hits:
                    if self.player.velocity_y > 0:
                        self.player.rect.bottom = hits[0].rect.top
                        self.player.velocity_y = 0
                        self.player.on_ground = True
                else:
                    self.player.on_ground = False

                # Enemy updates and combat
                for enemy in list(self.enemies):  # Create a list copy to safely modify during iteration
                    enemy.update(self.player, self.platforms)

                    # Check for melee combat
                    if self.player.weapon == 1 and self.player.attack_cooldown == 14:
                        if self.player.rect.colliderect(enemy.rect.inflate(20, 20)):
                            enemy.health -= self.player.damage
                            if enemy.health <= 0:
                                enemy.kill()
                                self.score += 1

                # Check for enemy collision with player
                if pygame.sprite.collide_rect(enemy, self.player):
                    if not self.player.shield and self.player.invincibility_frames <= 0:
                        self.player.take_damage(enemy.damage)
                        if self.player.lives <= 0:
                            self.game_over = True

                # Remove enemies that are too far behind
                if enemy.rect.right < self.player.rect.x - 800:
                    enemy.kill()
                    self.score += 1

                # Draw everything
                for sprite in self.decor_tiles:
                    self.screen.blit(sprite.image, self.camera.apply(sprite))

                # Draw projectiles if they exist
                if hasattr(self.player, 'projectiles'):
                    self.player.projectiles.draw(self.screen)

                for enemy in self.enemies:
                    self.screen.blit(enemy.image, self.camera.apply(enemy))

                self.screen.blit(self.player.image, self.camera.apply(self.player))

                # UI elements
                score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
                enemy_text = self.font.render(f"Enemies: {len(self.enemies)}", True, (255, 100, 100))
                lives_text = self.font.render(f"Lives: {self.player.lives}", True, (255, 0, 0))

                self.screen.blit(score_text, (10, 10))
                self.screen.blit(enemy_text, (10, 40))
                self.screen.blit(lives_text, (10, 70))

                return None
        # Draw everything
        for sprite in self.decor_tiles:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for enemy in self.enemies:
            self.screen.blit(enemy.image, self.camera.apply(enemy))

        self.screen.blit(self.player.image, self.camera.apply(self.player))

        # Draw score and other UI elements
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 0))
        enemy_text = self.font.render(f"Enemies: {len(self.enemies)}", True, (255, 100, 100))
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, (255, 0, 0))

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(enemy_text, (10, 40))
        self.screen.blit(lives_text, (10, 70))

        return None