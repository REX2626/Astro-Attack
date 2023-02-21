"""
This file contains functions to draw graphics
This includes: chunk drawer, background star layer
"""

import pygame
from random import randint
from objects import Object
from game import *
import game



def get_entities_to_draw():
    """Returns the entities that are visible on the screen
    \nSorts the order to draw entities based on their 'z value'"""

    # Get number of chunks until going off the screen
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2)) + 1 # Round up

    centre: Vector = game.CHUNKS.get_chunk(game.player).position

    entities: list[Object] = []

    for y in range(centre.y - radius, centre.y + radius + 1):
        for x in range(centre.x - radius, centre.x + radius + 1):

            chunk = game.CHUNKS.get_chunk((x, y))
            entities.extend(chunk.entities)

    return sorted(entities, key=z_sort)


def z_sort(entity):
    if hasattr(entity, "z"):
        return entity.z
    return 0



def draw_chunks():

    # Developer Tools
    # Chunk drawer

    # Get number of chunks until going off the screen
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2)) + 1 # Round up

    centre: Vector = game.CHUNKS.get_chunk(game.player).position

    for y in range(centre.y - radius, centre.y + radius + 1):
        for x in range(centre.x - radius, centre.x + radius + 1):

            chunk_pos = (x, y)
            chunk = game.CHUNKS.get_chunk(chunk_pos)

            pos = Vector(chunk_pos[0], chunk_pos[1]) * CHUNK_SIZE * game.ZOOM - game.player.position * game.ZOOM + game.CENTRE_POINT
            rect = (pos.x+1, pos.y-1, CHUNK_SIZE*game.ZOOM, CHUNK_SIZE*game.ZOOM)

            if len(chunk.entities.intersection(game.CHUNKS.entities)):
                pygame.draw.rect(WIN, (0, 255, 0), rect, width=1)

            else:
                pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
        


# Generate list of 6 layers, each layer has 100 coordinates of stars
star_speed = 0.005
layers = 6
stars: list[list[list]] = list()
for _ in range(layers):
    layer: list[list] = list()
    for _ in range(100):
        layer.append([randint(-10, WIDTH + 10), randint(-10, HEIGHT + 10)])
    stars.append(layer)


# 100 is the number of pixels a star can go outside the screen before being destroyed
MIN_X = -100
MAX_X = WIDTH + 100
MIN_Y = -100
MAX_Y = HEIGHT + 100

# Generate 6 star images, from smallest to largest
circles = []
for layer in range(layers):
    diameter = layer + 2
    radius = diameter / 2
    surf = pygame.Surface((diameter, diameter))
    pygame.draw.circle(surf, (200, 200, 200), (radius, radius), radius) # Colour is a light grey, so the stars are not emphasised too much
    surf = surf.convert()
    circles.append(surf)

draw_circle = WIN.blit


# This function has been OPTIMIZED
def draw_stars():
    # Layered Stars
    # Bigger stars move more

    star_velocity = (game.LAST_PLAYER_POS - game.player.position) * star_speed

    for layer in range(layers):

        # Sometimes layer is incremented by 1 (layer + 1)
        # This is because the smallest layer should still have
        # a speed / size > 0

        # Move each star opposite direction to player
        shiftx = star_velocity.x * (layer+1)
        shifty = star_velocity.y * (layer+1)

        for star in stars[layer]:
            star[0] += shiftx
            star[1] += shifty

            # If the star is outside of the screen, remove it
            if star[0] < MIN_X:
                star[0] = WIDTH + layer
                star[1] = randint(-layer, HEIGHT+layer)

            elif star[0] > MAX_X:
                star[0] = -layer
                star[1] = randint(-layer, HEIGHT+layer)

            elif star[1] < MIN_Y:
                star[0] = randint(-layer, WIDTH+layer)
                star[1] = HEIGHT+layer

            elif star[1] > MAX_Y:
                star[0] = randint(-layer, WIDTH+layer)
                star[1] = -layer

            # Draw star
            draw_circle(circles[layer], star)