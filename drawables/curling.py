from .base import Drawable, Rotatable

import pygame
import layers
import math

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

def pythag(*args):
    return math.sqrt(sum(args))

class CurlingRock(Drawable):
    RADIUS = 32

    def __init__(self, game):
        super().__init__(pygame.image.load('img/rock.png'))
        self.handle = Rotatable('img/handle/red-handle-{}.png')
        self.add_child(self.handle, layers.LAYER_HANDLE)
        self.pos = (0, 0)
        self.vel = (0, 0)
        self.rotvel = 0

    def pre_update(self):
        pass

    def update(self):
        self.pos = (self.pos[0] + self.vel[0] / FRAMERATE, self.pos[1] + self.vel[1] / FRAMERATE)
        self.handle.rotate(self.rotvel / FRAMERATE)
        if any(self.vel) or self.rotvel:
            self.invalidate()

    def post_update(self):
        for other in game.rocks[:game.rocks.index(self)]:
            if (self.vel or other.vel):
                d = pythag(self.pos[i] - other.pos[i] for i in range(2))
                if d <= self.RADIUS + other.RADIUS:
                    # TODO this only works if they hit head-on!
                    avg_vel = tuple((self.vel[i] + other.vel[i]) / 2 for i in range(2))
                    weighted_avg_vel = tuple(avg_vel[i] * (1 - ENERGY_CONSERVATION) for i in range(2))
                    weighted_self_vel = tuple(self_vel[i] * ENERGY_CONSERVATION for i in range(2))
                    weighted_other_vel = tuple(other_vel[i] * ENERGY_CONSERVATION for i in range(2))
                    self.vel = tuple(weighted_avg_vel[i] + weighted_other_vel[i] for i in range(2))
                    other.vel = tuple(weighted_avg_vel[i] + weighted_self_vel[i] for i in range(2))
