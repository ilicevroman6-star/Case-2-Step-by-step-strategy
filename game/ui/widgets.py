# game/ui/widgets.py
import pygame
from game.config import COLORS, PLAYER_RESOURCES_COLORS
from game.ui import theme


def draw_resource_pill(screen, pos, kind, value, font):
    """Маленькая плашка: иконка-буква + значение. kind ∈ money|stamina|reputation|arena|prestige."""
    color = PLAYER_RESOURCES_COLORS.get(kind, COLORS["text_main"])
    icon = {"money": "$", "stamina": "⚡", "reputation": "♥",
            "arena": "▲", "prestige": "★"}.get(kind, "•")
    txt = font.render(f"{icon} {value}", True, color)
    screen.blit(txt, pos)
    return txt.get_width()


def draw_progress(screen, rect, ratio, color_from, color_to):
    """Градиентный прогресс-бар."""
    pygame.draw.rect(screen, COLORS["bg_main"], rect, border_radius=rect.h // 2)
    pygame.draw.rect(screen, COLORS["border"], rect, 1, border_radius=rect.h // 2)
    fill_w = max(0, min(rect.w, int(rect.w * ratio)))
    if fill_w <= 0:
        return
    fill = pygame.Rect(rect.x, rect.y, fill_w, rect.h)
    grad = pygame.Surface((fill_w, rect.h), pygame.SRCALPHA)
    for x in range(fill_w):
        t = x / max(1, fill_w - 1)
        c = tuple(int(color_from[i] + (color_to[i] - color_from[i]) * t)
                  for i in range(3))
        pygame.draw.line(grad, c, (x, 0), (x, rect.h))
    mask = pygame.Surface((fill_w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                     border_radius=rect.h // 2)
    grad.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(grad, fill.topleft)


def draw_badge(screen, rect, text, color_bg, color_text, font):
    pygame.draw.rect(screen, color_bg, rect, border_radius=rect.h // 2)
    t = font.render(text, True, color_text)
    screen.blit(t, t.get_rect(center=rect.center))