# game/ui/player_card.py
import pygame
from game.config import (COLORS, PLAYER_CHIPS_COLORS, PLAYER_RESOURCES_COLORS)
from game.ui import theme, widgets


class PlayerCard:
    def __init__(self, player, player_id: int, rect: pygame.Rect):
        self.player = player
        self.player_id = player_id
        self.rect = rect
        self.f_name = theme.get_font("inter", 15, bold=True)
        self.f_small = theme.get_font("inter", 13, bold=False)
        self.f_num = theme.get_font("oswald", 22, bold=True)

    def draw(self, screen, active: bool = False):
        r = self.rect
        chip = PLAYER_CHIPS_COLORS.get(self.player_id, COLORS["hover"])

        # фон + активная обводка
        if active:
            theme.glow_circle(screen, r.center, max(r.w, r.h) // 2, chip, layers=3)
        theme.drop_shadow(screen, r, radius=10, alpha=100, offset=4)
        pygame.draw.rect(screen, COLORS["bg_card"], r, border_radius=10)
        border_col = chip if active else COLORS["border"]
        pygame.draw.rect(screen, border_col, r, 2 if active else 1, border_radius=10)

        # цветной ярлык + имя
        tag = pygame.Rect(r.x + 12, r.y + 12, 6, 22)
        pygame.draw.rect(screen, chip, tag, border_radius=3)

        name = self.f_name.render(self.player.name, True, COLORS["text_h"])
        screen.blit(name, (r.x + 26, r.y + 12))

        # бейдж "СЕЙЧАС"
        if active:
            b = pygame.Rect(r.right - 76, r.y + 14, 64, 18)
            widgets.draw_badge(screen, b, "СЕЙЧАС", chip,
                               (10, 20, 40), theme.get_font("inter", 10, True))

        # блоки ресурсов
        y = r.y + 46
        col_w = (r.w - 36) // 2
        items = [
            ("money",      getattr(self.player, "money", 0)),
            ("stamina",    getattr(self.player, "stamina", 0)),
            ("reputation", getattr(self.player, "reputation", 0)),
            ("prestige",   getattr(self.player, "prestige", 0)),
        ]
        for i, (kind, val) in enumerate(items):
            cx = r.x + 16 + (i % 2) * col_w
            cy = y + (i // 2) * 26
            lbl = {"money": "Монеты", "stamina": "Выносл.",
                   "reputation": "Репутация", "prestige": "Престиж"}[kind]
            t_lbl = self.f_small.render(lbl, True, COLORS["text_secondary"])
            t_val = self.f_num.render(str(val), True,
                                      PLAYER_RESOURCES_COLORS[kind])
            screen.blit(t_lbl, (cx, cy))
            screen.blit(t_val, (cx + col_w - t_val.get_width() - 6, cy - 4))