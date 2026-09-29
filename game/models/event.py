from dataclasses import dataclass
from typing import Callable


@dataclass
class RandomEvent:
    id: str
    title: str
    apply_func: Callable

    def apply(self, player, positive: bool) -> str:
        """Метод, который будет вызывать движок игры."""
        return self.apply_func(player, positive)