def take_turn(self):
    player = self.players[self.current]
    # 1. Неуправляемое событие
    event = random.choice(EVENTS)
    positive = random.random() < 0.5
    log = self.apply_event(player, event, positive)
    yield ("event", event, log)      # UI показывает модалку

    # 2. Управляемое действие
    yield ("await_action", player, None)
    # ... после выбора действия и цели:
    # self.apply_action(player, action, target)
    # self.current = (self.current + 1) % 4