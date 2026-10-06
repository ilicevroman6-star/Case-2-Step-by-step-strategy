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
        self.winner_idx: int | None = None

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
                               "  БРОСИТЬ КОСТИ", self.f_btn)

        # Лог
        self.log_lines: list[str] = []
        self.max_log = 5
        # Последний бросок
        self.last_dice = None
        self.last_player = None
        # Лог (короткая строка внизу)
        self.log_rect = pygame.Rect(20, 690, 1240, 30)
        self.round_state = {"global_fired": False}

    # ---------------------------------------------------- EVENTS
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        if self.current_modal:
            self._modal_click(event.pos)
        elif self.roll_btn.is_clicked(event.pos, True):
            self._roll_click()

    def _modal_click(self, pos):
        print(f"[MC] buttons={[(b.text, a) for b, a in self.current_modal.buttons]}")
        for btn, action in self.current_modal.buttons:
            if not btn.is_clicked(pos, True):
                continue

            # ── Специальные действия без генератора ─────────────────


            if action == "skip_turn":
                # Закрыли S13/S16 — пропускаем ход, передаём дальше
                self.current_modal = None
                self._finish_turn()
                return

            # ── Обычные действия через turn_generator ───────────────
            if not self.turn_generator:
                # Модалка-сирота без генератора — просто закрыть
                self.current_modal = None
                return

            self.current_modal = None

            if action is None:
                self._advance_generator()
            else:
                try:
                    step_type, obj, msg = self.turn_generator.send(action)
                except StopIteration:
                    self._finish_turn()
                else:
                    self._process_step(step_type, obj, msg)
            return

    def _roll_click(self):
        # Если ход уже идёт — игнорируем клик
        if self.turn_generator is not None:
            return

        active = self.players[self.current_idx]

        # Банкрот — молча передаём ход
        if getattr(active, "is_bankruptcy", False):
            self.current_idx = (self.current_idx + 1) % len(self.players)
            return

        # Кончилась стамина — S16, пропуск хода
        if hasattr(active, "check_stamina_depletion") and active.check_stamina_depletion():
            self._show_modal("S16 · Экстренные сборы",
                             f"{active.name} теряет стамину. Ход пропущен.",
                             [("Понятно · на сборы", "skip_turn", "danger")])
            return

        # Time Out — S13, пропуск хода
        if getattr(active, "skip_next_turn", False):
            active.skip_next_turn = False
            self._show_modal("S13 · Time Out",
                             f"{active.name} пропускает раунд.",
                             [("Пропустить паузу", "skip_turn", "success")])
            return

        # Всё чисто — старт хода.
        # S10 при необходимости выпадет внутри take_turn, при пересечении старта.
        self._start_turn(active)

    def _start_turn(self, active):
        self.last_player = active
        self.turn_generator = take_turn(self.players, self.current_idx, self.round_state)
        self._advance_generator()
        self.last_dice = getattr(active, "last_dice", None)

    def _advance_generator(self):
        """Ровно один next() и обработка полученного шага."""
        if not self.turn_generator:
            return
        try:
            step_type, obj, msg = next(self.turn_generator)
        except StopIteration:
            self._finish_turn()
            return
        self._process_step(step_type, obj, msg)

    def _process_step(self, step_type, obj, msg):
        """Единственное место, где решается, какую модалку показывать."""
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
        elif step_type == "global_event":  # ← вернуть блок
            self._show_modal("S10 · Глобальное событие", msg,
                             [("Принять закон круга", None, "active")])  # action=None
        else:
            self._show_modal("Событие", msg, [("ОК", None, "active")])

    def _show_modal(self, title, text, buttons):
        self.current_modal = EventModal(title, text, self.f_h2, (1280, 720))
        for label, action, state in buttons:
            self.current_modal.add_button(label, action, state=state)

    def _finish_turn(self):
        old = self.current_idx
        self.turn_generator = None
        self.current_modal = None

        if self.players[self.current_idx].prestige >= 30 and not self.goal_reached:
            self.goal_reached = True
            self.winner_idx = self.current_idx
            self.app.winner_idx = self.current_idx

        # Переход к следующему
        self.current_idx = (self.current_idx + 1) % len(self.players)

        # Если ход вернулся к 0 — круг завершён, разрешаем новое событие
        if self.current_idx == 0:
            self.round_state["global_fired"] = False

        if self.goal_reached and self.current_idx == self.winner_idx:
            from game.ui.screens.victory import VictoryScreen
            self.app.goto(VictoryScreen)

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


        turn = self.players[self.current_idx]
        right = self.f_body.render(f"Ход: {turn.name}", True, COLORS["hover"])
        screen.blit(right, right.get_rect(right=1280 - 24, centery=28))

    def _draw_log(self, screen):
        r = self.log_rect
        n = len(self.log_lines)
        for i, line in enumerate(self.log_lines):
            # i=0 — самая старая строка; i=n-1 — самая свежая
            # рисуем сверху вниз внутри log_rect
            color = COLORS["text_main"] if i == n - 1 \
                else COLORS["text_secondary"]
            t = self.f_body.render("• " + line[:110], True, color)
            screen.blit(t, (r.x, r.y + i * 16))

    def draw(self, screen):
        screen.fill(COLORS["bg_main"])
        self._draw_header(screen)

        # Карточки игроков
        for i, card in enumerate(self.cards):
            card.draw(screen, active=(i == self.current_idx))


        # Доска — собираем карту владельцев арен
        owned = {}
        for p_idx, p in enumerate(self.players):
            for arena_idx in getattr(p, "owned_arenas", []):
                owned[arena_idx] = p_idx
        self.board.draw(screen, self.players, owned)

        # Показываем последний бросок (сохранён в self.last_dice)
        if self.last_dice is not None and self.last_player is not None:
            dice_surf = self.f_h2.render(
                f"{self.last_player.name}: {self.last_dice}",
                True,
                COLORS["hover"]
            )
            dice_rect = dice_surf.get_rect(
                center=(self.board.rect.left - 170, self.board.rect.centery)
            )
            screen.blit(dice_surf, dice_rect)

        # Кнопка броска — только когда нет активного хода
        if self.turn_generator is None:
            self.roll_btn.draw(screen)

        self._draw_log(screen)

        # Модалка поверх всего
        if self.current_modal:
            self.current_modal.draw(screen)