# models/player.py
class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.grain = 10
        self.money = 10
        self.land = 5
        self.people = 10
        self.smuta = 0

    @property
    def prestige(self):
        return self.land * 2 + self.money // 5 + self.people // 5 - self.smuta

    @property
    def is_dead(self):
        return self.smuta >= 10 or self.people <= 0

    def can_afford(self, action):
        return all(getattr(self, res) >= cost for res, cost in action.cost.items())