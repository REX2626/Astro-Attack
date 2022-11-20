from objects import Vector, Ship
import images



class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, scale=1, rotation=0, fire_rate=1, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, scale, rotation, fire_rate, image)