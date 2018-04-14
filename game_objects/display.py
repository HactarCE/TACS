from .base import Drawable

import pygame

__all__ = ['Display']

class Display(Drawable):
    def __init__(self, *args, **kwargs):
        super().__init__(pygame.display.set_mode(*args, **kwargs))

    def blit_on_parent(self, area=None):
        if area:
            pygame.display.update(area)
        else:
            pygame.display.flip()
