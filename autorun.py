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

    def move(self, x, face_dir):
        x += face_dir * self.SPEED
        if x <= self.MIN_X:
            return self.MIN_X, 1
        if x >= self.MAX_X:
            return self.MAX_X, -1
        return x, face_dir

    def is_finished(self):
        if self.started_at is None:
            raise RuntimeError('AutoRunState must be entered before checking its duration')
        return monotonic() - self.started_at >= self.DURATION

    def draw(self, image, frame, face_dir, x):
        row = 100 if face_dir == 1 else 0
        image.clip_draw(
            frame * 100,
            row,
            100,
            100,
            x,
            self.DRAW_Y,
            self.DRAW_SIZE,
            self.DRAW_SIZE,
        )
