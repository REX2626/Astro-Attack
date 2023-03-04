import pygame

from game import *
import game
from entities import Bullet, Asteroid
from player import add_player
from weapons import PlayerGun, PlayerGatlingGun, PlayerSniper, Laser
from particles import ParticleSystem
import ui
import menu
import graphics
import math
from time import perf_counter

pygame.display.set_caption("Astro Attack")



def update_playing_screen_size():
    """Updates live objects positions"""

    "Get objects position on screen by ratio e.g. 20% of the screen"

    game.update_screen_size()

    graphics.WIDTH = game.WIDTH
    graphics.HEIGHT = game.HEIGHT

    "Set the x and y of objects based on new width and height, with ratios"

    "Clip the coords of any object out of bounds"


rand_x = 0
rand_y = 0
delay = 0
def screen_shake(delta_time):
    global delay, rand_x, rand_y
    width, height = pygame.display.get_window_size()

    delay -= delta_time
    if delay < 0:
        delay = 0.1

        if abs(math.sin(perf_counter()*2*rand_x)) < 0.03:
            rand_x = random.random() * 20

        if abs(math.sin(perf_counter()*2*rand_y)) < 0.03:
            rand_y = random.random() * 20

    game.CENTRE_POINT.x = width /2 + math.sin(perf_counter()*rand_x) * math.log2(game.SCREEN_SHAKE+1) * 5
    game.CENTRE_POINT.y = height/2 + math.sin(perf_counter()*rand_y) * math.log2(game.SCREEN_SHAKE+1) * 5

    game.SCREEN_SHAKE = max(0, game.SCREEN_SHAKE - delta_time * (game.SCREEN_SHAKE + 7))


def draw_window(delta_time):
    """Draw window"""
    WIN.fill(BLACK)

    screen_shake(delta_time)

    graphics.draw_stars()


    for object in graphics.get_entities_to_draw():
        object.draw(WIN, player.position)

    if game.DEBUG_SCREEN:
        graphics.draw_chunks()

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
        player.max_speed = game.MAX_PLAYER_SPEED # Reset max speed so that the high velocity is not maintained after a boost
        player.boost_particles1.active = False
        player.boost_particles2.active = False

        # Increase player.boost_amount
        player.boost_amount = min(game.MAX_BOOST_AMOUNT,
                                    player.boost_amount + (player.boost_change * delta_time) / 2)
                                    # Caps the boost amount to a specific max value

    if pygame.mouse.get_pressed()[0]: # left click
        player.shoot()

    if player.cursor_highlighted and pygame.mouse.get_pressed()[2]: # right click
        player.tracked_enemy = player.aiming_enemy

    if keys_pressed[pygame.K_UP]:
        game.ZOOM = min(game.ZOOM + game.ZOOM * delta_time, 20) # MAX ZOOM is 20x normal

    if keys_pressed[pygame.K_DOWN]:
        game.ZOOM = max(game.ZOOM - game.ZOOM * delta_time, (game.WIDTH)/(2*(game.LOAD_DISTANCE)*CHUNK_SIZE)) # MIN ZOOM is automatic, based on chunk loading distance

    if keys_pressed[pygame.K_1]:
        game.player.weapon = PlayerGun(game.player)
        ui.weapon_selected = 0

    if keys_pressed[pygame.K_2]:
        game.player.weapon = PlayerGatlingGun(game.player)
        ui.weapon_selected = 1

    if keys_pressed[pygame.K_3]:
        game.player.weapon = PlayerSniper(game.player)
        ui.weapon_selected = 2

    if keys_pressed[pygame.K_4]:
        game.player.weapon = Laser(game.player)
        ui.weapon_selected = 3

    if keys_pressed[pygame.K_n]:
        game.SCREEN_SHAKE += 10*delta_time


    # Mouse
    mouse_position = pygame.mouse.get_pos()
    angle = math.atan2(-mouse_position[1]+game.CENTRE_POINT.y, mouse_position[0]-game.CENTRE_POINT.x) - math.pi/2
    player.set_rotation(angle)
    game.LAST_PLAYER_POS = player.position


def scroll(scroll_amount: int):

    if scroll_amount > 0:
        game.ZOOM = min(game.ZOOM + game.ZOOM * scroll_amount * 0.2, game.MAX_ZOOM)

    else:
        game.ZOOM = max(game.ZOOM + game.ZOOM * scroll_amount * 0.2, game.CURRENT_MIN_ZOOM) # automatic min zoom: (game.WIDTH)/(2*(game.LOAD_DISTANCE)*CHUNK_SIZE)


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

    # Unload all chunks and load chunks around player
    CHUNKS.update(player)
        
    # Update particles
    for particle_system in filter(lambda object: type(object) == ParticleSystem, CHUNKS.entities.copy()):
        particle_system.update(delta_time)


def main():
    """Main game loop"""

    delta_time = 1

    global CHUNKS
    CHUNKS = init_chunks()

    global player
    player = add_player()
    player.open_station_menu = lambda: menu.Menu.station()

    if game.SCORE > game.HIGHSCORE:
        game.HIGHSCORE = game.SCORE
    game.SCORE = 0
    game.SCRAP_COUNT = 0

    menu.Menu.running = False

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

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_e:

                start = perf_counter()

                if player.station_highlighted:
                    menu.Menu.station()

                else:
                    menu.Menu.systems()

                time1 = perf_counter() - start + time1

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:

                # Fix delta_time so that time paused is not included
                start = perf_counter()

                # Darken the background when paused
                surf = pygame.Surface((game.WIN.get_size()), pygame.SRCALPHA)
                pygame.draw.rect(surf, (0, 0, 0, 120), (0, 0, game.WIDTH, game.HEIGHT))
                game.WIN.blit(surf, (0, 0))

                menu.Menu.pause()

                # Correct time1
                time1 = perf_counter() - start + time1

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_F3:
                if game.DEBUG_SCREEN:
                    game.DEBUG_SCREEN = False
                else:
                    game.DEBUG_SCREEN = True

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_SLASH:
                # Fix delta_time so that time paused is not included
                start = perf_counter()

                game.CONSOLE_SCREEN = True

                # Runs main console loop which pauses the game
                ui.canvas.console_panel.check_for_inputs()

                # Runs all of the commands written after the console is closed since we want the commands to run in this main loop
                ui.canvas.console_panel.run_commands()

                # Correct time1
                time1 = perf_counter() - start + time1
                
        time2 = perf_counter()
        delta_time = time2 - time1


def main_menu():
    """Initializes Menu"""
    menu.Menu()


if __name__ == "__main__":
    main_menu()