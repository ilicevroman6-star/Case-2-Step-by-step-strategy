# game/ui/board_view.py
import pygame
from game.config import BOARD, BOARD_CELLS, COLORS, TILE_COLORS, PLAYER_CHIPS_COLORS
from game.ui import theme


def tile_grid_pos(idx: int, cells: int = BOARD_CELLS) -> tuple[int, int]:
    """Позиция клетки idx (0..27) на сетке 8×8.
    idx=0 — правый-нижний угол, движение против часовой стрелки."""
    if idx < 8:                # нижний ряд справа-налево
        return cells - 1, cells - 1 - idx
    if idx < 14:               # левая колонка снизу-вверх
        return cells - 2 - (idx - 8), 0
    if idx < 22:               # верхний ряд слева-направо
        return 0, idx - 14
    return idx - 21, cells - 1 # правая колонка сверху-вниз


class BoardView:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.cw = rect.w // BOARD_CELLS
        self.ch = rect.h // BOARD_CELLS
        self.f_label = theme.get_font("inter", 10, bold=True)
        self.f_price = theme.get_font("oswald", 14, bold=True)

    def _cell_rect(self, idx: int) -> pygame.Rect:
        row, col = tile_grid_pos(idx)
        return pygame.Rect(self.rect.x + col * self.cw,
                           self.rect.y + row * self.ch,
                           self.cw, self.ch)

    def _draw_tile(self, screen, idx, name):
        r = self._cell_rect(idx)
        base = TILE_COLORS.get(name, COLORS["bg_card"])
        pygame.draw.rect(screen, base, r, border_radius=6)
        pygame.draw.rect(screen, COLORS["border"], r, 1, border_radius=6)

        # Полоса-подсветка сверху (как в макете)
        stripe = pygame.Rect(r.x + 4, r.y + 3, r.w - 8, 3)
        pygame.draw.rect(screen, tuple(min(255, c + 40) for c in base),
                         stripe, border_radius=2)

        # Подпись: крупная для углов (Старт, Допинг, Time Out, Трансфер), мелкая для остальных
        is_corner = idx in (0, 7, 14, 21)
        label = name.upper()
        color = COLORS["text_h"] if is_corner else COLORS["text_main"]
        f = self.f_price if is_corner else self.f_label
        text = f.render(label, True, color)
        screen.blit(text, text.get_rect(center=r.center))

    def _draw_center(self, screen):
        """Центральная площадка: логотип/статус."""
        inner = pygame.Rect(self.rect.x + self.cw,
                            self.rect.y + self.ch,
                            self.rect.w - 2 * self.cw,
                            self.rect.h - 2 * self.ch)
        pygame.draw.rect(screen, COLORS["bg_panel"], inner, border_radius=16)
        pygame.draw.rect(screen, COLORS["border"], inner, 2, border_radius=16)

    def draw_players(self, screen, players):
        """Рисуем фишки игроков. Ожидается player.position ∈ 0..27."""
        # группируем по клетке, чтобы фишки не накладывались
        buckets: dict[int, list[int]] = {}
        for i, p in enumerate(players):
            pos = getattr(p, "arena", 0)
            buckets.setdefault(pos, []).append(i)

        for tile_idx, player_ids in buckets.items():
            r = self._cell_rect(tile_idx)
            n = len(player_ids)
            for k, pid in enumerate(player_ids):
                # веерная раскладка по 4 точкам
                offs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
                ox, oy = offs[k % 4]
                cx = r.centerx + int(ox * r.w * 0.35)
                cy = r.centery + int(oy * r.h * 0.35)

                color = PLAYER_CHIPS_COLORS.get(pid, COLORS["hover"])
                theme.glow_circle(screen, (cx, cy), 8, color, layers=2)
                pygame.draw.circle(screen, color, (cx, cy), 14)
                pygame.draw.circle(screen, (255, 255, 255), (cx, cy), 14, 2)

                num = theme.get_font("oswald", 14, bold=True).render(
                    str(pid + 1), True, (10, 20, 40))
                screen.blit(num, num.get_rect(center=(cx, cy)))

    def draw(self, screen, players, owned_map=None):
        """owned_map: {tile_idx: player_id} для цветовой метки владельца."""
        # фон доски
        theme.drop_shadow(screen, self.rect, radius=16, alpha=120, offset=8)
        pygame.draw.rect(screen, COLORS["bg_main"], self.rect, border_radius=16)

        self._draw_center(screen)
        for i, name in enumerate(BOARD):
            self._draw_tile(screen, i, name)
            if owned_map and i in owned_map:
                r = self._cell_rect(i)
                bar = pygame.Rect(r.x + 4, r.bottom - 6, r.w - 8, 4)
                pygame.draw.rect(screen,
                                 PLAYER_CHIPS_COLORS[owned_map[i]],
                                 bar, border_radius=2)

        self.draw_players(screen, players)