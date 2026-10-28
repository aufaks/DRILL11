from ctypes import byref
from pathlib import Path
from time import monotonic

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_SPACE,
    load_image,
)
import pico2d.pico2d as pico2d_impl
from transitions import Machine

from autorun import AutoRunState


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.directions = []
        self.auto_run = AutoRunState()
        image_path = Path(__file__).resolve().parent / 'animation_sheet.png'
        self.image = load_image(str(image_path))
        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'SLEEP', 'AUTORUN'],
            transitions=[
                {'trigger': 'sleep', 'source': 'IDLE', 'dest': 'SLEEP'},
                {'trigger': 'wake_up', 'source': 'SLEEP', 'dest': 'IDLE'},
                {
                    'trigger': 'start_running',
                    'source': ['IDLE', 'SLEEP', 'AUTORUN'],
                    'dest': 'RUN',
                },
                {'trigger': 'stop_running', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'start_auto_run', 'source': 'IDLE', 'dest': 'AUTORUN'},
                {'trigger': 'stop_auto_run', 'source': 'AUTORUN', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )
        self.idle_started_at = monotonic()

    def update(self):
        if self.state == 'IDLE':
            if monotonic() - self.idle_started_at >= 5:
                self.sleep()
                self.frame = 0
            else:
                self.frame = (self.frame + 1) % 8
        elif self.state == 'RUN':
            self.x = max(50, min(750, self.x + self.face_dir * 5))
            self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE and self.state == 'SLEEP':
            self.wake_up()
            self.idle_started_at = monotonic()
        elif event.type in (SDL_KEYDOWN, SDL_KEYUP) and event.key in (SDLK_LEFT, SDLK_RIGHT):
            if self.state not in ('IDLE', 'RUN', 'SLEEP'):
                return

            direction = -1 if event.key == SDLK_LEFT else 1
            if event.type == SDL_KEYDOWN:
                if direction not in self.directions:
                    self.directions.append(direction)
                self.face_dir = direction
                if self.state in ('IDLE', 'SLEEP'):
                    self.start_running()
                    self.frame = 0
            elif direction in self.directions:
                self.directions.remove(direction)
                if self.directions:
                    self.face_dir = self.directions[-1]
                elif self.state == 'RUN':
                    self.stop_running()
                    self.frame = 0
                    self.idle_started_at = monotonic()

    def draw(self):
        if self.state == 'SLEEP':
            src_rect = pico2d_impl.SDL_Rect(
                self.frame * 100,
                self.image.h - 300 - 100 if self.face_dir == 1 else self.image.h - 200 - 100,
                100,
                100,
            )
            dest_rect = pico2d_impl.to_sdl_rect(self.x - 50, 0, 100, 100)
            pico2d_impl.SDL_RenderCopyEx(
                pico2d_impl.renderer,
                self.image.texture,
                byref(src_rect),
                byref(dest_rect),
                -90 if self.face_dir == 1 else 90,
                None,
                pico2d_impl.SDL_FLIP_NONE,
            )
            return

        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
        elif self.face_dir == 1:
            row = 300
        else:
            row = 200

        if self.state in ('IDLE', 'RUN'):
            self.image.clip_draw(self.frame * 100, row, 100, 100, self.x, self.y)
