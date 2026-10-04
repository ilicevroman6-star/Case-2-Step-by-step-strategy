import pygame
from game.config import COLORS
from game.ui import theme
from game.ui.button import Button
from game.ui.screens.base_screen import BaseScreen


class VictoryScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.f_h1 = theme.get_font("oswald", 48, bold=True)
        self.f_b = theme.get_font("inter", 16)
        self.f_btn = theme.get_font("inter", 14, bold=True)
        self.exit_btn = Button(1280 // 2 - 120, 520, 240, 52, "ВЫХОД", self.f_btn)
        self.winner = max(app.players, key=lambda p: p.prestige)

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            if self.exit_btn.is_clicked(e.pos, True):
                self.app.running = False

    def update(self, dt, m):
        self.exit_btn.update(m)

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])
        t = self.f_h1.render("ПОБЕДА!", True, COLORS["hover"])
        screen.blit(t, t.get_rect(centerx=1280 // 2, top=180))
        s = self.f_b.render(
            f"Менеджер {self.winner.name} · престиж {self.winner.prestige}",
            True, COLORS["text_main"])
        screen.blit(s, s.get_rect(centerx=1280 // 2, top=270))
        self.exit_btn.draw(screen)