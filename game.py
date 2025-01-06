"""
This file has all constants for other files to use

It also has functions that can be used in any file e.g. game.quit()

Settings are loaded from save at the start of the program

Game constants are loaded from save at the start of a game
"""

from __future__ import annotations
import os
import json
import pygame

pygame.init()

# ==================
# SETTINGS
# ==================

base_path = os.path.join(os.getenv("APPDATA"), "AstroAttack")
storage = os.path.join(base_path, "storage")

display_info = pygame.display.Info()

FULLSCREEN = True
WIDTH = display_info.current_w
HEIGHT = display_info.current_h
LOAD_DISTANCE = 5  # Chunks loaded from player
ENTITY_CULLING = False

settings = [
    "WIDTH",
    "HEIGHT",
    "FULLSCREEN",
    "LOAD_DISTANCE",
    "ENTITY_CULLING"
]

def save_settings():
    settings_list = {setting: globals()[setting] for setting in settings}
    with open(os.path.join(storage, "settings.json"), "w") as file:
        json.dump(settings_list, file)

# Create storage directory if it does not exist
if not os.path.isdir(storage):
    os.makedirs(storage)

# If settings.json exists - load it, else create settings.json
if os.path.isfile(os.path.join(storage, "settings.json")):
    with open(os.path.join(storage, "settings.json"), "r") as file:
        settings_list = json.load(file)
        for setting in settings_list:
            globals()[setting] = settings_list[setting]

else:
    save_settings()

# ==================
# BEGIN DISPLAY
# ==================

if FULLSCREEN: WIN = pygame.display.set_mode(flags=pygame.RESIZABLE+pygame.FULLSCREEN)
else: WIN = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.RESIZABLE)

import images
pygame.display.set_icon(images.RED_SHIP)

import sys
from objects import Vector

# ==================
# PERMANENT CONSTANTS
# ==================

WIDTH, HEIGHT = pygame.display.get_window_size()
FULLSCREEN_SIZE = display_info.current_w, display_info.current_h
WINDOW_SIZE = FULLSCREEN_SIZE[0] * 0.8, FULLSCREEN_SIZE[1] * 0.8

# CENTRE_POINT is the position of player on screen
CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
MEDIUM_GREY = (60, 60, 60)
DARK_GREY = (30, 30, 30)
BLACK = (0, 0, 0)

# Mission Types
KILL = 0
COLLECT = 1
UPGRADE = 2

CHUNK_SIZE = 600  # How big each chunk is

SPAWN_SIZE = 4

ENTITY_DICT = {"Enemy_Ship": "Enemy Ship", "Mother_Ship": "Mother Ship", "Drone_Enemy": "Drone Ship", "Missile_Ship": "Missile Ship"}
ENTITY_IMAGE_DICT = {"Enemy_Ship": images.ENEMY_SHIP, "Mother_Ship": images.MOTHER_SHIP, "Drone_Enemy": images.DRONE_SHIP, "Missile_Ship": images.MISSILE_SHIP}
for ship in ENTITY_IMAGE_DICT:
    ENTITY_IMAGE_DICT[ship] = pygame.transform.scale2x(ENTITY_IMAGE_DICT[ship])

# ==================
# WORLD CONSTANTS
# ==================

# This allows type hinting for game.player, done this way to avoid circular import errors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Player_Ship

import dill

global_variables = globals().copy()

NAME = None
SEED = None
CHUNKS = None
player: Player_Ship = None

SCREEN_SHAKE = 0

LAST_PLAYER_POS = Vector(0, 0)
MAX_PLAYER_HEALTH = 40
MAX_PLAYER_ARMOUR = 40
MAX_PLAYER_SHIELD = 5
PLAYER_SHIELD_RECHARGE = 1
MAX_BOOST_AMOUNT = 20
MIN_PLAYER_SPEED = 500
MAX_PLAYER_SPEED = MIN_PLAYER_SPEED
PLAYER_ACCELERATION = 700
WEAPON_SELECTED = 0

PLAYER_BLASTER_DAMAGE = 1
PLAYER_BLASTER_FIRE_RATE = 8
PLAYER_BLASTER_BULLET_SPEED = 750

PLAYER_GATLING_DAMAGE = 0.5
PLAYER_GATLING_FIRE_RATE = 20
PLAYER_GATLING_BULLET_SPEED = 800

PLAYER_SNIPER_DAMAGE = 2
PLAYER_SNIPER_FIRE_RATE = 3
PLAYER_SNIPER_BULLET_SPEED = 1500

PLAYER_LASER_DAMAGE = 10
PLAYER_LASER_RANGE = 200

# Upgrade bar levels
MAX_PLAYER_HEALTH_LEVEL = 0
MAX_PLAYER_SHIELD_LEVEL = 0
PLAYER_SHIELD_RECHARGE_LEVEL = 0

PLAYER_ACCELERATION_LEVEL = 0
MAX_PLAYER_SPEED_LEVEL = 0
MAX_BOOST_AMOUNT_LEVEL = 0

PICKUP_DISTANCE_LEVEL = 0
CURRENT_MIN_ZOOM_LEVEL = 0

PLAYER_BLASTER_FIRE_RATE_LEVEL = 0
PLAYER_BLASTER_DAMAGE_LEVEL = 0
PLAYER_BLASTER_BULLET_SPEED_LEVEL = 0

PLAYER_GATLING_FIRE_RATE_LEVEL = 0
PLAYER_GATLING_DAMAGE_LEVEL = 0
PLAYER_GATLING_BULLET_SPEED_LEVEL = 0

PLAYER_SNIPER_FIRE_RATE_LEVEL = 0
PLAYER_SNIPER_DAMAGE_LEVEL = 0
PLAYER_SNIPER_BULLET_SPEED_LEVEL = 0

PLAYER_LASER_RANGE_LEVEL = 0
PLAYER_LASER_DAMAGE_LEVEL = 0

SCORE = 0
KILLED_SHIP_IMAGES = []

CURRENT_MISSION_SLOT: int = None
MISSIONS: list[dict] = [None, None, None]

CURRENT_SHIP_LEVEL = 0

SCRAP_COUNT = 0

PICKUP_DISTANCE = 150

BULLET_SPEED = 750

ZOOM = 1.5
CURRENT_MIN_ZOOM = 1.5
MIN_ZOOM = 0.4
MAX_ZOOM = 8

DOCKING = False
OPEN_STATION = False

DEBUG_SCREEN = False
CONSOLE_SCREEN = False

new_global_variables = globals().copy()
del new_global_variables["global_variables"]
set1 = set(name for name in global_variables if name[:2] != "__")
set2 = set(name for name in new_global_variables if name[:2] != "__")
constants = {name: globals()[name] for name in (set1 ^ set2)}

class Pickler(dill.Pickler):
    def reducer_override(self, obj):
        """Remove Surface or Mask as they cannot be pickled"""

        for name in dir(obj):
            if isinstance(getattr(obj, name), (pygame.Surface, pygame.Mask)):
                delattr(obj, name)

        return NotImplemented

def reset_constants():
    globals().update(constants)

def save_constants(file_name):
    constants_dict = {}
    for name in constants:
        constants_dict[name] = globals()[name]

    with open(os.path.join(storage, "worlds", f"{file_name}.pkl"), "wb") as file:
        Pickler(file, dill.HIGHEST_PROTOCOL).dump(constants_dict)

def load_constants(file_name):
    with open(os.path.join(storage, "worlds", f"{file_name}.pkl"), "rb") as file:
        constants_dict = dill.load(file)

    for constant in constants_dict:
        globals()[constant] = constants_dict[constant]

def get_world_dir():
    with open(os.path.join(storage, "world_dir.json"), "r+") as file:
        return json.load(file)

def update_world_dir(name, seed):
    with open(os.path.join(storage, "world_dir.json"), "r") as file:
        world_dir: list = json.load(file)

    world_dir.append((name, seed))

    with open(os.path.join(storage, "world_dir.json"), "w") as file:
        json.dump(world_dir, file)

def set_name_to_top_of_world_dir(name):
    with open(os.path.join(storage, "world_dir.json"), "r") as file:
        world_dir: list = json.load(file)

    for idx, world in enumerate(world_dir):
        if world[0] == name:
            break

    world_dir.insert(0, world_dir.pop(idx))

    with open(os.path.join(storage, "world_dir.json"), "w") as file:
        json.dump(world_dir, file)

def delete_world(name):
    # Delete world name from directory
    with open(os.path.join(storage, "world_dir.json"), "r") as file:
        world_dir: list = json.load(file)

    for world in world_dir:
        if world[0] == name:
            world_dir.remove(world)
            break

    with open(os.path.join(storage, "world_dir.json"), "w") as file:
        json.dump(world_dir, file)

    # Delete world data from worlds
    os.remove(os.path.join(storage, "worlds", f"{name}.pkl"))

reset_constants()

# Create world_dir.json if it doesn't exist
if not os.path.isfile(os.path.join(storage, "world_dir.json")):
    with open(os.path.join(storage, "world_dir.json"), "w") as file:
        json.dump([], file)

# Create worlds directory if it does not exist
if not os.path.isdir(os.path.join(storage, "worlds")):
    os.makedirs(os.path.join(storage, "worlds"))

# ==================
# FUNCTIONS
# ==================

import chunks
def init_chunks():
    global CHUNKS
    CHUNKS = chunks.Chunks()


def quit():
    """Stops the program"""
    pygame.quit()
    sys.exit(0)


def update_screen_size():
    """Updates objects size and position with new screen size"""

    global WIDTH, HEIGHT, CENTRE_POINT
    WIDTH, HEIGHT = pygame.display.get_window_size()
    CENTRE_POINT = Vector(WIDTH/2, HEIGHT/2)

    save_settings()
