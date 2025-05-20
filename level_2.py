import pygame
from player import Player
from enemy import Enemy
from coin import Coin
from checkpoint import Checkpoint
from npc import NPC

class Level2:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player((100, 100))

        self.all_sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.checkpoints = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()

        # Adăugăm platforme (podeaua și platforme suspendate)
        platform_data = [
            (0, 550, 1280, 50),       # podeaua
            (200, 450, 120, 20),
            (400, 350, 120, 20),
            (600, 250, 150, 20),
            (800, 150, 120, 20),
            (1000, 100, 150, 20),
        ]
        for x, y, w, h in platform_data:
            platform = pygame.sprite.Sprite()
            platform.image = pygame.Surface((w, h))
            platform.image.fill((100, 100, 100))
            platform.rect = platform.image.get_rect(topleft=(x, y))
            self.platforms.add(platform)

        # Adăugăm câteva obiecte
        for i in range(4):
            coin = Coin((200 + i * 50, 300))
            self.coins.add(coin)
            self.all_sprites.add(coin)

        # Adăugăm inamici
        enemy = Enemy((400, 200))
        enemy2 = Enemy((700, 100))
        self.enemies.add(enemy, enemy2)
        self.all_sprites.add(enemy, enemy2)

        # Adăugăm checkpoint
        cp = Checkpoint((600, 400))
        self.checkpoints.add(cp)
        self.all_sprites.add(cp)

        # Adăugăm NPC
        npc = NPC((600, 300), "collect", 3)
        self.npcs.add(npc)
        self.all_sprites.add(npc)

        self.font = pygame.font.SysFont("Arial", 24)

    def update(self):
        self.screen.fill((50, 50, 80))

        # Apelăm update la player și aplicăm gravitația
        self.player.update(self.platforms)

        # Coliziune cu platforme (doar pe Y)
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            if self.player.velocity_y > 0:
                self.player.rect.bottom = hits[0].rect.top
                self.player.velocity_y = 0
                self.player.on_ground = True
        else:
            self.player.on_ground = False

        # Inamicii urmăresc jucătorul
        self.enemies.update(self.player, self.platforms)
        self.player.projectiles.update()
        pygame.sprite.groupcollide(self.player.projectiles, self.enemies, True, True)

        for enemy in self.enemies:
            if self.player.weapon == 1 and self.player.attack_cooldown == 14:
                if self.player.rect.colliderect(enemy.rect.inflate(20, 20)):
                    enemy.health -= self.player.damage
                    if enemy.health <= 0:
                        enemy.kill()

        # Coin-uri
        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in hit_coins:
            self.player.coins += 1

        # Checkpoint
        hit_cp = pygame.sprite.spritecollide(self.player, self.checkpoints, False)
        if hit_cp:
            self.player.spawn_point = hit_cp[0].rect.topleft

        # NPC
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            for npc in self.npcs:
                if self.player.rect.colliderect(npc.rect.inflate(40, 40)):
                    npc.give_quest(self.player)

        # Desenăm toate
        self.platforms.draw(self.screen)
        self.all_sprites.draw(self.screen)
        self.player.projectiles.draw(self.screen)

        # UI Text
        coin_text = self.font.render(f"Monezi: {self.player.coins}", True, (255, 255, 0))
        lives_text = self.font.render(f"Vieți: {self.player.lives}", True, (255, 0, 0))
        dash_text = self.font.render(f"Dash CD: {self.player.dash_cooldown//60}s", True, (150, 150, 255))
        shield_text = self.font.render(f"Scut: {'ON' if self.player.shield else f'CD: {self.player.shield_cooldown//60}s'}", True, (200, 255, 200))

        self.screen.blit(coin_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))
        self.screen.blit(dash_text, (10, 70))
        self.screen.blit(shield_text, (10, 100))

        for npc in self.npcs:
            if self.player.rect.colliderect(npc.rect.inflate(40, 40)):
                text = self.font.render("Apasă E pentru a vorbi", True, (255, 255, 255))
                self.screen.blit(text, (npc.rect.x - 20, npc.rect.y - 30))
