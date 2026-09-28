from dataclasses import dataclass


@dataclass
class RandomEvent:
    id: str
    title: str
    effects: dict      # {"grain": -3, "land": -1}
    is_positive: bool  # если True — эффекты инвертируются при негативном исходе