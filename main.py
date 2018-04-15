#!/bin/env python3

import sys
import pygame
from text_engine import ALIGN_CENTER, render_text
import drawables
import scenes
import layers
import colors

TITLE = 'Totally Accurate Curling Simulator'

pygame.init()

# SIZE = width, height = 1600, 900
# FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
SIZE = width, height = 1920, 1080
FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
disp = drawables.Display(SIZE, FLAGS)

pygame.display.set_caption(TITLE)

main_menu = scenes.MainMenu(disp)

main_menu.show()

# Main loop
while True:
    main_menu.tick()
