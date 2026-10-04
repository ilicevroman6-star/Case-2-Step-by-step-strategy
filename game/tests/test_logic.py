from collections import Counter
import random
import pytest

from game.logic.events_pool import GLOBAL_EVENTS

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
    player.money = 64
    player.stamina = 52
    player.reputation = 40
    player.arena = 4
    player.rent = 1
    player.owned_arenas = ["snow", "wind", "lol", "kek"]
    assert player.prestige == 30

def test_bankruptcy():
    player = Player("Roman", "red")
    assert player.is_bankruptcy is False
    player.money =-100
    assert player.is_bankruptcy is True
    player.money = 100
    player.reputation =-100
    assert player.is_bankruptcy is True


def get_event(event_id: str) -> RandomEvent:
    return next(event for event in GLOBAL_EVENTS if event.event_id == event_id)

@pytest.fixture
def player():
    return Player("Roman", "red")

@pytest.mark.parametrize(
    "event_id, expected_stats",
    [
        ("E1", {"money": 60}),
        ("E2", {"stamina": 24}),
        ("E3", {"reputation": 19}),
        ("E4", {"money": 56}),
        ("E5", {"money": 55, "reputation": 18}),
        ("E6", {"money": 38}),
        ("E7", {"arena_price_modifier": -4}),
        ("E8", {"money": 55, "reputation": 20}),
    ],
)
def test_positive_event_changes_player_stats(player, event_id, expected_stats):
    event = get_event(event_id)

    log_text = event.realize(player, positive=True)

    #Проверка изменения нужных характеристик
    for stat_name, expected_value in expected_stats.items():
        assert getattr(player, stat_name) == expected_value

    #Проверка, что вернулся текст положительного события
    assert log_text == event.pos_text

@pytest.mark.parametrize(
    "event_id, expected_stats",
    [
        ("E1", {"money": 35}),
        ("E2", {"stamina": 13}),
        ("E3", {"reputation": 14}),
        ("E4", {"rent": 2}),
        ("E5", {"money": 47, "reputation": 13}),
        ("E6", {"reputation": 13}),
        ("E7", {"arena_price_modifier": 4}),
        ("E8", {"money": 46, "reputation": 14}),
    ],
)
def test_negative_event_changes_player_stats(player, event_id, expected_stats):
    event = get_event(event_id)

    log_text = event.realize(player, positive=False)

    #Проверка изменения характеристик
    for stat_name, expected_value in expected_stats.items():
        assert getattr(player, stat_name) == expected_value

    #Проверка текста отрицательного события
    assert log_text == event.neg_text

@pytest.fixture
def player():
    return Player("Test", "blue")

def player_state(player):
    """Снимок характеристик для проверки отсутствия побочных изменений."""
    return (
        player.money,
        player.stamina,
        player.reputation,
        player.arena,
        player.rent,
        player.arena_price_modifier,
        player.owned_arenas.copy(),
    )


def test_default_dictionaries_are_not_shared():
    first = Action()
    second = Action()

    first.cost["money"] = 10
    first.effects["stamina"] = 2

    assert second.cost == {}
    assert second.effects == {}


@pytest.mark.parametrize(
    ("cost", "effects"),
    [
        ({"reputation": 1}, {}),
        ({}, {"reputation": -1}),
    ],
)

#Проверяет, что нельзя указать reputation ни в стоимости, ни в награде действия.
def test_reputation_cannot_be_used(cost, effects):
    with pytest.raises(ValueError, match="Репутацией торговать нельзя"):
        Action(cost=cost, effects=effects)


@pytest.mark.parametrize(
    ("cost", "expected"),
    [
        ({}, True),
        ({"money": 50, "stamina": 20}, True),
        ({"money": 51}, False),
        ({"stamina": 21}, False),
        ({"money": 10, "stamina": 21}, False),
        ({"unknown_resource": 1}, False),
    ],
)

#Проверяет can_execute() при разных затратах: хватает ли денег и выносливости,
#что происходит при нехватке одного ресурса и при неизвестном ресурсе.
def test_can_execute_checks_resources(player, cost, expected):
    assert Action(cost=cost).can_execute(player) is expected


@pytest.mark.parametrize(
    ("owned_arenas", "expected"),
    [
        ([], False),
        (["A1"], True),
        (["A2"], False),
    ],
)

#Проверяет стоимость вида {"lose_arena": "A1"}. Действие доступно, только если A1 есть в player.owned_arenas
def test_can_execute_checks_arena(player, owned_arenas, expected):
    player.owned_arenas = owned_arenas

    assert Action(cost={"lose_arena": "A1"}).can_execute(player) is expected

#Проверяет успешное выполнение целиком: списание денег и выносливости, удаление A1,
#начисление эффектов, добавление A2 и умножение аренды.
def test_execute_applies_cost_and_effects(player):
    player.owned_arenas = ["A1"]
    player.rent = 4

    action = Action(
        cost={"money": 10, "stamina": 3, "lose_arena": "A1"},
        effects={
            "money": 5,
            "stamina": 2,
            "add_arena": "A2",
            "rent_multiplier": 3,
            "arena_price_modifier": -4,
        },
    )

    assert action.execute(player) is True
    assert player_state(player) == (
        45,      #50 - 10 + 5
        19,      #20 - 3 + 2
        16,      #репутация не изменилась
        0,       #arena не изменилась
        12,      #rent: 4 * 3
        -4,
        ["A2"],  #A1 удалена, A2 добавлена
    )


@pytest.mark.parametrize(
    "cost",
    [
        {"money": 51},
        {"stamina": 21},
        {"money": 10, "stamina": 21},
        {"money": 10, "lose_arena": "A2"},
    ],
)

#Запоминает состояние игрока, пытается выполнить недоступное действие и проверяет две вещи:
#execute() вернул False, а состояние игрока осталось прежним
def test_execute_does_not_change_player_if_cost_unavailable(player, cost):
    player.owned_arenas = ["A1"]
    player.rent = 4
    before = player_state(player)

    action = Action(
        cost=cost,
        effects={
            "money": 100,
            "add_arena": "A3",
            "rent_multiplier": 2,
        },
    )

    assert action.execute(player) is False
    assert player_state(player) == before

def test_positive_and_negative_outcomes_on_10000_iterations():
    results = Counter()

    for _ in range(10000):
        positive = random.choice([True, False])
        results[positive] += 1

    positive_count = results[True]
    negative_count = results[False]

    assert 4850 <= positive_count <= 5150, (
        f"Позитивный исход выпал {positive_count} раз вместо ~5000"
    )

    assert 4850 <= negative_count <= 5150, (
        f"Негативный исход выпал {negative_count} раз вместо ~5000"
    )

    print(negative_count, positive_count)

def test_random_event_selection_on_10000_iterations():
    event_ids = [event.event_id for event in GLOBAL_EVENTS]
    counts = Counter()

    for _ in range(10000):
        event = random.choice(GLOBAL_EVENTS)
        counts[event.event_id] += 1

    for event_id in event_ids:
        assert counts[event_id] > 0, (
            f"Событие {event_id} ни разу не выпало за 10000 итераций"
        )

    expected_count = 10000 / len(GLOBAL_EVENTS)

    min_count = expected_count * 0.9
    max_count = expected_count * 1.1

    for event_id in event_ids:
        assert min_count <= counts[event_id] <= max_count, (
            f"Событие {event_id} выпало {counts[event_id]} раз. "
            f"Ожидалось примерно {expected_count:.0f} раз "
            f"(допустимо от {min_count:.0f} до {max_count:.0f})."
        )