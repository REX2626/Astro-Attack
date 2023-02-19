from objects import Object
from entities import Ship, Bullet, entity_collision
from objects import random_vector, Vector
from aiship import Mother_Ship, Neutral_Ship
import images
import particles
import game
import math
import pygame
import random



class Station(Object):
    def __init__(self, position, rotation, image=images.STATION) -> None:
        super().__init__(position, pygame.transform.rotate(image, rotation / math.pi * 180))
        self.rotation = rotation
        self.mask = pygame.mask.from_surface(self.image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, delta_time):
        super().update(delta_time)

        chunk_pos = self.position // game.CHUNK_SIZE

        for y in range(chunk_pos.y-2, chunk_pos.y+3):
            for x in range(chunk_pos.x-2, chunk_pos.x+3):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():

                    if isinstance(entity, Ship):

                        #entity_collision(self, entity, delta_time)
                        return

                    elif isinstance(entity, Bullet):
                        entity_mask = pygame.mask.from_surface(entity.image)

                        x_offset = (entity.position.x - entity.image.get_width()/2) - (self.position.x - self.image.get_width()/2)
                        y_offset = (entity.position.y - entity.image.get_height()/2) - (self.position.y - self.image.get_height()/2)

                        if self.mask.overlap(entity_mask, (x_offset, y_offset)):
                            entity.unload() # if bullet collides with asteroid then destroy bullet
                            particles.ParticleSystem(entity.position, start_size=3, max_start_size=5, end_size=1, colour=(200, 0, 0), max_colour=(255, 160, 0), duration=None, lifetime=0.6, frequency=int(30*entity.damage+1), speed=120, speed_variance=40)



class FriendlyStation(Station):
    def __init__(self, position, rotation, image=images.STATION) -> None:
        super().__init__(position, rotation, image)

        # Spawn in neutral ships
        enemy_spawn_number = random.randint(1, 3)

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            neutral = Neutral_Ship(random_position, Vector(0, 0), current_station=self)
            
            game.CHUNKS.add_entity(neutral)



class EnemyStation(Station):
    def __init__(self, position, rotation, image=images.STATION) -> None:
        super().__init__(position, rotation, image)

        # Spawn in enemies
        enemy_spawn_number = random.randint(1, 2)

        for _ in range(enemy_spawn_number):

            random_position = self.position + random_vector(game.CHUNK_SIZE/2)

            enemy = Mother_Ship(random_position, Vector(0, 0))
            
            game.CHUNKS.add_entity(enemy)