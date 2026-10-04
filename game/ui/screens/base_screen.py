class BaseScreen:
    def __init__(self, app):
        self.app = app
    def handle_event(self, event): pass
    def update(self, dt, mouse_pos): pass
    def draw(self, screen): raise NotImplementedError