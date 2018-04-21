from .base import Drawable
from .rotatable import StepperRotatable

from utils import pythag, radian_angle_from_to, rot_vector, FRAMERATE

import pygame
import layers

__all__ = ['CurlingRock']

# This has got to be one of the weirdest constants I've ever set
ENERGY_CONSERVATION = 0.95
# > 1 - rocks bounce (it's weird)
# 1.0 - rocks transfer 100% of kinetic energy upon collision
#       (if a moving rock collides with a stationary one, the moving one comes
#        to a complete stop and the stationary one retains all momentum)
# 0.5 - rocks transfer 50% of kinetic energy upon collision
#       (if a moving rock collides with a stationary one, they stick together
#        and move at half the moving rock's original speed)
# < 0.5 - um... rocks pass through each other?

class CurlingRock(Drawable):
    RADIUS = 32

    def __init__(self, game):
        super().__init__(pygame.image.load('img/rock.png'))
        self.game = game
        self.handle = StepperRotatable('img/handle/handle-red-{}.png')
        self.handle.move((7, 7))
        self.handle.rotate(140)
        self.add_child(self.handle, layers.SPRITE_HANDLE)
        self.partial_pos = (0.0, 0.0)
        self.vel = (0.0, 0.0)
        self.rotvel = 180

    def pre_update(self):
        pass

    def update(self):
        self.partial_pos = tuple(self.partial_pos[i] + self.vel[i] / FRAMERATE for i in range(2))
        dx, dy = round(self.partial_pos[0]), round(self.partial_pos[1])
        self.partial_pos = (self.partial_pos[0] - dx, self.partial_pos[1] - dy)
        if dx or dy:
            self.move((dx, dy))
        if self.rotvel:
            self.handle.rotate(self.rotvel / FRAMERATE)

    def post_update(self):
        for other in self.game.rocks[:self.game.rocks.index(self)]:
            if (self.vel or other.vel):
                d = pythag(self.rect.center[i] - other.rect.center[i] for i in range(2))
                if d <= self.RADIUS + other.RADIUS:
                    # TODO test this please
                    # par=parallel, per=perpendiculuar
                    angle = radian_angle_from_to(self.pos, other.pos)
                    self_par_vel, self_per_vel = rot_vector_r(self.vel, angle)
                    other_par_vel, other_per_vel = rot_vector_r(other.vel, angle)
                    avg_vel = (self_per_vel + other_per_vel) / 2
                    weighted_avg_vel = avg_vel * (1 - ENERGY_CONSERVATION)
                    weighted_self_vel = self_per_vel * ENERGY_CONSERVATION
                    weighted_other_vel = other_per_vel * ENERGY_CONSERVATION
                    self.vel = rot_vector_r((weighted_avg_vel + weighted_other_vel), -angle)
                    other.vel = rot_vector_r((weighted_avg_vel + weighted_self_vel), -angle)
