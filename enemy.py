from objects import Vector, Ship
from objects import random_vector
import images
import game
import random
import pygame

class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, fire_rate=1, state=0, mother_ship=None, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, image)
        self.state = state
        self.mother_ship = mother_ship
        self.patrol_point = random_vector(random.randint(100, 400)) + self.mother_ship.position

    def update(self, delta_time):
        super().update(delta_time)

        if self.distance_to(game.red_ship) < 600:
            self.attack_state(delta_time)
        else:
            self.patrol_state(delta_time)

    # DEBUG DRAW PATROL POINTS

    # def draw(self, win: pygame.Surface, focus_point):
    #     super().draw(win, focus_point)
    #     pygame.draw.circle(game.WIN, (255, 0, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        
    def patrol_state(self, delta_time):
        self.max_speed = 150
        
        target_position = self.patrol_point
        target_distance = (target_position - self.position).magnitude()

        target_to_mothership_distance = (target_position - self.mother_ship.position).magnitude()

        if target_distance < 50 or target_to_mothership_distance > 500:   # Check if the enemy has reached the patrol point
            self.patrol_point = random_vector(random.randint(100, 400)) + self.mother_ship.position
            target_position = self.patrol_point
        
        #self.accelerate_to_point(target_position, 600 * delta_time, 1000 * delta_time)
        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle(target_position))
    
    def attack_state(self, delta_time):
        self.max_speed = 300
        self.set_rotation(self.position.get_angle(game.red_ship.position))
        self.shoot()
        self.accelerate_in_direction(game.red_ship.position, 400 * delta_time)


class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, fire_rate=1, state=0, enemy_list=None, image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, state, self, image)
        if enemy_list is None:
            enemy_list = []
        self.enemy_list = enemy_list

        self.patrol_point = random_vector(random.randint(1000, 1500)) + self.position

        enemy_spawn_number = random.randint(3, 6)

        for _ in range(enemy_spawn_number):

            random_position = Vector(random.randint(self.position.x, self.position.x + game.CHUNK_SIZE - 1),
            random.randint(self.position.y, self.position.y + game.CHUNK_SIZE - 1))

            enemy = Enemy_Ship(random_position, Vector(0, 0), mother_ship=self)
            
            game.CHUNKS.add_entity(enemy)

    # DEBUG DRAW PATROL POINTS

    # def draw(self, win: pygame.Surface, focus_point):
    #     super().draw(win, focus_point)
    #     pygame.draw.circle(game.WIN, (0, 255, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        
    def patrol_state(self, delta_time):
        self.max_speed = 50

        target_position = self.patrol_point
        distance = (target_position - self.position).magnitude()

        if distance < 50:   # Check if the enemy has reached the patrol point
            self.patrol_point = random_vector(random.randint(1000, 1500)) + self.position
            target_position = self.patrol_point

        #self.accelerate_to_point(target_position, 200 * delta_time, 500 * delta_time)
        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle(target_position))

