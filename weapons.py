from objects import Vector
import entities
import images
import game
import random
import math
import pygame


class DefaultGun():
    def __init__(self, ship: "entities.Ship", damage=1, fire_rate=1, speed=game.BULLET_SPEED, spread=0, image=lambda: images.BULLET) -> None:
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
            rotation = ship.rotation + self.spread * (random.random()*2-1) # ship rotation with some spread
            bullet_position = ship.position + Vector(0, -ship.image.get_height()/2 - images.BULLET.get_height()/2) # spawns bullet at ship's gun
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



class Laser():
    def __init__(self, ship: "entities.Ship", damage=game.PLAYER_LASER_DAMAGE, charge=10, recharge=1, range=game.PLAYER_LASER_RANGE) -> None:
        self.ship = ship
        self.damage = damage
        self.charge = charge
        self.recharge = recharge
        self.max_range = range

        self.range = self.max_range
        self.shooting = False
        self.delta_time = 0 # used for shoot

    def update(self, delta_time):
        self.charge += self.recharge * delta_time
        self.delta_time = delta_time

    def shoot(self):
        self.shooting = True
        self.range, entity = self.raycast()
        self.damage = game.PLAYER_LASER_DAMAGE # assuming only player has a laser

        if hasattr(entity, "damage") and callable(entity.damage):
            entity.damage(self.damage*self.delta_time, self.ship)

    def raycast(self):

        entity_hit = None
        self.max_range = game.PLAYER_LASER_RANGE # assuming only player has a laser
        sin_rotation = math.sin(self.ship.rotation)
        cos_rotation = math.cos(self.ship.rotation)
        x = self.ship.position.x - self.ship.image.get_height() * sin_rotation
        y = self.ship.position.y - self.ship.image.get_height() * cos_rotation
        for step in range(self.max_range):
            x, y = x - sin_rotation, y - cos_rotation
            chunk = game.CHUNKS.get_chunk((int(x//game.CHUNK_SIZE), int(y//game.CHUNK_SIZE)))

            for entity in chunk.entities:
                if isinstance(entity, entities.Ship) or isinstance(entity, entities.Asteroid)or isinstance(entity, entities.Missile):
                    image = entity.image
                    width, height = image.get_width(), image.get_height()
                    entity_rect = pygame.Rect(entity.position.x-width/2, entity.position.y-height/2, width, height)

                    if entity_rect.collidepoint(x, y):
                        entity_hit = entity
                        break

            if entity_hit:
                break

        return step, entity_hit

    def draw_beam(self):

        beam_width = 10*game.ZOOM
        glow_radius = 100*game.ZOOM
        width, height = beam_width+glow_radius, self.range*game.ZOOM+glow_radius
        surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)

        # Draw beam glow
        for step in range(int(glow_radius/4)+1):
            step=step*2
            pygame.draw.rect(surf, (40, 100, 150, (step/width)**1.3*510), (step, step, width-step*2, height-step*2), border_radius=round(width-step), width=3)

        # Draw light beam
        pygame.draw.rect(surf, (81, 200, 252), (glow_radius/2, glow_radius/2, beam_width, self.range*game.ZOOM), border_radius=round(beam_width))

        surf = pygame.transform.rotozoom(surf, self.ship.rotation / math.pi * 180, 1)
        return surf

    def draw(self, win: pygame.Surface, focus_point):
        if not self.shooting:
            return
        self.shooting = False

        ship = self.ship
        centre = ship.position + Vector(0, -ship.image.get_height()/2 - self.range/2) # centre of laser
        centre.rotate_about(ship.rotation, ship.position)

        surf = self.draw_beam()

        win.blit(surf, ((centre - focus_point) * game.ZOOM + game.CENTRE_POINT - Vector(surf.get_width()/2, surf.get_height()/2)).to_tuple())
