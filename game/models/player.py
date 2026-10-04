class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.money = 50
        self.stamina = 20
        self.reputation = 16
        self.arena = 0
        self.owned_arenas = []
        self.rent = 1
        self.arena_price_modifier = 0

    @property
    def prestige(self) -> int:
        """Считает очки престижа игрока для финального рейтинга."""
        return (
            len(self.owned_arenas) * 3
            + self.money // 8
            + self.reputation // 4
        )

    @property
    def is_bankruptcy(self) -> bool:
        """Проверяет, обанкротился ли игрок."""
        return self.money < 0 or self.reputation < 0

    def check_stamina_depletion(self) -> bool:
        """UX-правило №4: Экстренные сборы при выносливости <= 0."""
        if self.stamina <= 0:
            self.stamina = 10
            setattr(self, "skip_next_turn", True)
            return True
        return False

    def can_afford(self, action) -> bool:
        """Прослойка для совместимости с внешним кодом (вызывает проверку Action)."""
        return action.can_execute(self)