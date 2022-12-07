from objects import Vector, Ship
import images
import particles
import math


class Player_Ship(Ship):
    def __init__(

        self,
        position: Vector, velocity: Vector,
        max_speed=500,
        rotation=0, max_rotation_speed=3,
        fire_rate=10, health=20,
        boost_amount=10, boost_change=5,
        image=images.RED_SHIP

        ) -> None:

        super().__init__(position, velocity, max_speed, rotation, fire_rate, health, image)

        self.max_rotation_speed = max_rotation_speed
        self.boost_amount = boost_amount
        self.boost_change = boost_change

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_rotation(self, acceleration):
        self.rotation_speed += acceleration
        self.rotation_speed.clamp(self.max_rotation_speed)

    def move_forward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, -700))

    def move_backward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, 500))

    def move_left(self, delta_time):
        self.accelerate_relative(delta_time * Vector(-300, 0))

    def move_right(self, delta_time):
        self.accelerate_relative(delta_time * Vector(300, 0))

    def boost(self, delta_time):
        if self.boost_amount > 0: # Makes sure that you have boost to boost
            self.max_speed = 1000
            self.accelerate_relative(delta_time * Vector(0, -1000))
            self.boost_amount -= self.boost_change * delta_time # Decrease the amount of boost you have while boosting over time

            boost_distance = 20
            boost_position = Vector(boost_distance * math.sin(self.rotation), boost_distance * math.cos(self.rotation))

            particles.ParticleSystem(self.position + boost_position, start_size=6, end_size=0, colour=(20, 100, 255), duration=None, lifetime=0.5, frequency=1)
        else:
            self.max_speed = 500 # Resets max speed once you run out of boost

    def turn_left(self, delta_time):
        self.accelerate_rotation(delta_time * 8)

    def turn_right(self, delta_time):
        self.accelerate_rotation(delta_time * -8)

    def destroy(self):
        super().destroy()
        particles.ParticleSystem(self.position, start_size=3, end_size=0, colour=(255, 0, 0), duration=0.2, lifetime=0.5, frequency=500, speed=500, speed_variance=100)