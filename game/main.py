# main.py
import sys
import pygame
from game.models.player import Player
from game.ui.screens.main_menu import MainMenuScreen

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Монополия на льду v1.1")
clock = pygame.time.Clock()


class App:
    def __init__(self):
        self.running = True
        # 4 игрока
        self.players = [
            Player("Игорь (СКА)",   "Синий"),
            Player("Артем (ЦСКА)",  "Золотой"),
            Player("Марина (Динамо)", "Красный"),
            Player("Олег (Спартак)",  "Лайм"),
        ]
        # позиции фишек — 0 (Старт)
        for p in self.players:
            if not hasattr(p, "position"):
                p.position = 0
        self.screen = MainMenuScreen(self)

    def goto(self, screen_cls, **kw):
        self.screen = screen_cls(self, **kw)


def main():
    app = App()
    while app.running:
        dt = clock.tick(60) / 1000.0
        mouse = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                app.running = False
                break
            app.screen.handle_event(e)
        app.screen.update(dt, mouse)
        app.screen.draw(screen)
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()