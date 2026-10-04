BOARD = [
    "Старт", "Арена", "Медиа", "Тренировка", "Арена", "Random", "Арена",
    "Time out", "Арена", "Медиа", "Random", "Арена", "Тренировка", "Арена",
    "Допинг контроль", "Арена", "Матч", "Random", "Тренировка", "Медиа",
    "Арена", "Громкий трансфер", "Арена", "Тренировка", "Медиа", "Арена",
    "Random", "Матч",
]

DEFAULT_BUY_PRICE = 12
DEFAULT_RENT_PRICE = 4
MORTGAGE_VALUE = 6

ARENA_PRICES = {
    index: {'buy_price': DEFAULT_BUY_PRICE, 'rent_price': DEFAULT_RENT_PRICE}
    for index, tile in enumerate(BOARD) if tile == 'Арена'
}