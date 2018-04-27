from .base import Scene
from drawables import Text, Image
from text_engine import wrap_text
import layers

import pygame

__all__ = ['TextWall']

class TextWall(Scene):
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bg = Image('img/ice.png')
        self.add(bg, layers.BG)
        # text = wrap_text(text, 'big_button', 1880)
        text = Text(text, 'big_button')
        text.move((20, 40))
        self.add(text, layers.UI_FG)
        text = Text('(Press any key to continue)', 'bottom_panel')
        text.move_center_to(bg.rect.center)
        text.move((0, 400))
        self.add(text, layers.UI_FG)

    def handle_event(self, ev):
        if ev.type is pygame.KEYDOWN:
            self.leave()
