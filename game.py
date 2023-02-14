"""
This file has all constants for other files to use
It also has functions that can be used in any file e.g. game.quit()
"""

import pygame

WIN = pygame.display.set_mode(flags=pygame.FULLSCREEN+pygame.RESIZABLE)

import images
pygame.display.set_icon(images.RED_SHIP)

pygame.init()

import sys
import random
from objects import Vector


WIDTH, HEIGHT = pygame.display.get_window_size()
FULLSCREEN = True
FULLSCREEN_SIZE = WIDTH, HEIGHT
WINDOW_SIZE = WIDTH * 0.8, HEIGHT * 0.8
SIZE_LINK = True

# CENTRE_POINT is the position of player on screen
CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

SCREEN_SHAKE = 0

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
MAX_PLAYER_SHIELD = 5
PLAYER_SHIELD_RECHARGE = 1
MAX_BOOST_AMOUNT = 20
MIN_PLAYER_SPEED = 500
MAX_PLAYER_SPEED = MIN_PLAYER_SPEED
PLAYER_ACCELERATION = 700

PLAYER_DEFAULT_DAMAGE = 1
PLAYER_DEFAULT_FIRE_RATE = 8
PLAYER_DEFAULT_BULLET_SPEED = 750

PLAYER_GATLING_DAMAGE = 0.5
PLAYER_GATLING_FIRE_RATE = 20
PLAYER_GATLING_BULLET_SPEED = 800

PLAYER_SNIPER_DAMAGE = 2
PLAYER_SNIPER_FIRE_RATE = 3
PLAYER_SNIPER_BULLET_SPEED = 1500

SCORE = 0
HIGHSCORE = 0

ZOOM = 2

BULLET_SPEED = 750

PICKUP_DISTANCE = 150

SCRAP_COUNT = 0

DEBUG_SCREEN = False

SEED = random.randint(0, 100000)


import _chunks
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

    global WIDTH, HEIGHT, CENTRE_POINT
    WIDTH, HEIGHT = pygame.display.get_window_size()
    CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

    if SIZE_LINK:
        "Adjust objects size"