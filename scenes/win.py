from .base import Scene
from .game import Game

from drawables import Image, Text
import colors
import layers

import pygame

__all__ = ['WinScreen']

class WinScreen(Scene):
    def __init__(self, message, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bg = Image('img/ice.png')
        self.add(bg, layers.BG)
        text = Text(f'{message}', 'title', color)
        text.move_center_to(bg.rect.center)
        self.add(text, layers.UI_FG)
        text = Text('(Press any key to continue)', 'bottom_panel')
        text.move_center_to(bg.rect.center)
        text.move((0, 400))
        self.add(text, layers.UI_FG)

    def handle_event(self, ev):
        if ev.type is pygame.KEYDOWN:
            # TODO THIS IS NO PERMANENT FIX ASAP OH MY GOD THE BLOOD THE HORROR FIX IT NOW AAAAAAAAAAAAHHHHHHHHHHHHHHHHH
            # self.scene_manager.scenes['Game'] = Game
            self.leave()
