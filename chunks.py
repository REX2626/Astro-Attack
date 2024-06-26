from __future__ import annotations
from objects import Vector, Object, Entity
from entities import Asteroid
from station import FriendlyStation, EnemyStation
from aiship import Mother_Ship
import random
import game


class Chunks():
    __slots__ = ("list", "entities")
    def __init__(self) -> None:
        self.list = {}
        self.entities: set[Object] = set()  # The currently loaded entities

        self.create_initial_chunks()

    def create_initial_chunks(self) -> None:
        for y in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
            for x in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
                chunk = Chunk(Vector(x, y))
                self.list[(x, y)] = chunk
        self.add_entity(FriendlyStation(position=game.LAST_PLAYER_POS))

    def update(self, player: Entity) -> None:

        # Turn coordinates into chunk coordinates
        chunk_coords = player.position // game.CHUNK_SIZE

        # Unload all entities
        original_entities = self.entities
        self.entities = set()

        # Loop through chunks in square around player's position
        for y in range(chunk_coords.y - game.LOAD_DISTANCE, chunk_coords.y + game.LOAD_DISTANCE + 1):
            for x in range(chunk_coords.x - game.LOAD_DISTANCE, chunk_coords.x + game.LOAD_DISTANCE + 1):

                # If chunk hasn't been created, then create a new chunk
                position = (x, y)
                if position not in self.list:
                    chunk = Chunk(Vector(position[0], position[1]))
                    self.list[position] = chunk
                    chunk.generate()

                # Load entities in loaded chunks
                self.entities.update(self.get_chunk_from_coord(position).entities)

        for entity in original_entities.difference(self.entities):
            if hasattr(entity, "unload"):
                entity.unload()

    def get_chunk(self, arg: tuple[int, int] | Object) -> Chunk:
        """Returns the chunk, arg can be a chunk_coord or an object"""

        # Check if arg is chunk_coord or an entity
        if type(arg) == tuple:
            position = arg
        else:
            position = (int(arg.position.x // game.CHUNK_SIZE), int(arg.position.y // game.CHUNK_SIZE))

        # Create chunk, if chunk hasn't been generated
        if position not in self.list:
            chunk = Chunk(Vector(position[0], position[1]))
            self.list[position] = chunk
            chunk.generate()

        return self.list[position]

    def get_chunk_from_coord(self, position: tuple[int, int]) -> Chunk:
        """Returns the chunk, arg is a chunk_coord"""

        # Create chunk, if chunk hasn't been generated
        if position not in self.list:
            chunk = Chunk(Vector(position[0], position[1]))
            self.list[position] = chunk
            chunk.generate()

        return self.list[position]

    def get_chunk_from_entity(self, entity: Object) -> Chunk:
        """Returns the chunk, arg is an object"""

        # Check if arg is chunk_coord or an entity
        position = (int(entity.position.x // game.CHUNK_SIZE), int(entity.position.y // game.CHUNK_SIZE))

        # Create chunk, if chunk hasn't been generated
        if position not in self.list:
            chunk = Chunk(Vector(position[0], position[1]))
            self.list[position] = chunk
            chunk.generate()

        return self.list[position]

    def add_entity(self, entity: Object) -> None:

        self.get_chunk_from_entity(entity).entities.add(entity)

    def remove_entity(self, entity: Object) -> None:

        self.get_chunk_from_entity(entity).entities.remove(entity)

        if entity in self.entities:
            self.entities.remove(entity)

    # optimized
    def move_entity(self, entity: Entity, delta_time: float) -> None:
        """Moves the entity using it's velocity"""
        original_chunk_pos = (int(entity.position.x // game.CHUNK_SIZE), int(entity.position.y // game.CHUNK_SIZE))
        entity.position += entity.velocity * delta_time
        new_chunk_pos = (int(entity.position.x // game.CHUNK_SIZE), int(entity.position.y // game.CHUNK_SIZE))

        if new_chunk_pos != original_chunk_pos:
            self.get_chunk_from_coord(original_chunk_pos).entities.remove(entity)
            self.get_chunk_from_coord(new_chunk_pos).entities.add(entity)

    # optimized
    def set_position(self, entity: Entity, position: Vector) -> None:
        """Moves the entity to `position`"""
        original_chunk_pos = (int(entity.position.x // game.CHUNK_SIZE), int(entity.position.y // game.CHUNK_SIZE))
        entity.position = position
        new_chunk_pos = (int(entity.position.x // game.CHUNK_SIZE), int(entity.position.y // game.CHUNK_SIZE))

        if new_chunk_pos != original_chunk_pos:
            self.get_chunk_from_coord(original_chunk_pos).entities.remove(entity)
            self.get_chunk_from_coord(new_chunk_pos).entities.add(entity)



class Chunk():
    __slots__ = ("position", "entities", "chance_offset")
    def __init__(self, position: Vector) -> None:
        self.position = position
        self.entities = set()
        self.chance_offset = 0

    def generate(self) -> None:

        # elif is used so that ships don't spawn in an asteroid chunk
        # the ships make sure they don't spawn inside a chunk by
        # checking if this chunk is adjoining a chunk with an asteroid in

        if not self.adjoining_empty_chunks():
            return

        # Asteroid - 10%
        if self.chance(0.1):
            self.entities.add(

                Asteroid(self.random_position())
            )

        # Enemy Station - 2.5%
        elif self.chance(0.025):
            self.entities.add(

                EnemyStation(self.random_position())
            )

        # Friendly Station - 1.7%
        elif self.chance(0.017):
            self.entities.add(

                FriendlyStation(self.random_position())
            )

        # Mother Ship - 1%
        elif self.chance(0.01):
            self.entities.add(

                Mother_Ship(self.position * game.CHUNK_SIZE + game.CHUNK_SIZE/2, level=game.CURRENT_SHIP_LEVEL)
            )


    def chance(self, chance: float) -> bool:
        self.chance_offset += chance
        random.seed(game.SEED + self.position.x*374761393 + self.position.y*668265263)
        return self.chance_offset > random.random()

    def adjoining_asteroid_chunk(self) -> bool:

        for y in range(self.position.y-1, self.position.y+2):
            for x in range(self.position.x-1, self.position.x+2):

                if (x, y) not in game.CHUNKS.list:
                    continue

                for entity in game.CHUNKS.get_chunk_from_coord((x, y)).entities:
                    if isinstance(entity, Asteroid):
                        return True

        return False

    def adjoining_empty_chunks(self) -> bool:

        for y in range(self.position.y-1, self.position.y+2):
            for x in range(self.position.x-1, self.position.x+2):

                if (x, y) not in game.CHUNKS.list:
                    continue

                if len(game.CHUNKS.get_chunk_from_coord((x, y)).entities) > 0: # check if there are any entities in the chunk
                    return False

        return True

    def random_position(self) -> Vector:
        return Vector(random.randint(self.position.x * game.CHUNK_SIZE, self.position.x * game.CHUNK_SIZE + game.CHUNK_SIZE - 1),
            random.randint(self.position.y * game.CHUNK_SIZE, self.position.y * game.CHUNK_SIZE + game.CHUNK_SIZE - 1))
