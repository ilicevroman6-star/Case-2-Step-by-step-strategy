import random
from game.config import BOARD, ARENA_PRICES, DEFAULT_BUY_PRICE
from game.logic.events_pool import EVENTS_POOL, RANDOM_TILE_EVENTS, MEDIA_TILE_EVENTS


def apply_event(player, event, positive):
    """Обычная функция для применения события."""
    return event.apply(player, positive)

def apply_action(player, action, target):
    """Обычная функция для применения действия игрока."""
    for res, cost in action.cost.items():
        current_value = getattr(player, res)
        setattr(player, res, current_value - cost)

    return action.apply(player, target)


def apply_trade(sender, receiver, trade_data):
    """
    Чистая функция для обработки обмена ресурсами.
    trade_data = {
    "send_money": 10, "send_stamina": 5, "send_arenas":,
    "get_money": 0, "get_stamina": 0, "get_arenas": [6]
    }
    """
    # 1. Передача ресурсов от инициатора (sender) к получателю (receiver)
    sender.money -= trade_data.get("send_money", 0)
    receiver.money += trade_data.get("send_money", 0)

    sender.stamina -= trade_data.get("send_stamina", 0)
    receiver.stamina += trade_data.get("send_stamina", 0)

    for arena_id in trade_data.get("send_arenas", []):
        if arena_id in sender.owned_arenas:
            sender.owned_arenas.remove(arena_id)
            receiver.owned_arenas.append(arena_id)

    # 2. Передача ресурсов от получателя (receiver) к инициатору (sender)
    receiver.money -= trade_data.get("get_money", 0)
    sender.money += trade_data.get("get_money", 0)

    receiver.stamina -= trade_data.get("get_stamina", 0)
    sender.stamina += trade_data.get("get_stamina", 0)

    for arena_id in trade_data.get("get_arenas", []):
        if arena_id in receiver.owned_arenas:
            receiver.owned_arenas.remove(arena_id)
            sender.owned_arenas.append(arena_id)

    return f"🤝 Сделка совершена! {sender.name} и {receiver.name} успешно обменялись ресурсами."

def take_turn(players, current_index):
    """
    Чистая функция-генератор хода.
    Вместо self принимает список игроков и индекс текущего ходящего.
    """
    player = players[current_index]

    if player.is_bankruptcy:
        return  # Если игрок выбыл, функция просто завершает работу

    # ЭТАП 1: БРОСОК КУБИКА И ПЕРЕМЕЩЕНИЕ С ПРОВЕРКОЙ КРУГА.
    dice = random.randint(1, 6)
    old_position = player.arena
    new_position = old_position + dice

    passed_start = new_position >= len(BOARD)
    if passed_start:
        # Награда за круг.
        player.money += 20
        player.stamina += 5
        player.reputation += 3

    player.arena = new_position % len(BOARD)
    current_tile = BOARD[player.arena]

    movement_log = f"🎲 {player.name} выбросил {dice} и перешел на клетку '{current_tile}' (№{player.arena})."
    if passed_start:
        movement_log += f"\n🔄 {player.name} завершил круг!"

    # ЭТАП 2: ГЛОБАЛЬНОЕ СОБЫТИЕ ЛИГИ (Только при прохождении круга)
    if passed_start:
        global_event = random.choice(EVENTS_POOL)
        global_positive = random.random() < 0.5
        global_log = apply_event(player, global_event, global_positive)

        yield ("global_event", global_event, f"📢 Событие Лиги:\n{global_log}")

    # ЭТАП 3: АВТОМАТИЧЕСКИЙ РАСЧЕТ РЕНТЫ
    rent_log = ""
    if current_tile == "Арена":
        owner = None
        for other_player in players:
            if other_player != player and player.arena in other_player.owned_arenas:
                owner = other_player
                break

        if owner:
            base_rent = ARENA_PRICES[player.arena]["rent_price"]
            final_rent = base_rent * player.rent
            player.money -= final_rent
            owner.money += final_rent
            rent_log = f"\n💰 Уплачена рента {final_rent} монет игроку {owner.name}."

    # ЭТАП 4: ЛОКАЛЬНЫЕ СОБЫТИЯ КЛЕТОК ("Random" и "Медиа")
    tile_event_log = ""
    tile_event_obj = None

    # 1. Клетки Шанса (Random)
    if current_tile == "Random":
        tile_event_obj = random.choice(RANDOM_TILE_EVENTS)
        tile_event_log = tile_event_obj.apply(player, positive=True)

        # 2. Клетки Пиара (Медиа)
    elif current_tile == "Медиа":
        tile_event_obj = random.choice(MEDIA_TILE_EVENTS)
        tile_event_log = tile_event_obj.apply(player, positive=True)

    # 3. Зеленые клетки (Тренировка)
    elif current_tile == "Тренировка":
        player.stamina += 4
        tile_event_log = "🏋️ Команда прибыла на сборы. Выносливость +4."

    # 4. Угловая зона: Time Out
    elif current_tile == "Time out":
        tile_event_log = "🧘 Время передышки. Вы просто отдыхаете текущий ход."


    # 5. Угловая зона: Допинг-контроль (Интерактивный выбор)
    elif current_tile == "Допинг контроль":
        choice_data = yield ("await_doping_choice", player, "Выберите проверку: Честная (5 монет, пропуск хода) или Темная (-7 репутации)")
        if choice_data.get("doping_type") == "fair":
            player.money -= 5
            setattr(player, "skip_next_turn", True)
            tile_event_log = "📋 Выбрана Честная проверка: -5 монет, следующий ход будет пропущен."
        else:
            player.reputation -= 7
            tile_event_log = "🕵️ Выбрана Темная проверка: потеряно 7 репутации, но штрафов по ходам нет."

    # 6. Угловая зона: Громкий трансфер (Интерактивный грабеж)
    elif current_tile == "Громкий трансфер":
        transfer_data = yield ("await_transfer_choice", player, "Выберите соперника и ресурс для изъятия")
        target_idx = transfer_data.get("target_index")
        victim = players[target_idx]
        chosen_res = transfer_data.get("resource")

    if chosen_res == "arena" and getattr(victim, "owned_arenas", []):
        stolen_arena = random.choice(victim.owned_arenas)
        victim.owned_arenas.remove(stolen_arena)
        player.owned_arenas.append(stolen_arena)
        tile_event_log = f"🔄 Принудительно забрана Арена №{stolen_arena} у игрока {victim.name}."
    elif chosen_res == "reputation":
        amount = min(4, victim.reputation)
        victim.reputation -= amount
        player.reputation += amount
        tile_event_log = f"🔄 Похищено {amount} репутации у игрока {victim.name}."
    elif chosen_res == "stamina":
        amount = min(6, victim.stamina)
        victim.stamina -= amount
        player.stamina += amount
        tile_event_log = f"🔄 Похищено {6} выносливости у игрока {victim.name}."
    elif chosen_res == "money":
        amount = min(10, victim.money)
        victim.money -= amount
        player.money += amount
        tile_event_log = f"🔄 Похищено {amount} монет у игрока {victim.name}."

    # 7. Свободная оранжевая клетка Арены (Предложение покупки)
    elif current_tile == "Арена" and not rent_log:
        action_data = yield ("await_buy_arena", player,
                         f"Хотите купить Арену №{player.arena} за {DEFAULT_BUY_PRICE} монет?")
        if action_data and action_data.get("buy") is True and player.money >= DEFAULT_BUY_PRICE:
            player.money -= DEFAULT_BUY_PRICE
            player.owned_arenas.append(player.arena)
            tile_event_log = f"🏛️ Вы успешно выкупили Арену №{player.arena}!"
        else:
            tile_event_log = "❌ Вы отказались от покупки этой арены."

    # Вывод результатов в UI модалку
    if tile_event_log or rent_log:
        full_tile_log = f"{movement_log}{rent_log}\n{tile_event_log}"
        yield ("tile_event", tile_event_obj, full_tile_log)
    else:
        yield ("tile_info", None, f"{movement_log}\nНикаких дополнительных эффектов.")

    # ЭТАП 5: УПРАВЛЯЕМОЕ ДЕЙСТВИЕ ИГРОКА
    while True:
        # Запрашиваем действие у UI
        action_data = yield ("await_action", player, None)

        if not action_data:
            break  # Игрок просто завершил ход (нажал "Пас")

        action_type = action_data.get("type")  # "trade" или "standard"

        # СЦЕНАРИЙ А: Игрок инициировал фазу переговоров и обмен
        if action_type == "trade":
            target_index = action_data.get("target_index")
            partner = players[target_index]

            trade_details = action_data.get("trade_details")
            trade_log = apply_trade(player, partner, trade_details)

            # Отправляем лог успешного обмена в UI и ОСТАЕМСЯ в цикле ходов
            yield ("trade_resolved", trade_log)
            continue

        # СЦЕНАРИЙ Б: Обычное действие (Покупка арены, использование карты и т.д.)
        elif action_type == "standard":
            action = action_data.get("action")
            target_index = action_data.get("target_index")
            target = players[target_index] if target_index is not None else None

            action_log = apply_action(player, action, target)
            yield ("action_resolved", action_log)
            break  # Обычное действие завершает ход игрока