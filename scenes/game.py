from .base import Scene
from drawables import CurlingRock, Image, Movable, Pannable, Rotatable, SolidColor, Text
from text_engine import ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT
import colors
import layers
import utils

# linear velocity is ~420 px/s (2 m/s)
# angular velocity ranges from 0-360 deg/s

import math
import pygame
import random

PRE_GAME        = 0
PRE_END         = 1
PRE_THROW       = 2
AIMING          = 3
THROWING        = 4
SWEEPING        = 5
WATCHING        = 6

__all__ = ['Game']

RANDOM_MULTIPLIER = 1

def up_key_is_pressed():
    p = pygame.key.get_pressed()
    return p[pygame.K_w] or p[pygame.K_UP] or p[pygame.K_i]

def down_key_is_pressed():
    p = pygame.key.get_pressed()
    return p[pygame.K_s] or p[pygame.K_DOWN] or p[pygame.K_k]

ACTION_KEYS = (pygame.K_SPACE, pygame.K_RETURN, pygame.K_f)
def action_key_is_pressed():
    p = pygame.key.get_pressed()
    return any(p[k] for k in ACTION_KEYS)

class Game(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.game_state = PRE_GAME
        self.team = 0 # team 0 has green pants; team 1 has gold pants
        self.timer = 0

        self.minimap = Image('img/sheet-mini.png')
        self.add(self.minimap, layers.BG)

        separator = SolidColor(colors.BLACK, (1920, 5))
        separator.move_to((0, 200))
        self.add(separator, layers.BG)

        self.pannable = Pannable((9600, 1000), pygame.Rect(0, 205, 1920, 825))

        self.bottom_panel = SolidColor(colors.DARK_GREY, (1920, 50))
        self.bottom_panel.move_to((0, 1030))
        self.add(self.bottom_panel, layers.BG)

        bg = Image('img/sheet-large.png')
        self.pannable.add_child(bg, layers.SPRITE_ICE)
        self.pannable.invalidate()

        #region People
        self.thrower_1      = Movable('img/people/thrower-1.png', True)
        self.thrower_1_alt  = Movable('img/people/thrower-1-alt.png', True)
        self.thrower_2      = Movable('img/people/thrower-2.png', True)
        self.thrower_2_alt  = Movable('img/people/thrower-2-alt.png', True)
        self.sweeper_1      = Movable('img/people/sweeper-1.png', True)
        self.sweeper_2      = Movable('img/people/sweeper-2.png', True)
        self.broom          = Movable('img/broom.png', True)
        self.pannable.add_child(self.broom, layers.SPRITE_BROOM)
        self.thrower = None
        self.sweeper = None
        #endregion

        self.thrower_1_alt.move_to((240, 255))
        self.thrower_2_alt.move_to((240, 255))

        self.trajectory = Rotatable(pygame.image.load('img/dashed-line-5px.png').convert_alpha())
        self.mini_trajectory = Rotatable(pygame.image.load('img/dashed-line-2px.png').convert_alpha())

        self.active_rock = None
        self.rocks = []

    #region Rocks
    def add_rock(self, position, team=None):
        if team is None:
            team = self.team
        rock = CurlingRock(self, team)
        rock.move_to(position)
        self.rocks.append(rock)
        self.pannable.add_child(rock, layers.SPRITE_ROCK)
        self.minimap.add_child(rock.preview, layers.SPRITE_ROCK)
        return rock

    def remove_rock(self, rock):
        print('remove_rock', rock)
        self.rocks.remove(rock)
        self.pannable.remove_child(rock)
        self.minimap.remove_child(rock.preview)

    def remove_all_rocks(self):
        print('removing', self.rocks)
        for r in self.rocks:
            print('remove', r)
            self.remove_rock(r)
    #endregion

    def show(self):
        super().show()
        self.pannable.set_parent(self.disp)
        self.pannable.blit_on_parent()

    def pre_update(self):
        pressed = pygame.key.get_pressed()
        if self.active_rock:
            self.pannable.pan_to_game_object(self.active_rock)
        if self.game_state is PRE_GAME:
            self.p1_score, self.p2_score = 0, 0
            self.game_state = PRE_END
            self.end = 0
        if self.game_state is PRE_END:
            self.end += 1
            self.remove_all_rocks()
            print('just removed all rocks:', self.rocks)
            self.team = not self.end % 2
            self.throws_left = 6
            self.update_bottom_panel()
            self.game_state = PRE_THROW
        if self.game_state is PRE_THROW:
            self.start_aim()
        self.broom.move_to(self.sweeper.rect.move((150, 75 + self.broom_offset)).topleft)
        if self.game_state is AIMING:
            if not self.active_rock:
                self.active_rock = self.add_rock((1000, 500))
            # region Aim
            rot_limit = 3
            if up_key_is_pressed() and not 180 > self.trajectory.get_rotation() > rot_limit:
                self.trajectory.rotate(0.1)
            if down_key_is_pressed() and not 180 < self.trajectory.get_rotation() < 360 - rot_limit:
                self.trajectory.rotate(-0.1)
            self.mini_trajectory.set_rotation(self.trajectory.get_rotation())
            source = (605, 500)
            if self.trajectory.get_rotation() < 180:
                self.trajectory.move_to((source[0], source[1] - self.trajectory.rect.height + 2))
                self.mini_trajectory.move_to((source[0] // 5, source[1] // 5 - self.mini_trajectory.rect.height + 1))
            else:
                self.trajectory.move_to((source[0], source[1] - 2))
                self.mini_trajectory.move_to((source[0] // 5, source[1] // 5 - 1))
            traj_pos = self.trajectory.rect.topleft
            #endregion
        if self.game_state is THROWING:
            if self.active_rock.rect.right > 2590: # hog line
                self.release_rock()
            if up_key_is_pressed():
                self.active_rock.rotvel += 3
            if down_key_is_pressed():
                self.active_rock.rotvel -= 3
            # TODO adjust spin
        if self.game_state is SWEEPING:
            sweep_limit = 50
            sweep_speed = 3
            if up_key_is_pressed() and self.sweeper_offset > -50:
                self.sweeper_offset -= sweep_speed
                self.sweeper.move((0, -sweep_speed))
            if down_key_is_pressed() and self.sweeper_offset < 50:
                self.sweeper_offset += sweep_speed
                self.sweeper.move((0, sweep_speed))
            if action_key_is_pressed():
                self.active_rock.use_reduced_friction()
                self.active_rock.vel = utils.add_vector(self.active_rock.vel, (0, math.hypot(*self.active_rock.vel) * self.sweeper_offset / 200000))
                self.animate_broom_frame()
            else:
                self.active_rock.use_normal_friction()
            if self.active_rock.rect.right > 9000 or self.active_rock.vel[0] < 30:
                self.deactivate_sweeper()
        if self.game_state is WATCHING:
            if self.timer or not(any(r.vel != (0, 0) or r.rotvel for r in self.rocks)):
                self.timer += 1
                if self.timer >= 60:
                    self.timer = 0
                    if self.throws_left:
                        self.prep_next_throw()
                    else:
                        s = self.get_end_scores()
                        print('last throw happened; here are the rocks')
                        for r in self.rocks:
                            print(r.rect.center, r.team)
                        print()
                        self.p1_score += s[0]
                        self.p2_score += s[1]
                        self.game_state = PRE_END
                        self.update_bottom_panel()
                        # if self.end == 2: # TODO
                        if self.end == 1:
                            self.end_game()

    def update(self):
        if self.game_state is THROWING:
            self.sweeper.vel = self.thrower.vel = self.active_rock.vel
        if self.game_state is SWEEPING:
            if self.thrower.vel != (0, 0):
                self.thrower.vel = utils.reduce_vector(self.thrower.vel, 1)
            self.sweeper.vel = self.active_rock.vel
        if self.game_state is WATCHING:
            if self.sweeper.rect.top > self.pannable.pan_size[1]:
                self.pannable.remove_child(self.sweeper)

    def post_update(self):
        for rock in self.rocks:
            if not rock.rect.colliderect(pygame.Rect((0, 0), self.pannable.pan_size)):
                self.remove_rock(rock)

    def handle_event(self, ev):
        if super().handle_event(ev):
            return True
        if ev.type is pygame.KEYDOWN and ev.key in ACTION_KEYS:
            if self.game_state is AIMING:
                self.start_throw()
            elif self.game_state is THROWING:
                self.release_rock()

    def animate_broom_frame(self):
        self.broom_animate += 0.5
        self.broom_offset = 10 * math.cos(self.broom_animate)

    def start_aim(self):
        self.active_rock = self.add_rock((530, 468))
        # self.active_rock.do_friction = False
        self.thrower = self.thrower_2_alt if self.team else self.thrower_1_alt
        self.pannable.add_child(self.thrower, layers.SPRITE_PERSON)
        self.sweeper = self.sweeper_2 if self.team else self.sweeper_1
        self.pannable.add_child(self.sweeper, layers.SPRITE_PERSON)
        self.sweeper.move_to(self.active_rock.rect.move((-55, -100)).topleft)
        self.pannable.add_child(self.trajectory, layers.SPRITE_DECALS)
        self.minimap.add_child(self.mini_trajectory, layers.SPRITE_DECALS)
        self.sweeper_offset = 0
        self.broom_offset = 0
        self.sweeper.vel = (0, 0)
        self.trajectory.set_rotation(0)
        self.update_bottom_panel()
        self.game_state = AIMING

    def start_throw(self):
        # TODO adjust power somehow
        self.pannable.remove_child(self.thrower)
        self.thrower = self.thrower_2 if self.team else self.thrower_1
        self.thrower.move_to((285, 255))
        self.active_rock.move((45, 0))
        self.pannable.add_child(self.thrower, layers.SPRITE_PERSON)
        self.pannable.remove_child(self.trajectory)
        self.minimap.remove_child(self.mini_trajectory)
        v = utils.rot_vector((420, 0), -self.trajectory.get_rotation())
        v = (v[0] + RANDOM_MULTIPLIER * random.random(), v[1] + RANDOM_MULTIPLIER * random.random())
        self.active_rock.vel = self.sweeper.vel = self.thrower.vel = v
        self.throws_left -= 1
        self.update_bottom_panel()
        self.game_state = THROWING

    def release_rock(self):
        self.active_rock.do_friction = True
        self.sweeper = self.sweeper_2 if self.team else self.sweeper_1
        self.pannable.add_child(self.sweeper, layers.SPRITE_PERSON)
        self.pannable.add_child(self.broom, layers.SPRITE_BROOM)
        # self.active_rock.rotvel = 120 # TODO
        self.broom_animate = 0
        self.broom_offset = 0
        self.game_state = SWEEPING

    def deactivate_sweeper(self):
        self.active_rock.use_normal_friction()
        self.pannable.remove_child(self.thrower)
        self.sweeper.vel = (self.sweeper.vel[0], 300)
        self.game_state = WATCHING

    def prep_next_throw(self):
        self.team = not self.team
        self.game_state = PRE_THROW
        print('rock list:')
        for r in self.rocks:
            print(r.rect.center, r.team)
        print()

    def update_bottom_panel(self):
        for child in self.bottom_panel.children:
            self.bottom_panel.remove_all_children()
        score = self.get_end_scores()
        t = Text(f'Player 1 score: {self.p1_score + score[0]}', 'bottom_panel', colors.RED, align=ALIGN_LEFT)
        t.move_to((30, 2))
        self.bottom_panel.add_child(t, layers.UI_FG)
        # t = Text(f'{self.throws_left} throws remaining / round #{self.end}', 'bottom_panel', colors.WHITE, align=ALIGN_RIGHT) # TODO
        t = Text(f'{self.throws_left} throws remaining', 'bottom_panel', colors.WHITE, align=ALIGN_RIGHT)
        t.move_to((960 - t.rect.width // 2, 2))
        self.bottom_panel.add_child(t, layers.UI_FG)
        t = Text(f'Player 2 score: {self.p2_score + score[1]}', 'bottom_panel', colors.YELLOW, align=ALIGN_CENTER)
        t.move_to((1920 - 30 - t.rect.width, 2))
        self.bottom_panel.add_child(t, layers.UI_FG)

    def get_end_scores(self):
        sorted_rocks = sorted(self.rocks, key=lambda r: math.hypot(r.rect.centerx - 8448, r.rect.centery - 500))
        if self.active_rock in sorted_rocks:
            sorted_rocks.remove(self.active_rock)
        if sorted_rocks:
            winning_team = sorted_rocks[0].team
            score = 0
            for r in sorted_rocks:
                if r.team == winning_team:
                    score += 1
                else:
                    break
            return (0, score) if winning_team else (score, 0)
        else:
            return (0, 0)

    def end_game(self):
        self.leave()
        if self.p1_score > self.p2_score:
            self.enter('win1')
        elif self.p1_score < self.p2_score:
            self.enter('win2')
        else:
            self.enter('tie')
