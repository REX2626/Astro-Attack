"""
This file loads all the images
1 pixel in a .png is equvilent to 1 game unit
All images have the same scale, i.e. they're pixels are all 1 game unit in size
"""

import sys
import os
import pygame



def outline_station_image(image, colour, width, scale):
    # Scale image and blit on to surface, so there is a bit more room for the outline
    image = pygame.transform.scale_by(image, scale)
    surf = pygame.Surface((image.get_width()+2*int(width/2), image.get_height()+2*int(width/2)), flags=pygame.SRCALPHA)
    surf.blit(image, (int(width/2), int(width/2)))
    image = surf

    # Take a mask to make an outline of the station
    mask = pygame.mask.from_surface(image)
    outline = mask.outline()

    # Default outline
    pygame.draw.polygon(image, colour, outline, width=width)
    return image

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
GATLING_BULLET = load_image("assets/gatling_bullet.png")
RED_GATLING_BULLET = load_image("assets/red_gatling_bullet.png")
SNIPER_BULLET = load_image("assets/sniper_bullet.png")
RED_SNIPER_BULLET = load_image("assets/red_sniper_bullet.png")
MISSILE = load_image("assets/missile.png")
STATION_CANNON_BULLET = pygame.transform.scale2x(RED_BULLET)
PLAYER_SHIP = load_image("assets/player_ship.png")
RED_SHIP = load_image("assets/red_ship.png")
NEUTRAL_SHIP = load_image("assets/neutral_ship.png")
NEUTRAL_SHIP_CARGO = load_image("assets/neutral_ship_cargo.png")
ENEMY_SHIP = load_image("assets/enemy_ship.png")
MOTHER_SHIP = load_image("assets/mother_ship.png")
MISSILE_SHIP = load_image("assets/missile_ship.png")
DRONE_SHIP = load_image("assets/drone_ship.png")
ASTRO_ATTACK_LOGO = load_image("assets/AstroAttackLogo.png")
CURSOR = load_image("assets/cursor.png")
CURSOR_HIGHLIGHTED = load_image("assets/cursor_highlighted.png")
SCRAP = load_image("assets/scrap.png")
ARMOUR_ICON = load_image("assets/armour_icon.png")
WEAPON_ICON = load_image("assets/weapon_icon.png")
ENGINE_ICON = load_image("assets/engine_icon.png")
RADAR_ICON = load_image("assets/radar_icon.png")
PADLOCK = load_image("assets/padlock.png")
PLAYER_MINIMAP_IMAGE = load_image("assets/player_minimap.png")
FRIENDLY_STATION = outline_station_image(load_image("assets/space_station.png"), (5, 230, 20), width=3, scale=10)
FRIENDLY_STATION_ICON = outline_station_image(load_image("assets/space_station.png"), (5, 230, 20), width=1, scale=1)
ENEMY_STATION = outline_station_image(load_image("assets/space_station.png"), (230, 0, 0), width=3, scale=10)
ENEMY_STATION_ICON = outline_station_image(load_image("assets/space_station.png"), (230, 0, 0), width=1, scale=1)
SELECTED_STATION = outline_station_image(load_image("assets/space_station.png"), (252, 225, 5), width=3, scale=10)
STATION_CANNON = pygame.transform.scale_by(load_image("assets/station_cannon.png"), 3)
