from .base import Drawable

import pygame

__all__ = ['Pannable']

clamp = lambda x, l, u: l if x < l else u if x > u else x

class Pannable(Drawable):
    def __init__(self, pan_size, window_rect):
        super().__init__(None)
        self.rect = window_rect
        self.pan_size = pan_size
        self.window_rect = window_rect
        self.comp_surf = pygame.Surface(self.pan_size)
        self.comp_surf.fill((255, 0, 0), pygame.Rect(25, 50, 100, 300))
        self.parent_subsurf = None
        self.pan_x, self.pan_y = 0, 0
        self.last_pan = (self.pan_x, self.pan_y)

    def set_parent(self, parent):
        self.parent = parent
        self.parent_subsurf = parent.allocate_subsurf(self, self.window_rect)

    #region Movement
    def move(self, *_, **__):
        self.finish_move()

    def move_to(self, *_, **__):
        self.finish_move()

    def move_center_to(self, *_, **__):
        self.finish_move()

    def finish_move(self):
        raise Exception('Cannot move Pannable after it has been created -- use Pannable.pan() instead')
    #endregion

    #region Panning
    def pan(self, dx, dy):
        self.pan_x += dx
        self.pan_y += dy
        self.finish_pan()

    def pan_to(self, x, y):
        self.pan_x, self.pan_y = x, y
        self.finish_pan()

    def pan_to_game_object(self, game_object):
        self.pan_center_to(*game_object.rect.center)

    def pan_center_to(self, x, y):
        self.pan_x = x - self.window_rect.width // 2
        self.pan_y = y - self.window_rect.height // 2
        self.finish_pan()

    def get_pan_pos(self):
        return (self.pan_x, self.pan_y)

    def get_inverse_pan_pos(self):
        return (-self.pan_x, -self.pan_y)

    def finish_pan(self):
        self.pan_x = clamp(self.pan_x, 0, self.pan_size[0] - self.window_rect.width)
        self.pan_y = clamp(self.pan_y, 0, self.pan_size[1] - self.window_rect.height)
        def update_rect(*args):
            # converts rectangle from window space to panning space, then calls blit_on_parent() with it
            r = pygame.Rect(*args)
            r.normalize() # ffs pygame, ever heard of immutability? this could be a one-liner
            self.blit_on_parent(r)
        if self.last_pan and self.last_pan != (self.pan_x, self.pan_y):
            dx = self.pan_x - self.last_pan[0]
            dy = self.pan_y - self.last_pan[1]
            w, h = self.window_rect.size
            if abs(dx) < w and abs(dy) < h:
                old_visible_rect = self.get_visible_rect()
                self.parent_subsurf.scroll(-dx, -dy)
                preserved_rect = old_visible_rect.clip(self.get_visible_rect()).move(self.get_inverse_pan_pos())
                # self.force_parent_blit(preserved_rect)
                if dy > 0:
                    update_rect(0, h, w, -dy)
                elif dy < 0:
                    update_rect(0, 0, w, -dy)
                if dx > 0:
                    update_rect(w, preserved_rect.top, -dx, preserved_rect.height)
                elif dx < 0:
                    update_rect(0, preserved_rect.top, -dx, preserved_rect.height)
            else:
                self.blit_on_parent()
            self.force_parent_blit()
        self.last_pan = self.pan_x, self.pan_y
    #endregion

    #region Drawing
    def invalidate(self, area=None):
        # invalidated_rects is a list of Rects in local space (within panning content)
        if not area:
            area = pygame.Rect((0, 0), self.pan_size)
        super().invalidate(area)

    def redraw_if_needed(self):
        rects = self.invalidated_rects
        if super().redraw_if_needed():
            for r in rects:
                self.blit_on_parent(r.move((-self.pan_x, -self.pan_y)))

    def blit_on_parent(self, area=None):
        # area is in window space
        if self.parent:
            if area:
                area = area.clip(pygame.Rect((0, 0), self.window_rect.size))
            else:
                area = pygame.Rect((0, 0), self.window_rect.size)
            self.parent_subsurf.blit(self.comp_surf.subsurface(self.get_visible_rect()), area, area)

    def force_parent_blit(self, area=None):
        # area is in window space
        if area:
            area = area.move(self.window_rect.topleft)
        else:
            area = self.window_rect
        self.parent.blit_on_parent(area)
    #endregion

    #region Transformations
    def transform_point_to_parent(self, point):
        return tuple(point[i] + self.rect[i] - self.get_pan_pos()[i] for i in range(2))

    def transform_point_from_parent(self, point):
        return tuple(point[i] - self.rect[i] + self.get_pan_pos()[i] for i in range(2))

    def transform_rect_to_parent(self, rect):
        return pygame.Rect(self.transform_point(rect.topleft), rect.size)

    def transform_rect_from_parent(self, rect):
        return pygame.Rect(self.inverse_transform_point(rect.topleft), rect.size)
    #endregion

    def get_visible_rect(self):
        return pygame.Rect(self.get_pan_pos(), self.window_rect.size)
