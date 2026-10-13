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
    player.last_dice = dice
    print(f"[ХОД] {player.name} выбросил кубик: {dice}")
    new_position = player.arena + dice
    passed_start = new_position >= len(BOARD)
    old_pos = player.arena
    player.arena = new_position % len(BOARD)
    print(f"[ХОД] {player.name}: позиция {old_pos} → {player.arena}")

    if (passed_start
            and current_index == 0
            and not round_state.get("global_fired", False)):
        round_state["global_fired"] = True
        global_event = random.choice(GLOBAL_EVENTS)
        text = global_event.realize(player, positive=random.random() < 0.5)
        yield (
            "global_event",
            global_event,
            f"Закон круга: {text}",
        )

    if passed_start:
        player.money += 20
        player.stamina += 5
        player.reputation += 3

    current_tile = BOARD[player.arena]

    # 2. АРЕНА — РЕНТА, ПЕРЕКУП, ПОКУПКА
    if current_tile == "Арена":
        owner = None
        for p in players:
            if p != player and player.arena in p.owned_arenas:
                owner = p
                break

        if owner is not None:
            # Чужая — перекуп или рента
            base_price = DEFAULT_BUY_PRICE + getattr(player, "arena_price_modifier", 0)
            buyout_price = base_price * 2
            rent_price = ARENA_PRICES[player.arena]["rent_price"] * player.rent
            choice = yield (
                "await_buyout",
                {
                    "owner": owner,
                    "rent": rent_price,
                    "buyout": buyout_price,
                    "arena_idx": player.arena,
                },
                f"Арена {owner.name}. Рента {rent_price} или перекуп {buyout_price}?",
            )
            if choice and choice.get("buyout"):
                if Action(cost={"money": buyout_price}).execute(player):
                    owner.owned_arenas.remove(player.arena)
                    player.owned_arenas.append(player.arena)
                    yield ("log", None,
                           f"{player.name} перекупил арену у {owner.name}!")
                else:
                    yield ("log", None,
                           f"{player.name} не хватает. Платит ренту.")
                    Action(cost={"money": rent_price}).execute(player)
                    Action(effects={"money": rent_price}).execute(owner)
            else:
                Action(cost={"money": rent_price}).execute(player)
                Action(effects={"money": rent_price}).execute(owner)
                yield ("log", None,
                       f"{player.name} заплатил ренту {rent_price} игроку {owner.name}.")

        elif player.arena in player.owned_arenas:
            # Своя — ничего
            yield ("log", None,
                   f"{player.name}: своя арена, ничего не происходит.")

        else:
            # Свободная — покупка
            price = max(0, DEFAULT_BUY_PRICE +
                        getattr(player, "arena_price_modifier", 0))
            buy = yield "await_buy", player, f"Купить Арену за {price} монет?"
            if buy and buy.get("buy"):
                buy_action = Action(
                    cost={"money": price},
                    effects={"add_arena": player.arena},
                )
                if buy_action.execute(player):
                    yield ("log", None,
                           f"{player.name} купил Арену за {price} монет.")
                else:
                    yield ("log", None,
                           f"{player.name} не смог купить Арену.")
            else:
                yield ("log", None,
                       f"{player.name} отказался от покупки Арены.")

    # 3. RANDOM
    elif current_tile == "Random":
        pool = RANDOM_POSITIVE if random.random() < 0.5 else RANDOM_NEGATIVE
        is_positive = pool is RANDOM_POSITIVE
        event = random.choice(pool)
        text = event.realize(player, positive=is_positive)
        yield "log", None, f"{player.name}: {text}"

    # 4. МЕДИА
    elif current_tile == "Медиа":
        pool = MEDIA_POSITIVE if random.random() < 0.5 else MEDIA_NEGATIVE
        is_positive = pool is MEDIA_POSITIVE
        event = random.choice(pool)
        text = event.realize(player, positive=is_positive)
        yield "log", None, f"{player.name}: {text}"


    # 5. МАТЧ — побеждает сильный
    elif current_tile == "Матч":
        opponents = [p for p in players
                     if p != player and not p.is_bankruptcy]
        if not opponents:
            yield ("log", None, "Нет соперников для матча.")
        else:
            opponent = random.choice(opponents)
            total = player.stamina + opponent.stamina
            chance_p = player.stamina / total if total > 0 else 0.5
            choice = yield (
                "await_match",
                {
                    "player": player,
                    "opponent": opponent,
                    "chance_p": chance_p,
                },
                f"Хоккейная дуэль: {player.name} vs {opponent.name}",
            )
            if choice and choice.get("play"):
                # Побеждает сильный; при равенстве — рандом
                player_wins = (
                    player.stamina > opponent.stamina
                    or (player.stamina == opponent.stamina
                        and random.random() < 0.5)
                )
                if player_wins:
                    player.reputation += 3
                    player.money += 5
                    player.stamina -= 5
                    opponent.stamina -= 7
                    opponent.reputation -= 3
                    yield ("log", None,
                           f"ПОБЕДА: {player.name} обыграл {opponent.name}! "
                           f"{player.name}: +3 реп, +5 денег, -5 выносл. "
                           f"{opponent.name}: -7 выносл, -3 реп.")
                else:
                    opponent.reputation += 3
                    opponent.money += 5
                    opponent.stamina -= 5
                    player.stamina -= 7
                    player.reputation -= 3
                    yield ("log", None,
                           f"ПОРАЖЕНИЕ: {opponent.name} обыграл {player.name}. "
                           f"{opponent.name}: +3 реп, +5 денег, -5 выносл. "
                           f"{player.name}: -7 выносл, -3 реп.")
                for p in (player, opponent):
                    if p.stamina <= 0:
                        p.stamina = 0
                        setattr(p, "skip_next_turn", True)

    # 6. ТРЕНИРОВКА
    elif current_tile == "Тренировка":
        Action(effects={"stamina": 4}).execute(player)
        yield (
            "await_training",
            None,
            f"{player.name} на тренировке! +4 выносливости.",
        )

    # 6.5. TIME OUT
    elif current_tile == "Time out":
        yield (
            "await_timeout",
            None,
            f"{player.name} отдыхает. Ход пропущен без потерь.",
        )

    # 7. ДОПИНГ-КОНТРОЛЬ
    elif current_tile == "Допинг":
        choice = yield (
            "await_choice",
            player,
            "1. Честная (-5 монет, пропуск хода) 2. Темная (-7 репутации)",
        )
        if choice.get("doping_type") == "fair":
            if Action(cost={"money": 5}).execute(player):
                setattr(player, "skip_next_turn", True)
                yield ("log", None,
                       f"{player.name}: честная проверка. -5 монет, пропуск хода.")
            else:
                player.reputation -= 7
                yield ("log", None,
                       f"{player.name}: не хватило на честную. -7 репутации.")
        else:
            player.reputation -= 7
            yield ("log", None,
                   f"{player.name}: тёмная проверка. -7 репутации.")

    # 8. ГРОМКИЙ ТРАНСФЕР
    elif current_tile == "Трансфер":
        victim_idx, chosen_res = yield (
            "await_transfer",
            player,
            "Выбери жертву и действие",
        )
        victim = players[victim_idx]

        if chosen_res == "reputation":
            amount = min(4, max(0, victim.reputation))
            victim.reputation -= amount
            player.reputation += amount
            yield ("log", None,
                   f"{player.name} отнял {amount} репутации у {victim.name}.")
        elif chosen_res in ["money", "stamina"]:
            steal_amount = 10 if chosen_res == "money" else 6
            stolen_action = Action(cost={chosen_res: steal_amount})
            if stolen_action.execute(victim):
                Action(effects={chosen_res: steal_amount}).execute(player)
                name = "монет" if chosen_res == "money" else "выносливости"
                yield ("log", None,
                       f"{player.name} отнял {steal_amount} {name} у {victim.name}.")
            else:
                yield ("log", None,
                       f"{player.name} не смог отнять у {victim.name}.")