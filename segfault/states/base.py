"""Base class for game states + a tiny stack-based state machine.

The Game owns a stack of states. Only the top state updates/draws (except
states that opt into drawing the one below, e.g. pause/lesson overlays).
"""


class State:
    # overlay states draw the state beneath them first (transparent UI)
    transparent = False

    def __init__(self, game):
        self.game = game

    # lifecycle ------------------------------------------------------------
    def enter(self):
        """Push self onto the stack."""
        self.game.push_state(self)
        return self

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def on_resume(self):
        """Called when a state above us is popped and we're top again."""
        pass

    # per-frame ------------------------------------------------------------
    def handle_events(self, events):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface):
        pass

    # helpers --------------------------------------------------------------
    def pop(self):
        self.game.pop_state()

    @property
    def sound(self):
        return self.game.sound

    @property
    def bank(self):
        return self.game.bank

    @property
    def save(self):
        return self.game.save_data
