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

    @property
    def prestige(self):
        return self.arena * 3 + self.money // 8 + self.reputation // 4

    @property
    def is_bankruptcy(self):
        return self.money < 0 or self.reputation < 0

    def can_afford(self, action):
        return all(getattr(self, res) >= cost for res, cost in action.cost.items())