#!/bin/env python3

import pygame
import scenes
from drawables import Display

TITLE = 'Totally Accurate Curling Simulator'

pygame.init()

try:

    # SIZE = width, height = 1600, 900
    # FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
    SIZE = width, height = 1920, 1080
    FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME

    pygame.display.set_caption(TITLE)

    scene_manager = scenes.SceneManager(Display(SIZE, FLAGS))
    scenes.MainMenu(scene_manager).init()

    scene_manager.run('MainMenu')

finally:

    pygame.quit()
