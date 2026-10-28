import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

import autorun
import boy


class AutoRunStateTests(unittest.TestCase):
    def test_move_advances_and_reverses_at_screen_edges(self):
        state = autorun.AutoRunState()

        self.assertEqual(state.move(400, 1), (412, 1))
        self.assertEqual(state.move(719, 1), (720, -1))
        self.assertEqual(state.move(81, -1), (80, 1))

    def test_duration_starts_on_entry_and_expires_after_five_seconds(self):
        state = autorun.AutoRunState()
        with patch.object(autorun, 'monotonic', return_value=10):
            state.enter()
        with patch.object(autorun, 'monotonic', return_value=14.99):
            self.assertFalse(state.is_finished())
        with patch.object(autorun, 'monotonic', return_value=15):
            self.assertTrue(state.is_finished())

    def test_draw_uses_visibly_larger_sprite_dimensions(self):
        state = autorun.AutoRunState()
        image = Mock()

        state.draw(image, frame=2, face_dir=1, x=400)

        image.clip_draw.assert_called_once_with(200, 100, 100, 100, 400, 110, 160, 160)


class BoyAutoRunTests(unittest.TestCase):
    def make_boy(self):
        with patch.object(boy, 'load_image', return_value=Mock()), \
             patch.object(boy, 'monotonic', return_value=100):
            return boy.Boy()

    def send_key(self, character, event_type, key):
        character.handle_event(SimpleNamespace(type=event_type, key=key))

    def test_a_starts_autorun_from_idle_and_arrow_key_takes_over(self):
        character = self.make_boy()
        with patch.object(autorun, 'monotonic', return_value=100):
            self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_a)
            character.update()
        self.assertEqual(character.state, 'AUTORUN')
        self.assertEqual(character.x, 412)

        self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_LEFT)
        self.assertEqual(character.state, 'RUN')
        self.assertEqual(character.face_dir, -1)
        character.update()
        self.assertEqual(character.x, 407)

    def test_a_starts_autorun_from_run(self):
        character = self.make_boy()
        self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_RIGHT)
        self.assertEqual(character.state, 'RUN')

        with patch.object(autorun, 'monotonic', return_value=100):
            self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_a)

        self.assertEqual(character.state, 'AUTORUN')
        self.assertEqual(character.auto_run.started_at, 100)

    def test_a_starts_autorun_from_sleep(self):
        character = self.make_boy()
        with patch.object(boy, 'monotonic', return_value=105):
            character.update()
        self.assertEqual(character.state, 'SLEEP')

        with patch.object(autorun, 'monotonic', return_value=200):
            self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_a)

        self.assertEqual(character.state, 'AUTORUN')
        self.assertEqual(character.auto_run.started_at, 200)

    def test_autorun_returns_to_idle_after_five_seconds(self):
        character = self.make_boy()
        with patch.object(autorun, 'monotonic', return_value=20):
            self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_a)
        with patch.object(autorun, 'monotonic', return_value=25), \
             patch.object(boy, 'monotonic', return_value=25):
            character.update()

        self.assertEqual(character.state, 'IDLE')
        self.assertEqual(character.idle_started_at, 25)

    def test_existing_sleep_wake_and_run_controls_remain_available(self):
        character = self.make_boy()
        with patch.object(boy, 'monotonic', return_value=105):
            character.update()
        self.assertEqual(character.state, 'SLEEP')

        self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_SPACE)
        self.assertEqual(character.state, 'IDLE')
        self.send_key(character, boy.SDL_KEYDOWN, boy.SDLK_RIGHT)
        self.assertEqual(character.state, 'RUN')
        self.assertEqual(character.face_dir, 1)


if __name__ == '__main__':
    unittest.main()
