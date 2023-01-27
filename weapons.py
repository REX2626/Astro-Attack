from objects import Vector
import entities
import images
import game


class DefaultGun():
    def __init__(self, ship, damage=1, fire_rate=1, speed=game.BULLET_SPEED, image=images.BULLET) -> None:
        self.ship = ship
        self.damage = damage
        self.reload_time = 1 / fire_rate
        self.speed = speed
        self.image = image

        self.time_reloading = 0

    def update(self, delta_time):
        self.time_reloading += delta_time

    def shoot(self):
        if self.time_reloading >= self.reload_time:
            
            ship = self.ship
            bullet_position = ship.position + Vector(0, -ship.image.get_height()/2 - images.BULLET.get_height()/2) # spawns bullet at ship's gun
            bullet_position.rotate_about(ship.rotation, ship.position)
            bullet_velocity = Vector(0, -self.speed)
            bullet_velocity.rotate(ship.rotation)
            bullet = entities.Bullet(

                position=bullet_position,
                velocity=bullet_velocity + ship.velocity,
                rotation=ship.rotation,
                ship=ship,
                damage=self.damage,
                lifetime=3,
                image=self.image
                )

            game.CHUNKS.add_entity(bullet)
            self.time_reloading = 0



class EnemyGun(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=1, fire_rate=1, image=images.RED_BULLET)



class PlayerGun(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=game.PLAYER_DAMAGE, fire_rate=game.PLAYER_FIRE_RATE)

    def shoot(self):
        self.reload_time = 1 / game.PLAYER_FIRE_RATE
        self.damage = game.PLAYER_DAMAGE
        self.speed = game.PLAYER_BULLET_SPEED
        super().shoot()



class GatlingGun(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=0.5, fire_rate=20, speed=1000)



class Sniper(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=2, fire_rate=3, speed=1500)