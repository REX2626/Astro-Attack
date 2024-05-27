"""
This file contains functions to draw graphics
This includes: get_entities_to_draw, draw_chunks, draw_stars
"""

from objects import Object
import game
from game import *
from random import randint
import pygame



def get_entities_to_draw() -> list[Object]:
    """Returns the entities that are visible on the screen
    \nSorts the order to draw entities based on their 'z value'"""

    # TODO: Have a different radius for width and height of screen
    # TODO: Optimize culling more, check both axis
    # NOTE: Aggressive entity culling currently experimental

    # Get number of chunks until going off the screen
    radius = int((WIDTH / game.ZOOM) / (CHUNK_SIZE * 2))  # Ensure every entity that can be seen is drawn

    centre = game.CHUNKS.get_chunk(game.player).position

    entities: set[Object] = set()

    # Aggresive, only draw if player can see entity
    if game.ENTITY_CULLING:
        # XXXXX
        # XXXXX
        # OO@OO
        # XXXXX
        # XXXXX

        # Chunks that are definitely in the screen
        for y in range(centre.y - radius + 1, centre.y + radius):
            for x in range(centre.x - radius + 1, centre.x + radius):

                chunk = game.CHUNKS.get_chunk((x, y))
                entities.update(chunk.entities)

        # Get visible entities around edge of the screen
        for x in range(centre.x - radius - 1, centre.x + radius + 2):
            for y in range(centre.y + radius, centre.y + radius + 2):
                chunk = game.CHUNKS.get_chunk((x, y))
                for entity in chunk.entities:
                    if not hasattr(entity, "size") or (game.player.position.y - entity.position.y - entity.size.y/2) * game.ZOOM < HEIGHT/2:
                        entities.add(entity)

        for x in range(centre.x - radius - 1, centre.x + radius + 2):
            for y in range(centre.y - radius - 1, centre.y - radius + 1):
                chunk = game.CHUNKS.get_chunk((x, y))
                for entity in chunk.entities:
                    if not hasattr(entity, "size") or (entity.position.y - entity.size.y/2 - game.player.position.y) * game.ZOOM < HEIGHT/2:
                        entities.add(entity)

        for y in range(centre.y - radius + 1, centre.y + radius):
            for x in range(centre.x + radius, centre.x + radius + 2):
                chunk = game.CHUNKS.get_chunk((x, y))
                for entity in chunk.entities:
                    if not hasattr(entity, "size") or (entity.position.x - entity.size.x/2 - game.player.position.x) * game.ZOOM < WIDTH/2:
                        entities.add(entity)

        for y in range(centre.y - radius + 1, centre.y + radius):
            for x in range(centre.x - radius - 1, centre.x - radius + 1):
                chunk = game.CHUNKS.get_chunk((x, y))
                for entity in chunk.entities:
                    if not hasattr(entity, "size") or (game.player.position.x - entity.position.x - entity.size.x/2) * game.ZOOM < WIDTH/2:
                        entities.add(entity)

    # Passive, draw all entities in chunks around screen
    else:
        radius += 2
        for y in range(centre.y - radius, centre.y + radius + 1):
            for x in range(centre.x - radius, centre.x + radius + 1):

                chunk = game.CHUNKS.get_chunk((x, y))
                entities.update(chunk.entities)

    return sorted(entities, key=z_sort)


def z_sort(entity: Object) -> int:
    if hasattr(entity, "z"):
        return entity.z
    return 0



def draw_chunks() -> None:

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

def update_graphics_screen_size() -> None:
    global WIDTH, HEIGHT, stars
    WIDTH, HEIGHT = game.WIDTH, game.HEIGHT
    stars = list()
    for _ in range(layers):
        layer: list[list] = list()
        for _ in range(100):
            layer.append([randint(-10, WIDTH + 10), randint(-10, HEIGHT + 10)])
        stars.append(layer)


# Generate 6 star images, from smallest to largest
circles = []
for layer in range(layers):
    diameter = layer + 1
    surf = pygame.Surface((200, 200), flags=pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 200, 200), (100, 100), 100)
    surf = pygame.transform.smoothscale(surf, (diameter, diameter))
    circles.append(surf)

draw_circle = WIN.blit


# This function has been OPTIMIZED
def draw_stars() -> None:
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
            # 100 is the number of pixels a star can go outside the screen before being destroyed
            if star[0] < -100:
                star[0] = WIDTH + layer
                star[1] = randint(-layer, HEIGHT+layer)

            elif star[0] > WIDTH + 100:
                star[0] = -layer
                star[1] = randint(-layer, HEIGHT+layer)

            elif star[1] < -100:
                star[0] = randint(-layer, WIDTH+layer)
                star[1] = HEIGHT+layer

            elif star[1] > HEIGHT + 100:
                star[0] = randint(-layer, WIDTH+layer)
                star[1] = -layer

            # Draw star
            draw_circle(circles[layer], star)
