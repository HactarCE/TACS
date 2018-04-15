from .base import Drawable

import pygame
import colors
import text_engine

__all__ = ['Text', 'TextButton']

class Text(Drawable):
    def __init__(self, *args, **kwargs):
        super().__init__(text_engine.render_text(*args, **kwargs))

class TextButton(Drawable):
    def __init__(self, text, click_handler, font,
                 fg=colors.BLACK, bg=colors.WHITE,
                 fg_hover=None, bg_hover=None,
                 fg_click=None, bg_click=None,
                 *args, **kwargs):
        if not fg_hover:
            fg_hover = fg
        if not bg_hover:
            bg_hover = bg
        if not fg_click:
            fg_click = fg_hover
        if not bg_click:
            bg_click = bg_hover
        self.idle_surf = text_engine.render_text(text, font, fg=fg, bg=bg, *args, **kwargs)
        self.hover_surf = text_engine.render_text(text, font, fg=fg_hover, bg=bg_hover, *args, **kwargs)
        self.click_surf = text_engine.render_text(text, font, fg=fg_click, bg=bg_click, *args, **kwargs)
        self.click_handler = click_handler
        self.pressed = False
        super().__init__(self.idle_surf)

    def update(self):
        super().update()
        new_surf = self.idle_surf
        if self.touching_mouse():
            if self.pressed:
                new_surf = self.click_surf
            elif not pygame.mouse.get_pressed()[0]:
                new_surf = self.hover_surf
        if new_surf is not self.surf:
            self.surf = new_surf
            self.invalidate()

    def handle_event(self, ev):
        handled = super().handle_event(ev)
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and ev.button == 1:
            if ev.type is pygame.MOUSEBUTTONDOWN and self.touching_mouse():
                self.pressed = True
                return True
            if ev.type is pygame.MOUSEBUTTONUP and self.pressed:
                if self.touching_mouse():
                    self.click_handler()
                self.pressed = False
                return True
        return handled
