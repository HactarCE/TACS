#!/bin/env python3

import colors
import pygame
import scenes
from drawables import Display

TITLE = 'Totally Accurate Curling Simulator'

ABOUT_TEXT = '''

The goal in TACS (Totally Accurate Curling Simulator) is to complete a round
with as many of your own rocks closer to the center of the target zone than
any of your opponent's. Each "throw" consists of three stages:

AIM: Use the up/down arrow keys to adjust aim, and spacebar to launch.

SLIDE-UP: Use the up/down arrow keys adjust spin, and spacebar to release
early. The thrower will automatically release the stone when the hogline
(first red line) is reached.

SWEEP: Use the up/down arrow keys to move the sweeper up and down, and
hold spacebar to sweep. Sweeping reduces friction on the ice, steering the
stone and making it travel farther.

'''.strip().split('\n')

pygame.init()

try:

    # SIZE = width, height = 1600, 900
    # FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME
    SIZE = width, height = 1920, 1080
    FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME

    pygame.display.set_caption(TITLE)

    scene_manager = scenes.SceneManager(Display(SIZE, FLAGS))
    scenes.MainMenu(scene_manager).init()
    scenes.Game(scene_manager).init()
    scenes.TextWall(ABOUT_TEXT, scene_manager).init('about')
    scenes.WinScreen("Player 1 wins!", colors.RED, scene_manager).init('win1')
    scenes.WinScreen("Player 2 wins!", colors.GREEN, scene_manager).init('win2')
    scenes.WinScreen("It's a tie!", colors.BLACK, scene_manager).init('tie')

    scene_manager.run('MainMenu')
    # scene_manager.run('Game')
    # scene_manager.run('tie')

finally:

    pygame.quit()
