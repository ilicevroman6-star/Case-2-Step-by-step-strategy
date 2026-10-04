import pygame
from game.config import COLORS
from game.ui import theme
from game.ui.button import Button
from game.ui.screens.base_screen import BaseScreen


class RulesScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.f_h1 = theme.get_font("oswald", 32, bold=True)
        self.f_h2 = theme.get_font("oswald", 20, bold=True)
        self.f_body = theme.get_font("inter", 14)
        self.f_btn = theme.get_font("inter", 14, bold=True)

        self.back_btn = Button(1280 // 2 - 100, 640, 200, 48, "НАЗАД", self.f_btn)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.back_btn.is_clicked(event.pos, True):
                from game.ui.screens.main_menu import MainMenuScreen
                self.app.goto(MainMenuScreen)

    def update(self, dt, mouse_pos):
        self.back_btn.update(mouse_pos)

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])

        # Заголовок
        title = self.f_h1.render("ПРАВИЛА ИГРЫ", True, COLORS["text_h"])
        screen.blit(title, title.get_rect(centerx=1280 // 2, top=40))

        # Текст правил
        rules = [
            ("ЦЕЛЬ ИГРЫ", [
                "Первым набрать 30 очков престижа",
                "или остаться последним выжившим.",
            ]),
            ("РЕСУРСЫ", [
                " Деньги — валюта (старт 50)",
                " Выносливость — силы (старт 20)",
                " Репутация — фанаты (старт 16)",
                " Арены — инфраструктура (старт 0)",
            ]),
            ("ФОРМУЛА ПРЕСТИЖА", [
                "Престиж = арены×3 + деньги//8 + реп//4",
            ]),
            ("КЛЕТКИ ПОЛЯ", [
                " Арена — купить за 12, рента 4",
                " Тренировка — +4 выносливости",
                " Медиа — ±3 репутации",
                " Random — карточка события",
                " Матч — дуэль по выносливости",
                " Старт — +20 монет, +5 выносливости, +3 репутации",
            ]),
        ]

        y = 110
        for header, items in rules:
            h = self.f_h2.render(header, True, COLORS["hover"])
            screen.blit(h, (100, y))
            y += 30
            for item in items:
                t = self.f_body.render("• " + item, True, COLORS["text_main"])
                screen.blit(t, (120, y))
                y += 22
            y += 12

        self.back_btn.draw(screen)