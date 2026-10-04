import pygame
from game.config import COLORS, FONTS_CONFIG, BOARD
from game.logic.game_state import take_turn
from game.ui import theme
from game.ui.board_view import BoardView
from game.ui.button import Button
from game.ui.event_modal import EventModal
from game.ui.player_card import PlayerCard
from game.ui.screens.base_screen import BaseScreen


class GameBoardScreen(BaseScreen):
    def __init__(self, app):
        super().__init__(app)
        self.players = app.players
        self.current_idx = 0
        self.turn_generator = None
        self.current_modal = None
        self.goal_reached = False

        self.f_h1 = theme.get_font("oswald", 32, bold=True)
        self.f_h2 = theme.get_font("oswald", 24, bold=True)
        self.f_logo = theme.get_font("oswald", 17, bold=True)
        self.f_body = theme.get_font("inter", 14)
        self.f_btn = theme.get_font("inter", 14, bold=True)

        # ---------- Layout ----------
        # Header 0..56, board 620×620 по центру, сбоку 4 карточки.
        board_size = 540
        bx = (1280 - board_size) // 2
        self.board = BoardView(pygame.Rect(bx, 64, board_size, board_size))

        card_w, card_h = 300, 120
        self.cards = []
        positions = [
            (16, 72),                            # 1 — верх-лево
            (16, 720 - card_h - 24),             # 2 — низ-лево
            (1280 - card_w - 16, 72),            # 3 — верх-право
            (1280 - card_w - 16, 720 - card_h - 24),  # 4 — низ-право
        ]
        for i, p in enumerate(self.players[:4]):
            rect = pygame.Rect(positions[i][0], positions[i][1], card_w, card_h)
            self.cards.append(PlayerCard(p, i, rect))

        # Кнопка хода
        self.roll_btn = Button(1280 // 2 - 130, 640, 260, 44,
                               "🎲  БРОСИТЬ КОСТИ", self.f_btn)

        self.log_lines: list[str] = []
        self.max_log = 3
        # Лог (короткая строка внизу)
        self.log_rect = pygame.Rect(self.board.rect.x, 600, self.board.rect.w, 32)

    # ---------------------------------------------------- EVENTS
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        # Защита: если модалка есть, но генератор уже мёртв — просто закрываем окно
        if self.current_modal and not self.turn_generator:
            self.current_modal = None
            return

        if self.current_modal:
            self._modal_click(event.pos)
        elif self.roll_btn.is_clicked(event.pos, True):
            self._roll_click()

    def _modal_click(self, pos):
        # Двойная страховка
        if not self.turn_generator:
            self.current_modal = None
            return

        for btn, action in self.current_modal.buttons:
            if not btn.is_clicked(pos, True):
                continue

            # Сразу закрываем окно — что бы дальше ни случилось
            self.current_modal = None

            try:
                if action is not None:
                    step_type, _, msg = self.turn_generator.send(action)
                else:
                    step_type, _, msg = next(self.turn_generator)

                self._push_log(msg)
                # Продолжаем крутить генератор до следующего yield/StopIteration
                self._advance_generator()
            except StopIteration:
                # Ход завершён — модалки уже нет, генератора тоже
                self._finish_turn()

            break

    def _roll_click(self):
        if self.turn_generator is not None:
            return
        active = self.players[self.current_idx]
        if getattr(active, "is_bankruptcy", False):
            self.current_idx = (self.current_idx + 1) % len(self.players)
            return
        if hasattr(active, "check_stamina_depletion") and active.check_stamina_depletion():
            self._show_modal("S16 · Экстренные сборы",
                             f"{active.name} теряет стамину. Ход пропущен.",
                             [("Понятно · на сборы", None, "danger")])
            return
        if getattr(active, "skip_next_turn", False):
            active.skip_next_turn = False
            self._show_modal("S13 · Time Out",
                             f"{active.name} пропускает раунд.",
                             [("Пропустить паузу", None, "success")])
            return
        self.turn_generator = take_turn(self.players, self.current_idx)
        self._advance_generator()

    def _advance_generator(self):
        """Прогоняет генератор до следующего модального шага.
        Если генератор пуст или мёртв — завершает ход."""
        if not self.turn_generator:
            return

        try:
            step_type, obj, msg = next(self.turn_generator)
        except StopIteration:
            self._finish_turn()
            return

        self._push_log(msg)

        if step_type == "await_buy":
            self._show_modal("S06 · Арена", msg,
                             [("Купить", {"buy": True}, "success"),
                              ("Отказаться", {"buy": False}, "danger")])
        elif step_type == "await_choice":
            self._show_modal("S12 · Допинг-контроль", msg,
                             [("Честная", {"doping_type": "fair"}, "active"),
                              ("Тёмная", {"doping_type": "dark"}, "danger")])

        elif step_type == "await_transfer":
            opp = 1 - self.current_idx
            self._show_modal("S14 · Громкий трансфер", msg,
                             [("Монеты (10)", (opp, "money"), "active"),
                              ("Стамина (6)", (opp, "stamina"), "active")])
        elif step_type == "global_event":
            self._show_modal("S10 · Глобальное событие", msg,
                             [("Принять закон круга", None, "danger")])
        else:
            self._show_modal("Событие", msg, [("ОК", None, "active")])

    def _show_modal(self, title, text, buttons):
        self.current_modal = EventModal(title, text, self.f_h2, (1280, 720))
        for label, action, state in buttons:
            self.current_modal.add_button(label, action, state=state)

    def _finish_turn(self):
        # 1) Всегда сначала обнуляем всё, что связано с активным ходом
        self.turn_generator = None
        self.current_modal = None

        # 2) Проверка цели
        if self.players[self.current_idx].prestige >= 30:
            self.goal_reached = True

        # 3) Переход на победный экран только после доигранного круга
        if self.goal_reached and self.current_idx == len(self.players) - 1:
            from game.ui.screens.victory import VictoryScreen
            self.app.goto(VictoryScreen)
            return

        # 4) Передаём ход следующему
        self.current_idx = (self.current_idx + 1) % len(self.players)

    def _push_log(self, msg):
        self.log_lines.append(msg)
        self.log_lines = self.log_lines[-self.max_log:]

    # ---------------------------------------------------- UPDATE / DRAW
    def update(self, dt, mouse_pos):
        self.roll_btn.update(mouse_pos)
        if self.current_modal:
            for b, _ in self.current_modal.buttons:
                b.update(mouse_pos)

    def _draw_header(self, screen):
        bar = pygame.Rect(0, 0, 1280, 56)
        pygame.draw.rect(screen, COLORS["bg_panel"], bar)
        pygame.draw.line(screen, COLORS["border"], (0, 56), (1280, 56), 1)

        logo = self.f_logo.render("МОНОПОЛИЯ НА ЛЬДУ", True, COLORS["text_h"])
        screen.blit(logo, (24, 18))

        sub = self.f_body.render("S04 · ПОЛЕ", True, COLORS["text_secondary"])
        screen.blit(sub, sub.get_rect(centerx=1280 // 2, centery=28))

        turn = self.players[self.current_idx]
        right = self.f_body.render(f"Ход: {turn.name}", True, COLORS["hover"])
        screen.blit(right, right.get_rect(right=1280 - 24, centery=28))

    def _draw_log(self, screen):
        r = self.log_rect
        for i, line in enumerate(self.log_lines):
            color = COLORS["text_main"] if i == len(self.log_lines) - 1 \
                else COLORS["text_secondary"]
            t = self.f_body.render("• " + line[:110], True, color)
            screen.blit(t, (r.x, r.y - i * 16))

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])
        self._draw_header(screen)

        # Карточки игроков
        for i, card in enumerate(self.cards):
            card.draw(screen, active=(i == self.current_idx))

        # Доска
        owned = getattr(self, "owned_map", None)
        self.board.draw(screen, self.players, owned)

        # Кнопка броска — только когда нет активного хода
        if self.turn_generator is None and not self.goal_reached:
            self.roll_btn.draw(screen)

        self._draw_log(screen)

        # Модалка поверх всего
        if self.current_modal:
            self.current_modal.draw(screen)