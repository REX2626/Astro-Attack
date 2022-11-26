from objects import Vector, Vector1D, Ship, Bullet
import images
import game



class Player_Ship(Ship):
    def __init__(

        self,
        position: Vector, velocity: Vector,
        max_speed=700, scale=1,
        rotation=0, max_rotation_speed=3,
        fire_rate=10, health=20,
        image=images.RED_SHIP

        ) -> None:

        super().__init__(position, velocity, max_speed, scale, rotation, fire_rate, image)

        self.max_rotation_speed = max_rotation_speed
        self.health = health

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

    def turn_left(self, delta_time):
        self.accelerate_rotation(delta_time * 8)

    def turn_right(self, delta_time):
        self.accelerate_rotation(delta_time * -8)