import pygame
import layers

__all__ = ['Drawable', 'Rotatable', 'SolidColor', 'Image']

class Drawable(object):
    def __init__(self, surface):
        self.parent = None
        self.surf = surface
        if surface:
            self.comp_surf = surface.copy()
            self.rect = surface.get_rect()
            self.old_rect = self.rect
        self.invalidated_rects = []
        self.remove_all_children()

    #region Movement
    def move(self, offset):
        self.rect.move_ip(offset)
        self.finish_move()

    def move_to(self, pos):
        self.rect = self.surf.get_rect().move(pos)
        self.finish_move()

    def move_center_to(self, pos):
        self.move_to(tuple(pos[i] - self.rect[i + 2] // 2 for i in range(2)))

    def finish_move(self):
        if self.old_rect != self.rect:
            if self.parent:
                self.parent.invalidate(self.old_rect)
                self.parent.invalidate(self.rect)
            self.old_rect = self.rect.copy()
    #endregion

    #region Children
    def add_child(self, child, layer=1):
        if child not in self.children:
            self.children.append(child)
            self.layers[layer].append(child)
        child.parent = self
        self.invalidate()

    def allocate_subsurf(self, drawable, rect):
        self.subsurf_children.append(drawable)
        return self.comp_surf.subsurface(rect)

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
        for layer in layers:
            if child in layer:
                layer.remove(child)
        child.parent = None
        self.invalidate()

    def unallocate_subsurf(self, drawable):
        if drawable in self.subsurf_children:
            self.subsurf_children.remove(drawable)

    def remove_all_children(self):
        self.children = []
        self.layers = [[] for i in range(layers.LAYER_COUNT)]
        self.subsurf_children = []
    #endregion

    #region Events
    def handle_event(self, ev):
        handled = False
        for child in self.children + self.subsurf_children:
            handled = child.handle_event(ev) or handled
        return handled
    #endregion

    #region Updates
    def pre_update(self):
        for child in self.children:
            child.pre_update()

    def update(self):
        for child in self.children:
            child.update()

    def post_update(self):
        for child in self.children:
            child.post_update()
    #endregion

    #region Drawing
    def invalidate(self, area=None):
        # invalidated_rects is a list of Rects in local space
        if not area:
            area = self.surf.get_rect()
        if self.parent:
            self.parent.invalidate(self.transform_rect_to_parent(area))
        # TODO maybe add logic for combining Rects, or at least removing Rects
        # that are completely contained by others
        self.invalidated_rects.append(area)

    def redraw_if_needed(self):
        if self.invalidated_rects:
            if self.surf:
                for r in self.invalidated_rects:
                    self.comp_surf.blit(self.surf, r)
            for layer in self.layers:
                for child in layer:
                    child.redraw_if_needed()
                    for rect in self.invalidated_rects:
                        if rect.colliderect(child.rect):
                            r = child.transform_rect_from_parent(rect.clip(child.rect))
                            child.blit_on_parent(r)
            for child in self.subsurf_children:
                child.redraw_if_needed()
            self.invalidated_rects = []
            return True
        return False

    def blit_on_parent(self, area=None):
        # area is a Rect in local space
        if self.parent:
            if area:
                area = area.clip(self.surf.get_rect())
            else:
                area = self.surf.get_rect()
            # TODO if you're having issues, try messing with these lines
            # self.parent.comp_surf.blit(self.comp_surf, area.move(self.rect.topleft), area)
            self.parent.comp_surf.blit(self.comp_surf, self.rect, area)
    #endregion

    #region Transformations
    def transform_point_to_parent(self, point):
        return tuple(point[i] + self.rect[i] for i in range(2))

    def transform_point_from_parent(self, point):
        return tuple(point[i] - self.rect[i] for i in range(2))

    def transform_rect_to_parent(self, rect):
        return rect.move(self.rect.topleft)

    def transform_rect_from_parent(self, rect):
        return rect.move((-self.rect[0], -self.rect[1]))

    def transform_point(self, point):
        # local space --> screen space
        p = self.transform_point_to_parent(point)
        if self.parent:
            return self.parent.transform_point(p)
        else:
            return p

    def inverse_transform_point(self, point):
        # screen space --> local space
        if self.parent:
            p = self.parent.inverse_transform_point(point)
        else:
            p = point
        return self.transform_point_from_parent(p)

    def transform_rect(self, rect):
        # local space --> screen space
        r = self.transform_rect_to_parent(rect)
        if self.parent:
            return self.parent.transform_rect(r)
        else:
            return r

    def inverse_transform_rect(self, rect):
        # screen space --> local space
        if self.parent:
            r = self.parent.inverse_transform_rect(rect)
        else:
            r = rect
        return self.transform_rect_from_parent(r)
    #endregion

    def touching_mouse(self):
        return self.transform_rect(self.surf.get_rect()).collidepoint(pygame.mouse.get_pos())

class Rotatable(Drawable):
    def __init__(self, image_name_pattern, angle_increment=15):
        self.angle_increment = angle_increment
        self.surfs = [pygame.image.load(image_name_pattern.format(i)) for i in range(0, 90, angle_increment)]
        self.rot = 0
        super().__init__(self.surfs[0])

    #region Rotation
    def set_rotation(self, angle):
        self.rot = angle
        self.invalidate()

    def get_rotation(self):
        return self.rot

    def rotate(self, angle):
        self.rot = (self.rot + angle) % 360
        a = round(self.rot / self.angle_increment) * self.angle_increment % 90
        b = round((self.rot - a) / 90) * 90
        self.surf = pygame.transform.rotate(self.surfs[round(a // 15)], b)
        self.invalidate()
    #endregion

    # TODO Transformations (probably not necessary)

class SolidColor(Drawable):
    def __init__(self, color, size):
        s = pygame.Surface(size)
        s.fill(color)
        super().__init__(s)

class Image(Drawable):
    def __init__(self, image_path, convert=True):
        img_surf = pygame.image.load(image_path)
        if convert:
            img_surf = img_surf.convert()
        super().__init__(img_surf)
