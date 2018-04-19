from drawables import Drawable

import pygame
import sys

__all__ = ['SceneManager', 'Scene']

def is_quit_event(ev):
    if ev.type is pygame.QUIT:
        return True
    if ev.type is pygame.KEYDOWN:
        if ev.key is pygame.K_ESCAPE and pygame.key.get_mods() & pygame.KMOD_SHIFT:
            return True
        if ev.key is pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
            return True
    return False

class SceneManager(object):
    def __init__(self, display):
        self.disp = display
        self.scene_stack = []
        self.scenes = {}

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def enter(self, scene):
        if scene in self.scenes:
            scene = self.scenes[scene]
        if self.scene_stack:
            self.scene_stack[-1].hide()
        self.scene_stack.append(scene)
        self.active_scene = scene
        scene.show()

    def leave(self):
        self.scene_stack.pop().hide()
        self.active_scene = None

    def run(self, root_scene):
        self.enter(root_scene)
        while self.active_scene:
            self.active_scene.tick()
            if (not self.active_scene) and self.scene_stack:
                self.active_scene = self.scene_stack[-1]
                self.active_scene.show()

class Scene(object):
    FRAMERATE = 60
    CLOCK = pygame.time.Clock()

    def __init__(self, scene_manager):
        self.scene_manager = scene_manager
        self.disp = scene_manager.disp
        self.drawables = []

    def init(self, name=None):
        self.scene_manager.add_scene(name or self.__class__.__name__, self)

    def add(self, drawable, layer):
        self.drawables.append((drawable, layer))

    def remove(self, drawable):
        self.drawables = [d for d in self.drawables if d[0] is not drawable]

    def show(self):
        self.disp.remove_all_children()
        for drawable, layer in self.drawables:
            self.disp.add_child(drawable, layer)

    def leave(self):
        self.scene_manager.leave()

    def enter(self, scene):
        self.scene_manager.enter(scene)

    def hide(self):
        pass

    def pre_update(self):
        pass

    def post_update(self):
        pass

    def tick(self):
        # Handle events
        for event in pygame.event.get():
            self.handle_event(event)
        # Update objects
        self.pre_update()
        self.disp.pre_update()
        self.disp.update()
        self.disp.post_update()
        self.post_update()
        # Render screen
        self.disp.redraw_if_needed()
        self.CLOCK.tick(self.FRAMERATE)

    def handle_event(self, ev):
        if is_quit_event(ev):
            self.leave()
        elif ev.type is pygame.KEYDOWN and ev.key is pygame.K_f:
            print(self.CLOCK.get_fps())
            return True
        else:
            return self.disp.handle_event(ev)
