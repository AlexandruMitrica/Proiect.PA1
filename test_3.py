import pygame
from pytmx import load_pygame

from Tiles.Tile import Tile
from player import Player
from camera import Camera
from boss import Boss

class Test3:
    def __init__(self, screen):
        self.screen = screen
        self.screen.fill((50, 50, 80))

        self.player = Player((0, 0))

        # Grupuri de sprite-uri
        self.platforms = pygame.sprite.Group()      # pentru coliziuni
        self.decor_tiles = pygame.sprite.Group()    # doar pentru desenare
        self.all_sprites = pygame.sprite.Group()    # decor + player
        self.enemies = pygame.sprite.Group()        # inamici

        # Add a new sprite group for the boss
        self.bosses = pygame.sprite.Group()

        # Încarcă harta Tiled
        tmx_data = load_pygame(r'E:\Python\Proiect Python V\level_3v2.tmx')

        tile_size = tmx_data.tileheight
        map_pixel_height = tile_size * tmx_data.height
        vertical_offset = self.screen.get_height() - map_pixel_height
        self.camera = Camera(tmx_data.width * tile_size, tmx_data.height * tile_size)
        # Adaugă playerul
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


        # After loading the map and creating other entities, add the boss
        # Adjust the position (800, 400) as needed for your level
        self.boss = Boss((800, 400))
        self.bosses.add(self.boss)
        self.all_sprites.add(self.boss)

        # Victory variables
        self.victory = False
        self.victory_font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 72)
        self.victory_start_time = None

    def update(self):
        self.camera.update(self.player)
        self.screen.fill((50, 50, 80))

        # Update player
        self.player.update(self.platforms)

        # Coliziuni player cu platforme
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            if self.player.velocity_y > 0:
                self.player.rect.bottom = hits[0].rect.top
                self.player.velocity_y = 0
                self.player.on_ground = True
        else:
            self.player.on_ground = False

        # Update inamici
        for enemy in self.enemies:
            enemy.update(self.player, self.platforms)

        # Update boss
        self.bosses.update(self.player, self.platforms)

        # Check for collisions between player projectiles and boss
        hits = pygame.sprite.groupcollide(self.player.projectiles, self.bosses, True, False)
        for projectile, boss_list in hits.items():
            for boss in boss_list:
                boss.take_damage(self.player.damage)

        # Check for melee attack hits on boss
        if self.player.weapon == 1 and self.player.attack_cooldown == 14:
            for boss in self.bosses:
                if self.player.rect.colliderect(boss.rect.inflate(20, 20)):
                    boss.take_damage(self.player.damage)

        # Draw everything as before
        for sprite in self.decor_tiles:
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        for enemy in self.enemies:
            self.screen.blit(enemy.image, self.camera.apply(enemy))

        # Draw boss and its health bar
        for boss in self.bosses:
            self.screen.blit(boss.image, self.camera.apply(boss))
            # Adjust the health bar position based on camera
            boss_pos = self.camera.apply(boss)
            health_bar_y = boss_pos[1] - 30
            health_bar_x = boss_pos[0] + boss.rect.width // 2 - 100  # Center the health bar

            # Draw health bar background
            pygame.draw.rect(self.screen, (255, 0, 0),
                           (health_bar_x, health_bar_y, 200, 20))

            # Draw current health
            health_width = (boss.health / boss.max_health) * 200
            pygame.draw.rect(self.screen, (0, 255, 0),
                           (health_bar_x, health_bar_y, health_width, 20))

            # Draw border
            pygame.draw.rect(self.screen, (0, 0, 0),
                           (health_bar_x, health_bar_y, 200, 20), 2)

        self.screen.blit(self.player.image, self.camera.apply(self.player))

        # After drawing everything else, check for victory and display the text
        if len(self.bosses) == 0:
            if not self.victory:
                self.victory = True
                self.victory_start_time = pygame.time.get_ticks()  # Get current time when victory occurs

            # Create bold victory text
            victory_text = self.victory_font.render("VICTORY!", True, (255, 215, 0))
            shadow_text = self.victory_font.render("VICTORY!", True, (139, 69, 19))

            # Position the text in the center
            text_rect = victory_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            shadow_rect = shadow_text.get_rect(center=(self.screen.get_width() // 2 + 4, self.screen.get_height() // 2 + 4))

            # Draw shadow first, then main text
            self.screen.blit(shadow_text, shadow_rect)
            self.screen.blit(victory_text, text_rect)

            # Check if 5 seconds have passed
            if pygame.time.get_ticks() - self.victory_start_time >= 5000:  # 5000 milliseconds = 5 seconds
                return "back"  # Signal to return to menu

        return None  # Continue game if no return signal