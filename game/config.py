BOARD = [
    "Старт", "Арена", "Медиа", "Тренировка", "Арена", "Random", "Арена",
    "Time out", "Арена", "Медиа", "Random", "Арена", "Тренировка", "Арена",
    "Допинг контроль", "Арена", "Матч", "Random", "Тренировка", "Медиа",
    "Арена", "Громкий трансфер", "Арена", "Тренировка", "Медиа", "Арена",
    "Random", "Матч",
]
BOARD_CELLS = 8

DEFAULT_BUY_PRICE = 12
DEFAULT_RENT_PRICE = 4
MORTGAGE_VALUE = 6

ARENA_PRICES = {
    index: {'buy_price': DEFAULT_BUY_PRICE, 'rent_price': DEFAULT_RENT_PRICE}
    for index, tile in enumerate(BOARD) if tile == 'Арена'
}

# 1.1 Основа + 1.2 Текст + 1.3 Акценты
COLORS = {
    "bg_main":   (10, 20, 40),      # #0A1428 ночной лёд
    "bg_panel":  (18, 32, 61),      # #12203D раздевалка
    "bg_card":   (27, 47, 85),      # #1B2F55 лёд в тени
    "border":    (42, 68, 112),     # #2A4470 голубой туман
    "text_h":    (255, 255, 255),   # #FFFFFF снег
    "text_main": (201, 220, 240),   # #C9DCF0 иней
    "text_secondary": (124, 140, 168),  # #7C8CA8 сталь
    "btn_primary": (79, 184, 240),  # #4FB8F0 ледяной
    "hover":     (143, 227, 255),   # #8FE3FF свечение
    "negative":  (228, 57, 59),     # #E4393B красная линия
    "positive":  (47, 181, 107),    # #2FB56B зелёный рывок
    "overlay":   (7, 13, 26, 189),  # rgba(7,13,26,0.74) для модалок
}

# 1.4 Ресурсы
PLAYER_RESOURCES_COLORS = {
    "money":      (245, 197, 24),   # gold
    "stamina":    (47, 181, 107),   # stam
    "reputation": (255, 93, 143),   # rep
    "arena":      (255, 138, 31),   # orange
    "prestige":   (143, 227, 255),  # glow
}

# 1.5 Цвета клеток
TILE_COLORS = {
    "Старт":           (228, 57, 59),
    "Арена":           (255, 138, 31),
    "Тренировка":      (47, 181, 107),
    "Медиа":           (155, 81, 224),
    "Random":          (11, 15, 26),
    "Матч":            (37, 99, 235),
    "Допинг контроль": (226, 232, 240),
    "Time out":        (100, 116, 139),
    "Громкий трансфер":(245, 197, 24),
}

# 1.6 Фишки
PLAYER_CHIPS_COLORS = {
    0: (79, 184, 240),   # Ледоруб  – Primary
    1: (245, 197, 24),   # Золото
    2: (255, 93, 143),   # Король
    3: (163, 230, 53),   # Лайм
}

# 1.7 Состояния
UI_STATES_COLORS = {
    "active":   {"bg": (79, 184, 240),  "text": (10, 20, 40)},
    "disabled": {"bg": (27, 47, 85),    "text": (124, 140, 168)},
    "danger":   {"bg": (228, 57, 59),   "text": (255, 255, 255)},
    "success":  {"bg": (47, 181, 107),  "text": (4, 38, 15)},
}

# 2. Шрифты (Oswald — заголовки, Inter — текст; Arial как fallback)
FONTS_CONFIG = {
    "h1":         {"name": "oswald", "size": 48, "bold": True},
    "h2":         {"name": "oswald", "size": 32, "bold": True},
    "h3":         {"name": "oswald", "size": 24, "bold": True},
    "h4":         {"name": "oswald", "size": 17, "bold": True},
    "body":       {"name": "inter",  "size": 16, "bold": False},
    "body_small": {"name": "inter",  "size": 14, "bold": False},
    "body_strong":{"name": "inter",  "size": 16, "bold": True},
    "caption":    {"name": "inter",  "size": 12, "bold": True},
    "caption_xs": {"name": "inter",  "size": 10, "bold": True},
    "resources":  {"name": "oswald", "size": 28, "bold": True},
    "buttons":    {"name": "inter",  "size": 14, "bold": True},
}