import pygame
import colors
import layers
import text_engine
import utils

class GameObject(object):
    def __init__(self, surface):
        self.parent = None
        self.surf = surface
        self.rect = surface.get_rect()
        self.children = []
        self.layers = [[] for i in range(layers.LAYER_COUNT)]
        self.need_blit = True

    def move(self, offset):
        self.rect.move_ip(offset)

    def move_to(self, pos):
        self.rect = self.surf.get_rect().move(pos)

    def move_center_to(self, pos):
        new_pos = tuple(pos[i] - self.rect[i + 2] // 2 for i in range(2))
        self.rect = self.surf.get_rect().move(new_pos)

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

    def pre_update(self):
        for child in self.children:
            child.pre_update()

    def update(self):
        for child in self.children:
            child.update()

    def post_update(self):
        for child in self.children:
            child.post_update()

    def redraw_if_needed(self):
        updated_rects = []
        for layer in self.layers:
            for child in layer:
                if child.rect.collidelist(updated_rects) != -1:
                    child.invalidate()
                if child.redraw_if_needed():
                    updated_rects.append(child.rect)
        if self.need_blit:
            self.blit()
            self.need_blit = False
            return True
        return False

    def handle_event(self, ev):
        handled = False
        for child in self.children:
            handled = child.handle_event(ev) or handled
        return handled

    def invalidate(self):
        self.need_blit = True
        if self.parent:
            self.parent.invalidate()

    def blit(self):
        if self.parent:
            self.parent.surf.blit(self.surf, self.rect)

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

    def touching_mouse(self):
        return self.transform_rect(self.surf.get_rect()).collidepoint(pygame.mouse.get_pos())

class Display(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(pygame.display.set_mode(*args, **kwargs))

    def blit(self):
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
        super().__init__(self.idle_surf)
        self.click_handler = click_handler
        self.pressed = False

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
