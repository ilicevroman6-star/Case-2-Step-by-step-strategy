from types import SimpleNamespace
from unittest.mock import Mock

import random
import pytest

from game.logic.events_pool import (
    contract,
    game_calendar,
    fan_activity,
    taxes,
    abroad_activity,
    marketing,
    EVENTS_POOL
)
from game.logic.game_state import apply_action, apply_trade
from game.models.action import Action
from game.models.event import RandomEvent
from game.models.player import Player


def test_player_created_correctly():
    player = Player("Roman", "red")
    assert player.name == 'Roman'
    assert player.color == 'red'
    assert player.money == 50
    assert player.stamina == 20
    assert player.reputation == 16
    assert player.arena == 0
    assert player.rent == 1
    assert player.owned_arenas == []

def test_prestige_created_correctly():
    player = Player("Roman", "red")
    player.money += 14
    player.stamina += 32
    player.reputation += 24
    player.arena += 4
    player.rent += 1
    assert player.prestige == 30

def test_bankruptcy():
    player = Player("Roman", "red")
    assert player.is_bankruptcy is False
    player.money =-100
    assert player.is_bankruptcy is True
    player.money = 100
    player.reputation =-100
    assert player.is_bankruptcy is True

def test_cannot_afford():
    player = Player("Roman", "red")
    action = SimpleNamespace(cost={"money":51})
    assert player.can_afford(action) is False
    action = SimpleNamespace(cost={"stamina":51})
    assert player.can_afford(action) is False
    action = SimpleNamespace(cost={"stamina":5})
    assert player.can_afford(action) is True

@pytest.fixture
def player():
    return Player("Roman", "red")

@pytest.mark.parametrize(
    "event_func, positive, expected_money, expected_stamina, expected_reputation, expected_rent",
    [
        # contract
        (contract, True, 60, 20, 16, 1),
        (contract, False, 35, 20, 16, 1),

        # game_calendar
        (game_calendar, True, 50, 24, 16, 1),
        (game_calendar, False, 50, 13, 16, 1),

        # fan_activity
        (fan_activity, True, 50, 20, 19, 1),
        (fan_activity, False, 50, 20, 14, 1),

        # taxes
        (taxes, True, 56, 20, 16, 1),
        (taxes, False, 50, 20, 16, 2),

        # abroad_activity
        (abroad_activity, True, 55, 20, 18, 1),
        (abroad_activity, False, 47, 20, 13, 1),

        # marketing
        (marketing, True, 55, 20, 20, 1),
        (marketing, False, 46, 20, 14, 1),
    ]
)

def test_random_apply(player, event_func, positive, expected_money, expected_stamina,
                      expected_reputation, expected_rent):
    event = RandomEvent(
        id=event_func.__name__,
        title="Тестовое событие",
        apply_func=event_func
    )

    result = event.apply(player, positive)

    assert isinstance(result, str)
    assert result != ""

    assert player.money == expected_money
    assert player.stamina == expected_stamina
    assert player.reputation == expected_reputation
    assert player.rent == expected_rent

def test_apply_action_deducts_resources_and_returns_log():
    player = Player(name="Rilic", color="blue")

    action_function = Mock(return_value="Тренировка успешно выполнена")

    action = Action(
        id="training",
        title="Тренировка",
        cost={
            "money": 10,
            "stamina": 5,
            "reputation": 2
        },
        target_required=False,
        apply=action_function
    )

    result = apply_action(player, action, None)

    assert player.money == 40        # 50 - 10
    assert player.stamina == 15      # 20 - 5
    assert player.reputation == 14   # 16 - 2

    action_function.assert_called_once_with(player, None)

    assert result == "Тренировка успешно выполнена"

def test_apply_action_passes_target_to_action_function():
    attacker = Player("Roman", "red")
    target = Player("Dmitry", "blue")

    action_function = Mock(return_value="Roman атаковал Dmitry")

    action = Action(
        id="attack",
        title="Атака",
        cost={
            "money": 5,
            "stamina": 4,
        },
        target_required=True,
        apply=action_function
    )

    result = apply_action(attacker, action, target)

    assert attacker.money == 45
    assert attacker.stamina == 16

    action_function.assert_called_once_with(attacker, target)

    assert result == "Roman атаковал Dmitry"

def test_apply_trade_exchanges_money_stamina_and_arenas():
    sender = Player(name="Rilic", color="blue")
    receiver = Player(name="Enemy", color="red")

    #Арены, которыми владеют игроки до обмена
    sender.owned_arenas = [1, 2]
    receiver.owned_arenas = [3, 4]

    trade_data = {
        #Отправитель отдаёт получателю
        "send_money": 10,
        "send_stamina": 5,
        "send_arenas": [1],

        #Получатель отдаёт отправителю
        "get_money": 7,
        "get_stamina": 4,
        "get_arenas": [3],
    }

    result = apply_trade(sender, receiver, trade_data)


    assert sender.money == 47
    assert sender.stamina == 19
    assert sender.owned_arenas == [2, 3]

    assert receiver.money == 53
    assert receiver.stamina == 21
    assert receiver.owned_arenas == [4, 1]

    #Проверяем лог сделки
    assert sender.name in result
    assert receiver.name in result
    assert "Сделка совершена" in result

def test_random_events_positive_and_negative_10000_iterations():
    event_stats = {
        event.id: {
            "positive": 0,
            "negative": 0
        }
        for event in EVENTS_POOL
    }

    positive_count = 0
    negative_count = 0
    for _ in range(10000):
        player = Player(name="Roman", color="blue")
        global_event = random.choice(EVENTS_POOL)
        global_positive = random.random() < 0.5

        result = global_event.apply(player, positive=global_positive)

        assert isinstance(result, str)
        assert result != ""

        if global_positive:
            positive_count += 1
            event_stats[global_event.id]["positive"] += 1
        else:
            negative_count += 1
            event_stats[global_event.id]["negative"] += 1

    assert positive_count + negative_count == 10000
    assert 0.942 < positive_count / negative_count < 1.062

