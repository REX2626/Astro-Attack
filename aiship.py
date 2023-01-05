from objects import Vector
from entities import Ship, Asteroid
from objects import random_vector
import images
import game
import random
import pygame # rex keep this here for debugging reasons

class Enemy_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=250, rotation=0, fire_rate=1, health=3, state=0, mother_ship=None, image=images.GREEN_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, health, image)
        self.state = state
        self.mother_ship = mother_ship
        self.patrol_point = random_vector(random.randint(100, 400)) + self.mother_ship.position

    def update(self, delta_time):
        super().update(delta_time)

        if self.distance_to(game.red_ship) < 600 or self.state == 1:
            self.attack_state(delta_time)
            self.enemy_spotted()
        else:
            self.patrol_state(delta_time)

        if self.state == 1 and self.distance_to(game.red_ship) > 1000:
            self.state = 0

    # DEBUG DRAW PATROL POINTS

    # def draw(self, win: pygame.Surface, focus_point):
    #     super().draw(win, focus_point)
    #     pygame.draw.circle(game.WIN, (255, 0, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        
        
    def patrol_state(self, delta_time):
        self.max_speed = 150
        
        target_position = self.patrol_point
        direction_vector = target_position - self.position

        distance = (direction_vector).magnitude()

        target_to_mothership_distance = (target_position - self.mother_ship.position).magnitude()

        if distance < 50 or target_to_mothership_distance > 500:   # Check if the enemy has reached the patrol point
            self.patrol_point = random_vector(random.randint(100, 400)) + self.mother_ship.position
            target_position = self.patrol_point
        
        #self.accelerate_to_point(target_position, 600 * delta_time, 1000 * delta_time)
        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle_to(target_position))

    def make_new_patrol_point(self):
        self.patrol_point = random_vector(random.randint(100, 400)) + self.mother_ship.position
    
    def attack_state(self, delta_time):
        self.max_speed = 300
        self.set_rotation(self.position.get_angle_to(game.red_ship.position))
        self.shoot()
        self.accelerate_in_direction(game.red_ship.position, 400 * delta_time)

    def enemy_spotted(self):
        self.mother_ship.alert_group()



class Mother_Ship(Enemy_Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, fire_rate=1, health=10, state=0, enemy_list=None, image=images.MOTHER_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, health, state, self, image)
        if enemy_list is None:
            enemy_list = []
        self.enemy_list = enemy_list

        while True:
            self.patrol_point = random_vector(random.randint(1000, 1500)) + self.position
            target_position = self.patrol_point

            chunk_pos = target_position // game.CHUNK_SIZE

            if self.check_for_asteroid(chunk_pos) == False:
                break
            else:
                continue

        enemy_spawn_number = random.randint(3, 6)

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            enemy = Enemy_Ship(random_position, Vector(0, 0), mother_ship=self)
            self.enemy_list.append(enemy)
            
            game.CHUNKS.add_entity(enemy)

    # DEBUG DRAW PATROL POINTS

    # def draw(self, win: pygame.Surface, focus_point):
    #     super().draw(win, focus_point)
    #     pygame.draw.circle(game.WIN, (0, 0, 255), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
    #     pygame.draw.circle(game.WIN, (0, 0, 255), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 600 * game.ZOOM, width=1)
        

    def patrol_state(self, delta_time):
        self.max_speed = 50

        target_position = self.patrol_point
        direction_vector = target_position - self.position
        distance = (direction_vector).magnitude()

        if distance < 50:   # Check if the enemy has reached the patrol point
            while True:
                self.patrol_point = random_vector(random.randint(1000, 1500)) + self.position
                target_position = self.patrol_point

                chunk_pos = target_position // game.CHUNK_SIZE

                if self.check_for_asteroid(chunk_pos) == False:
                    break
                else:
                    continue
        
        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle_to(target_position))

    def check_for_asteroid(self, chunk_pos):
        for y in range(chunk_pos.y-1, chunk_pos.y+2):
            for x in range(chunk_pos.x-1, chunk_pos.x+2):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():
                    if isinstance(entity, Asteroid):

                        return True
                    else:
                        # No Asteroid
                        return False

    def alert_group(self):
        for enemy in self.enemy_list:
            enemy.state = 1
        
        self.state = 1



class Neutral_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed=100, rotation=0, fire_rate=1, health=5, state=0, recent_enemy=None, image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, max_speed, rotation, fire_rate, health, image)
        self.state = state
        self.recent_enemy = recent_enemy
        self.patrol_point = random_vector(random.randint(1000, 4000)) + self.position

    def update(self, delta_time):
        super().update(delta_time)

        if self.state == 0:
            self.patrol_state(delta_time)
        elif self.state == 1:
            self.attack_player_state(delta_time)
        elif self.state == 2:
            self.attack_enemy_state(delta_time)

        if self.state == 1 and self.distance_to(game.red_ship) > 1000:
            self.state = 0

    # DEBUG DRAW PATROL POINTS

    # def draw(self, win: pygame.Surface, focus_point):
    #     super().draw(win, focus_point)
    #     pygame.draw.circle(game.WIN, (0, 255, 0), ((self.patrol_point.x - focus_point.x) * game.ZOOM + game.CENTRE_POINT.x, (self.patrol_point.y - focus_point.y) * game.ZOOM + game.CENTRE_POINT.y), 20 * game.ZOOM)
        
        
    def patrol_state(self, delta_time):
        self.max_speed = 100
        
        target_position = self.patrol_point
        direction_vector = target_position - self.position

        distance = (direction_vector).magnitude()

        chunk_pos = target_position // game.CHUNK_SIZE

        nearby_asteroid = False

        for y in range(chunk_pos.y-1, chunk_pos.y+2):
            for x in range(chunk_pos.x-1, chunk_pos.x+2):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():

                    if isinstance(entity, Asteroid):
                        nearby_asteroid = True
                        break

        if distance < 50 or nearby_asteroid:   # Check if the enemy has reached the patrol point
            self.patrol_point = random_vector(random.randint(1000, 4000)) + self.position
            target_position = self.patrol_point
        
        self.accelerate_in_direction(target_position, 300 * delta_time)
        self.set_rotation(self.position.get_angle_to(target_position))

    def make_new_patrol_point(self):
        self.patrol_point = random_vector(random.randint(1000, 4000)) + self.position
    
    def attack_player_state(self, delta_time):
        self.max_speed = 300
        self.set_rotation(self.position.get_angle_to(game.red_ship.position))
        self.shoot()
        self.accelerate_in_direction(game.red_ship.position, 400 * delta_time)

    def attack_enemy_state(self, delta_time):
        if self.recent_enemy.health > 0:
            self.max_speed = 300
            self.set_rotation(self.position.get_angle_to(self.recent_enemy.position))
            self.shoot()
            self.accelerate_in_direction(self.recent_enemy.position, 400 * delta_time)
        else:
            self.recent_enemy = None
            self.state = 0