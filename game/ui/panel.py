import pygame
from game.config import COLORS, PLAYER_RESOURCES_COLORS
from game.models.player import Player


class InfoPanel:
    def __init__(
        self, x: int, y: int, width: int, height: int, font: pygame.font.Font
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font

    def draw(self, surface: pygame.Surface, player: Player):
        """Отрисовывает панель ресурсов игрока по дизайн-макету."""
        # Рисуем подложку панели и нижнюю границу
        pygame.draw.rect(surface, COLORS["bg_panel"], self.rect)
        pygame.draw.line(
            surface,
            COLORS["border"],
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom),
            2,
        )

        # Вывод названия игрока
        name_surf = self.font.render(
            f"👤 {player.name} ({player.color})", True, COLORS["text_h"]
        )
        surface.blit(name_surf, (self.rect.left + 20, self.rect.top + 18))

        # Вывод ресурсов с их фирменными цветами
        resources = [
            (f"💰 {player.money}", PLAYER_RESOURCES_COLORS["money"]),
            (f"⚡ {player.stamina}", PLAYER_RESOURCES_COLORS["stamina"]),
            (f"🎭 {player.reputation}", PLAYER_RESOURCES_COLORS["reputation"]),
            (f"👑 {player.prestige}/30", PLAYER_RESOURCES_COLORS["prestige"]),
        ]

        curr_x = self.rect.left + 350
        for text, color in resources:
            res_surf = self.font.render(text, True, color)
            surface.blit(res_surf, (curr_x, self.rect.top + 18))
            curr_x += 160
