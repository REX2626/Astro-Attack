from objects import Vector, Ship
import images
import game



class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=500, scale=2, rotation=0, fire_rate=1, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, scale, rotation, fire_rate, image)

    def update(self, delta_time):
        super().update(delta_time)

        self.set_rotation(self.position.get_angle(game.red_ship.position))

        if self.distance_to(game.red_ship) < 500:
            self.shoot()

        if self.distance_to(game.red_ship) < 750 and self.distance_to(game.red_ship) > 300:
            self.accelerate_towards(game.red_ship.position, 20)

        elif self.distance_to(game.red_ship) < 200:
            self.accelerate_towards(game.red_ship.position, -20)
        
            print(self.velocity)
    
