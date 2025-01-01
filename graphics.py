
"""
This module handles all rendering logic, including:
- Determining which entities to draw
- Drawing chunk boundaries (in developer mode)
- Drawing a layered starfield background
"""

from random import randint
from typing import List, Set

import pygame

import game
from game import WIN, WIDTH, HEIGHT  # Be mindful: referencing these global game vars
from objects import Object
from vectors import Vector  # Hypothetical Vector class. Ensure your code references the correct one.


CHUNK_SIZE = 64  # Imported from somewhere else? Or define here
layers = 6       # Number of star layers
star_speed = 0.005
star_count_per_layer = 100


def get_entities_to_draw() -> List[Object]:
    """
    Returns the list of entities that are currently visible on screen,
    sorted by their 'z' attribute for proper layering (foreground vs. background).

    Visibility is determined by chunk-based culling or a simpler approach, based on config.
    """
    # Pull from global config. For future expansions, pass them in as parameters.
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2))
    center_chunk = game.CHUNKS.get_chunk(game.player).position

    result_entities: Set[Object] = set()

    if game.ENTITY_CULLING:
        # Aggressive culling: we only draw entities from chunks near the player
        # plus expansions near the screen border.
        # The logic ensures that large entities or partial overlap are also included.
        for y in range(center_chunk.y - radius, center_chunk.y + radius + 1):
            for x in range(center_chunk.x - radius, center_chunk.x + radius + 1):
                chunk = game.CHUNKS.get_chunk((x, y))
                result_entities.update(chunk.entities)

        # If you need further expansions in cardinal directions, do it similarly.
        # ...
    else:
        # Passive culling: just pick a bigger radius of chunks
        radius += 2
        for y in range(center_chunk.y - radius, center_chunk.y + radius + 1):
            for x in range(center_chunk.x - radius, center_chunk.x + radius + 1):
                chunk = game.CHUNKS.get_chunk((x, y))
                result_entities.update(chunk.entities)

    # Sort the final set of found entities by their 'z' attribute
    return sorted(result_entities, key=_z_sort)


def _z_sort(ent: Object) -> float:
    """
    Returns the 'z' attribute for an object, or 0 if none exists.
    Allows us to draw in correct layered order.
    """
    return getattr(ent, "z", 0.0)


def draw_chunks() -> None:
    """
    Debug function: draw chunk boundaries to help visualize the chunk grid.

    Green chunk box => chunk has at least one entity in the global set
    Red chunk box => chunk is empty
    """
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2)) + 1
    centre = game.CHUNKS.get_chunk(game.player).position

    for y in range(centre.y - radius, centre.y + radius + 1):
        for x in range(centre.x - radius, centre.x + radius + 1):
            chunk_pos = (x, y)
            chunk = game.CHUNKS.get_chunk(chunk_pos)

            # Position in screen space
            pos = Vector(x, y) * CHUNK_SIZE * game.ZOOM - game.player.position * game.ZOOM + game.CENTRE_POINT
            rect = (pos.x + 1, pos.y - 1, CHUNK_SIZE * game.ZOOM, CHUNK_SIZE * game.ZOOM)

            color = (0, 255, 0) if len(chunk.entities.intersection(game.CHUNKS.entities)) else (255, 0, 0)
            pygame.draw.rect(WIN, color, rect, width=1)


# PREPARE STARS
circles = []
stars = []  # Will hold the star positions, with shape: List[List[List[int]]]
def _init_stars() -> None:
    """
    Initialize or re-initialize the star layers and star circle images for each layer.
    Called on game start or on window size change.
    """
    global stars, circles

    # Regenerate star positions
    # star_count_per_layer can be made dynamic if needed
    stars = []
    for layer_idx in range(layers):
        star_layer_positions = []
        for _ in range(star_count_per_layer):
            # We allow some negative range so it spawns offscreen
            star_layer_positions.append([
                randint(-10, WIDTH + 10),
                randint(-10, HEIGHT + 10)
            ])
        stars.append(star_layer_positions)

    # Pre-generate the star images, from smallest to largest
    circles = []
    for layer_idx in range(layers):
        diameter = layer_idx + 1
        surface = pygame.Surface((200, 200), flags=pygame.SRCALPHA)
        pygame.draw.circle(surface, (200, 200, 200), (100, 100), 100)
        scaled = pygame.transform.smoothscale(surface, (diameter, diameter))
        # Convert to remove alpha for performance, but we keep colorkey for transparency
        scaled.convert()
        scaled.set_colorkey((0, 0, 0))
        circles.append(scaled)


def update_graphics_screen_size() -> None:
    """
    Called whenever the screen is resized or if you want to adapt star positions
    to new resolution. Regenerate star parallax layers.
    """
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = game.WIDTH, game.HEIGHT
    _init_stars()


def draw_stars() -> None:
    """
    Draw a multi-layer star background with parallax effect.

    The star field moves slightly opposite to the player's last movement,
    creating a sense of depth. Larger stars move more rapidly, smaller
    ones move more slowly (like parallax layers).
    """
    star_velocity = (game.LAST_PLAYER_POS - game.player.position) * star_speed

    # For each layer, shift the star positions and then draw them
    for layer_idx, star_layer in enumerate(stars):
        # e.g. layer 0 is smallest star, moves the least
        # layer N is largest star, moves the most
        # We do (layer_idx + 1) so smallest layer still moves a bit
        shift_x = star_velocity.x * (layer_idx + 1)
        shift_y = star_velocity.y * (layer_idx + 1)

        # Move each star in the layer
        for star in star_layer:
            star[0] += shift_x
            star[1] += shift_y

            # If the star is out of screen by a margin, re-spawn to avoid
            # indefinite growth in array size
            if star[0] < -100:
                star[0] = WIDTH + layer_idx
                star[1] = randint(-layer_idx, HEIGHT + layer_idx)
            elif star[0] > WIDTH + 100:
                star[0] = -layer_idx
                star[1] = randint(-layer_idx, HEIGHT + layer_idx)
            elif star[1] < -100:
                star[1] = HEIGHT + layer_idx
                star[0] = randint(-layer_idx, WIDTH + layer_idx)
            elif star[1] > HEIGHT + 100:
                star[1] = -layer_idx
                star[0] = randint(-layer_idx, WIDTH + layer_idx)

        # Now draw them in a batch using fblits (faster if available),
        # or do single draws if that's more straightforward.
        # We'll do the single draws for clarity.
        star_image = circles[layer_idx]
        for sx, sy in star_layer:
            WIN.blit(star_image, (sx, sy))


# Initialize star layers at import time, or let the game call _init_stars
_init_stars()
