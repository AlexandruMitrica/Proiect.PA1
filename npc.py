import pygame

class NPC(pygame.sprite.Sprite):
    def __init__(self, pos, quest_type="collect", required=3):
        super().__init__()
        self.scale = 2  # Aceasta va fi folosită pentru scalarea imaginii NPC-ului
        self.animations = {}
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 10  # Timpul între cadrele animației
        self.current_animation = "idle"  # Animația curentă

        # Încarcă animațiile
        self._load_animations()

        self.image = self.animations[self.current_animation][self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)

        self.quest_type = quest_type
        self.required = required
        self.completed = False
        self.quest_given = False

        # Creăm fontul pentru text
        self.font = pygame.font.SysFont("Arial", 20)
        self.text_surface = None
        self.text_rect = None

    def _load_animations(self):
        """
        Încarcă toate cadrele de animație pentru NPC din fișierele PNG.
        """
        # Descarcă fișierele din directorul de imagini al NPC-ului
        sheet = [pygame.image.load(f"assets/images/npc/idle{i}.png").convert_alpha() for i in range(1, 7)]

        # Salvăm animatiile într-un dicționar
        self.animations["idle"] = [pygame.transform.scale(img, (64 * self.scale, 64 * self.scale)) for img in sheet]

    def update(self, player, screen):
        # Actualizăm animația pe baza timerului
        self.frame_timer += 1
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.animations[self.current_animation]):
                self.current_frame = 0

        # Setăm imaginea curentă
        self.image = self.animations[self.current_animation][self.current_frame]

        # Actualizează questul NPC-ului
        self.give_quest(player)

        # Afișăm textul questului pe ecran
        self.display_quest_text(screen)

    def give_quest(self, player):
        if not self.quest_given:
            self.text_surface = self.font.render(f"Colectează {self.required} monezi!", True, (255, 255, 255))
            self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 50))
            print("Salut! Colectează", self.required, "monezi!")
            self.quest_given = True
        elif not self.completed:
            if player.coins >= self.required:
                player.coins -= self.required
                self.completed = True
                player.damage += 1
                self.text_surface = self.font.render("Mulțumesc! Ai primit +1 damage.", True, (255, 255, 255))
                self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 50))
                print("Mulțumesc! Ai primit +1 damage.")
            else:
                self.text_surface = self.font.render(f"Încă nu ai destule monezi...", True, (255, 255, 255))
                self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 50))
                print("Încă nu ai destule monezi...")
        else:
            self.text_surface = self.font.render("Ai terminat questul deja!", True, (255, 255, 255))
            self.text_rect = self.text_surface.get_rect(center=(self.rect.centerx, self.rect.centery - 50))
            print("Ai terminat questul deja!")

    def display_quest_text(self, screen):
        """
        Afișează textul de quest pe ecran.
        """
        if self.text_surface:
            screen.blit(self.text_surface, self.text_rect)
