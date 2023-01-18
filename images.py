"""
This file loads all the images
1 pixel in a .png is equvilent to 1 game unit
All images have the same scale, i.e. they're pixels are all 1 game unit in size
"""

import pygame
import sys
import os

def resource_path(relative_path):
    """Get absolute path to asset, used because the .exe stores assets in a different place"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_image(path):
    return pygame.image.load(resource_path(path)).convert_alpha()

DEFAULT = load_image("assets/default_image.png")
ASTEROID1 = load_image("assets/asteroid1.png")
ASTEROID2 = load_image("assets/asteroid2.png")
ASTEROID3 = load_image("assets/asteroid3.png")
ASTEROIDS = [ASTEROID1, ASTEROID2, ASTEROID3]
BULLET = load_image("assets/bullet.png")
RED_BULLET = load_image("assets/red_bullet.png")
RED_SHIP = load_image("assets/red_ship.png")
GREEN_SHIP = load_image("assets/green_ship.png")
MOTHER_SHIP = load_image("assets/mother_ship.png")
HEALTH_PICKUP = load_image("assets/health_pickup.png")
ASTRO_ATTACK_LOGO = load_image("assets/AstroAttackLogo.png")
CURSOR = load_image("assets/cursor.png")
CURSOR_HIGHLIGHTED = load_image("assets/cursor_highlighted.png")
SCRAP = load_image("assets/scrap.png")
ENGINE_ICON = load_image("assets/engine_icon.png")
RADAR_ICON = load_image("assets/radar_icon.png")
WEAPON_ICON = load_image("assets/weapon_icon.png")
PADLOCK = load_image("assets/padlock.png")