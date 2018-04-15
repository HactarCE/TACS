from drawables import Drawable

import pygame
import sys

__all__ = ['Scene']

def is_quit_event(ev):
    if ev.type is pygame.QUIT:
        return True
    if ev.type is pygame.KEYDOWN:
        if ev.key is pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            return True
        if ev.key is pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
            return True
    return False

class Scene(object):
    FRAMERATE = 60
    CLOCK = pygame.time.Clock()

    def __init__(self, disp):
        self.disp = disp
        self.drawables = []

    def add(self, drawable, layer):
        self.drawables.append((drawable, layer))

    def remove(self, drawable):
        self.drawables = [d for d in self.drawables if d[0] is not drawable]

    def show(self):
        self.disp.remove_all_children()
        for drawable, layer in self.drawables:
            self.disp.add_child(drawable, layer)

    def tick(self):
        # Handle events
        for event in pygame.event.get():
            if is_quit_event(event):
                self.quit(event)
            else:
                self.disp.handle_event(event)
        # Update objects
        self.disp.pre_update()
        self.disp.update()
        self.disp.post_update()
        # Render screen
        self.disp.redraw_if_needed()
        self.CLOCK.tick(self.FRAMERATE)

    def handle_event(self, ev):
        pass

    def quit(self, ev=None):
        sys.exit()
