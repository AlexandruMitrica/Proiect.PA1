import pygame
from menu import Menu
from level_menu import LevelMenu
from level_1 import Level1
from level_2 import Level2
from level_3 import Level3
from endless_level import EndlessLevel
from test_1 import Test1
from test_2 import Test2
from test_3 import Test3

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Cipicel's Adventure")
clock = pygame.time.Clock()

#Muzica de fundal
pygame.mixer.music.load("assets/music/background-music.mp3")
pygame.mixer.music.play(-1)

def run_level(level_class):
    game = level_class(screen)
    running = True
    paused = False

    font = pygame.font.SysFont(None, 72)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                if event.key == pygame.K_TAB:
                    paused = not paused

        if not paused:
            result = game.update()
            if result == "back":  # Handle the return value from victory
                running = False  # Exit the level loop
                return "back"  # Return to menu
        else:
            pause_text = font.render("PAUZĂ", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(pause_text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    return "exit"


# Bucla principală a jocului
while True:
    menu = Menu(screen)
    choice = menu.run()

    if choice == "level":
        level_menu = LevelMenu(screen)
        level_choice = level_menu.run()

        if level_choice == "level_1":
            result = run_level(Test1)
        elif level_choice == "level_2":
            result = run_level(Test2)
        elif level_choice == "level_3":
            result = run_level(Test3)
        elif level_choice == "back":
            continue
        else:
            break

    elif choice == "endless":
        result = run_level(EndlessLevel)
    elif choice == "exit":
        break
    else:
        continue

pygame.quit()
exit()