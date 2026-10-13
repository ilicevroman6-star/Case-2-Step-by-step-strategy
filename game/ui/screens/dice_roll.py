import random
import pygame
from game.config import COLORS
from game.ui import theme
from game.ui.button import Button
from game.ui.screens.base_screen import BaseScreen


class DiceRollScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.f_h1 = theme.get_font("oswald", 32, bold=True)
        self.f_h2 = theme.get_font("oswald", 24, bold=True)
        self.f_body = theme.get_font("inter", 14)
        self.f_btn = theme.get_font("inter", 14, bold=True)

        self.players = app.players
        self.rolls = {}          # {idx: значение}
        self.rolled = False      # флаг, что броски уже сделаны
        self.winner_idx = None

        self.roll_btn = Button(1280 // 2 - 130, 600, 260, 52,
                               "  БРОСИТЬ КОСТИ", self.f_btn)
        self.start_btn = Button(1280 // 2 - 130, 600, 260, 52,
                                "НАЧАТЬ ИГРУ", self.f_btn, state="success")

    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        if not self.rolled and self.roll_btn.is_clicked(event.pos, True):
            self._do_roll()
        elif self.rolled and self.start_btn.is_clicked(event.pos, True):
            from game.ui.screens.game_board import GameBoardScreen
            self.app.goto(GameBoardScreen, first_player=self.winner_idx)

    def _do_roll(self):
        """Бросаем кости для всех игроков. При ничьей — повторяем у лидеров."""
        while True:
            self.rolls = {i: random.randint(1, 6)
                          for i in range(len(self.players))}
            max_val = max(self.rolls.values())
            leaders = [i for i, v in self.rolls.items() if v == max_val]
            if len(leaders) == 1:
                self.winner_idx = leaders[0]
                break
            # Ничья — крутим ещё раз (упрощённо: всем заново)
        self.rolled = True

    def update(self, dt, mouse_pos):
        if not self.rolled:
            self.roll_btn.update(mouse_pos)
        else:
            self.start_btn.update(mouse_pos)

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])

        # Заголовок
        title = self.f_h1.render("ЖЕРЕБЬЁВКА", True, COLORS["text_h"])
        screen.blit(title, title.get_rect(centerx=1280 // 2, top=60))

        sub = self.f_body.render(
            "Первый ход — у команды с наибольшим броском",
            True, COLORS["text_secondary"])
        screen.blit(sub, sub.get_rect(centerx=1280 // 2, top=110))

        # 4 карточки с бросками
        card_w = 260
        gap = 20
        total_w = 4 * card_w + 3 * gap
        start_x = (1280 - total_w) // 2
        y = 200

        for i, p in enumerate(self.players):
            x = start_x + i * (card_w + gap)
            rect = pygame.Rect(x, y, card_w, 200)
            # фон
            pygame.draw.rect(screen, COLORS["bg_card"], rect, border_radius=14)
            border = COLORS["border"]
            if self.rolled and i == self.winner_idx:
                border = COLORS["positive"]
            pygame.draw.rect(screen, border, rect, 3, border_radius=14)

            # имя
            name = self.f_h2.render(p.name, True, COLORS["text_h"])
            screen.blit(name, name.get_rect(centerx=rect.centerx,
                                            top=rect.y + 16))

            # бросок
            if self.rolled:
                val = self.rolls.get(i, "—")
                big = theme.get_font("oswald", 64, bold=True)
                color = COLORS["hover"] if i == self.winner_idx \
                    else COLORS["text_main"]
                num = big.render(str(val), True, color)
                screen.blit(num, num.get_rect(centerx=rect.centerx,
                                              centery=rect.y + 120))
                if i == self.winner_idx:
                    win = self.f_body.render("ПЕРВЫЙ ХОД", True,
                                             COLORS["positive"])
                    screen.blit(win, win.get_rect(centerx=rect.centerx,
                                                  top=rect.bottom - 30))
            else:
                q = self.f_h2.render("?", True, COLORS["text_secondary"])
                screen.blit(q, q.get_rect(centerx=rect.centerx,
                                          centery=rect.y + 120))

        # Кнопка
        if not self.rolled:
            self.roll_btn.draw(screen)
        else:
            self.start_btn.draw(screen)