from __future__ import annotations
from objects import Vector
import entities
import images
import game
import random



class DefaultGun():
    def __init__(self, ship: entities.Ship, damage=1, fire_rate=1, speed=game.BULLET_SPEED, spread=0, image=lambda: images.BULLET) -> None:
        self.ship = ship
        self.damage = damage
        self.reload_time = 1 / fire_rate
        self.speed = speed
        self.spread = spread
        self.image = image()

        self.load_image = image

        self.time_reloading = 0

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.image = self.load_image()

    def update(self, delta_time):
        self.time_reloading += delta_time

    def shoot(self):
        if self.time_reloading >= self.reload_time:

            ship = self.ship
            rotation = ship.rotation + self.spread * (random.random()*2-1)  # ship rotation with some spread
            bullet_position = ship.position + Vector(0, -ship.image.get_height()/2 - images.BULLET.get_height()/2)  # spawns bullet at ship's gun
            bullet_position.rotate_about(rotation, ship.position)
            bullet_velocity = Vector(0, -self.speed)
            bullet_velocity.rotate(rotation)
            bullet = entities.Bullet(

                position=bullet_position,
                velocity=bullet_velocity + ship.velocity,
                rotation=rotation,
                ship=ship,
                damage=self.damage,
                lifetime=3,
                image=self.load_image
                )

            game.CHUNKS.add_entity(bullet)
            self.time_reloading = 0


    def fire_missile(self, position, velocity, rotation):
        missile = entities.Missile(position, velocity, rotation)
        game.CHUNKS.add_entity(missile)



class PlayerGun(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=game.PLAYER_DEFAULT_DAMAGE, fire_rate=game.PLAYER_DEFAULT_FIRE_RATE, speed=game.PLAYER_DEFAULT_BULLET_SPEED, spread=0.05)

    def shoot(self):
        self.reload_time = 1 / game.PLAYER_DEFAULT_FIRE_RATE
        self.damage = game.PLAYER_DEFAULT_DAMAGE
        self.speed = game.PLAYER_DEFAULT_BULLET_SPEED
        super().shoot()



class EnemyGun(DefaultGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=1, fire_rate=1, image=lambda: images.RED_BULLET)



class GatlingGun(DefaultGun):
    def __init__(self, ship, damage=0.5, fire_rate=20, speed=800, spread=0.2, image=lambda: images.GATLING_BULLET) -> None:
        super().__init__(ship, damage, fire_rate, speed, spread, image)



class PlayerGatlingGun(GatlingGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=game.PLAYER_GATLING_DAMAGE, fire_rate=game.PLAYER_GATLING_FIRE_RATE, speed=game.PLAYER_GATLING_BULLET_SPEED)

    def shoot(self):
        self.reload_time = 1 / game.PLAYER_GATLING_FIRE_RATE
        self.damage = game.PLAYER_GATLING_DAMAGE
        self.speed = game.PLAYER_GATLING_BULLET_SPEED
        super().shoot()



class EnemyGatlingGun(GatlingGun):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=0.4, fire_rate=3, speed=600, image=lambda: images.RED_GATLING_BULLET)



class Sniper(DefaultGun):
    def __init__(self, ship, damage=2, fire_rate=3, speed=1500, spread=0, image=lambda: images.SNIPER_BULLET) -> None:
        super().__init__(ship, damage, fire_rate, speed, spread, image)



class PlayerSniper(Sniper):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=game.PLAYER_SNIPER_DAMAGE, fire_rate=game.PLAYER_SNIPER_FIRE_RATE, speed=game.PLAYER_SNIPER_FIRE_RATE)

    def shoot(self):
        self.reload_time = 1 / game.PLAYER_SNIPER_FIRE_RATE
        self.damage = game.PLAYER_SNIPER_DAMAGE
        self.speed = game.PLAYER_SNIPER_BULLET_SPEED
        super().shoot()



class EnemySniper(Sniper):
    def __init__(self, ship) -> None:
        super().__init__(ship, damage=3, fire_rate=0.5, speed=1200, image=lambda: images.RED_SNIPER_BULLET)
