import pygame


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        font: pygame.font.Font,
        state: str = "active",
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.state = state  # active, disabled, danger, success
        self.is_hovered = False

    def draw(self, surface: pygame.Surface):
        """Отрисовка кнопки на основе состояний палитры UX."""
        from game.config import UI_STATES_COLORS

        # Берем цвета из UX-констант
        colors = UI_STATES_COLORS.get(self.state, UI_STATES_COLORS["active"])
        bg_color = colors["bg"]

        # Если кнопка активна и на неё навели — подсвечиваем цветом ховера
        if self.state == "active" and self.is_hovered:
            bg_color = (143, 227, 255)

        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(
            surface, (42, 68, 112), self.rect, width=2, border_radius=8
        )

        text_surf = self.font.render(self.text, True, colors["text"])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos: tuple):
        """Обновление статуса наведения курсора."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos: tuple, mouse_up: bool) -> bool:
        """UX-правило №1: кнопка в состоянии disabled игнорирует клики."""
        if self.state == "disabled":
            return False
        return self.rect.collidepoint(mouse_pos) and mouse_up