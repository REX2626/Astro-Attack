from objects import Vector, Vector1D, Ship, Bullet
import images
import game



class Player_Ship(Ship):
    def __init__(

        self,
        position: Vector, velocity: Vector,
        max_speed, scale=1, rotation=0, max_rotation_speed=3,
        fire_rate=1, health=10,
        image=images.RED_SHIP

        ) -> None:

        super().__init__(position, velocity, scale, rotation, fire_rate, image)

        self.max_speed = max_speed
        self.max_rotation_speed = max_rotation_speed
        self.health = health

    def accelerate(self, acceleration: Vector):
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_rotation(self, acceleration):
        self.rotation_speed += acceleration
        self.rotation_speed.clamp(self.max_rotation_speed)

    def move_forward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, -1000))

    def move_backward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, 800))

    def move_left(self, delta_time):
        self.accelerate_relative(delta_time * Vector(-500, 0))

    def move_right(self, delta_time):
        self.accelerate_relative(delta_time * Vector(500, 0))

    def turn_left(self, delta_time):
        self.accelerate_rotation(delta_time * 8)

    def turn_right(self, delta_time):
        self.accelerate_rotation(delta_time * -8)