"""
This file contains functions to draw graphics
This includes: chunk drawer, background star layer
"""

import pygame
import random
from objects import Object
from game import *
import game



def get_entities_to_draw():
    """Returns the entities that are visible on the screen"""

    # Get number of chunks until going off the screen
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2)) + 1 # Round up

    centre: Vector = game.CHUNKS.get_chunk(game.player).position

    entities: set[Object] = set()

    for y in range(centre.y - radius, centre.y + radius + 1):
        for x in range(centre.x - radius, centre.x + radius + 1):

            chunk = game.CHUNKS.get_chunk((x, y))
            entities.update(chunk.entities)

    return entities



def draw_chunks():

    # Developer Tools
    # Chunk drawer
    loaded_chunks = set()
    for chunk in game.CHUNKS.list:
        c = game.CHUNKS.get_chunk(chunk)
        pos = c.position * CHUNK_SIZE * game.ZOOM - game.player.position * game.ZOOM + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE*game.ZOOM, CHUNK_SIZE*game.ZOOM)
        if len(c.entities.intersection(game.CHUNKS.entities)):
            loaded_chunks.add(c)
        else:
            pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
    
    for c in loaded_chunks:
        pos = c.position * CHUNK_SIZE * game.ZOOM - game.player.position * game.ZOOM + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE*game.ZOOM, CHUNK_SIZE*game.ZOOM)
        pygame.draw.rect(WIN, (0, 255, 0), rect, width=1)


star_speed = 0.005
layers = 6
stars: list[set[Vector]] = list()
for _ in range(layers):
    layer: set[Vector] = set()
    for _ in range(100):
        layer.add(Vector(random.randint(-10, WIDTH + 10), random.randint(-10, HEIGHT + 10)))
    stars.append(layer)

MIN_X = -100
MAX_X = WIDTH + 100
MIN_Y = -100
MAX_Y = HEIGHT + 100

draw_circle = pygame.draw.circle

# This function has been OPTIMIZED
def draw_stars():
    # Layered Stars
    # Bigger stars move more

    player_position_difference = game.player.position - game.LAST_PLAYER_POS

    for layer in range(layers):

        # Sometimes layer is incremented by 1 (layer + 1)
        # This is because the smallest layer should still have
        # a speed / size > 0

        radius = int((layer+2) / 2)

        # Move each star opposite direction to player
        shiftx = player_position_difference.x * star_speed * (layer+1)
        shifty = player_position_difference.y * star_speed * (layer+1)
        for star in stars[layer]:
            star.x -= shiftx
            star.y -= shifty
            # If the star is outside of the screen, remove it
            # 200 is the number of pixels a star can go outside the screen before being destroyed

            if star.x < MIN_X:
                star.x = WIDTH + radius
                star.y = random.randint(-radius, HEIGHT+radius)

            elif star.x > MAX_X:
                star.x = -radius
                star.y = random.randint(-radius, HEIGHT+radius)

            elif star.y < MIN_Y:
                star.x = random.randint(-radius, WIDTH+radius)
                star.y = HEIGHT+radius

            elif star.y > MAX_Y:
                star.x = random.randint(-radius, WIDTH+radius)
                star.y = -radius

            # Draw star
            draw_circle(WIN, (200, 200, 200), (star.x, star.y), (layer+2)/2) # Colour is a light grey, so the stars are not emphasised too much