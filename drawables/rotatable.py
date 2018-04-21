from .base import Drawable

import pygame

__all__ = ['Rotatable', 'StepperRotatable']

class Rotatable(Drawable):
    def __init__(self, surface):
        self.source_surf = surface
        self.rot = 0
        super().__init__(self.source_surf)

    #region Rotation
    def set_rotation(self, angle):
        self.rot = angle % 360
        self.finish_rotation()

    def get_rotation(self):
        return self.rot

    def rotate(self, angle):
        self.set_rotation(self.rot + angle)

    def finish_rotation(self):
        self.surf = pygame.transform.rotate(self.source_surf, self.rot)
        self.invalidate()
    #endregion

    # TODO Transformations (probably not necessary)

class StepperRotatable(Rotatable):
    def __init__(self, image_path_pattern, angle_increment=15):
        self.angle_increment = angle_increment
        self.source_surfs = [pygame.image.load(image_path_pattern.format(i)) for i in range(0, 90, angle_increment)]
        self.rot = 0
        super().__init__(self.source_surfs[0])

    def finish_rotation(self):
        a = round(self.rot / self.angle_increment) * self.angle_increment % 90
        b = round((self.rot - a) / 90) * 90
        self.surf = pygame.transform.rotate(self.source_surfs[round(a // 15)], b)
        self.invalidate()
