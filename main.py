from time import perf_counter
import pygame
import sys
import decimal
from objects import Object, MoveableObject
import _menu

pygame.init()

WIN = pygame.display.set_mode((1600, 1000), flags=pygame.RESIZABLE)
pygame.display.set_caption("GamingX Framework")
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

    for object in objects:
        object.draw(WIN)

    if delta_time:
        label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
        WIN.blit(label, (WIDTH - 300, 0))

    pygame.display.update()


def handle_player_movement(keys_pressed, objects):
    """Adjust player velocity depnding on input. NOTE: Not for changing position"""
    # Example:
    if keys_pressed[pygame.K_UP]:
        "move_up()"


def handle_movement(objects: list[MoveableObject], static_objects: list[Object], delta_time):
    """Handles movement for all objects, adjusts positions based on velocity"""
    
    # Loop until every object has moved for the given time
    dt = decimal.Decimal(delta_time)
    while dt:
        # Find two objects closest to collision
        closest_time = dt
        closest_objects_x: dict[MoveableObject, list[MoveableObject | Object]] = {}
        closest_objects_y: dict[MoveableObject, list[MoveableObject | Object]] = {}

        # For each object, find it's closest collision to every object
        for idx, object1 in enumerate(objects):
            for object2 in objects[idx:]:
                
                # Collision for x axis
                dist_between = min(object2.x - (object1.x + object1.width), (object2.x + object2.width) - object1.x, key=abs) # Closest distance between two objects, adjusted for width
                rel_vel = object1.vx - object2.vx # Relative velocity between two objects
                if rel_vel != 0 and dist_between != 0: # Two objects will never collide if moving at same velocity
                    coll_time = dist_between / rel_vel # Time until the two objects collide

                    if coll_time >= 0 and overlapping_y(object1, object2, coll_time): # Check that two objects will collide and that the two objects are at overlapping x width
                        
                        if coll_time < closest_time:
                            closest_time = coll_time
                            closest_objects_x = {object1: [object2], object2: [object1]}

                        elif coll_time == closest_time: # Check if colliding at the same time

                            # Add objects to collision lists
                            if object1 not in closest_objects_x:
                                closest_objects_x[object1] = []
                            closest_objects_x[object1].append(object2)

                            if object2 not in closest_objects_x:
                                closest_objects_x[object2] = []
                            closest_objects_x[object2].append(object1)

                # Same again for y axis
                dist_between = min(object2.y - (object1.y + object1.height), (object2.y + object2.height) - object1.y, key=abs) # Closest distance between two objects, adjusted for height
                rel_vel = object1.vy - object2.vy # Relative velocity between two objects
                if rel_vel != 0 and dist_between != 0: # Two objects will never collide if moving at same velocity
                    coll_time = dist_between / rel_vel # Time until the two objects collide

                    if coll_time >= 0 and overlapping_x(object1, object2, coll_time): # Check that two objects will collide and that two objects are at overlapping y height
                        
                        if coll_time < closest_time:
                            closest_time = coll_time
                            closest_objects_y = {object1: [object2], object2: [object1]}

                        elif coll_time == closest_time: # Check if colliding at the same time

                            # Add objects to collision lists
                            if object1 not in closest_objects_y:
                                closest_objects_y[object1] = []
                            closest_objects_y[object1].append(object2)

                            if object2 not in closest_objects_y:
                                closest_objects_y[object2] = []
                            closest_objects_y[object2].append(object1)

            # Check for any closer collisions with immoveable_objects
            for object2 in static_objects:

                dist_between = min(object2.x - (object1.x + object1.width), (object2.x + object2.width) - object1.x, key=abs) # Closest distance between two objects, adjusted for width
                if object1.vx != 0 and dist_between != 0: # If touching, Moveable_Object will be moving away
                    coll_time = dist_between / object1.vx # Time until the two objects collide

                    if coll_time >= 0 and overlapping_y(object1, object2, coll_time): # Check that two objects will collide and that the two objects are at overlapping x width
                        
                        if coll_time < closest_time:
                            closest_time = coll_time
                            closest_objects_x = {object1: [object2], object2: [object1]}

                        elif coll_time == closest_time: # Check if colliding at the same time

                            # Add objects to collision lists
                            if object1 not in closest_objects_x:
                                closest_objects_x[object1] = []
                            closest_objects_x[object1].append(object2)

                            if object2 not in closest_objects_x:
                                closest_objects_x[object2] = []
                            closest_objects_x[object2].append(object1)

                # Same again for y axis
                dist_between = min(object2.y - (object1.y + object1.height), (object2.y + object2.height) - object1.y, key=abs) # Closest distance between two objects, adjusted for height
                if object1.vy != 0 and dist_between != 0: # If touching, Moveable_Object will be moving away
                    coll_time = dist_between / object1.vy # Time until the two objects collide

                    if coll_time >= 0 and overlapping_x(object1, object2, coll_time): # Check that two objects will collide and that the two objects are at overlapping y height
                        
                        if coll_time < closest_time:
                            closest_time = coll_time
                            closest_objects_y = {object1: [object2], object2: [object1]}

                        elif coll_time == closest_time: # Check if colliding at the same time

                            # Add objects to collision lists
                            if object1 not in closest_objects_y:
                                closest_objects_y[object1] = []
                            closest_objects_y[object1].append(object2)

                            if object2 not in closest_objects_y:
                                closest_objects_y[object2] = []
                            closest_objects_y[object2].append(object1)


        if closest_objects_x or closest_objects_y: # Check for any collisions

            # Move all other objects to same point in time that collision occurs
            for object1 in objects:

                object1.x += closest_time * object1.vx
                object1.y += closest_time * object1.vy
                object1.x = object1.x.quantize(decimal.Decimal("1.0000000000"))
                object1.y = object1.y.quantize(decimal.Decimal("1.0000000000"))


            # Group closest_objects into groups of objects that are colliding with each other

            x_objects: list[list[MoveableObject]] = []
            y_objects: list[list[MoveableObject]] = []

            for object1 in closest_objects_x:
                if closest_objects_x[object1] and not any(object1 in grouped_list for grouped_list in x_objects):
                    x_objects.append(group_objects_x(object1, closest_objects_x, []))

            for object1 in closest_objects_y:
                if closest_objects_y[object1] and not any(object1 in grouped_list for grouped_list in y_objects):
                    y_objects.append(group_objects_y(object1, closest_objects_y, []))


            # Set the velocities of each collision group by reversing NOTE: A bit cheaty, should work but not accurate, need to average in some cases

            for collision_group in x_objects:
                if any(type(object1) == Object for object1 in collision_group):
                    for object1 in filter(lambda obj: type(obj) == MoveableObject, collision_group):
                        object1.vx *= -1
                else:
                    collision_group.sort(key=lambda object: object.x)
                    velocities = [object1.vx for object1 in reversed(collision_group)]
                    for idx, object1 in enumerate(collision_group):
                        object1.vx = velocities[idx]

            for collision_group in y_objects:
                if any(type(object1) == Object for object1 in collision_group):
                    for object1 in filter(lambda obj: type(obj) == MoveableObject, collision_group):
                        object1.vy *= -1
                else:
                    collision_group.sort(key=lambda object: object.vy) # Ensures that objects with a larger vy will be prioritized when sorting with the same y postion
                    collision_group.sort(key=lambda object: object.y)
                    velocities = [object1.vy for object1 in reversed(collision_group)]
                    for idx, object1 in enumerate(collision_group):
                        object1.vy = velocities[idx]

                
            # Subtract closest_time from dt as the game time has advance by closest_time seconds
            dt -= closest_time

        # If no collision
        else:
            # Move objects the rest of the way
            for object in objects:
                object.x += dt * object.vx
                object.y += dt * object.vy
                object.x = object.x.quantize(decimal.Decimal("1.0000000000"))
                object.y = object.y.quantize(decimal.Decimal("1.0000000000"))
            break


def overlapping_y(object1: MoveableObject, object2: MoveableObject | Object, coll_time: float = 0):
    """Check if two objects are overlapping in the y axis
    \nAdjusts y coords to collision positions"""
    y1 = object1.y + coll_time * object1.vy
    y2 = object2.y + coll_time * object2.vy if type(object2) == MoveableObject else object2.y
    return ((y2 <= y1 <= y2 + object2.height) or # top object1 overlaps object2
            (y2 <= y1 + object1.height <= y2) or # bottom object1 overlaps object 2
            (y1 <= y2 <= y1 + object1.height) or # top object2 overlaps object1
            (y1 <= y2 + object2.height <= y1)) # bottom object2 overlaps object 1


def overlapping_x(object1: MoveableObject, object2: MoveableObject | Object, coll_time: float = 0):
    """Check if two objects are overlapping in the x axis
    \nAdjusts x coords to collision positions"""
    x1 = object1.x + coll_time * object1.vx
    x2 = object2.x + coll_time * object2.vx if type(object2) == MoveableObject else object2.x
    return ((x2 <= x1 <= x2 + object2.width) or # left object1 overlaps object2
            (x2 <= x1 + object1.width <= x2) or # right object1 overlaps object 2
            (x1 <= x2 <= x1 + object1.width) or # left object2 overlaps object1
            (x1 <= x2 + object2.width <= x1)) # right object2 overlaps object 1


def group_objects_x(object1, closest_objects: list, grouped_list: list):

    # Loop through all colliding objects than recurse through all of theirs
    for object2 in closest_objects[object1]:
        if object2 not in grouped_list:
            grouped_list.append(object2)
            grouped_list = group_objects_x(object2, closest_objects, grouped_list)

    return grouped_list


def group_objects_y(object1, closest_objects: list, grouped_list: list):

    # Loop through all colliding objects than recurse through all of theirs
    for object2 in closest_objects[object1]:
        if object2 not in grouped_list:
            grouped_list.append(object2)
            grouped_list = group_objects_y(object2, closest_objects, grouped_list)

    return grouped_list


def quit():
    """Stops the program"""
    pygame.quit()
    sys.exit(0)


def main(menu: "_menu.Menu"):
    """Main game loop"""
    delta_time = 0

    objects = []
    static_objects = []
    static_objects.append(Object(0, 0, 1, HEIGHT, None))
    static_objects.append(Object(WIDTH - 1, 0, 1, HEIGHT, None))
    static_objects.append(Object(0, 0, WIDTH, 1, None))
    static_objects.append(Object(0, HEIGHT - 1, WIDTH, 1, None))
    from random import randint
    for _ in range(50):
        while True:
            x, y = randint(1, WIDTH - 101), randint(1, HEIGHT - 101)
            overlapping = False
            for obj in objects:
                if overlapping_x(MoveableObject(x, y, 0, 0, 100, 100, None), obj) and overlapping_y(MoveableObject(x, y, 0, 0, 100, 100, None), obj):
                    overlapping = True
            if not overlapping:
                break
        objects.append(MoveableObject(x, y, randint(-200, 200), randint(-200, 200), 100, 100, pygame.transform.scale(pygame.image.load("./assets/example.png"), (100, 100)).convert()))

    running = True
    paused = False
    while running:
        while not paused:
            time1 = perf_counter()

            keys_pressed = pygame.key.get_pressed()

            handle_player_movement(keys_pressed, objects)
            #print("\nSTARTING COLLISION")
            handle_movement(objects, static_objects, delta_time)
            for object1 in objects:
                for object2 in objects:
                    if object1 != object2 and overlapping_x(object1, object2) and overlapping_y(object1, object2):
                        print("\nERROR")
                        print(f"Velocities: {object1.vx=} {object2.vx=}")
                        print(f"Velocities: {object1.vy=} {object2.vy=}")
                        print(f"Coordinates: {object1.x=} {object2.x=}")
                        print(f"Coordinates: {object1.y=} {object2.y=}")
                        print(f"Object1: {object1}, Object2: {object2}")
                        print("Delta time:", delta_time)
                        paused = True

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