import pygame
from game.config import COLORS
from game.ui.button import Button


class EventModal:
    def __init__(
        self,
        title: str,
        message: str,
        font: pygame.font.Font,
        screen_size: tuple,
    ):
        self.font = font
        self.screen_width, self.screen_height = screen_size

        self.width = 520
        self.height = 320
        self.rect = pygame.Rect(
            (self.screen_width - self.width) // 2,
            (self.screen_height - self.height) // 2,
            self.width,
            self.height,
        )

        self.title = title
        self.message = message
        self.buttons = []

    def add_button(self, text: str, action_value, state: str = "active"):
        """Добавляет кнопку в окно и выравнивает её снизу."""
        btn_width = 140
        btn_height = 40
        spacing = 15
        idx = len(self.buttons)

        # Центрирование кнопок в ряд на нижней панели модалки
        total_buttons_width = (idx + 1) * btn_width + idx * spacing
        start_x = self.rect.centerx - total_buttons_width // 2

        # Пересчитываем координаты для уже созданных кнопок, чтобы они стояли ровно
        for i, (b, val) in enumerate(self.buttons):
            b.rect.x = start_x + i * (btn_width + spacing)

        x = start_x + idx * (btn_width + spacing)
        y = self.rect.bottom - btn_height - 25

        btn = Button(x, y, btn_width, btn_height, text, self.font, state=state)
        self.buttons.append((btn, action_value))

    def draw(self, surface: pygame.Surface):
        """Отрисовка оверлея и тела карточки модального окна."""
        # 1. Затемнение поля по ТЗ (rgba(7, 13, 26, 0.74))
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        overlay.fill((7, 13, 26, 188))
        surface.blit(overlay, (0, 0))

        # 2. Карточка окна
        pygame.draw.rect(surface, COLORS["bg_card"], self.rect, border_radius=12)
        pygame.draw.rect(
            surface, COLORS["border"], self.rect, width=3, border_radius=12
        )

        # 3. Заголовок события
        title_surf = self.font.render(self.title, True, (245, 197, 24))
        title_rect = title_surf.get_rect(
            centerx=self.rect.centerx, top=self.rect.top + 20
        )
        surface.blit(title_surf, title_rect)

        # 4. Вывод текста с переносом строк
        words = self.message.split(" ")
        lines = []
        curr_line = ""
        for word in words:
            test_line = curr_line + word + " "
            if self.font.size(test_line)[0] < self.width - 40:
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = word + " "
        lines.append(curr_line)

        y_offset = self.rect.top + 80
        for line in lines[:4]:
            txt_surf = self.font.render(line.strip(), True, COLORS["text_main"])
            txt_rect = txt_surf.get_rect(
                centerx=self.rect.centerx, top=y_offset
            )
            surface.blit(txt_surf, txt_rect)
            y_offset += self.font.get_linesize() + 4

        # 5. Отрисовка кнопок
        for btn, _ in self.buttons:
            btn.draw(surface)
