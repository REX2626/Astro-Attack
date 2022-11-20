from objects import Vector, Ship
import images



class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, scale=1, rotation=0, fire_rate=1, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, scale, rotation, fire_rate, image)

    def update(self, delta_time):
        super().update(delta_time)

        self.set_rotation(self.position.get_angle(Vector(0, 0)))

        self.shoot()