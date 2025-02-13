from objects import Vector, random_vector
from entities import Ship, Scrap
from weapons import PlayerBlaster
import particles
import images
import game
import random
import math
import pygame


class Player_Ship(Ship):
    def __init__(

        self,
        position: Vector, velocity: Vector,
        max_speed=game.MAX_PLAYER_SPEED,
        rotation=0,
        weapon=PlayerBlaster,
        health=game.MAX_PLAYER_HEALTH,
        armour=game.MAX_PLAYER_ARMOUR,
        shield=game.MAX_PLAYER_SHIELD, shield_delay=3, shield_recharge=game.PLAYER_SHIELD_RECHARGE,
        boost_amount=game.MAX_BOOST_AMOUNT, boost_change=5,
        image=lambda: images.PLAYER_SHIP

        ) -> None:

        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, armour, shield_delay, shield_recharge, image)

        self.boost_amount = boost_amount
        self.boost_change = boost_change
        self.aiming_enemy = None
        self.aim_pos = Vector(0, 0)
        self.cursor_highlighted = False
        self.tracked_enemy: Ship = None
        self.closest_station = None
        self.station_to_dock = None
        self.z = 1

        boost_distance = 20

        def ship_offset(ship, distance): return Vector(distance * math.sin(ship.rotation), distance * math.cos(ship.rotation))

        def boost_offset(player): return ship_offset(player, boost_distance)
        self.boost_particles1 = particles.ParticleSystem(self, entity_offset=boost_offset, z=2, start_size=4, end_size=0, colour=(207, 77, 17), bloom=2, duration=None, lifetime=0.5, frequency=150, initial_velocity=lambda player: Vector(0, 600).get_rotated(player.rotation)+player.velocity)

        def boost_offset(player): return ship_offset(player, boost_distance) + random_vector(1)
        self.boost_particles2 = particles.ParticleSystem(self, entity_offset=boost_offset, z=3, start_size=3, end_size=0, colour=(227, 97, 37), bloom=0, duration=None, lifetime=0.5, frequency=250, speed_variance=50, initial_velocity=lambda player: Vector(0, 700).get_rotated(player.rotation)+player.velocity)

        def smoke_offset(player): return ship_offset(player, 4) + random_vector(7)
        self.smoke_particles = particles.ParticleSystem(self, entity_offset=smoke_offset, z=0, start_size=4, colour=game.LIGHT_GREY, duration=None, lifetime=1.5, frequency=80, speed_variance=10, initial_velocity=lambda player: Vector(0, 0))

    def update(self, delta_time):

        super().update(delta_time)

        # If the player ship has just finished boosting, then the intertial dampening will be twice as strong
        if self.velocity.magnitude() >= self.max_speed: self.velocity -= self.velocity.get_clamp(200 * delta_time)

        if self.tracked_enemy in game.CHUNKS.entities: # if enemy is loaded
            self.track_enemy()
        else:
            self.tracked_enemy = None

        if game.DOCKING:

            if self.station_to_dock is None:
                self.station_to_dock = self.closest_station
                self.max_speed = 200

            if self.distance_to(self.station_to_dock) < 1:  # Docked
                game.DOCKING = False
                self.max_speed = game.MAX_PLAYER_SPEED
                game.OPEN_STATION = True
                game.CHUNKS.set_position(self, self.station_to_dock.position)
                self.velocity = Vector(0, 0)
                self.station_to_dock = None

            else:
                self.accelerate_onto_pos(self.station_to_dock.position, 500*delta_time, self.max_speed)

        self.max_shield = game.MAX_PLAYER_SHIELD
        self.shield_recharge = game.PLAYER_SHIELD_RECHARGE

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)

        # the acceleration is clamped so that velocity will not increase over max_speed
        # if velocity is already above max_speed, the new velocity will be of the same magnitude
        acceleration = ((self.velocity + acceleration).get_clamp(max(self.velocity.magnitude(), self.max_speed))
                        - self.velocity) # velocity + acceleration that is the same speed as current velocity

        self.velocity += acceleration

    def move_forward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, -game.PLAYER_ACCELERATION))

    def move_backward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, 0.8*game.PLAYER_ACCELERATION))

    def move_left(self, delta_time):
        self.accelerate_relative(delta_time * Vector(-0.5*game.PLAYER_ACCELERATION, 0))

    def move_right(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0.5*game.PLAYER_ACCELERATION, 0))

    def boost(self, delta_time):
        if self.boost_amount > 0: # Makes sure that you have boost to boost
            self.max_speed = game.MAX_PLAYER_SPEED*2
            self.accelerate_relative(delta_time * Vector(0, -1000))
            self.boost_amount -= self.boost_change * delta_time # Decrease the amount of boost you have while boosting over time

            self.boost_particles1.active = True
            self.boost_particles2.active = True
        else:
            self.max_speed = game.MAX_PLAYER_SPEED # Resets max speed once you run out of boost
            self.boost_particles1.active = False
            self.boost_particles2.active = False

    def no_boost(self, delta_time):
        self.max_speed = game.MAX_PLAYER_SPEED # Reset max speed so that the high velocity is not maintained after a boost
        self.boost_particles1.active = False
        self.boost_particles2.active = False

        # Increase boost_amount
        self.boost_amount = min(game.MAX_BOOST_AMOUNT,
                                    self.boost_amount + (self.boost_change * delta_time) / 2)
                                    # Caps the boost amount to a specific max value

    def track_enemy(self):
        enemy = self.tracked_enemy
        if hasattr(self.weapon, "speed"):
            time_to_enemy = self.distance_to(enemy) / self.weapon.speed
        else:
            time_to_enemy = 0
        self.aim_pos = ((enemy.velocity - self.velocity) * time_to_enemy) + enemy.position

    def damage(self, damage, entity=None):
        super().damage(damage, entity)

        game.SCREEN_SHAKE += damage

    def destroy(self):
        self.boost_particles1.active = False
        self.boost_particles2.active = False
        self.smoke_particles.active = False

        # Drop scrap
        for _ in range(game.SCRAP_COUNT):
            scrap = Scrap(self.position, random_vector(random.randint(0, 500)), rotation=random.random() * math.pi * 2)
            game.CHUNKS.add_entity(scrap)
        game.SCRAP_COUNT = 0

        game.SCREEN_SHAKE = 0

        game.CHUNKS.remove_entity(self)

        game.LAST_PLAYER_POS = Vector(0, 0)
        game.WEAPON_SELECTED = 0
        game.player = get_player()

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)

        if hasattr(self.weapon, "draw"):
            self.weapon.draw(win, focus_point)

        if self.health < 0.7 * game.MAX_PLAYER_HEALTH:
            self.smoke_particles.active = True
        else:
            self.smoke_particles.active = False

        if self.tracked_enemy:
            pygame.draw.circle(game.WIN, (255, 0, 0), ((self.aim_pos.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.aim_pos.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20*game.ZOOM, width=round(2*game.ZOOM))



def get_player():

    # Create Player_Ship
    player = Player_Ship(position=game.LAST_PLAYER_POS, velocity=Vector(0, 0))
    game.CHUNKS.add_entity(player)
    return player
