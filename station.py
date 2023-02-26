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
    def __init__(self, position, rotation, max_entities=1, entity_type=Neutral_Ship, image=images.STATION) -> None:
        super().__init__(position, pygame.transform.rotate(image, rotation / math.pi * 180))
        self.rotation = rotation
        self.max_entities = max_entities
        self.entity_type = entity_type

        self.mask = pygame.mask.from_surface(self.image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        enemy_spawn_number = random.randint(1, self.max_entities)

        for _ in range(enemy_spawn_number):
            self.spawn_entity(self.entity_type)

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
    
                            
    def spawn_entity(self, entity_type):
        random_position = self.position + random_vector(game.CHUNK_SIZE/2)

        entity = entity_type(random_position, Vector(0, 0), current_station=self)
        
        game.CHUNKS.add_entity(entity)



class FriendlyStation(Station):
    def __init__(self, position, rotation, max_entities=3, entity_type=Neutral_Ship, image=images.STATION) -> None:
        super().__init__(position, rotation, max_entities, entity_type, image)



class EnemyStation(Station):
    def __init__(self, position, rotation, max_entities=2, entity_type=Mother_Ship, image=images.STATION) -> None:
        super().__init__(position, rotation, max_entities, entity_type, image)