# models/action.py
@dataclass
class Action:
    id: str
    title: str
    cost: dict           # {"money": 3}
    target_required: bool
    apply: callable      # функция(actor, target) -> str (лог)