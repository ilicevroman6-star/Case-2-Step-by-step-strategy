class Action:
    def __init__(self, cost=None, effects=None):
        """Класс действия игрока.

        :param cost: Словарь ресурсов, которые нужно списать (цена).
        :param effects: Словарь ресурсов, которые нужно начислить (награда).
        """
        self.cost = cost if cost is not None else {}
        self.effects = effects if effects is not None else {}

        if 'reputation' in self.cost or 'reputation' in self.effects:
            raise ValueError(
                '🚨 Критическая ошибка: Репутацией торговать нельзя!'
            )

    def can_execute(self, player) -> bool:
        """Проверяет, может ли конкретный игрок выполнить это действие."""
        for res, cost_val in self.cost.items():
            # Проверка владения конкретной ареной при продаже/торге
            if res == 'lose_arena':
                if cost_val not in getattr(player, 'owned_arenas', []):
                    return False
            # Проверка стандартных числовых ресурсов (money, stamina)
            else:
                if getattr(player, res, 0) < cost_val:
                    return False
        return True

    def execute(self, player) -> bool:
        """Выполняет действие: проверяет ресурсы,
        списывает стоимость и начисляет эффекты.

        Возвращает True в случае успеха и False, если у игрока не хватило
        ресурсов.
        """
        # 1. Сначала обязательно проверяем, доступно ли действие
        if not self.can_execute(player):
            return False

        # 2. Списываем стоимость (cost)
        for res, cost_val in self.cost.items():
            if res == "lose_arena":
                player.owned_arenas.remove(cost_val)
            else:
                current_val = getattr(player, res)
                setattr(player, res, current_val - cost_val)

        # 3. Начисляем эффекты (effects)
        for res, effect_val in self.effects.items():
            if res == "add_arena":
                player.owned_arenas.append(effect_val)
            elif res == "rent_multiplier":
                player.rent *= effect_val
            else:
                current_val = getattr(player, res)
                setattr(player, res, current_val + effect_val)

        return True