from objects import Vector, Ship
from objects import random_vector
import images
import game
import random
import math


class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, fire_rate=1, state=0, mother_ship=None, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, image)
        self.state = state
        self.mother_ship = mother_ship
        self.patrol_point = random_vector(random.randint(500, 1000)) + self.position

    def update(self, delta_time):
        super().update(delta_time)

        if self.distance_to(game.red_ship) < 600:
            self.attack_state(delta_time)
        else:
            self.patrol_state(delta_time)


        # if self.distance_to(game.red_ship) < 200:
        #     self.accelerate_in_direction(game.red_ship.position, -500 * delta_time)
        
    def patrol_state(self, delta_time):
        self.max_speed = 200
        
        target_position = self.patrol_point
        target_distance = (target_position - self.position).magnitude()

        mother_ship_distance = (self.mother_ship.position - self.position).magnitude()

        if target_distance < 50 or mother_ship_distance > 400:   # Check if the enemy has reached the patrol point
            #if (self.mother_ship.position - target_position).magnitude() > 400:
            self.patrol_point = random_vector(random.randint(200, 400)) + self.mother_ship.position
            target_position = self.patrol_point
        
        self.accelerate_to_point(target_position, 250 * delta_time)
        self.set_rotation(self.position.get_angle(target_position))
    
    def attack_state(self, delta_time):
        self.max_speed = 300
        self.set_rotation(self.position.get_angle(game.red_ship.position))
        self.shoot()
        self.accelerate_in_direction(game.red_ship.position, 250 * delta_time)


class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, fire_rate=1, state=0, enemy_list=[], image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, state, self, image)
        self.enemy_list = enemy_list
        enemy_spawn_number = random.randint(3, 6)

        for _ in range(enemy_spawn_number):

            random_position = Vector(random.randint(self.position.x, self.position.x + game.CHUNK_SIZE - 1),
            random.randint(self.position.y, self.position.y + game.CHUNK_SIZE - 1))

            enemy = Enemy_Ship(random_position, Vector(0, 0), mother_ship=self)
            
            game.CHUNKS.add_entity(enemy)
        
    def patrol_state(self, delta_time):
        pass

