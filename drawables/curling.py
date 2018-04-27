from .base import Image
from .movable import Movable
from .rotatable import StepperRotatable

from utils import reduce_vector, radian_angle_from_to, rot_vector, rot_vector_r, FRAMERATE

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

CURL_COEFFICIENT = 5 / 100000000 # 0.05 millionths
# higher number -> more curling

# FRICTION_COEFFICIENT = 0.0115
FRICTION_COEFFICIENT = 0.0130
# ANGULAR_FRICTION_COEFFICIENT = 0.3
# ANGULAR_FRICTION_COEFFICIENT = 0.02
ANGULAR_FRICTION_COEFFICIENT = 2
# higher number -> more friction


class CurlingRock(Movable):
    RADIUS = 32

    def __init__(self, game, team):
        super().__init__('img/rock.png', True)
        self.game = game
        self.team = team
        team_color = ('red', 'yellow')[team]
        self.handle = StepperRotatable(f'img/handle/{team_color}/{{}}.png', 5)
        self.handle.move((7, 7))
        self.handle.rotate(270)
        self.add_child(self.handle, layers.SPRITE_HANDLE)
        self.rotvel = 0
        self.preview = Image(f'img/rock-{team_color}-mini.png', True)
        self.do_friction = True
        self.use_normal_friction()
        self.update_preview()

    def use_reduced_friction(self):
        self.linear_friction = FRICTION_COEFFICIENT / 2
        self.angular_friction = ANGULAR_FRICTION_COEFFICIENT / 2

    def use_normal_friction(self):
        self.linear_friction = FRICTION_COEFFICIENT
        self.angular_friction = ANGULAR_FRICTION_COEFFICIENT

    def finish_move(self):
        super().finish_move()
        self.update_preview()

    def update_preview(self):
        self.preview.move_to((self.rect.left // 5, self.rect.top // 5))

    def pre_update(self):
        if self.do_friction:
            # LINEAR VELOCITY
            self.vel = rot_vector(self.vel, -self.rotvel * math.hypot(*self.vel) * CURL_COEFFICIENT)
            self.vel = reduce_vector(self.vel, self.linear_friction * 17)
            # f=μN; N = normal force and f = frictional force
            # using gravity*mass for N, mass cancels out on both sides, resulting in:
            # a=μg
            # 17 = (16 ft/s^2) * (64 px/ft) / (60 frame/s) = acceleration due to gravity (px/s/frame)

            # ANGULAR VELOCITY
            dr = self.angular_friction / max(1, math.hypot(*self.vel))
            # dr = self.angular_friction
            if abs(self.rotvel) < dr:
                self.rotvel = 0
            else:
                self.rotvel -= math.copysign(dr, self.rotvel)
            # Angular friction calculation is not nearly as accurate as the linear
            # friction, simply because NOBODY KNOWS HOW CURLING PHYSICS WORKS

    def update(self):
        super().update()
        # MOVEMENT
        if self.rotvel:
            self.handle.rotate(self.rotvel / FRAMERATE)

    def post_update(self):
        if self in self.game.rocks:
            for other in self.game.rocks[:self.game.rocks.index(self)]:
                if self.vel or other.vel:
                    d = math.hypot(*(self.rect.center[i] - other.rect.center[i] for i in range(2)))
                    if d <= self.RADIUS + other.RADIUS:
                        # TODO test this please
                        # par=parallel, per=perpendiculuar
                        angle = radian_angle_from_to(self.rect.topleft, other.rect.topleft)
                        self_per_vel, self_par_vel = rot_vector_r(self.vel, -angle)
                        other_per_vel, other_par_vel = rot_vector_r(other.vel, -angle)
                        avg_vel = (self_per_vel + other_per_vel) / 2
                        weighted_avg_vel = avg_vel * (1 - ENERGY_CONSERVATION)
                        weighted_self_vel = self_per_vel * ENERGY_CONSERVATION
                        weighted_other_vel = other_per_vel * ENERGY_CONSERVATION
                        self.vel = rot_vector_r((weighted_avg_vel + weighted_other_vel, self_par_vel), angle)
                        other.vel = rot_vector_r((weighted_avg_vel + weighted_self_vel, other_par_vel), angle)
                        if not self.yep:
                            print(angle)
                            print(self_par_vel, self_per_vel)
                            print(other_par_vel, other_per_vel)
                            print(avg_vel)
                            print(weighted_avg_vel)
                            print(weighted_self_vel)
                            print(weighted_other_vel)
                            self.yep = 1

    yep = 0
