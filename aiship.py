from objects import Vector
import entities
from entities import Ship, Asteroid
from objects import random_vector
from weapons import EnemyGun
import images
import game
import random
import math
import pygame


class AI_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed, rotation=0, weapon=EnemyGun, health=1, shield=0, shield_delay=1, shield_recharge=1, state=0, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, shield_delay, shield_recharge, image)
        
        self.state = state
        # Initialises start patrol point
        self.make_new_patrol_point(0, 0, self.position)
        self.time_strafing = 0
        self.time_to_stop_strafing = 0
        start_accelerations = [300, -300]
        self.acceleration_constant = random.choice(start_accelerations)
        

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

    def patrol_state(self, delta_time, min_dist, max_dist, max_speed=50, mother_ship_pos=None):
        self.max_speed = max_speed

        target_position = self.patrol_point
        direction_vector = target_position - self.position
        distance = (direction_vector).magnitude()

        if mother_ship_pos:
            target_to_mothership_distance = (target_position - mother_ship_pos).magnitude()
        else:
            target_to_mothership_distance = 0

        if distance < 50 or target_to_mothership_distance > 500:
            while True:
                self.make_new_patrol_point(min_dist, max_dist, self.position)
                target_position = self.patrol_point

                chunk_pos = target_position // game.CHUNK_SIZE

                if self.check_for_asteroid(chunk_pos) == False:
                    break
                else:
                    continue

        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle_to(target_position))

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
        bullet_speed = game.BULLET_SPEED

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



class Enemy_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, weapon=EnemyGun, health=3, shield=0, shield_delay=1, shield_recharge=1, state=0, mother_ship=None, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, shield_delay, shield_recharge, state, image)
        self.mother_ship = mother_ship
        self.new_ship_pos = Vector(0, 0)
        self.attack_min_dist = 100
        self.attack_max_dist = 400
        self.attack_max_speed = 300
        self.patrol_min_dist = 100
        self.patrol_max_dist = 400

    def update(self, delta_time):
        super().update(delta_time)

        distance_to_player = self.distance_to(game.player)

        if self.health == 1 and distance_to_player < 2000 and game.player.health > 5 and len(self.mother_ship.enemy_list) <= 2:
            self.retreat_state(delta_time)
        else:
            if distance_to_player < 600 or self.state == 1:
                self.attack_player_state(delta_time, self.attack_min_dist, self.attack_max_dist, self.attack_max_speed)
                self.enemy_spotted()
            else:
                self.patrol_state(delta_time, self.patrol_min_dist, self.patrol_max_dist, max_speed=(self.attack_max_speed / 2), mother_ship_pos=self.mother_ship.position)

            if self.state == 1 and distance_to_player > 1000:
                self.state = 0

    # DEBUG DRAW PATROL POINTS

    def damage(self, damage, entity=None):

        if entity and isinstance(entity, entities.Bullet):
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
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, weapon=EnemyGun, health=1, shield=5, shield_delay=5, shield_recharge=1, state=0, mother_ship=None, image=images.RADAR_ICON) -> None:
        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, shield_delay, shield_recharge, state, mother_ship, image)
        self.mother_ship = mother_ship
        self.attack_max_speed = 800
        self.explode_radius = 100
        self.explode_damage = 10
    
    def update(self, delta_time):
        super(AI_Ship, self).update(delta_time)
        
        distance_to_player = self.distance_to(game.player)

        if distance_to_player < 600 or self.state == 1:
            self.attack_player_state(delta_time, distance_to_player, self.attack_max_speed)
            self.enemy_spotted()
        else:
            self.patrol_state(delta_time, self.patrol_min_dist, self.patrol_max_dist, max_speed=(self.attack_max_speed / 2), mother_ship_pos=self.mother_ship.position)

        if self.state == 1 and distance_to_player > 1000:
            self.state = 0

    def attack_player_state(self, delta_time, distance_to_player, max_speed=300):
        # Set max speed to a higher value
        self.max_speed = max_speed

        # Rotation
        self.set_rotation(self.position.get_angle_to(game.player.position))

        # Movement
        self.accelerate_in_direction(game.player.position, 2000 * delta_time)

        if distance_to_player < 60:
            self.explode(self.explode_radius)
            self.destroy()

    def explode(self, radius):
        entity_list = game.CHUNKS.entities
        entity_list.remove(self)

        # Have to create separate list otherwise the set game.CHUNKS.entities will change size while iterating though it
        entities_to_damage = []

        for entity in entity_list:
            if isinstance(entity, Ship):
                if entity.distance_to(self) < radius:
                    entities_to_damage.append(entity)
        
        for entity in entities_to_damage:
            entity.damage(self.explode_damage)



class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, weapon=EnemyGun, health=10, shield=3, shield_delay=5, shield_recharge=1, state=0, enemy_list=None, image=images.MOTHER_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, shield_delay, shield_recharge, state, self, image)
        if enemy_list is None:
            enemy_list = []
        self.enemy_list = enemy_list

        self.attack_min_dist = 300
        self.attack_max_dist = 600
        self.attack_max_speed = 100
        self.patrol_min_dist = 1000
        self.patrol_max_dist = 1500

        # Make start patrol point
        while True:
            self.make_new_patrol_point(self.patrol_min_dist, self.patrol_max_dist, self.position)
            target_position = self.patrol_point

            chunk_pos = target_position // game.CHUNK_SIZE

            if self.check_for_asteroid(chunk_pos) == False:
                break
            else:
                continue
        
        # Spawn in enemies
        enemy_spawn_number = random.randint(3, 6)

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            if random.random() > 0.3:
                enemy = Enemy_Ship(random_position, Vector(0, 0), mother_ship=self)
            else:
                enemy = Missile_Ship(random_position, Vector(0, 0), mother_ship=self)
            self.enemy_list.append(enemy)
            
            game.CHUNKS.add_entity(enemy)

    def update(self, delta_time):
        super(AI_Ship, self).update(delta_time)

        distance_to_player = self.distance_to(game.player)

        if self.health == 1 and distance_to_player < 2000 and game.player.health > 5 and len(self.mother_ship.enemy_list) <= 2:
            self.retreat_state(delta_time)
        else:
            if distance_to_player < 600 or self.state == 1:
                self.attack_player_state(delta_time, self.attack_min_dist, self.attack_max_dist, self.attack_max_speed)
                self.enemy_spotted()
            else:
                self.patrol_state(delta_time, self.patrol_min_dist, self.patrol_max_dist)

            if self.state == 1 and distance_to_player > 1000:
                self.state = 0

    # DEBUG DRAW PATROL POINTS

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 0, 255), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        

    def alert_group(self):
        for enemy in self.enemy_list:
            enemy.state = 1
        
        self.state = 1



class Neutral_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, weapon=EnemyGun, health=5, shield=0, shield_delay=1, shield_recharge=1, state=0, recent_enemy=None, image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, weapon, health, shield, shield_delay, shield_recharge, state, image)
        self.recent_enemy = recent_enemy

    def update(self, delta_time):
        super().update(delta_time)

        if self.state == 0:
            self.patrol_state(delta_time, min_dist=1000, max_dist=4000)
        elif self.state == 1:
            self.attack_player_state(delta_time)
        elif self.state == 2:
            self.attack_enemy_state(delta_time)

        if self.state == 1 and self.distance_to(game.player) > 1000:
            self.state = 0

    # DEBUG DRAW PATROL POINTS

    def damage(self, damage, entity=None):
        if entity and isinstance(entity, entities.Bullet):
            if type(entity.ship).__name__ == "Player_Ship":
                self.state = 1
            elif isinstance(entity.ship, Enemy_Ship):
                self.state = 2
                self.recent_enemy = entity.ship
        
        super().damage(damage)


    def attack_enemy_state(self, delta_time):
        if self.recent_enemy.health > 0:
            self.max_speed = 300
            self.set_rotation(self.position.get_angle_to(self.recent_enemy.position))
            self.shoot()
            self.accelerate_in_direction(self.recent_enemy.position, 400 * delta_time)
        else:
            self.recent_enemy = None
            self.state = 0

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 255, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)