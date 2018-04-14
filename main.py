#!/bin/env python3

import sys
import pygame
from text_engine import ALIGN_CENTER, render_text
import game_objects
import layers
import colors

TITLE_WRAPPED = ["Totally Accurate", "Curling Simulator"]
TITLE = ' '.join(TITLE_WRAPPED)

FRAMERATE = 60

pygame.init()
size = width, height = 1600, 900
# size = width, height = 1920, 1080
# flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
# flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
flags = pygame.FULLSCREEN | pygame.HWSURFACE | pygame.NOFRAME
flags = pygame.HWSURFACE | pygame.NOFRAME
speed = [2, 2]
black = 0, 0, 0

clock = pygame.time.Clock()

disp = game_objects.Display()
pygame.display.set_caption(TITLE)

# ball = pygame.image.load('img/ball.png')
# ballrect = ball.get_rect()

title = game_objects.Text('title', TITLE_WRAPPED, align=ALIGN_CENTER)
title.move_center_to((disp.rect[2] // 2, disp.rect[3] // 3))
disp.add_child(title, layers.UI_FG)

background = game_objects.GameObject(pygame.image.load('img/icebg-temp.jpg'))
disp.add_child(background, layers.BG)

button1 = game_objects.TextButton('big_button', 'Button!', lambda: print('pushy button'), bg=None, fg_hover=colors.DARK_GREY, fg_click=colors.DARK_GREY)
button1.move_center_to((disp.rect[2] // 2, disp.rect[3] // 2))
disp.add_child(button1, layers.UI_FG)

rock = game_objects.Rotatable('img/handle/handle-red-{}.png')
rock.move_center_to((disp.rect[2] // 5, disp.rect[3] // 2))
# rock.surf = pygame.transform.smoothscale(rock.surf, tuple(rock.rect.size[i] * 2 for i in range(2)))
# rock.surf = pygame.transform.rotate(rock.surf, 90)
disp.add_child(rock, layers.SPRITE_0)


# Main loop
while True:

    # Handle events
    for event in pygame.event.get():
        disp.handle_event(event)
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_ESCAPE):
            # print(clock.get_fps())
            sys.exit()

    # Update objects
    rock.rotate(1)
    disp.pre_update()
    disp.update()
    disp.post_update()
    # background.invalidate()

    # Render screen
    disp.redraw_if_needed()

    clock.tick(FRAMERATE)
    # print('tick')
