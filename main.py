import pygame

from game import *
import game
from objects import Bullet, Asteroid
import _menu
import graphics

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

    graphics.draw_stars(delta_time)

    for object in graphics.get_entities_to_draw():
        object.draw(WIN, red_ship.position)

    if delta_time:
        label = font.render(f"Angle: {round(red_ship.rotation / math.pi * 180 - 180) % 360 - 180}", True, (255, 255, 255))
        WIN.blit(label, (200, 0))

        label = font.render(f"Speed: {round(red_ship.velocity.magnitude())}", True, (255, 255, 255))
        WIN.blit(label, (200, 50))

        label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 0))
        
        label = font.render(f"Health: {round(red_ship.health)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 50))

        label = font.render(f"Boost Amount: {round(red_ship.boost_amount)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 100))

        font2 = pygame.font.SysFont("comicsans", 50)
        label = font2.render(f"SCORE: {game.SCORE}", True, (255, 10, 10))
        WIN.blit(label, (WIDTH/2 - label.get_width()/2, 100))

        graphics.draw_chunks()


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
        red_ship.boost(delta_time)
    else:
        red_ship.max_speed = 500 # Reset max speed so that the high velocity is not maintained after a boost

        if red_ship.boost_amount < 10: # If the boost amount is not at the maximum, add boost over time

            red_ship.boost_amount += (red_ship.boost_change * delta_time) / 2
        else:
            red_ship.boost_amount = 10 # Caps the boost amount to a specific max value

    if pygame.mouse.get_pressed()[0]:
        red_ship.shoot()

    if keys_pressed[pygame.K_UP]:
        game.ZOOM = min(game.ZOOM + game.ZOOM * delta_time, 20) # MAX ZOOM is 20x normal

    if keys_pressed[pygame.K_DOWN]:
        game.ZOOM = max(game.ZOOM - game.ZOOM * delta_time, (WIDTH)/(2*(CHUNK_DISTANCE)*CHUNK_SIZE)) # MIN ZOOM is automatic, based on chunk loading distance


    # Mouse
    mouse_position = pygame.mouse.get_pos()
    angle = math.atan2(-mouse_position[1]+CENTRE_POINT.y, mouse_position[0]-CENTRE_POINT.x) - math.pi/2
    red_ship.set_rotation(angle)


    CHUNKS.update(red_ship)

def scroll(scroll_amount: int):

    if scroll_amount > 0:
        game.ZOOM = min(game.ZOOM + game.ZOOM * scroll_amount * 0.2, 20)

    else:
        game.ZOOM = max(game.ZOOM + game.ZOOM * scroll_amount * 0.2, (WIDTH)/(2*(CHUNK_DISTANCE)*CHUNK_SIZE))


def update_objects(delta_time):
    """Updates all objects, e.g. adjusts positions based on velocity"""
    
    # Loop until every object has been updated e.g. moved
    # Entity set has to be copied as entity might be deleted from the actual set
    for object in filter(lambda object: type(object) != Bullet and type(object) != Asteroid, CHUNKS.entities.copy()):
        
        # Update object e.g. move it
        object.update(delta_time)

    # Bullets are updated after everything else to ensure that the ships they may hit have been updated (and moved to the right position)
    for object in filter(lambda object: type(object) == Bullet or type(object) == Asteroid, CHUNKS.entities.copy()):
        object.update(delta_time)


def main(menu: "_menu.Menu"):
    """Main game loop"""

    delta_time = 1

    global CHUNKS
    CHUNKS = init_chunks()

    global red_ship
    red_ship = add_player()

    game.SCORE = 0

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

                elif event.type == pygame.MOUSEWHEEL:
                    scroll(event.y)

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