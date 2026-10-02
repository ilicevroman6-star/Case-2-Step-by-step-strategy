import random
from game.config import BOARD, ARENA_PRICES, DEFAULT_BUY_PRICE
from game.logic.events_pool import GLOBAL_EVENTS, RANDOM_TILE_EVENTS, MEDIA_TILE_EVENTS
from game.models.action import Action


def take_turn(players, current_index):
    """Генератор хода. Отвечает только за перемещение и логику шагов."""

    player = players[current_index]
    if player.is_bankruptcy:
        return

    # 1. ПЕРЕМЕЩЕНИЕ И КРУГ.
    dice = random.randint(1, 6)
    # Считаем чистую новую позицию БЕЗ деления по кругу.
    new_position = player.arena + dice

    # Проверяем, пересек ли игрок конец доски.
    passed_start = new_position >= len(BOARD)

    # И только теперь сохраняем игроку его позицию с учетом круга.
    player.arena = new_position % len(BOARD)

    if passed_start:
        Action(effects={"money": 20, "stamina": 5, "reputation": 3}).execute(
            player
        )
        global_event = random.choice(GLOBAL_EVENTS)
        yield (
            "global_event",
            global_event,
            global_event.realize(player, positive=random.random() < 0.5),
        )

    current_tile = BOARD[player.arena]

    # 2. АВТОМАТИЧЕСКАЯ РЕНТА
    if current_tile == "Арена":
        for owner in players:
            if owner != player and player.arena in owner.owned_arenas:
                final_rent = (
                    ARENA_PRICES[player.arena]["rent_price"] * player.rent
                )
                Action(cost={"money": final_rent}).execute(player)
                Action(effects={"money": final_rent}).execute(owner)
                break

    # 3. ЛОКАЛЬНЫЕ СОБЫТИЯ И ИНТЕРАКТИВНЫЕ КЛЕТКИ
    if current_tile == "Random":
        is_positive = random.random() < 0.5
        yield "log", random.choice(RANDOM_TILE_EVENTS).realize(
            player, positive=is_positive
        )

    elif current_tile == "Медиа":
        is_positive = random.random() < 0.5
        yield "log", random.choice(MEDIA_TILE_EVENTS).realize(
            player, positive=is_positive
        )

    elif current_tile == "Тренировка":
        Action(effects={"stamina": 4}).execute(player)

    elif current_tile == "Допинг контроль":
        choice = yield (
            "await_choice",
            player,
            "1. Честная (-5 монет, пропуск хода) 2. Темная (-7 репутации)",
        )
        if choice.get("doping_type") == "fair":
            if Action(cost={"money": 5}).execute(player):
                setattr(player, "skip_next_turn", True)
        else:
            player.reputation -= 7

    elif current_tile == "Громкий трансфер":
        # Изъятие ресурсов теперь возвращает готовое действие Action!
        victim_idx, act = yield (
            "await_transfer",
            player,
            "Выбери жертву и действие",
        )
        # act — это готовый Action(cost={ресурс: X}), присланный из интерфейса
        if act.execute(players[victim_idx]):
            # Даем игроку зеркальный эффект (забрали деньги -> получил деньги)
            Action(effects=act.cost).execute(player)

    elif current_tile == "Арена":
        price = max(
            0,
            DEFAULT_BUY_PRICE + getattr(player, "arena_price_modifier", 0),
        )
        buy = yield ("await_buy", player, f"Купить Арену за {price} монет?")
        if buy and buy.get("buy"):
            Action(cost={"money": price}, effects={"add_arena": player.arena}).execute(
                player
            )