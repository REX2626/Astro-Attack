from objects import Vector
import entities
from entities import Ship, Asteroid, HealthPickup
from objects import random_vector
from weapons import EnemyGun, EnemyGatlingGun, EnemySniper
from player import Player_Ship
import images
import game
import random
import math
import pygame
import particles


PATROL = 0
ATTACK = 1
RETREAT = 2
ATTACK_ENEMY = 3



class AI_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=1, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, image)
        
        self.state = state
        # Initialises start patrol point
        self.make_new_patrol_point(0, 0, self.position)
        self.time_strafing = 0
        self.time_to_stop_strafing = 0
        start_accelerations = [300, -300]
        self.acceleration_constant = random.choice(start_accelerations)
        self.max_rotation_speed = max_rotation_speed
        

    def check_for_asteroid(self, chunk_pos):
        # Loop through chunks in a 3x3 grid centred around the original chunk you are checking
        for y in range(chunk_pos.y-1, chunk_pos.y+2):
            for x in range(chunk_pos.x-1, chunk_pos.x+2):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():
                    if isinstance(entity, Asteroid):

                        return True
                    else:
                        # No Asteroid
                        return False

    def patrol_state(self, delta_time, min_dist, max_dist, max_speed=50, mother_ship=None):
        self.max_speed = max_speed

        target_position = self.patrol_point
        direction_vector = target_position - self.position
        distance = (direction_vector).magnitude()

        if mother_ship:
            target_to_mothership_distance = (target_position - mother_ship.position).magnitude()
        else:
            target_to_mothership_distance = 0

        if distance < 50 or target_to_mothership_distance > 500:
            for _ in range(100): # try to find new patrol point, if none have been found after 100 iterations then cry
                self.make_new_patrol_point(min_dist, max_dist, self.position)
                target_position = self.patrol_point

                chunk_pos = target_position // game.CHUNK_SIZE

                if self.check_for_asteroid(chunk_pos) == False:
                    break

        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.rotate_to(delta_time, self.position.get_angle_to(target_position), self.max_rotation_speed)

    def attack_player_state(self, delta_time, min_dist=100, max_dist=400, max_speed=300):
        # Set max speed to a higher value
        self.max_speed = max_speed

        # Aiming and shooting functionality
        self.set_rotation(self.position.get_angle_to(self.predicted_player_position()))
        self.shoot()

        # Movement
        if self.distance_to(game.player) < min_dist:
            self.accelerate_in_direction(game.player.position, 400 * -delta_time)
        elif self.distance_to(game.player) > max_dist:
            self.accelerate_in_direction(game.player.position, 400 * delta_time)
        else:
            # Strafing
            self.strafe(delta_time)

    def predicted_player_position(self):
        ship_pos = game.player.position
        ship_vel = game.player.velocity
        current_vel = self.velocity
        bullet_speed = self.weapon.speed

        # Calculates basic time to reach player and the next position of the player ship
        time_to_player = self.distance_to(game.player) / bullet_speed
        self.new_ship_pos = ((ship_vel - current_vel) * time_to_player) + ship_pos
        return self.new_ship_pos

    def strafe(self, delta_time):

        # Get vector 90 degrees from player
        direction_vector = game.player.position - self.position
        rotated_vector = direction_vector.get_rotate(math.pi / 2)
        final_vector = Vector(rotated_vector.x + self.position.x, rotated_vector.y + self.position.y)

        # Alternate directions to strafe
        self.time_strafing += delta_time
        if self.time_strafing > self.time_to_stop_strafing:
            self.acceleration_constant *= -1
            self.time_to_stop_strafing += random.randint(2, 5)
        
        # Accelerate in that direction
        self.accelerate_in_direction(final_vector, self.acceleration_constant * delta_time)

    def retreat_state(self, delta_time):

        # Ship retreats in opposite direction to player
        self.max_speed = 500
        self.set_rotation(self.position.get_angle_to(game.player.position) + math.pi)
        self.accelerate_in_direction(game.player.position, 400 * -delta_time)

    def find_nearest_health_pickup(self):
        health_pickups = []
        for entity in game.CHUNKS.entities:
            if isinstance(entity, HealthPickup):
                health_pickups.append(entity)

        dist_to_health = math.inf
        index = 0

        for i, health_pickup in enumerate(health_pickups):
            dist = (health_pickup.position - self.position).magnitude()
            if dist < dist_to_health:
                dist_to_health = dist
                index = i

        return health_pickups[index]



class Enemy_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=3, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, mother_ship=None, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, state, image)
        self.mother_ship = mother_ship
        self.mother_ship_patrol = mother_ship
        self.new_ship_pos = Vector(0, 0)
        self.attack_min_dist = 100
        self.attack_max_dist = 400
        self.attack_max_speed = 300
        self.patrol_min_dist = 100
        self.patrol_max_dist = 400
        self.hp = None

    def update(self, delta_time):
        super().update(delta_time)

        distance_to_player = self.distance_to(game.player)

        # Initially check if it should be retreating
        if self.health == 1 and distance_to_player < 1500 and game.player.health > 5 and len(self.mother_ship.enemy_list) <= 2:
            self.state = RETREAT
            self.retreat_state(delta_time)
        else:
            # Check if it should be attacking
            if (distance_to_player < 600 or self.state == ATTACK) and self.state != RETREAT:
                self.attack_player_state(delta_time, self.attack_min_dist, self.attack_max_dist, self.attack_max_speed)
                self.enemy_spotted()
            # Check if it should be patroling
            elif self.state != RETREAT:
                self.patrol_state(delta_time, self.patrol_min_dist, self.patrol_max_dist, max_speed=(self.attack_max_speed / 2), mother_ship=self.mother_ship_patrol)

            # Enemy ships will go into patrol state if the player gets too far while attacking
            if self.state == ATTACK and distance_to_player > 1500:
                self.state = PATROL
            
            # Enemy will stop retreating if its health goes above 1
            if self.state == RETREAT and self.health > 1:
                self.state = PATROL

            # Check to see if the retreating enemy if far enough from the player to then collect health
            elif self.state == RETREAT and self.health == 1 and distance_to_player > 1500:
                self.hp = self.find_nearest_health_pickup()
                self.set_rotation(self.position.get_angle_to(self.hp.position) + math.pi)
                self.accelerate_in_direction(self.hp.position, 400 * delta_time)

                # Add health if close to a health pickup
                if (self.hp.position - self.position).magnitude() < 50:
                    self.hp.destroy()
                    self.health += 5


    def damage(self, damage, entity=None):

        if entity and isinstance(entity, Player_Ship):
            self.enemy_spotted()

        super().damage(damage)

    def destroy(self):
        super().destroy()
        if type(self) == Enemy_Ship:
            self.mother_ship.enemy_list.remove(self)
            game.SCORE += 1
        elif type(self) == Mother_Ship:
            game.SCORE += 3

        scrap = entities.Scrap(self.position, rotation=random.random() * math.pi * 2)
        game.CHUNKS.add_entity(scrap)


    def enemy_spotted(self):
        self.mother_ship.alert_group()

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (255, 0, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)



class Missile_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=5, shield=0, shield_delay=1, shield_recharge=1, state=0, mother_ship=None, image=images.MISSILE_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, state, mother_ship, image)
        self.attack_max_speed = 800
        self.explode_radius = 100
        self.explode_damage = 10
    

    def attack_player_state(self, delta_time, attack_min_dist, attack_max_dist, attack_max_speed):
        # Set max speed to a higher value
        self.max_speed = attack_max_speed

        distance_to_player = self.distance_to(game.player)

        # Rotation
        self.set_rotation(self.position.get_angle_to(game.player.position))

        # Movement
        self.accelerate_in_direction(game.player.position, 2000 * delta_time)

        # Boost particle effect
        boost_distance = 20
        boost_position = Vector(boost_distance * math.sin(self.rotation), boost_distance * math.cos(self.rotation))

        particles.ParticleSystem(self.position + boost_position, start_size=4, end_size=0, colour=(207, 77, 17), bloom=2, duration=None, lifetime=0.5, frequency=1, initial_velocity=Vector(0, 300).get_rotate(self.rotation))

        if distance_to_player < 60:
            self.explode(self.explode_radius)

    def explode(self, radius):
        self.destroy()

        # Have to create separate list otherwise the set game.CHUNKS.entities will change size while iterating though it
        entities_to_damage = []

        for entity in game.CHUNKS.entities:
            if isinstance(entity, Ship):
                if entity.distance_to(self) < radius:
                    entities_to_damage.append(entity)
        
        for entity in entities_to_damage:
            entity.damage(self.explode_damage)



class Drone_Enemy(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, max_rotation_speed=5, weapon=EnemyGatlingGun, health=1, shield=2, shield_delay=2, shield_recharge=4, state=PATROL, mother_ship=None, image=images.DRONE_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, state, mother_ship, image)



class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, max_rotation_speed=1.5, weapon=EnemySniper, health=10, shield=3, shield_delay=5, shield_recharge=1, state=PATROL, enemy_list=None, image=images.MOTHER_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, state, self, image)
        if enemy_list is None:
            enemy_list = []
        self.enemy_list = enemy_list

        self.mother_ship_patrol = None

        self.attack_min_dist = 300
        self.attack_max_dist = 600
        self.attack_max_speed = 100
        self.patrol_min_dist = 1000
        self.patrol_max_dist = 1500

        self.missile_fire_rate = 0.2
        self.reload_time = 1 / self.missile_fire_rate
        self.time_reloading = 0

        # Make start patrol point
        for _ in range(100): # try to find new patrol point, if none have been found after 100 iterations then cry
            self.make_new_patrol_point(self.patrol_min_dist, self.patrol_max_dist, self.position)
            target_position = self.patrol_point

            chunk_pos = target_position // game.CHUNK_SIZE

            if self.check_for_asteroid(chunk_pos) == False:
                break
        
        # Spawn in enemies
        enemy_spawn_number = random.randint(3, 6)

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            if random.random() < 0.2:
                enemy = Missile_Ship(random_position, Vector(0, 0), mother_ship=self)
            elif random.random() < 0.4:
                enemy = Drone_Enemy(random_position, Vector(0, 0), mother_ship=self)
            else:
                enemy = Enemy_Ship(random_position, Vector(0, 0), mother_ship=self)
            
            self.enemy_list.append(enemy)
            
            game.CHUNKS.add_entity(enemy)

    
    def update(self, delta_time):
        super().update(delta_time)

        self.time_reloading += delta_time

    
    def attack_player_state(self, delta_time, min_dist=300, max_dist=600, max_speed=100):
        super().attack_player_state(delta_time, min_dist, max_dist, max_speed)

        # Fire Missiles

        if self.time_reloading >= self.reload_time:

            # Get vector 90 degrees from player
            direction_vector = game.player.position - self.position
            rotated_vector = direction_vector.get_rotate(math.pi / 2)
            final_vector = Vector(rotated_vector.x + self.position.x, rotated_vector.y + self.position.y)

            # Fire 2 missiles, one on eather side of the ship
            self.weapon.fire_missile(self.position, final_vector * 100 * delta_time, 1000, 100, 150, 5)
            self.weapon.fire_missile(self.position, final_vector * 100 * -delta_time, 1000, 100, 150, 5)

            self.time_reloading = 0


    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 0, 255), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        

    def alert_group(self):
        for enemy in self.enemy_list:
            if enemy.state != RETREAT:
                enemy.state = ATTACK
        
        self.state = ATTACK



class Neutral_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=5, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, recent_enemy=None, image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, shield_delay, shield_recharge, state, image)
        self.recent_enemy = recent_enemy

    def update(self, delta_time):
        super().update(delta_time)

        if self.state == PATROL:
            self.patrol_state(delta_time, min_dist=1000, max_dist=4000)
        elif self.state == ATTACK:
            self.attack_player_state(delta_time)
        elif self.state == ATTACK_ENEMY:
            self.attack_enemy_state(delta_time)

        if self.state == ATTACK and self.distance_to(game.player) > 1500:
            self.state = PATROL


    def damage(self, damage, entity=None):
        if entity and isinstance(entity, Ship):

            if isinstance(entity, Player_Ship):
                self.state = ATTACK

            elif isinstance(entity, Enemy_Ship):
                self.state = ATTACK_ENEMY
                self.recent_enemy = entity
        
        super().damage(damage)


    def attack_enemy_state(self, delta_time):
        if self.recent_enemy.health > 0:
            self.max_speed = 300
            self.set_rotation(self.position.get_angle_to(self.recent_enemy.position))
            self.shoot()
            self.accelerate_in_direction(self.recent_enemy.position, 400 * delta_time)
        else:
            self.recent_enemy = None
            self.state = PATROL

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 255, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)