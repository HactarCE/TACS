import pygame
import colors
import layers
import text_engine
import utils

# TODO fix blitting logic

class GameObject(object):
    def __init__(self, surface):
        self.parent = None
        self.surf = surface
        self.comp_surf = surface.copy()
        self.old_rect = None
        self.rect = surface.get_rect()
        self.children = []
        self.layers = [[] for i in range(layers.LAYER_COUNT)]
        self.invalidated_rects = []
        self.invalidate()

    #region Movement
    def move(self, offset):
        self.rect.move_ip(offset)

    def move_to(self, pos):
        self.rect = self.surf.get_rect().move(pos)

    def move_center_to(self, pos):
        new_pos = tuple(pos[i] - self.rect[i + 2] // 2 for i in range(2))
        self.rect = self.surf.get_rect().move(new_pos)
    #endregion

    #region Children
    def add_child(self, child, layer=1):
        if child not in self.children:
            self.children.append(child)
            self.layers[layer].append(child)
        child.parent = self

    def remove_child(self, child):
        if child in self.children:
            self.children.remove(child)
        for layer in layers:
            if child in layer:
                layer.remove(child)
        child.parent = None
    #endregion

    #region Events
    def handle_event(self, ev):
        handled = False
        for child in self.children:
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
        # invlaidated_rects is a list of a Rects in local space
        if not area:
            area = self.surf.get_rect()
        if self.parent:
            self.parent.invalidate(area.move(self.rect.topleft))
        else:
            # TODO maybe add logic for combining Rects, or at least removing
            #      Rects that are completely contained by others
            self.invalidated_rects.append(area)

    def redraw_if_needed(self):
        if self.invalidated_rects:
            for r in self.invalidated_rects:
                self.comp_surf.blit(self.surf, r)
            for layer in self.layers:
                for child in layer:
                    child.redraw_if_needed()
                    for rect in self.invalidated_rects:
                        if rect.colliderect(child.rect):
                            r = rect.move((-child.rect.left, -child.rect.top))
                            child.blit_on_parent(r.clip(child.rect))
            for r in self.invalidated_rects:
                self.blit_on_parent(r)
            self.invalidated_rects = []
            return True
        return False

    def blit_on_parent(self, area=None):
        # area is a Rect in local space
        if not area:
            area = self.surf.get_rect()
        if self.parent:
            self.parent.surf.blit(self.surf, area.move(self.rect.topleft), area)
    #endregion

    #region Transformations
    def transform_point(self, point):
        # local space --> screen space
        p = tuple(point[i] * self.rect.size[i] // self.surf.get_rect().size[i] + self.rect[i] for i in range(2))
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
        return ((p[i] - self.rect[i]) * self.surf.get_rect().size[i] // self.rect.size[i] for i in range(2))

    def transform_rect(self, rect):
        # local space --> screen space
        r = rect.copy()
        r.topleft = self.transform_point(r.topleft)
        r.size = tuple(rect.size[i] * self.rect.size[i] // self.surf.get_rect().size[i] for i in range(2))
        if self.parent:
            return self.parent.transform_rect(r)
        else:
            return r

    def inverse_transform_rect(self, rect):
        # screen space --> local space
        if self.parent:
            r = self.parent.inverse_transform_rect(rect)
        else:
            r = rect.copy()
        r.topleft = self.inverse_transform_point(r.topleft)
        r.size = tuple(r[i] * self.rect[i] // self.rect[i] for i in range(2))
        return r
    #endregion

    def touching_mouse(self):
        return self.transform_rect(self.surf.get_rect()).collidepoint(pygame.mouse.get_pos())

class Display(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(pygame.display.set_mode(*args, **kwargs))

    def blit_on_parent(self, area=None):
        if area:
            pygame.display.update(area)
        else:
            pygame.display.flip()

class Text(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(text_engine.render_text(*args, **kwargs))

class TextButton(GameObject):
    def __init__(self, font, text, click_handler,
                 fg=colors.BLACK, bg=colors.WHITE,
                 fg_hover=None, bg_hover=None,
                 fg_click=None, bg_click=None,
                 *args, **kwargs):
        if not fg_hover:
            fg_hover = fg
        if not bg_hover:
            bg_hover = bg
        if not fg_click:
            fg_click = fg_hover
        if not bg_click:
            bg_click = bg_hover
        self.idle_surf = text_engine.render_text(font, text, fg=fg, bg=bg, *args, **kwargs)
        self.hover_surf = text_engine.render_text(font, text, fg=fg_hover, bg=bg_hover, *args, **kwargs)
        self.click_surf = text_engine.render_text(font, text, fg=fg_click, bg=bg_click, *args, **kwargs)
        self.click_handler = click_handler
        self.pressed = False
        super().__init__(self.idle_surf)

    def update(self):
        super().update()
        new_surf = self.idle_surf
        if self.touching_mouse():
            if self.pressed:
                new_surf = self.click_surf
            elif not pygame.mouse.get_pressed()[0]:
                new_surf = self.hover_surf
        if new_surf is not self.surf:
            self.surf = new_surf
            self.invalidate()

    def handle_event(self, ev):
        handled = super().handle_event(ev)
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and ev.button == 1:
            if ev.type is pygame.MOUSEBUTTONDOWN and self.touching_mouse():
                self.pressed = True
                return True
            if ev.type is pygame.MOUSEBUTTONUP and self.pressed:
                if self.pressed:
                    self.click_handler()
                    self.pressed = False
                    return True
        return handled

class Rotatable(GameObject):
    def __init__(self, image_name_pattern, angle_increment=15):
        self.angle_increment = angle_increment
        self.surfs = [pygame.image.load(image_name_pattern.format(i)) for i in range(0, 90, angle_increment)]
        self.rot = 0
        super().__init__(self.surfs[0])

    def set_rotation(self, angle):
        self.rot = angle
        self.invalidate()

    def get_rotation(self):
        return self.rot

    def rotate(self, angle):
        self.rot = (self.rot + angle) % 360
        self.invalidate()

    def invalidate(self):
        a = round(self.rot / self.angle_increment) * self.angle_increment % 90
        b = round((self.rot - a) / 90) * 90
        self.surf = pygame.transform.rotate(self.surfs[round(a // 15)], b)
        super().invalidate()
