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

    centre: Vector = game.CHUNKS.get_chunk(game.red_ship).position

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
        pos = c.position * CHUNK_SIZE - game.red_ship.position + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
        if len(c.entities.intersection(game.CHUNKS.entities)):
            loaded_chunks.add(c)
        else:
            pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
    
    for c in loaded_chunks:
        pos = c.position * CHUNK_SIZE - game.red_ship.position + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
        pygame.draw.rect(WIN, (0, 255, 0), rect, width=1)


star_speed = 0.005
layers = 6
stars: list[set[Vector]] = list()
for _ in range(layers):
    layer: set[Vector] = set()
    for _ in range(150):
        layer.add(Vector(random.randint(-100, WIDTH + 100), random.randint(-100, HEIGHT + 100)))
    stars.append(layer)

def draw_stars(delta_time):
    # Layered Stars
    # Bigger stars move more

    for layer in range(layers):

        # Sometimes layer is incremented by 1 (layer + 1)
        # This is because the smallest layer should still have
        # a speed / size > 0

        radius = int((layer+2) / 2)

        # Move each star opposite direction to red_ship
        for star in stars[layer]:
            star.x -= game.red_ship.velocity.x * delta_time * star_speed * (layer+1)
            star.y -= game.red_ship.velocity.y * delta_time * star_speed * (layer+1)

            # If the star is outside of the screen, remove it
            # 200 is the number of pixels a star can go outside the screen before being destroyed

            if star.x < -200:
                stars[layer].remove(star)
                star = Vector(WIDTH + radius, random.randint(-radius, HEIGHT+radius))
                stars[layer].add(star)

            elif star.x > WIDTH + 200:
                stars[layer].remove(star)
                star = Vector(-radius, random.randint(-radius, HEIGHT+radius))
                stars[layer].add(star)

            elif star.y < -200:
                stars[layer].remove(star)
                star = Vector(random.randint(-radius, WIDTH+radius), HEIGHT+radius)
                stars[layer].add(star)

            elif star.y > HEIGHT + 200:
                stars[layer].remove(star)
                star = Vector(random.randint(-radius, WIDTH+radius), -radius)
                stars[layer].add(star)

        # Draw all the stars in this layer
        for star in stars[layer]:
            pygame.draw.circle(WIN, (255, 255, 255), star.to_tuple(), (layer+2)/2)