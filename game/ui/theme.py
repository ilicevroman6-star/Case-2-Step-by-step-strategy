# game/ui/theme.py
import os
import pygame

_FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts")
_CACHE: dict[tuple, pygame.font.Font] = {}

def _sys_fallback(name: str) -> str:
    # Oswald/Inter в системах не стоят — откатываемся на Arial
    return "arial"

def get_font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    key = (name, size, bold)
    if key in _CACHE:
        return _CACHE[key]
    ttf = os.path.join(_FONT_DIR, f"{name}.ttf")
    if os.path.exists(ttf):
        font = pygame.font.Font(ttf, size)
        if bold:
            font.set_bold(True)
    else:
        font = pygame.font.SysFont(_sys_fallback(name), size, bold=bold)
    _CACHE[key] = font
    return font

def font_from(cfg: dict) -> pygame.font.Font:
    return get_font(cfg["name"], cfg["size"], cfg.get("bold", False))

# Тени и свечения
def drop_shadow(surface, rect, radius=12, alpha=140, offset=6):
    sh = pygame.Surface((rect.w + 2 * offset, rect.h + 2 * offset), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0, 0, 0, alpha),
                     pygame.Rect(offset, offset, rect.w, rect.h),
                     border_radius=radius)
    surface.blit(sh, (rect.x - offset, rect.y - offset))

def glow_circle(surface, center, radius, color, layers=4):
    for i in range(layers, 0, -1):
        alpha = max(6, 30 // i)
        r = radius * i
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, alpha), (r, r), r)
        surface.blit(s, (center[0] - r, center[1] - r))