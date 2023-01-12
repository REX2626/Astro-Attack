"""
This file loads all the images
1 pixel in a .png is equvilent to 1 game unit
All images have the same scale, i.e. they're pixels are all 1 game unit in size
"""

import pygame

ALIEN = pygame.image.load("assets/alien.png").convert_alpha()
ASTEROID1 = pygame.image.load("assets/asteroid1.png").convert_alpha()
ASTEROID2 = pygame.image.load("assets/asteroid2.png").convert_alpha()
ASTEROID3 = pygame.image.load("assets/asteroid3.png").convert_alpha()
ASTEROIDS = [ASTEROID1, ASTEROID2, ASTEROID3]
BULLET = pygame.image.load("assets/bullet3.png").convert_alpha()
DEFAULT = pygame.image.load("assets/default_image.png").convert_alpha()
RED_SHIP = pygame.image.load("assets/red_ship2.png").convert_alpha()
GREEN_SHIP = pygame.image.load("assets/green_ship.png").convert_alpha()
MOTHER_SHIP = pygame.image.load("assets/mother_ship.png").convert_alpha()
HEALTH_PICKUP = pygame.image.load("assets/health_pickup.png").convert_alpha()
ASTRO_ATTACK_LOGO1 = pygame.image.load("assets/AstroAttackLogo1.png").convert_alpha()
CURSOR = pygame.image.load("assets/cursor2.png").convert_alpha()
CURSOR_HIGHLIGHTED = pygame.image.load("assets/cursor_highlighted2.png").convert_alpha()