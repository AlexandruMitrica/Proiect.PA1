import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Încărcăm sprite sheet-ul cu moneda
        self.image_sheet = pygame.image.load("assets/images/coins/coin.png").convert_alpha()

        # Dimensiunile fiecărui cadru (în sprite sheet-ul tău sunt pe verticală)
        self.frame_width = 16
        self.frame_height = 16
        self.num_frames = self.image_sheet.get_height() // self.frame_height  # cadre pe verticală

        # Extragem fiecare cadru din imagine și le mărim de două ori
        self.frames = []
        for i in range(self.num_frames):
            # Extragem fiecare cadru din sprite sheet
            frame = self.image_sheet.subsurface(
                pygame.Rect(0, i * self.frame_height, self.frame_width, self.frame_height)
            )

            # Mărim cadrul de două ori
            frame = pygame.transform.scale(frame, (self.frame_width * 2, self.frame_height * 2))
            self.frames.append(frame)

        # Cadrul curent
        self.current_frame = 0
        self.image = self.frames[self.current_frame]

        # Poziția
        self.rect = self.image.get_rect(topleft=pos)

        # Mărim hitbox-ul pentru a fi mai mic decât imaginea
        self.rect.inflate_ip(-self.rect.width // 2, -self.rect.height // 2)  # Reducem hitbox-ul la 50%

        # Timp animație
        self.animation_time = 100  # ms per frame
        self.last_update_time = pygame.time.get_ticks()

    def update(self):
        # Animăm cadrul
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_time:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.last_update_time = current_time
class Test1:
    def __init__(self, screen):
        # Add after other sprite groups
        self.coins = pygame.sprite.Group()
        
        # Keep existing initialization code...
        
        # Add after loading the map and spawning enemies
        # Add some coins in various locations
        coin_positions = [
            (400, 300),
            (600, 200),
            (800, 400),
            (1000, 300),
            (1200, 250),
            # Add more positions as needed
        ]
        
        for pos in coin_positions:
            coin = Coin(pos)
            self.coins.add(coin)
            self.all_sprites.add(coin)
            
        # Add font for UI
        self.font = pygame.font.SysFont("Arial", 24)

    def update(self):
        # Keep existing update code...
        
        # Add after enemy updates
        # Update coins
        self.coins.update()
        
        # Check for coin collection
        hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in hits:
            self.player.coins += 1

        # Add after drawing sprites
        # Draw coins
        for coin in self.coins:
            self.screen.blit(coin.image, self.camera.apply(coin))

        # Draw coin counter
        coin_text = self.font.render(f"Coins: {self.player.coins}", True, (255, 215, 0))
        self.screen.blit(coin_text, (10, 10))