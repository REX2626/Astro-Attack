"""
This file loads all the images
1 pixel in a .png is equvilent to 1 game unit
All images have the same scale, i.e. they're pixels are all 1 game unit in size
"""

import pygame

ALIEN = pygame.image.load("assets/alien.png").convert_alpha()
ASTEROID = pygame.image.load("assets/asteroid1.png").convert_alpha()
BULLET = pygame.image.load("assets/bullet3.png").convert_alpha()
DEFAULT = pygame.image.load("assets/default_image.png").convert_alpha()
RED_SHIP = pygame.image.load("assets/red_ship2.png").convert_alpha()
GREEN_SHIP = pygame.image.load("assets/green_ship.png").convert_alpha()
MOTHER_SHIP = pygame.image.load("assets/mother_ship.png").convert_alpha()