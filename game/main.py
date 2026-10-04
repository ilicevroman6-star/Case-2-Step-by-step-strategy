import pygame
from game.models.player import Player
from game.logic.game_state import take_turn


pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Хоккейный Менеджер Монополия")
clock = pygame.time.Clock()

# Создаем список наших игроков.
players = [
    Player("Алиса", "Red"),
    Player("Дима", "Blue"),
    Player("Андрей", "Green"),
    Player("Рома", "Yellow")
]

current_player_idx = 0  # Индекс игрока, который сейчас ходит
active_turn_gen = None  # Сюда мы запишем генератор, когда ход начнется
current_stage = "START_TURN"  # Состояние интерфейса: START_TURN, SHOW_MODAL, AWAIT_ACTION

# Переменная для хранения текста логов, чтобы рисовать их в UI
ui_log_text = "Игра началась! Нажмите ПРОБЕЛ, чтобы бросить кубик."
# =====================================================================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ PYGAME
# =====================================================================
running = True
while running:

    # 1. СБОР И ОБРАБОТКА СОБЫТИЙ
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        # Управление шагами игры через клавиатуру
        if e.type == pygame.KEYDOWN:

            # Нажатие ПРОБЕЛА продвигает ход вперед (кидает кубик, закрывает модалки)
            if e.key == pygame.K_SPACE:

                # Если ход игрока еще не начался (генератор пустой) — создаем его
                if active_turn_gen is None:
                    current_player = players[current_player_idx]

                    # Проверка на банкротство
                    if getattr(current_player, "is_bankruptcy", False) or getattr(current_player, "is_dead", False):
                        current_player_idx = (current_player_idx + 1) % len(players)
                        continue

                    # Проверка на пропуск хода от Честного допинг-контроля
                    if getattr(current_player, "skip_next_turn", False):
                        current_player.skip_next_turn = False
                        ui_log_text = f"🚫 {current_player.name} пропускает этот ход (Допинг-контроль)!\nНажмите ПРОБЕЛ для передачи хода."
                        current_player_idx = (current_player_idx + 1) % len(players)
                        continue

                    # Запускаем генератор для текущего игрока
                    active_turn_gen = take_turn(players, current_player_idx)

                try:
                    # Делаем следующий шаг внутри нашего генератора take_turn
                    # Функция возвращает нам кортеж: (тип_шага, объект_события, текст_лога)
                    step_type, obj, log = next(active_turn_gen)
                    ui_log_text = log  # Выводим текст события на экран

                    # Если генератор просит интерактивный выбор — меняем стадию игры
                    if step_type in ("await_doping_choice", "await_transfer_choice", "await_buy_arena", "await_action"):
                        current_stage = "CHOICE_PENDING"
                    else:
                        current_stage = "SHOW_MODAL"

                except StopIteration:
                    # Генератор хода выбросил StopIteration -> Ход полностью закончен
                    active_turn_gen = None
                    current_player_idx = (current_player_idx + 1) % len(players)
                    ui_log_text = f"🔄 Ход завершен.\nСледующим ходит: {players[current_player_idx].name}. (Нажмите ПРОБЕЛ)"
                    current_stage = "START_TURN"

            # --- Обработка интерактивного выбора на спец-клетках ---
            if current_stage == "CHOICE_PENDING":

                # Игрок нажал 'Y' (Да / Честный допинг / Купить Арену)
                if e.key == pygame.K_y:
                    try:
                        # Отправляем решение обратно в генератор через .send()
                        step_type, obj, log = active_turn_gen.send({"buy": True, "doping_type": "fair"})
                        ui_log_text = log
                        current_stage = "SHOW_MODAL"
                    except StopIteration:
                        active_turn_gen = None
                        current_player_idx = (current_player_idx + 1) % len(players)

                # Игрок нажал 'N' (Нет / Темный допинг / Отказаться от покупки)
                if e.key == pygame.K_n:
                    try:
                        step_type, obj, log = active_turn_gen.send({"buy": False, "doping_type": "dark"})
                        ui_log_text = log
                        current_stage = "SHOW_MODAL"
                    except StopIteration:
                        active_turn_gen = None
                        current_player_idx = (current_player_idx + 1) % len(players)

                # Игрок нажал 'P' (Пас в финальной фазе ходов await_action)
                if e.key == pygame.K_p:
                    try:
                        # Отправляем None или пустой словарь, чтобы выйти из цикла Этапа 5 в game_state
                        step_type, obj, log = active_turn_gen.send(None)
                    except StopIteration:
                        active_turn_gen = None
                        current_player_idx = (current_player_idx + 1) % len(players)
                        ui_log_text = f"🔄 Ход завершен.\nСледующим ходит: {players[current_player_idx].name}. (Нажмите ПРОБЕЛ)"
                        current_stage = "START_TURN"

    # 2. ОТРИСОВКА ИНТЕРФЕЙСА
    screen.fill((35, 35, 35))  # Темно-серый фон
    font = pygame.font.SysFont("Arial", 22)

    # --- Отрисовка логов и текста событий (в левой части экрана) ---
    y_offset = 60
    for line in ui_log_text.split('\n'):
        text_surface = font.render(line, True, (240, 240, 240))
        screen.blit(text_surface, (50, y_offset))
        y_offset += 32

    # --- Отрисовка статус-панелей игроков (в правой части экрана) ---
    for idx, p in enumerate(players):
        # Собираем строку характеристик
        p_arenas = len(getattr(p, 'owned_arenas', []))
        player_info = f"{p.name}: 💵 {p.money} | ⚡ {p.stamina} | ⭐ {p.reputation} | Клетка {p.arena} | Арен: {p_arenas}"

        # Если игрок обанкротился — зачеркиваем/красим в красный
        if getattr(p, "is_bankruptcy", False) or getattr(p, "is_dead", False):
            info_color = (200, 50, 50)
            player_info += " (ВЫБЫЛ)"
        # Подсвечиваем золотым того, чей сейчас ход
        elif idx == current_player_idx:
            info_color = (255, 215, 0)
        else:
            info_color = (170, 170, 170)

        info_surface = font.render(player_info, True, info_color)
        screen.blit(info_surface, (720, 60 + idx * 45))

    # --- Подсказки по управлению внизу экрана ---
    if current_stage == "CHOICE_PENDING":
        prompt_text = "[ВЫБОР]: Нажмите Y (Да / Честно) или N (Нет / Темно). Для фазы действий: P (Пас)"
        prompt_surface = font.render(prompt_text, True, (255, 120, 120))
        screen.blit(prompt_surface, (50, 640))
    else:
        prompt_surface = font.render("[УПРАВЛЕНИЕ]: Нажимайте ПРОБЕЛ для продвижения игры.", True, (120, 255, 120))
        screen.blit(prompt_surface, (50, 640))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
