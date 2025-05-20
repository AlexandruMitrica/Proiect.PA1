import pygame

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 40)
        self.options = ["Start Joc", "Mod Endless", "Ieșire"]

        self.hover_sound = pygame.mixer.Sound("assets/sounds/hover-sound.mp3")
        self.click_sound = pygame.mixer.Sound("assets/sounds/click-sound.mp3")
        self.bg_image = pygame.image.load("assets/images/background.png").convert()

        self.last_hover_index = -1  # Ca să nu redea sunetul de hover de fiecare dată

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        title = self.font.render("Cipicel's Adventure", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()
        selected_option = None

        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 200 + i * 60))

            if self.is_hover(mouse_pos, i):
                pygame.draw.rect(self.screen, (0, 0, 0), text_rect)

                # Redă sunetul de hover o singură dată când intră pe opțiune
                if self.last_hover_index != i:
                    self.hover_sound.stop()
                    self.hover_sound.play()
                    self.last_hover_index = i
            self.screen.blit(text, text_rect.topleft)

        return

    def is_hover(self, mouse_pos, option_index):
        option_rect = pygame.Rect(
            self.screen.get_width() // 2 - self.font.size(self.options[option_index])[0] // 2,
            200 + option_index * 60,
            self.font.size(self.options[option_index])[0],
            self.font.get_height()
        )
        return option_rect.collidepoint(mouse_pos)

    def run(self):
        running = True
        while running:
            self.screen.fill((0, 0, 0))
            self.draw()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i in range(len(self.options)):
                        if self.is_hover(pygame.mouse.get_pos(), i):
                            self.click_sound.play()
                            pygame.time.wait(200)  # Mic delay pentru click
                            if i == 0:
                                return "level"
                            elif i == 1:
                                return "endless"
                            elif i == 2:
                                return "exit"
