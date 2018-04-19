from .base import Scene
from drawables import SolidColor, Image, Pannable
import colors
import layers

import pygame

__all__ = ['Game']

class Game(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        minimap = Image('img/sheet-mini.png')
        self.add(minimap, layers.BG)

        separator = SolidColor(colors.BLACK, (1920, 5))
        separator.move_to((0, 200))
        self.add(separator, layers.BG)

        pannable = Pannable((9600, 1000), pygame.Rect(0, 205, 1920, 875))
        self.pannable = pannable

        bg = Image('img/sheet-large.png')
        pannable.add_child(bg, layers.SPRITE_ICE)
        pannable.invalidate()



    def show(self):
        super().show()
        self.pannable.set_parent(self.disp)

    def pre_update(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            self.pannable.pan(0, -10)
        if pressed[pygame.K_DOWN]:
            self.pannable.pan(0, 10)
        if pressed[pygame.K_LEFT]:
            self.pannable.pan(-10, 0)
        if pressed[pygame.K_RIGHT]:
            self.pannable.pan(10, 0)
        self.pannable.finish_pan()

    def handle_event(self, ev):
        if super().handle_event(ev):
            return True
