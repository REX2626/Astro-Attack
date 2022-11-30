"""
This file has all constants for other files to use
It also has functions that can be used in any file e.g. game.quit()
"""

import pygame

WIN = pygame.display.set_mode(flags=pygame.FULLSCREEN+pygame.RESIZABLE)

import sys
from objects import Vector
from player import Player_Ship
import _chunks


WIDTH, HEIGHT = pygame.display.get_window_size()
FULLSCREEN = True
FULLSCREEN_SIZE = WIDTH, HEIGHT
WINDOW_SIZE = WIDTH * 0.8, HEIGHT * 0.8
SIZE_LINK = True

# CENTRE_POINT is the position of red_ship on screen
CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
MEDIUM_GREY = (60, 60, 60)
DARK_GREY = (30, 30, 30)
BLACK = (0, 0, 0)

CHUNK_DISTANCE = 5 # Similar to RENDER DISTANCE, how many chunks are generated
CHUNK_SIZE = 200 # How big each chunk is

SPAWN_SIZE = 4

SCORE: int

ZOOM = 2


def init_chunks():
    global CHUNKS
    CHUNKS = _chunks.Chunks()
    return CHUNKS


def add_player():

    # Red Player Ship
    global red_ship
    red_ship = Player_Ship(position=(0, 0), velocity=(0, 0))
    CHUNKS.add_entity(red_ship)
    return red_ship


def quit():
    """Stops the program"""
    pygame.quit()
    sys.exit(0)


def update_screen_size():
    """Updates objects size and position with new screen size"""
    "Adjust any constants"

    if SIZE_LINK:
        "Adjust objects size"