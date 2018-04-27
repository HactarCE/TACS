from .base import Image

from utils import FRAMERATE

__all__ = ['Movable']

class Movable(Image):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vel = (0.0, 0.0)
        self.partial_pos = (0.0, 0.0)

    def update(self):
        self.partial_pos = tuple(self.partial_pos[i] + self.vel[i] / FRAMERATE for i in range(2))
        dx, dy = round(self.partial_pos[0]), round(self.partial_pos[1])
        self.partial_pos = (self.partial_pos[0] - dx, self.partial_pos[1] - dy)
        if dx or dy:
            self.move((dx, dy))
