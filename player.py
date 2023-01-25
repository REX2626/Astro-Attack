from objects import Vector
from entities import Ship
import entities
import images
import particles
import game
import math
import pygame


class Player_Ship(Ship):
    def __init__(

        self,
        position: Vector, velocity: Vector,
        max_speed=game.MAX_PLAYER_SPEED,
        rotation=0, max_rotation_speed=3,
        fire_rate=game.PLAYER_FIRE_RATE, 
        health=lambda: game.MAX_PLAYER_HEALTH, # health has to be a function, in case player health is changed in settings
        shield=5, shield_delay=3, shield_recharge=1,
        boost_amount=lambda: game.MAX_BOOST_AMOUNT, boost_change=5, # boost also could be changed in settings
        image=images.RED_SHIP

        ) -> None:

        super().__init__(position, velocity, max_speed, rotation, fire_rate, health(), shield, shield_delay, shield_recharge, image)

        self.max_rotation_speed = max_rotation_speed
        self.boost_amount = boost_amount()
        self.boost_change = boost_change
        self.aiming_enemy = None
        self.aim_pos = Vector(0, 0)
        self.cursor_highlighted = False
        self.tracked_enemy: Ship = None

    def update(self, delta_time):

        super().update(delta_time)

        # If the player ship has just finished boosting, then the intertial dampening will be twice as strong
        if self.velocity.magnitude() >= self.max_speed: self.velocity -= self.velocity.get_clamp(200 * delta_time)
        
        if self.tracked_enemy in game.CHUNKS.entities: # if enemy is loaded
            self.track_enemy()
        else:
            self.tracked_enemy = None

    def shoot(self):
        # Check if reloaded
        if self.time_reloading >= 1 / game.PLAYER_FIRE_RATE:
            
            bullet_position = self.position + Vector(0, -self.image.get_height()/2 - images.BULLET.get_height()/2) # spawns bullet at ship's gun
            bullet_position.rotate_about(self.rotation, self.position)
            bullet_velocity = Vector(0, -game.PLAYER_BULLET_SPEED)
            bullet_velocity.rotate(self.rotation)
            bullet = entities.Bullet(

                position=bullet_position,
                velocity=bullet_velocity + self.velocity,
                rotation=self.rotation,
                ship=self,
                damage=game.PLAYER_DAMAGE,
                lifetime=3,
                )

            game.CHUNKS.add_entity(bullet)
            self.time_reloading = 0

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)

        # the acceleration is clamped so that velocity will not increase over max_speed
        # if velocity is already above max_speed, the new velocity will be of the same magnitude
        acceleration = ((self.velocity + acceleration).get_clamp(max(self.velocity.magnitude(), self.max_speed))
                        - self.velocity) # velocity + acceleration that is the same speed as current velocity

        self.velocity += acceleration

    def accelerate_rotation(self, acceleration):
        self.rotation_speed += acceleration
        self.rotation_speed.clamp(self.max_rotation_speed)

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

            boost_distance = 20
            boost_position = Vector(boost_distance * math.sin(self.rotation), boost_distance * math.cos(self.rotation))

            particles.ParticleSystem(self.position + boost_position, start_size=4, end_size=0, colour=(207, 77, 17), bloom=1.5, duration=None, lifetime=0.5, frequency=1)
        else:
            self.max_speed = game.MAX_PLAYER_SPEED # Resets max speed once you run out of boost

    def turn_left(self, delta_time):
        self.accelerate_rotation(delta_time * 8)

    def turn_right(self, delta_time):
        self.accelerate_rotation(delta_time * -8)

    def track_enemy(self):
        enemy = self.tracked_enemy
        time_to_enemy = self.distance_to(enemy) / game.BULLET_SPEED
        self.aim_pos = ((enemy.velocity - self.velocity) * time_to_enemy) + enemy.position

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)

        if self.tracked_enemy:
            pygame.draw.circle(game.WIN, (255, 0, 0), ((self.aim_pos.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.aim_pos.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20*game.ZOOM, width=round(2*game.ZOOM))
     


def add_player():

    # Red Player Ship
    global player
    game.LAST_PLAYER_POS = Vector(0, 0)
    player = Player_Ship(position=game.LAST_PLAYER_POS, velocity=(0, 0))
    game.CHUNKS.add_entity(player)
    game.player = player
    return player