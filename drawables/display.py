from .base import Drawable

import pygame

__all__ = ['Display']

class Display(Drawable):
    def __init__(self, *args, **kwargs):
        super().__init__(pygame.display.set_mode(*args, **kwargs))
        self.comp_surf = self.surf
        self.captured_subsurfs = []

    def redraw_if_needed(self):
        rects = self.invalidated_rects
        if super().redraw_if_needed():
            for r in rects:
                self.blit_on_parent(r)
            return True
        return False

    def blit_on_parent(self, area=None):
        if area:
            pygame.display.update(area.clip(self.rect))
        else:
            pygame.display.flip()
