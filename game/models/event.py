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
        """Реализует событие и возвращает текст с эффектами."""
        if positive and self.pos_effects:
            effects = self.pos_effects
            log_text = self.pos_text
        elif not positive and self.neg_effects:
            effects = self.neg_effects
            log_text = self.neg_text if self.neg_text else 'Негативное событие.'
        else:
            if positive and self.neg_effects:
                effects = self.neg_effects
                log_text = self.neg_text
            else:
                effects = {}
                log_text = f'{self.title}: без изменений.'

        # Особый случай: B1
        if effects.get('action_type') == 'lose_random_arena':
            if getattr(player, 'owned_arenas', []):
                lost = random.choice(player.owned_arenas)
                player.owned_arenas.remove(lost)
                return f'{log_text}\nАрена №{lost} изъята.'
            else:
                player.money = max(0, player.money - 10)
                return f'{log_text}\nШтраф 10 монет (нет арен).'

        # Начисление + сбор текста эффектов
        effect_lines = []
        for res, value in effects.items():
            if res == 'rent_multiplier':
                player.rent *= value
                effect_lines.append(f'Рента ×{value}')
            else:
                current = getattr(player, res, 0)
                setattr(player, res, current + value)
                sign = '+' if value > 0 else ''
                name = {
                    'money': 'Деньги',
                    'stamina': 'Выносливость',
                    'reputation': 'Репутация',
                    'arena_price_modifier': 'Цена арен',
                }.get(res, res)
                effect_lines.append(f'{name}: {sign}{value}')

        if effect_lines:
            return log_text + '\n\n' + '\n'.join(effect_lines)
        return log_text