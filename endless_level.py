import pygame
import random
from player import Player
from enemy import Enemy
from enemy1 import Enemy1


class EndlessLevel:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player((100, 100))
        self.all_sprites = pygame.sprite.Group(self.player)
        self.enemies = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()  # Grupul pentru platforme

        # Adăugăm platforma la baza ecranului
        self.platform = Platform(0, 600, 1920, 50)  # Platforma pe care jucătorul stă
        self.platforms.add(self.platform)
        self.all_sprites.add(self.platform)

        self.spawn_timer = 0
        self.score = 0

        # Încarcă scorul înalt
        try:
            with open("highscore.txt", "r") as f:
                self.highscore = int(f.read())
        except:
            self.highscore = 0

        # Font pentru text
        self.font = pygame.font.SysFont("Arial", 24)

    def spawn_enemy(self):
        """Spawnează un inamic aleatoriu pe ecran."""
        x = random.randint(0, 1200)
        y = random.randint(0, 600)  # Inamicii pot apărea pe ecran, în fața platformei
        enemy = Enemy((x, y))
        enemy1 = Enemy1((x, y))
        self.enemies.add(enemy,enemy1)
        self.all_sprites.add(enemy,enemy1)

    def update(self):
        """Actualizează toate obiectele din joc (player, inamicii, scor)."""
        self.screen.fill((30, 30, 30))  # Fundalul nivelului

        # Actualizează jucătorul și inamicii
        self.player.update(self.platforms)  # Jucătorul se mișcă în funcție de platforme
        self.enemies.update(self.player, self.platforms)

        # Timer pentru spawnează inamicii
        self.spawn_timer += 1
        if self.spawn_timer >= 200:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Verifică coliziuni cu săgețile jucătorului și inamicii
        for arrow in self.player.projectiles:
            hit = pygame.sprite.spritecollide(arrow, self.enemies, False)
            for enemy in hit:
                enemy.health -= arrow.damage
                arrow.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    self.score += 10

        # Verifică atacul cu arma principală al jucătorului (dacă este activat)
        if self.player.weapon == 1 and self.player.attack_cooldown == 14:
            for enemy in self.enemies:
                if self.player.rect.colliderect(enemy.rect.inflate(20, 20)):
                    enemy.health -= self.player.damage
                    if enemy.health <= 0:
                        enemy.kill()
                        self.score += 10

        # Verifică dacă jucătorul a pierdut toate viețile
        if self.player.lives <= 0:
            # Salvează scorul dacă este mai mare decât highscore-ul
            if self.score > self.highscore:
                with open("highscore.txt", "w") as f:
                    f.write(str(self.score))
            print("Game Over – Scor:", self.score)
            pygame.quit()
            exit()

        # Desenează toate sprite-urile
        self.all_sprites.draw(self.screen)
        self.player.projectiles.draw(self.screen)

        # Afișează scorul și highscore-ul pe ecran
        score_text = self.font.render(f"Scor: {self.score}", True, (255, 255, 255))
        hs_text = self.font.render(f"High Score: {self.highscore}", True, (255, 215, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(hs_text, (10, 40))


# Platformă pe care jucătorul poate să stea
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill((0, 100, 200))  # Culoare platformei
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# Meniu de selectare a jocului
def menu(screen):
    font = pygame.font.SysFont("Arial", 50)
    title = font.render("Endless Level Game", True, (255, 255, 255))
    play_text = font.render("Press Enter to Play", True, (0, 255, 0))
    quit_text = font.render("Press Q to Quit", True, (255, 0, 0))

    while True:
        screen.fill((0, 0, 0))  # Fundalul meniului

        screen.blit(title, (300, 150))
        screen.blit(play_text, (320, 250))
        screen.blit(quit_text, (350, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Începe jocul endless
                    return "endless"
                if event.key == pygame.K_q:  # Ieși din joc
                    pygame.quit()
                    exit()

        pygame.display.flip()

