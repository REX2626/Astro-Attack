from objects import Vector
import entities
from entities import Ship, Asteroid
from objects import random_vector
from weapons import EnemyGun, EnemyGatlingGun, EnemySniper
from player import Player_Ship
import effects
import images
import game
import random
import math
import pygame

PATROL = 0
ATTACK = 1
RETREAT = 2
ATTACK_ENEMY = 3
PATROL_TO_STATION = 4

level_text_cache = dict()



class AI_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector=Vector(0, 0), max_speed=100, level=0, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=1, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, velocity, max_speed, rotation, max_rotation_speed, weapon, health, shield, armour, shield_delay, shield_recharge, image)

        self.state = state
        # Initialises start patrol point
        self.make_new_patrol_point(0, 0, self.position)
        self.time_strafing = 0
        self.time_to_stop_strafing = 0
        start_accelerations = [300, -300]
        self.acceleration_constant = random.choice(start_accelerations)
        self.max_rotation_speed = max_rotation_speed

        self.level = level

        # Every 10 levels damage is increased by +1
        self.weapon.damage += self.level/10

        # Adds 0.5 hp every level
        self.health += self.level/2

        # Enemies below lvl 5 do not have a shield
        if self.level < 5:
            self.shield = 0
            self.shield_recharge = 0

        self.intermediate_patrol_point = None

    def check_for_asteroid(self, chunk_pos):
        # Loop through chunks in a 3x3 grid centred around the original chunk you are checking
        for y in range(chunk_pos.y-1, chunk_pos.y+2):
            for x in range(chunk_pos.x-1, chunk_pos.x+2):

                for entity in game.CHUNKS.get_chunk((x, y)).entities:
                    if isinstance(entity, Asteroid):
                        return True

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

        if distance < 50:
            for _ in range(100): # try to find new patrol point, if none have been found after 100 iterations then cry
                self.make_new_patrol_point(min_dist, max_dist, self.position)
                target_position = self.patrol_point

                chunk_pos = target_position // game.CHUNK_SIZE

                if self.check_for_asteroid(chunk_pos) == False:
                    break

        # Makes Target around mother ship to keep it within distance of mothership
        if target_to_mothership_distance > 500:
            self.make_new_patrol_point(100, 400, mother_ship.position)
            target_position = self.patrol_point

        if max_dist > 2 * game.CHUNK_SIZE:
            # If the intermediate_patrol_point has not already been calculated, calculate it
            if self.intermediate_patrol_point == None:
                self.intermediate_patrol_point = self.find_intermediate_patrol_point(target_point=target_position, point_spacing=game.CHUNK_SIZE/2, intermediate_point_distance=game.CHUNK_SIZE)

            # If there is an intermediate_patrol_point, fly to it. Else, fly directly to the station
            if self.intermediate_patrol_point:
                self.rotate_to(delta_time, self.position.get_angle_to(self.intermediate_patrol_point), self.max_rotation_speed)
                self.accelerate_in_direction(self.rotation, 300 * delta_time)

                # Once at the intermediate point, set it equal to none so that the ship will then, next frame, start flying straight towards the point
                if (self.intermediate_patrol_point - self.position).magnitude() < 50:
                    self.intermediate_patrol_point = None

                return

        self.rotate_to(delta_time, self.position.get_angle_to(target_position), self.max_rotation_speed)
        self.accelerate_in_direction(self.rotation, 300 * delta_time)

    def find_intermediate_patrol_point(self, target_point: Vector, point_spacing: float, intermediate_point_distance: float) -> Vector | None:
        """
        `target_point`: position Vector of end location
        `point_spacing`: space between each intermediate point
        `intermediate_point_distance`: distance from asteroid to intermediate point, i.e. distance off course
        """
        # Find a couple useful values
        direction = target_point - self.position
        distance = direction.magnitude()
        dx = target_point.x - self.position.x
        dy = target_point.y - self.position.y

        # Calculates the vector displacement from point to point
        point_spacing_x = point_spacing * (dx / distance)
        point_spacing_y = point_spacing * (dy / distance)

        point_number = int(distance / point_spacing)

        for i in range(1, point_number+1):
            chunk_pos_x = int((i*point_spacing_x + self.position.x) // game.CHUNK_SIZE)
            chunk_pos_y = int((i*point_spacing_y + self.position.y) // game.CHUNK_SIZE)

            # Checks if there is an asteroid in the chunk of that node point
            for entity in game.CHUNKS.get_chunk((chunk_pos_x, chunk_pos_y)).entities:
                if isinstance(entity, Asteroid):
                    # If there is, then find a position intermediate_point_distance away from the asteroid along the normal line (-dx, dy = normal)
                    d_x = intermediate_point_distance * math.cos(math.atan2(-dx, dy))
                    d_y = intermediate_point_distance * math.sin(math.atan2(-dx, dy))

                    return Vector(entity.position.x + d_x, entity.position.y + d_y) # returns point of intermediate_point

        # There is no intermediate point
        return None

    def attack_entity_state(self, delta_time, entity, min_dist=100, max_dist=400, max_speed=300):
        # Set max speed to a higher value
        self.max_speed = max_speed

        # Aiming and shooting functionality
        self.rotate_to(delta_time, self.position.get_angle_to(self.predicted_entity_position(entity)), self.max_rotation_speed)
        self.shoot()

        # Movement
        if self.distance_to(entity) < min_dist:
            self.accelerate_in_direction(self.rotation, 400 * -delta_time)
        elif self.distance_to(entity) > max_dist:
            self.accelerate_in_direction(self.rotation, 400 * delta_time)
        else:
            # Strafing
            self.strafe(delta_time, entity)

    def predicted_entity_position(self, entity: Ship):
        # Calculates basic time to reach player and the next position of the player ship
        # new_ship_pos = (rel_vel * time_to_player) + ship_pos
        return ((entity.velocity - self.velocity) * self.distance_to(entity) / self.weapon.speed) + entity.position

    def strafe(self, delta_time, entity):

        # Get vector 90 degrees from player
        direction_vector = entity.position - self.position
        rotated_vector = direction_vector.get_rotate(math.pi / 2)
        final_vector = Vector(rotated_vector.x + self.position.x, rotated_vector.y + self.position.y)

        # Alternate directions to strafe
        self.time_strafing += delta_time
        if self.time_strafing > self.time_to_stop_strafing:
            self.acceleration_constant *= -1
            self.time_to_stop_strafing += random.randint(2, 5)

        # Accelerate in that direction
        self.accelerate_to(final_vector, self.acceleration_constant * delta_time)

    def retreat_state(self, delta_time):
        # Ship retreats in opposite direction to player
        self.max_speed = 500
        self.rotate_to(delta_time, self.position.get_angle_to(game.player.position) + math.pi, self.max_rotation_speed)
        self.accelerate_in_direction(self.rotation, 400 * delta_time)

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)

        if game.DEBUG_SCREEN:

            # Checking to see if level text has not been cached already
            if f"Lvl: {self.level}, {game.ZOOM}" not in level_text_cache:
                text_surface = pygame.font.SysFont("consolas", int(15 * game.ZOOM)).render(f"Lvl: {self.level}", True, (255, 255, 255))
                level_text_cache[f"Lvl: {self.level}, {game.ZOOM}"] = text_surface
            else:
                text_surface: pygame.Surface = level_text_cache[f"Lvl: {self.level}, {game.ZOOM}"]

            game.WIN.blit(text_surface, ((self.position.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x - (text_surface.get_width() / 2), (self.position.y - focus_point.y - 20) * game.ZOOM + game.CENTRE_POINT.y - (text_surface.get_height() / 2)))



class Enemy_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=250, level=0, rotation=0, max_rotation_speed=5, weapon=EnemyGun, scrap_count=1, health=2, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, mother_ship=None, image=lambda: images.ENEMY_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, health, armour, shield, shield_delay, shield_recharge, state, image)
        self.scrap_count = scrap_count
        self.mother_ship = mother_ship
        self.mother_ship_patrol = mother_ship
        self.attack_min_dist = 100
        self.attack_max_dist = 400
        self.attack_max_speed = 300
        self.patrol_min_dist = 100
        self.patrol_max_dist = 400
        self.hp = None

    def update(self, delta_time):
        super().update(delta_time)

        distance_to_player = self.distance_to(game.player)

        # Retreat, if far away then patrol
        if self.state == RETREAT:
            self.retreat_state(delta_time)
            if distance_to_player > 1500:
                self.state = PATROL

        # Check if should be retreating
        elif (self.health <= 1 and distance_to_player < 1500 and game.player.health > 5
            and self.mother_ship and len(self.mother_ship.enemy_list) <= 2):

            self.state = RETREAT
            self.retreat_state(delta_time)

        else:
            # Attack state
            if self.state == ATTACK:

                self.attack_entity_state(delta_time, game.player, self.attack_min_dist, self.attack_max_dist, self.attack_max_speed)
                self.group_attack_player()

                if distance_to_player > 1500:  # If too far from player then patrol
                    self.state = PATROL

            elif distance_to_player < 600:  # If close to player then attack
                self.attack_entity_state(delta_time, game.player, self.attack_min_dist, self.attack_max_dist, self.attack_max_speed)
                self.group_attack_player()

            # Check if it should be patroling
            elif self.state == PATROL:
                self.patrol_state(delta_time, self.patrol_min_dist, self.patrol_max_dist, max_speed=self.attack_max_speed/2, mother_ship=self.mother_ship_patrol)

    def damage(self, damage, entity=None):

        if entity and isinstance(entity, Player_Ship):
            self.group_attack_player()

        super().damage(damage)

    def destroy(self):
        super().destroy()

        if self in self.mother_ship.enemy_list:
            self.mother_ship.enemy_list.remove(self)

        if type(self) == Enemy_Ship:
            game.SCORE += 1
        elif type(self) == Drone_Enemy:
            game.SCORE += 1
        elif type(self) == Missile_Ship:
            game.SCORE += 2
        elif type(self) == Mother_Ship:
            game.SCORE += 3

        for _ in range(self.scrap_count):
            scrap = entities.Scrap(self.position, random_vector(random.randint(400, 600)), rotation=random.random() * math.pi * 2)
            game.CHUNKS.add_entity(scrap)

    def group_attack_player(self):
        if self.mother_ship:
            self.mother_ship.group_attack_player()

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (255, 0, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)



class Missile_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=250, level=0, rotation=0, max_rotation_speed=5, explode_countdown=0.1, weapon=EnemyGun, scrap_count=2, health=3, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=0, mother_ship=None, image=lambda: images.MISSILE_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, scrap_count, health, armour, shield, shield_delay, shield_recharge, state, mother_ship, image)
        self.attack_max_speed = 750
        self.explode_radius = 100
        self.explode_damage = 8
        self.explode_countdown = explode_countdown
        self.time_to_explode = 0
        self.exploding = False

        self.particles = effects.missile_ship_trail(self)


    def attack_entity_state(self, delta_time, entity, attack_min_dist, attack_max_dist, attack_max_speed):
        # Set max speed to a higher value
        self.max_speed = attack_max_speed

        distance_to_player = self.distance_to(entity)

        # Rotation
        self.rotate_to(delta_time, self.position.get_angle_to(entity.position), self.max_rotation_speed)

        # Movement
        self.accelerate_in_direction(self.rotation, 2000 * delta_time)

        self.particles.active = True

        if distance_to_player < 60:
            self.exploding = True

        if self.exploding:
            self.time_to_explode += delta_time
            if self.time_to_explode > self.explode_countdown:
                self.explode(self.explode_radius)

    def explode(self, radius):
        self.scrap_count=0

        # Have to create separate list otherwise the set game.CHUNKS.entities will change size while iterating though it
        entities_to_damage = []
        damage_values = []

        for entity in game.CHUNKS.entities:
            if isinstance(entity, Ship):
                distance = entity.distance_to(self)
                if distance < radius:
                    entities_to_damage.append(entity)
                    damage_values.append(1 - distance / self.explode_radius)

        for i, entity in enumerate(entities_to_damage):
            entity.damage(self.explode_damage * damage_values[i])

    def destroy(self):
        super().destroy()
        self.particles.entity = None



class Drone_Enemy(Enemy_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=250, level=0, rotation=0, max_rotation_speed=5, weapon=EnemyGatlingGun, scrap_count=1, health=1, armour=0, shield=2, shield_delay=2, shield_recharge=4, state=PATROL, mother_ship=None, image=lambda: images.DRONE_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, scrap_count, health, armour, shield, shield_delay, shield_recharge, state, mother_ship, image)



class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=100, level=0, rotation=0, max_rotation_speed=1.5, weapon=EnemySniper, scrap_count=3, health=8, armour=0, shield=3, shield_delay=5, shield_recharge=1, state=PATROL, enemy_list=None, current_station=None, image=lambda: images.MOTHER_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, scrap_count, health, armour, shield, shield_delay, shield_recharge, state, self, image)
        if enemy_list is None:
            enemy_list = []
        self.enemy_list = enemy_list

        self.mother_ship_patrol = None
        self.current_station = current_station

        self.attack_min_dist = 300
        self.attack_max_dist = 600
        self.attack_max_speed = 100
        self.patrol_min_dist = 1000
        self.patrol_max_dist = 1500

        self.missile_max_speed = 200
        self.missile_fire_rate = 0.2
        self.reload_time = 1 / self.missile_fire_rate
        self.time_reloading = -4

        # Make start patrol point
        for _ in range(100): # try to find new patrol point, if none have been found after 100 iterations then cry
            self.make_new_patrol_point(self.patrol_min_dist, self.patrol_max_dist, self.position)
            target_position = self.patrol_point

            chunk_pos = target_position // game.CHUNK_SIZE

            if self.check_for_asteroid(chunk_pos) == False:
                break

        # Spawn in enemies
        enemy_spawn_number = random.randint(2, int(4 * (self.level/10 + 1)))

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/3)

            if self.level < 10:
                if random.random() < 0.5:
                    enemy = Drone_Enemy(random_position, Vector(0, 0), level=self.level, mother_ship=self)
                else:
                    enemy = Enemy_Ship(random_position, Vector(0, 0), level=self.level, mother_ship=self)

            else:
                if random.random() < 0.2:
                    enemy = Missile_Ship(random_position, Vector(0, 0), level=self.level, mother_ship=self)
                elif random.random() < 0.4:
                    enemy = Drone_Enemy(random_position, Vector(0, 0), level=self.level, mother_ship=self)
                else:
                    enemy = Enemy_Ship(random_position, Vector(0, 0), level=self.level, mother_ship=self)

            self.enemy_list.append(enemy)

            game.CHUNKS.add_entity(enemy)


    def update(self, delta_time):
        super().update(delta_time)

        self.time_reloading += delta_time


    def attack_entity_state(self, delta_time, entity: entities.Entity, min_dist=300, max_dist=600, max_speed=100):
        super().attack_entity_state(delta_time, entity, min_dist, max_dist, max_speed)

        # Fire Missiles
        if self.level > 9:

            if self.time_reloading >= self.reload_time:

                # Get vector 90 degrees from rotation
                velocity = Vector(math.cos(self.rotation), -math.sin(self.rotation))  # y is positive downward
                velocity.set_magnitude(800)

                # Missile starts with current ship velocity
                velocity1 = self.velocity + velocity
                velocity2 = self.velocity - velocity

                # Missile points in direction of acceleration
                rotation1 = self.rotation - math.pi/2
                rotation2 = self.rotation + math.pi/2

                # Fire 2 missiles, one on either side of the ship
                self.weapon.fire_missile(self.position, velocity1, rotation1)
                self.weapon.fire_missile(self.position, velocity2, rotation2)

                self.time_reloading = 0


    def destroy(self):
        super().destroy()
        if self.current_station:
            self.current_station.entities_to_spawn += 1


    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 0, 255), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)


    def group_attack_player(self):
        for enemy in self.enemy_list:
            if enemy.state != RETREAT:
                enemy.state = ATTACK

        self.state = ATTACK



class Neutral_Ship(AI_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=100, level=0, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=1, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=PATROL, current_station=None, image=lambda: images.NEUTRAL_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, health, armour, shield, shield_delay, shield_recharge, state, image)

        self.mother_ship = None

        self.current_station = current_station
        self.target_station = None

        self.min_patrol_dist = 1000
        self.max_patrol_dist = 4000

        self.patrol_max_speed = 50

    def update(self, delta_time):
        super().update(delta_time)

        if self.state != ATTACK and self.state != ATTACK_ENEMY:
            self.check_nearby_stations(self.current_station)

        if self.state == PATROL_TO_STATION:
            self.patrol_to_station(delta_time)
        elif self.state == PATROL:
            self.patrol_state(delta_time, min_dist=self.min_patrol_dist, max_dist=self.max_patrol_dist, max_speed=self.patrol_max_speed, mother_ship=self.mother_ship)

    def check_nearby_stations(self, current_station):

        if self.target_station:
            self.state = PATROL_TO_STATION

        else:
            # Loop through entities to find friendly station entities
            stations = []
            for entity in game.CHUNKS.entities:
                if type(entity).__name__ == "FriendlyStation":
                    stations.append(entity)

            # Remove current station so it is not an option to travel to
            if current_station in stations:
                stations.remove(current_station)

            # If there is another station(s) to travel to
            if len(stations) > 0:
                weights = []

                # appends values to weights with 1 / dist so that the smaller distances have higher weighting
                for station in stations:
                    dist = (station.position - self.position).magnitude()
                    weights.append(1 / dist)

                # Randomly choose one of the available stations based on the weighting
                random_station = random.choices(stations, weights=weights)
                self.target_station = random_station[0]
                self.intermediate_patrol_point = self.find_intermediate_patrol_point(target_point=self.target_station.position, point_spacing=game.CHUNK_SIZE/2, intermediate_point_distance=game.CHUNK_SIZE)
                self.state = PATROL_TO_STATION

            # If there are no other stations available, just patrol around the current one
            else:
                self.state = PATROL

    def patrol_to_station(self, delta_time, max_speed=50):
        self.max_speed = max_speed

        # If there is an intermediate_patrol_point, fly to it. Else, fly directly to the station
        if self.intermediate_patrol_point:
            self.rotate_to(delta_time, self.position.get_angle_to(self.intermediate_patrol_point), self.max_rotation_speed)
            self.accelerate_in_direction(self.rotation, 300 * delta_time)

            # Once at the intermediate point, re-calculate a new one
            if (self.intermediate_patrol_point - self.position).magnitude() < 50:
                self.intermediate_patrol_point = self.find_intermediate_patrol_point(target_point=self.target_station.position, point_spacing=game.CHUNK_SIZE/2, intermediate_point_distance=game.CHUNK_SIZE)

        else:
            # Move and rotate towards target station
            self.rotate_to(delta_time, self.position.get_angle_to(self.target_station.position), self.max_rotation_speed)
            self.accelerate_in_direction(self.rotation, 300 * delta_time)

            # Checks if it is close enough to the target station to travel to a new one
            if self.distance_to(self.target_station) < 300:
                self.current_station = self.target_station
                self.target_station = None

    def draw(self, win: pygame.Surface, focus_point):
        super().draw(win, focus_point)
        if game.DEBUG_SCREEN:
            pygame.draw.circle(game.WIN, (0, 255, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)

            if self.intermediate_patrol_point:
                pygame.draw.circle(game.WIN, (200, 100, 0), ((self.intermediate_patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.intermediate_patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)



class Neutral_Ship_Cargo(Neutral_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=100, level=0, rotation=0, max_rotation_speed=1, weapon=EnemyGun, health=10, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=PATROL_TO_STATION, neutral_list=None, current_station=None, image=lambda: images.NEUTRAL_SHIP_CARGO) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, health, armour, shield, shield_delay, shield_recharge, state, current_station, image)
        if neutral_list is None:
            neutral_list = []
        self.neutral_list = neutral_list

        self.spawn_neutrals()

    def spawn_neutrals(self):
        for _ in range(2):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            neutral = Neutral_Ship_Fighter(random_position, Vector(0, 0), level=game.CURRENT_SHIP_LEVEL, mother_ship=self)

            self.neutral_list.append(neutral)

            game.CHUNKS.add_entity(neutral)

    def damage(self, damage, entity=None):
        if entity and isinstance(entity, Ship):

            if isinstance(entity, Player_Ship):
                self.group_attack_player()

            if isinstance(entity, Enemy_Ship):
                self.group_attack_enemy()

        super().damage(damage)

    def group_attack_player(self):
        for neutral in self.neutral_list:
            if neutral.state != RETREAT:
                neutral.state = ATTACK

    def group_attack_enemy(self):
        for neutral in self.neutral_list:
            if neutral.state != RETREAT:
                neutral.state = ATTACK_ENEMY

    def destroy(self):
        super().destroy()
        if self.current_station:
            self.current_station.entities_to_spawn += 1



class Neutral_Ship_Fighter(Neutral_Ship):
    def __init__(self, position: Vector, velocity=Vector(0, 0), max_speed=100, level=0, rotation=0, max_rotation_speed=5, weapon=EnemyGun, health=3, armour=0, shield=0, shield_delay=1, shield_recharge=1, state=PATROL_TO_STATION, mother_ship=None, current_station=None, image=lambda: images.NEUTRAL_SHIP) -> None:
        super().__init__(position, velocity, max_speed, level, rotation, max_rotation_speed, weapon, health, armour, shield, shield_delay, shield_recharge, state, current_station, image)

        self.mother_ship: Neutral_Ship_Cargo = mother_ship

        self.min_patrol_dist = 100
        self.max_patrol_dist = 400

        self.patrol_max_speed = 100

        self.recent_enemy = None

    def update(self, delta_time):
        super().update(delta_time)

        if self.state == ATTACK:
            if self.distance_to(game.player) < 1000:
                self.attack_entity_state(delta_time, entity=game.player)
            elif self.mother_ship in game.CHUNKS.entities:
                self.target_station = self.mother_ship.target_station
                self.state = PATROL_TO_STATION
            else:
                self.state = PATROL

        elif self.state == ATTACK_ENEMY:
            if self.recent_enemy in game.CHUNKS.entities:
                self.attack_entity_state(delta_time, entity=self.recent_enemy)
            elif self.mother_ship in game.CHUNKS.entities:
                self.target_station = self.mother_ship.target_station
                self.state = PATROL_TO_STATION
            else:
                self.state = PATROL

    def damage(self, damage, entity=None):
        if entity and isinstance(entity, Ship):

            if isinstance(entity, Player_Ship):
                self.mother_ship.group_attack_player()

            elif isinstance(entity, Enemy_Ship):
                self.mother_ship.group_attack_enemy()

        super().damage(damage)
