import pygame
from pytmx import load_pygame

from Tiles.Tile import Tile
from player import Player
from enemy1 import Enemy1
from camera import Camera

import random
import math


class Test2:
    def __init__(self, screen):
        self.screen = screen

        # Background elements
        self.sky_color = (135, 206, 235)  # Light blue sky

        # Sun
        self.sun_pos = (100, 100)
        self.sun_radius = 60
        self.sun_color = (255, 255, 100)
        self.sun_rays = []
        self.generate_sun_rays(12)  # Generate 12 sun rays

        # Clouds
        self.clouds = []
        self.generate_clouds(5)  # Generate 5 clouds

        # Hills (parallax backgrounds)
        self.back_hills = [
            {"color": (70, 120, 70), "points": self.generate_hill_points(0, 500, 3)},
            {"color": (90, 140, 90), "points": self.generate_hill_points(200, 450, 2)},
        ]

        self.front_hills = [
            {"color": (110, 160, 110), "points": self.generate_hill_points(-100, 400, 1)}
        ]

        # Birds
        self.birds = []
        self.generate_birds(8)  # Generate 8 birds

        # Grupuri de sprite-uri
        self.platforms = pygame.sprite.Group()
        self.decor_tiles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Încarcă harta Tiled
        tmx_data = load_pygame(r'E:\Python\Proiect Python V\level_2.tmx')

        tile_size = tmx_data.tileheight
        map_pixel_height = tile_size * tmx_data.height
        vertical_offset = self.screen.get_height() - map_pixel_height
        self.camera = Camera(tmx_data.width * tile_size, tmx_data.height * tile_size)

        # === Spawn jucător din obiect din Tiled ===
        spawn_x, spawn_y = 0, 0
        for obj in tmx_data.objects:
            if obj.name == "Player sp" or obj.properties.get("player.type") == "sp":  # aici verifici corect
                spawn_x = obj.x
                spawn_y = obj.y + vertical_offset
                break

        self.player = Player((spawn_x, spawn_y))
        self.all_sprites.add(self.player)

        # Layere decorative
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data') and layer.name != "Collision":
                for x, y, surf in layer.tiles():
                    pos = (x * tile_size, y * tile_size + vertical_offset)
                    Tile(pos=pos, surf=surf, groups=[self.decor_tiles, self.all_sprites])

        # Layere pentru coliziune
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'data') and layer.name == "Gnd":
                for x, y, surf in layer.tiles():
                    pos = (x * tile_size, y * tile_size + vertical_offset)
                    Tile(pos=pos, surf=surf, groups=[self.platforms])

        # Spawn inamici
        for obj in tmx_data.objects:
            if obj.properties.get("enemy_type") == "enemy":
                x = obj.x
                y = obj.y + vertical_offset
                enemy = Enemy1((x, y))
                self.enemies.add(enemy)

    def generate_sun_rays(self, count):
        for i in range(count):
            angle = (2 * math.pi * i) / count
            length = random.randint(20, 40)
            self.sun_rays.append({"angle": angle, "length": length})

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

    def generate_birds(self, count):
        for _ in range(count):
            x = random.randint(0, self.screen.get_width())
            y = random.randint(100, 300)
            speed = random.uniform(1, 2)
            wing_state = 0
            self.birds.append({"x": x, "y": y, "speed": speed, "wing_state": wing_state})

    def draw_cloud(self, x, y, size):
        cloud_color = (255, 255, 255)
        centers = [
            (x, y),
            (x + 20 * size, y - 10 * size),
            (x + 40 * size, y),
            (x + 20 * size, y + 10 * size),
            (x + 60 * size, y - 5 * size)
        ]
        for cx, cy in centers:
            pygame.draw.circle(self.screen, cloud_color,
                               (int(cx), int(cy)), int(25 * size))

    def draw_bird(self, x, y, wing_state):
        # Simple bird shape with animated wings
        wing_up = [(x - 15, y), (x, y - 10), (x + 15, y)]
        wing_down = [(x - 15, y), (x, y + 10), (x + 15, y)]
        body_points = [(x - 5, y), (x + 15, y), (x + 5, y - 5)]

        # Draw body
        pygame.draw.polygon(self.screen, (50, 50, 50), body_points)
        # Draw wings based on state
        wing_points = wing_up if wing_state > 0.5 else wing_down
        pygame.draw.lines(self.screen, (50, 50, 50), False, wing_points, 2)

    def draw_background(self):
        # Fill sky
        self.screen.fill(self.sky_color)

        # Draw sun and animated rays
        pygame.draw.circle(self.screen, self.sun_color, self.sun_pos, self.sun_radius)
        current_time = pygame.time.get_ticks() / 1000
        for ray in self.sun_rays:
            end_x = self.sun_pos[0] + math.cos(ray["angle"] + current_time * 0.5) * (self.sun_radius + ray["length"])
            end_y = self.sun_pos[1] + math.sin(ray["angle"] + current_time * 0.5) * (self.sun_radius + ray["length"])
            pygame.draw.line(self.screen, self.sun_color, self.sun_pos, (end_x, end_y), 3)

        # Draw background hills (parallax)
        for hill in self.back_hills:
            pygame.draw.polygon(self.screen, hill["color"], hill["points"])

        # Update and draw clouds
        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > self.screen.get_width() + 100:
                cloud["x"] = -200
            self.draw_cloud(cloud["x"], cloud["y"], cloud["size"])

        # Draw foreground hills
        for hill in self.front_hills:
            pygame.draw.polygon(self.screen, hill["color"], hill["points"])

        # Update and draw birds
        for bird in self.birds:
            bird["x"] += bird["speed"]
            if bird["x"] > self.screen.get_width() + 50:
                bird["x"] = -50
            bird["wing_state"] = (math.sin(pygame.time.get_ticks() * 0.01) + 1) / 2
            self.draw_bird(bird["x"], bird["y"], bird["wing_state"])

    def update(self):
        self.camera.update(self.player)

        # Draw background first
        self.draw_background()

        self.player.update(self.platforms)

        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            if self.player.velocity_y > 0:
                self.player.rect.bottom = hits[0].rect.top
                self.player.velocity_y = 0
                self.player.on_ground = True
        else:
            self.player.on_ground = False

        for enemy in self.enemies:
            enemy.update(self.player, self.platforms)

        for sprite in self.decor_tiles:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for enemy in self.enemies:
            self.screen.blit(enemy.image, self.camera.apply(enemy))

        self.screen.blit(self.player.image, self.camera.apply(self.player))