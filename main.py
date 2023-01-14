import pygame                

from game import *
import game
from entities import Bullet, Asteroid
from player import add_player
import ui
import menu
import graphics

import math
from time import perf_counter

pygame.display.set_caption("Astro Attack")



def update_playing_screen_size():
    """Updates live objects positions"""

    global WIDTH, HEIGHT

    "Get objects position on screen by ratio e.g. 20% of the screen"

    WIDTH, HEIGHT = pygame.display.get_window_size()
    menu.Menu.resize()

    "Set the x and y of objects based on new width and height, with ratios"

    "Clip the coords of any object out of bounds"


def draw_window(delta_time):
    """Draw window"""
    WIN.fill(BLACK)

    graphics.draw_stars()


    for object in graphics.get_entities_to_draw():
        object.draw(WIN, player.position)


    #graphics.draw_chunks()

    ui.draw(delta_time)

    pygame.display.update()


def handle_player_input(keys_pressed, delta_time):

    """Adjust player velocity depnding on input. NOTE: Not for changing position"""
    # Example:
    if keys_pressed[pygame.K_w]:
        player.move_forward(delta_time)

    if keys_pressed[pygame.K_s]:
        player.move_backward(delta_time)

    if keys_pressed[pygame.K_a]:
        player.move_left(delta_time)

    if keys_pressed[pygame.K_d]:
        player.move_right(delta_time)

    if keys_pressed[pygame.K_LEFT]:
        player.turn_left(delta_time)

    if keys_pressed[pygame.K_RIGHT]:
        player.turn_right(delta_time)
    
    if keys_pressed[pygame.K_SPACE]:
        player.boost(delta_time)
    else:
        player.max_speed = 500 # Reset max speed so that the high velocity is not maintained after a boost

        # Increase player.boost_amount
        player.boost_amount = min(player.max_boost_amount,
                                    player.boost_amount + (player.boost_change * delta_time) / 2)
                                    # Caps the boost amount to a specific max value

    if pygame.mouse.get_pressed()[0]: # left click
        player.shoot()

    if player.cursor_highlighted and pygame.mouse.get_pressed()[2]: # right click
        player.is_tracking_enemy = True
        player.current_enemy_tracking = player.current_enemy_aiming

    if keys_pressed[pygame.K_UP]:
        game.ZOOM = min(game.ZOOM + game.ZOOM * delta_time, 20) # MAX ZOOM is 20x normal

    if keys_pressed[pygame.K_DOWN]:
        game.ZOOM = max(game.ZOOM - game.ZOOM * delta_time, (WIDTH)/(2*(game.LOAD_DISTANCE)*CHUNK_SIZE)) # MIN ZOOM is automatic, based on chunk loading distance


    # Mouse
    mouse_position = pygame.mouse.get_pos()
    angle = math.atan2(-mouse_position[1]+CENTRE_POINT.y, mouse_position[0]-CENTRE_POINT.x) - math.pi/2
    player.set_rotation(angle)
    game.LAST_PLAYER_POS = player.position


    CHUNKS.update(player)


def scroll(scroll_amount: int):

    if scroll_amount > 0:
        game.ZOOM = min(game.ZOOM + game.ZOOM * scroll_amount * 0.2, 20)

    else:
        game.ZOOM = max(game.ZOOM + game.ZOOM * scroll_amount * 0.2, (WIDTH)/(2*(game.LOAD_DISTANCE)*CHUNK_SIZE))


def update_objects(delta_time):
    """Updates all objects, e.g. adjusts positions based on velocity"""
    
    # Loop until every object has been updated e.g. moved
    # Entity set has to be copied as entity might be deleted from the actual set
    for object in filter(lambda object: type(object) != Bullet and type(object) != Asteroid, CHUNKS.entities.copy()):
        
        # Update object e.g. move it
        object.update(delta_time)

    # Bullets are updated after everything else to ensure that the ships they may hit have been updated (and moved to the right position)
    for object in filter(lambda object: type(object) == Asteroid, CHUNKS.entities.copy()):
        object.update(delta_time)

    for object in filter(lambda object: type(object) == Bullet, CHUNKS.entities.copy()):
        object.update(delta_time)


def main():
    """Main game loop"""

    delta_time = 1

    global CHUNKS
    CHUNKS = init_chunks()

    global player
    player = add_player()

    if game.SCORE > game.HIGHSCORE:
        game.HIGHSCORE = game.SCORE
    game.SCORE = 0

    running = True
    while running:
        time1 = perf_counter()

        keys_pressed = pygame.key.get_pressed()

        handle_player_input(keys_pressed, delta_time)
        update_objects(delta_time)

        draw_window(delta_time)

        if player.health <= 0:
            menu.Menu.death_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.MOUSEWHEEL:
                scroll(event.y)

            elif event.type == pygame.VIDEORESIZE:
                update_playing_screen_size()

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                
                # Darken the background when paused
                surf = pygame.Surface((game.WIN.get_size()), pygame.SRCALPHA)
                pygame.draw.rect(surf, (0, 0, 0, 120), (0, 0, game.WIDTH, game.HEIGHT))
                game.WIN.blit(surf, (0, 0))

                menu.Menu.pause()
                
        time2 = perf_counter()
        delta_time = time2 - time1


def main_menu():
    """Initializes Menu"""
    menu.Menu()


if __name__ == "__main__":
    main_menu()