"""
This file contains functions to draw graphics
This includes: chunk drawer, background star layer
"""

import pygame
import random
from objects import Object
from game import *
import game



def draw_chunks():

    # Developer Tools
    # Chunk drawer
    """loaded_chunks = set()
    for chunk in game.CHUNKS.list:
        c = game.CHUNKS.get_chunk(chunk)
        pos = c.position * CHUNK_SIZE - red_ship.position + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
        if len(c.entities.intersection(game.CHUNKS.entities)):
            loaded_chunks.add(c)
        else:
            pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
    
    for c in loaded_chunks:
        pos = c.position * CHUNK_SIZE - red_ship.position + CENTRE_POINT
        rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
        pygame.draw.rect(WIN, (0, 255, 0), rect, width=1)"""


star_speed = 0.005
layers = 6
stars: list[set[Vector]] = list()
for _ in range(layers):
    layer: set[Vector] = set()
    for _ in range(200):
        layer.add(Vector(random.randint(-100, WIDTH + 100), random.randint(-100, HEIGHT + 100)))
    stars.append(layer)

def draw_stars(delta_time):
    # Layered Stars
    # Bigger stars move more

    for layer in range(layers):

        # Sometimes layer is incremented by 1 (layer + 1)
        # This is because the smallest layer should still have
        # a speed / size > 0

        # Move each star opposite direction to red_ship
        for star in stars[layer]:
            star.x -= game.red_ship.velocity.x * delta_time * star_speed * (layer+1)
            star.y -= game.red_ship.velocity.y * delta_time * star_speed * (layer+1)

            # If the star is outside of the screen, remove it
            # The + x needs to be double the -x
            # Because it is the -200 + 400 + WIDTH = WIDTH + 200
            if not star.in_range(-200, -200, WIDTH + 400, HEIGHT + 400):
                stars[layer].remove(star)

                # Keep on trying to add back star
                # That is not in the screen but around the outside
                star = Vector(random.randint(-100, WIDTH + 200), random.randint(-100, HEIGHT + 200))
                while star.in_range(0, 0, WIDTH, HEIGHT):
                    star = Vector(random.randint(-100, WIDTH + 200), random.randint(-100, HEIGHT + 200))
                stars[layer].add(star)

        # Draw all the stars in this layer
        for star in stars[layer]:
            pygame.draw.circle(WIN, (255, 255, 255), star.to_tuple(), (layer+2)/2)