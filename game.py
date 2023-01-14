"""
This file has all constants for other files to use
It also has functions that can be used in any file e.g. game.quit()
"""

import pygame

WIN = pygame.display.set_mode(flags=pygame.FULLSCREEN+pygame.RESIZABLE)

pygame.init()

import sys
from objects import Vector
import _chunks


WIDTH, HEIGHT = pygame.display.get_window_size()
FULLSCREEN = True
FULLSCREEN_SIZE = WIDTH, HEIGHT
WINDOW_SIZE = WIDTH * 0.8, HEIGHT * 0.8
SIZE_LINK = True

# CENTRE_POINT is the position of player on screen
CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
MEDIUM_GREY = (60, 60, 60)
DARK_GREY = (30, 30, 30)
BLACK = (0, 0, 0)

LOAD_DISTANCE = 5 # Similar to RENDER DISTANCE, how many chunks are generated
CHUNK_SIZE = 600 # How big each chunk is

SPAWN_SIZE = 4

SCORE: int
LAST_PLAYER_POS = Vector(0, 0)
MAX_PLAYER_HEALTH = 40
MAX_BOOST_AMOUNT = 20

SCORE = 0
HIGHSCORE = 0

ZOOM = 2

BULLET_SPEED = 750


def init_chunks():
    global CHUNKS
    CHUNKS = _chunks.Chunks()
    return CHUNKS


def quit():
    """Stops the program"""
    pygame.quit()
    sys.exit(0)


def update_screen_size():
    """Updates objects size and position with new screen size"""
    "Adjust any constants"

    if SIZE_LINK:
        "Adjust objects size"