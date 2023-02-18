from objects import Object
from entities import Ship, entity_collision
import images
import game
import math
import pygame



class Station(Object):
    def __init__(self, position, rotation, image=images.STATION) -> None:
        super().__init__(position, pygame.transform.rotate(pygame.transform.scale_by(image, 10), rotation / math.pi * 180))
        self.rotation = rotation
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        super().update(delta_time)

        chunk_pos = self.position // game.CHUNK_SIZE

        for y in range(chunk_pos.y-2, chunk_pos.y+3):
            for x in range(chunk_pos.x-2, chunk_pos.x+3):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():

                    if isinstance(entity, Ship):

                        entity_collision(self, entity, delta_time)