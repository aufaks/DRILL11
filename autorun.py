from time import monotonic


class AutoRunState:
    DURATION = 5
    SPEED = 12
    MIN_X = 80
    MAX_X = 720
    DRAW_SIZE = 160
    DRAW_Y = 110

    def __init__(self):
        self.started_at = None

    def enter(self):
        self.started_at = monotonic()
