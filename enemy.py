from objects import Vector, Ship
import images
import game
import random
import math



class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, scale=1, rotation=0, fire_rate=1, state=0, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, scale, rotation, fire_rate, image)
        self.state = state
        self.patrol_point = self.choose_point(random.randint(500, 1000)) + self.position

    def update(self, delta_time):
        super().update(delta_time)

        if self.distance_to(game.red_ship) < 750:
            self.attack_state(delta_time)
        else:
            self.patrol_state(delta_time)


        # if self.distance_to(game.red_ship) < 200:
        #     self.accelerate_in_direction(game.red_ship.position, -500 * delta_time)
        
    def patrol_state(self, delta_time):
        self.max_speed = 200
        
        target_position = self.patrol_point
        distance = (target_position - self.position).magnitude()

        if distance < 50:   # Check if the enemy has reached the patrol point
            self.patrol_point = self.choose_point(random.randint(1000, 1500)) + self.position
            target_position = self.patrol_point

        
        self.accelerate_to_point(target_position, 500 * delta_time)
        self.set_rotation(self.position.get_angle(target_position))
    
    def attack_state(self, delta_time):
        self.max_speed = 500
        self.set_rotation(self.position.get_angle(game.red_ship.position))
        self.shoot()
        self.accelerate_in_direction(game.red_ship.position, 500 * delta_time)
    
    def choose_point(self, distance):
        random_direction = random.random() * 2 * math.pi    # Get random direction

        target_position = Vector(distance * math.cos(random_direction), distance * math.sin(random_direction))  # Get random position a certain distance from the enemy

        return target_position