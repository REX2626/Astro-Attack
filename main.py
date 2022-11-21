import pygame

from game import *
from objects import Bullet
import _menu

import math
from time import perf_counter

pygame.init()

pygame.display.set_caption("Astro Attack")



def update_playing_screen_size(menu: "_menu.Menu"):
    """Updates live objects positions"""

    global WIDTH, HEIGHT

    "Get objects position on screen by ratio e.g. 20% of the screen"

    WIDTH, HEIGHT = pygame.display.get_window_size()
    menu.resize()

    "Set the x and y of objects based on new width and height, with ratios"

    "Clip the coords of any object out of bounds"


font = pygame.font.SysFont("comicsans", 30)
def draw_window(delta_time):
    """Draw window"""
    WIN.fill(BLACK)

    for object in CHUNKS.entities:
        object.draw(WIN, red_ship.position, CENTRE_POINT)

    if delta_time:
        label = font.render(f"Angle: {round(red_ship.rotation / math.pi * 180 - 180) % 360 - 180}", True, (255, 255, 255))
        WIN.blit(label, (200, 0))

        label = font.render(f"Speed: {round(red_ship.velocity.magnitude())}", True, (255, 255, 255))
        WIN.blit(label, (200, 50))

        label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 0))
        
        label = font.render(f"Health: {round(red_ship.health)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 50))

        # Developer Tools
        # Chunk drawer
        """loaded_chunks = set()
        for chunk in CHUNKS.list:
            c = CHUNKS.get_chunk(chunk)
            pos = c.position * CHUNK_SIZE - red_ship.position + CENTRE_POINT
            rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
            if len(c.entities.intersection(CHUNKS.entities)):
                loaded_chunks.add(c)
            else:
                pygame.draw.rect(WIN, (255, 0, 0), rect, width=1)
        
        for c in loaded_chunks:
            pos = c.position * CHUNK_SIZE - red_ship.position + CENTRE_POINT
            rect = (pos.x+1, pos.y-1, CHUNK_SIZE, CHUNK_SIZE)
            pygame.draw.rect(WIN, (0, 255, 0), rect, width=1)"""


    pygame.display.update()


def handle_player_movement(keys_pressed, delta_time):

    """Adjust player velocity depnding on input. NOTE: Not for changing position"""
    # Example:
    if keys_pressed[pygame.K_w]:
        red_ship.move_forward(delta_time)

    if keys_pressed[pygame.K_s]:
        red_ship.move_backward(delta_time)

    if keys_pressed[pygame.K_a]:
        red_ship.move_left(delta_time)

    if keys_pressed[pygame.K_d]:
        red_ship.move_right(delta_time)

    if keys_pressed[pygame.K_LEFT]:
        red_ship.turn_left(delta_time)

    if keys_pressed[pygame.K_RIGHT]:
        red_ship.turn_right(delta_time)

    if keys_pressed[pygame.K_SPACE]:
        red_ship.shoot()

    CHUNKS.update(red_ship)


def update_objects(delta_time):
    """Updates all objects, e.g. adjusts positions based on velocity"""
    
    # Loop until every object has been updated e.g. moved
    # Entity set has to be copied as entity might be deleted from the actual set
    for object in filter(lambda object: type(object) != Bullet, CHUNKS.entities.copy()):
        
        # Update object e.g. move it
        object.update(delta_time)

    # Bullets are updated after everything else to ensure that the ships they may hit have been updated (and moved to the right position)
    for object in filter(lambda object: type(object) == Bullet, CHUNKS.entities.copy()):
        object.update(delta_time)


def main(menu: "_menu.Menu"):
    """Main game loop"""
    delta_time = 0

    global CHUNKS
    CHUNKS = init_chunks()

    global red_ship
    red_ship = add_player()

    running = True
    paused = False
    while running:
        while not paused:
            time1 = perf_counter()

            keys_pressed = pygame.key.get_pressed()

            handle_player_movement(keys_pressed, delta_time)
            update_objects(delta_time)

            draw_window(delta_time)

            if red_ship.health <= 0:
                main_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

                elif event.type == pygame.VIDEORESIZE:
                    update_playing_screen_size(menu)

                elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                    menu.pause()
                    paused = True
                    
            time2 = perf_counter()
            delta_time = time2 - time1

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.VIDEORESIZE:
                update_playing_screen_size(menu)
                draw_window(delta_time)
                menu.pause()

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                paused = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                menu.mouse_click(mouse)


def main_menu():
    menu = _menu.Menu()
    menu.resize()
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.VIDEORESIZE:
                menu.resize()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                menu.mouse_click(mouse)


if __name__ == "__main__":
    main_menu()