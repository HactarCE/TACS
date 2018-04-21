from .base import Scene
from drawables import SolidColor, Image, Pannable, CurlingRock
import colors
import layers

import pygame

AIMING          = 1
THROWING        = 2
SWEEPING        = 3

__all__ = ['Game']

class Game(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_state = AIMING

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

        sweeper = Image('img/sweeper.png', True)
        pannable.add_child(sweeper, layers.SPRITE_PERSON)
        skipper = Image('img/skipper.png', True)
        pannable.add_child(skipper, layers.SPRITE_PERSON)

        skipper.move_to((400, 435))

        self.active_rock = None
        self.rocks = []

    def show(self):
        super().show()
        self.pannable.set_parent(self.disp)
        self.pannable.blit_on_parent()

    def pre_update(self):
        if self.game_state is AIMING:
            if not self.active_rock:
                self.active_rock = CurlingRock(self)
                self.rocks.append(self.active_rock)
                self.active_rock.move((1000, 200))
                # self.active_rock.vel = (30, 30)
                self.active_rock.vel = (300, 0)
                self.pannable.add_child(self.active_rock)
        # if self.active_rock:
            # self.pannable.pan_to_game_object(self.active_rock)
        pressed = pygame.key.get_pressed()
        # if pressed[pygame.K_SPACE]:
        #     self.active_rock.update_()
        dx, dy = 0, 0
        if pressed[pygame.K_UP]:
            dy -= 10
        if pressed[pygame.K_DOWN]:
            dy += 10
        if pressed[pygame.K_LEFT]:
            dx -= 10
        if pressed[pygame.K_RIGHT]:
            dx += 10
        self.pannable.pan(dx, dy)
        # self.pannable.invalidate()

    def handle_event(self, ev):
        if ev.type is pygame.KEYDOWN and ev.key is pygame.K_SPACE:
            self.active_rock.move((10, 10))
            # self.active_rock.update_()
        if super().handle_event(ev):
            return True
