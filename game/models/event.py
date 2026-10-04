import random


class RandomEvent:
    def __init__(
        self,
        event_id,
        title,
        pos_effects=None,
        pos_text=None,
        neg_effects=None,
        neg_text=None,
    ):
        self.event_id = event_id
        self.title = title
        self.pos_effects = pos_effects if pos_effects is not None else {}
        self.pos_text = pos_text
        self.neg_effects = neg_effects if neg_effects is not None else {}
        self.neg_text = neg_text

    def realize(self, player, positive: bool) -> str:
        """
        Универсальный метод реализации события.
        Принимает объект игрока и флаг исхода (True/False).
        Изменяет ресурсы игрока и возвращает строку лога.
        """
        # Проверка на случай, если рандом решил дать игроку
        # позитивное/негативное событие, однако в словаре такой ключ вообще
        # отсутствует и поэтому принудительно применяется
        # противоположный эффект.
        if positive and self.pos_effects:
            effects = self.pos_effects
            log_text = self.pos_text
        else:
            effects = self.neg_effects
            log_text = self.neg_text if self.neg_text else 'Ничего не произошло.'

        # 1. Особый случай для события B1 (лишение арены).
        if effects.get('action_type') == 'lose_random_arena':
            if getattr(player, 'owned_arenas', []):
                lost_arena = random.choice(player.owned_arenas)
                player.owned_arenas.remove(lost_arena)
                return f'{log_text}\n📉 Банк изъял у вас Арену №{lost_arena}.'
            else:
                player.money = max(0, player.money - 10)
                return (
                    '🏦 Вы задолжали банку. Так как у вас нет арен, '
                    'банк списал штраф 10 монет.'
                )

        # 2. Начисление стандартных бонусов и штрафов.
        for resource, value in effects.items():
            if resource == 'rent_multiplier':
                player.rent *= value
            else:
                current_val = getattr(player, resource)
                setattr(player, resource, current_val + value)

        return log_text