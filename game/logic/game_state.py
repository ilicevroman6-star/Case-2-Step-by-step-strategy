import random
from game.config import BOARD, ARENA_PRICES, DEFAULT_BUY_PRICE
from game.logic.events_pool import (
    GLOBAL_EVENTS,
    RANDOM_TILE_EVENTS, RANDOM_POSITIVE, RANDOM_NEGATIVE,
    MEDIA_TILE_EVENTS, MEDIA_POSITIVE, MEDIA_NEGATIVE,
)
from game.models.action import Action


def take_turn(players, current_index: int, round_state: dict):
    """Генератор хода. Отвечает только за перемещение и логику шагов."""

    player = players[current_index]
    if player.is_bankruptcy:
        return


    # 1. ПЕРЕМЕЩЕНИЕ И КРУГ.
    dice = random.randint(1, 6)
    player.last_dice = dice  # сохраняем бросок в игрока
    print(f"[ХОД] {player.name} выбросил кубик: {dice}")
    # Считаем чистую новую позицию БЕЗ деления по кругу.
    new_position = player.arena + dice

    # Проверяем, пересек ли игрок конец доски.
    passed_start = new_position >= len(BOARD)

    # И только теперь сохраняем игроку его позицию с учетом круга.
    old_pos = player.arena
    player.arena = new_position % len(BOARD)
    print(f"[ХОД] {player.name}: позиция {old_pos} → {player.arena}")

    if (passed_start
            and current_index == 0
            and not round_state.get("global_fired", False)):
        round_state["global_fired"] = True
        global_event = random.choice(GLOBAL_EVENTS)
        yield (
            "global_event",
            global_event,
            global_event.realize(player, positive=random.random() < 0.5),
        )

    if passed_start:
        # Начисляем бонусы за круг напрямую (репутация — не через Action)
        player.money += 20
        player.stamina += 5
        player.reputation += 3

    current_tile = BOARD[player.arena]

    # 2. АВТОМАТИЧЕСКАЯ РЕНТА
    if current_tile == "Арена":
        for owner in players:
            if owner != player and player.arena in owner.owned_arenas:
                final_rent = (
                        ARENA_PRICES[player.arena]["rent_price"] * player.rent
                )
                print(f"[РЕНТА] {player.name} платит {final_rent} монет игроку {owner.name}")
                Action(cost={"money": final_rent}).execute(player)
                Action(effects={"money": final_rent}).execute(owner)
                break

    # 3. ЛОКАЛЬНЫЕ СОБЫТИЯ И ИНТЕРАКТИВНЫЕ КЛЕТКИ
    if current_tile == "Random":
        pool = RANDOM_POSITIVE if random.random() < 0.5 else RANDOM_NEGATIVE
        is_positive = pool is RANDOM_POSITIVE
        yield "log", None, random.choice(pool).realize(player, positive=is_positive)

    elif current_tile == "Медиа":
        pool = MEDIA_POSITIVE if random.random() < 0.5 else MEDIA_NEGATIVE
        is_positive = pool is MEDIA_POSITIVE
        yield "log", None, random.choice(pool).realize(player, positive=is_positive)

    elif current_tile == "Тренировка":
        Action(effects={"stamina": 4}).execute(player)

    elif current_tile == "Допинг контроль":
        choice = yield (
            "await_choice",
            player,
            "1. Честная (-5 монет, пропуск хода) 2. Темная (-7 репутации)",
        )
        if choice.get("doping_type") == "fair":
            # Пытаемся списать деньги за честную проверку.
            if Action(cost={"money": 5}).execute(player):
                setattr(player, "skip_next_turn", True)
            else:
                # Если денег нет, принудительно отправляем на темную проверку
                player.reputation -= 7
        else:
            player.reputation -= 7

    elif current_tile == "Громкий трансфер":
        # Изъятие ресурсов теперь возвращает готовое действие Action!
        victim_idx, chosen_res = yield (
            "await_transfer",
            player,
            "Выбери жертву и действие",
        )
        victim = players[victim_idx]

        # СЦЕНАРИЙ 1: Кража репутации (В обход класса Action, напрямую)
        if chosen_res == "reputation":
            # Вычисляем, сколько реально можно забрать
            # (максимум 4, но не больше, чем есть у жертвы)
            amount = min(4, max(0, victim.reputation))
            victim.reputation -= amount
            player.reputation += amount

        # СЦЕНАРИЙ 2: Кража обычных ресурсов (Используем безопасный Action)
        elif chosen_res in ["money", "stamina"]:
            steal_amount = 10 if chosen_res == "money" else 6
            stolen_action = Action(cost={chosen_res: steal_amount})

            if stolen_action.execute(victim):
                Action(effects={chosen_res: steal_amount}).execute(player)



    elif current_tile == "Арена":

        # Проверяем, чья это арена

        owner = None

        for p in players:

            if player.arena in getattr(p, "owned_arenas", []):
                owner = p

                break

        if owner is not None and owner != player:

            # Чужая арена — рента уже списана выше

            pass

        elif owner == player:

            # Своя арена — ничего

            yield ("log", None,

                   f"{player.name}: своя арена, ничего не происходит.")

        else:

            # Свободная арена — предлагаем купить

            price = max(0, DEFAULT_BUY_PRICE +

                        getattr(player, "arena_price_modifier", 0))

            buy = yield "await_buy", player, f"Купить Арену за {price} монет?"

            if buy and buy.get("buy"):

                buy_action = Action(

                    cost={"money": price},

                    effects={"add_arena": player.arena},

                )

                if not buy_action.execute(player):
                    yield ("log", None,

                           f"{player.name} не смог купить Арену: "

                           "не хватает монет!")