import pygame
from game.config import COLORS
from game.ui import theme
from game.ui.button import Button
from game.ui.screens.base_screen import BaseScreen


class MainMenuScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.f_h1 = theme.get_font("oswald", 48, bold=True)
        self.f_sub = theme.get_font("inter", 16, bold=False)
        self.f_btn = theme.get_font("inter", 14, bold=True)
        cx = 1280 // 2
        self.new_btn = Button(cx - 130, 400, 260, 52, "НОВАЯ ИГРА", self.f_btn)
        self.rules_btn = Button(cx - 130, 470, 260, 52, "ПРАВИЛА", self.f_btn)
        self.buttons = [self.new_btn, self.rules_btn]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.new_btn.is_clicked(event.pos, True):
                from game.ui.screens.game_board import GameBoardScreen
                self.app.goto(GameBoardScreen)
            elif self.rules_btn.is_clicked(event.pos, True):
                from game.ui.screens.rules import RulesScreen
                self.app.goto(RulesScreen)

    def update(self, dt, mouse_pos):
        for b in self.buttons:
            b.update(mouse_pos)

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])
        title = self.f_h1.render("МОНОПОЛИЯ НА ЛЬДУ", True, COLORS["text_h"])
        screen.blit(title, title.get_rect(centerx=1280 // 2, top=180))
        sub = self.f_sub.render("Цель: набрать 30 очков престижа",
                                True, COLORS["text_secondary"])
        screen.blit(sub, sub.get_rect(centerx=1280 // 2, top=250))
        for b in self.buttons:
            b.draw(screen)