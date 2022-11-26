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
        pos = c.position * CHUNK_SIZE * game.ZOOM - game.red_ship.position * game.ZOOM + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE*game.ZOOM, CHUNK_SIZE*game.ZOOM)
        if len(c.entities.intersection(game.CHUNKS.entities)):
            loaded_chunks.add(c)
        else:
            pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
    
    for c in loaded_chunks:
        pos = c.position * CHUNK_SIZE * game.ZOOM - game.red_ship.position * game.ZOOM + CENTRE_POINT
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

def draw_stars(delta_time):
    # Layered Stars
    # Bigger stars move more

    for layer in range(layers):

        # Sometimes layer is incremented by 1 (layer + 1)
        # This is because the smallest layer should still have
        # a speed / size > 0

        radius = int((layer+2) / 2)

        # Move each star opposite direction to red_ship
        shiftx = game.red_ship.velocity.x * delta_time * star_speed * (layer+1)
        shifty = game.red_ship.velocity.y * delta_time * star_speed * (layer+1)
        for star in stars[layer]:
            star.x -= shiftx
            star.y -= shifty
            # If the star is outside of the screen, remove it
            # 200 is the number of pixels a star can go outside the screen before being destroyed

            if star.x < -100:
                stars[layer].remove(star)
                star = Vector(WIDTH + radius, random.randint(-radius, HEIGHT+radius))
                stars[layer].add(star)

            elif star.x > WIDTH + 100:
                stars[layer].remove(star)
                star = Vector(-radius, random.randint(-radius, HEIGHT+radius))
                stars[layer].add(star)

            elif star.y < -100:
                stars[layer].remove(star)
                star = Vector(random.randint(-radius, WIDTH+radius), HEIGHT+radius)
                stars[layer].add(star)

            elif star.y > HEIGHT + 100:
                stars[layer].remove(star)
                star = Vector(random.randint(-radius, WIDTH+radius), -radius)
                stars[layer].add(star)

            # Draw star
            pygame.draw.circle(WIN, (255, 255, 255), star.to_tuple(), (layer+2)/2)