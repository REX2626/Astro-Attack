from time import perf_counter
import pygame
import sys
from objects import Vector, Object, MoveableObject, Player_Ship
import _menu
import random
import math

pygame.init()

WIN = pygame.display.set_mode(flags=pygame.FULLSCREEN+pygame.RESIZABLE)
pygame.display.set_caption("Astro Attack")
WIDTH, HEIGHT = pygame.display.get_window_size()
FULLSCREEN = True
FULLSCREEN_SIZE = WIDTH, HEIGHT
WINDOW_SIZE = WIDTH * 0.8, HEIGHT * 0.8
SIZE_LINK = True

WHITE = (255, 255, 255)
LIGHT_GREY = (120, 120, 120)
MEDIUM_GREY = (60, 60, 60)
DARK_GREY = (30, 30, 30)
BLACK = (0, 0, 0)


def update_screen_size():
    """Updates objects size and position with new screen size"""
    "Adjust any constants"

    if SIZE_LINK:
        "Adjust objects size"


def update_playing_screen_size(menu: "_menu.Menu"):
    """Updates live objects positions"""

    global WIDTH, HEIGHT

    "Get objects position on screen by ratio e.g. 20% of the screen"

    WIDTH, HEIGHT = pygame.display.get_window_size()
    menu.resize()

    "Set the x and y of objects based on new width and height, with ratios"

    "Clip the coords of any object out of bounds"


font = pygame.font.SysFont("comicsans", 30)
def draw_window(objects: list[Object], delta_time):
    """Draw window"""
    WIN.fill(BLACK)

    # centre_point is the position of red_ship on screen
    centre_point = Vector(WIDTH/2, HEIGHT/2)
    for object in objects:
        object.draw(WIN, red_ship.position, centre_point)

    if delta_time:
        label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 0))

        label = font.render(f"Angle: {round(red_ship.rotation / math.pi * 180)}", True, (255, 255, 255))
        WIN.blit(label, (300, 0))

    pygame.display.update()


def handle_player_movement(keys_pressed, objects, delta_time):

    """Adjust player velocity depnding on input. NOTE: Not for changing position"""
    # Example:
    if keys_pressed[pygame.K_w]:
        move_up(delta_time)

    if keys_pressed[pygame.K_s]:
        move_down(delta_time)

    if keys_pressed[pygame.K_a]:
        move_left(delta_time)

    if keys_pressed[pygame.K_d]:
        move_right(delta_time)

    if keys_pressed[pygame.K_LEFT]:
        turn_left(delta_time)

    if keys_pressed[pygame.K_RIGHT]:
        turn_right(delta_time)
    


def move_up(delta_time):
    red_ship.accelerate_relative(delta_time * Vector(0, -2000))

def move_down(delta_time):
    red_ship.accelerate_relative(delta_time * Vector(0, 2000))

def move_left(delta_time):
    red_ship.accelerate_relative(delta_time * Vector(-2000, 0))

def move_right(delta_time):
    red_ship.accelerate_relative(delta_time * Vector(2000, 0))

def turn_left(delta_time):
    red_ship.set_rotation(red_ship.rotation + 1 * delta_time)

def turn_right(delta_time):
    red_ship.set_rotation(red_ship.rotation - 1 * delta_time)


def handle_movement(objects: list[MoveableObject], static_objects: list[Object], delta_time):
    """Handles movement for all objects, adjusts positions based on velocity"""
    
    # Loop until every object has moved for the given time
    for object in objects:
        object.update_pos(delta_time)


def add_objects():

    objects = []

    # Red Player Ship
    global red_ship
    red_ship = Player_Ship(position=(300, 300), velocity=(0, 0), size=(200, 200), max_speed=500, image="./assets/red_ship.png")
    objects.append(red_ship)

    return objects


def quit():
    """Stops the program"""
    pygame.quit()
    sys.exit(0)


def main(menu: "_menu.Menu"):
    """Main game loop"""
    delta_time = 0

    static_objects = []

    objects = add_objects()
    
    running = True
    paused = False
    while running:
        while not paused:
            time1 = perf_counter()

            keys_pressed = pygame.key.get_pressed()

            handle_player_movement(keys_pressed, objects, delta_time)
            handle_movement(objects, static_objects, delta_time)
            objects.append(MoveableObject(
                position=(random.randint(round(red_ship.position.x)-500, round(red_ship.position.x)+500), random.randint(round(red_ship.position.y)-500, round(red_ship.position.y)+500)),
                velocity=(0, 0),
                size=(50, 50),
                image="assets/GABE.png"))

            draw_window(objects, delta_time)

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
                draw_window(objects, delta_time)
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