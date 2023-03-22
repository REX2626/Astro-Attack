from objects import Vector, Object, Entity
from entities import Asteroid#, HealthPickup
from station import FriendlyStation, EnemyStation
import random
import game


class Chunks():
    def __init__(self) -> None:
        global LOAD_DISTANCE, CHUNK_SIZE
        LOAD_DISTANCE, CHUNK_SIZE = game.LOAD_DISTANCE, game.CHUNK_SIZE
        self.list = {}
        self.entities: set[Object] = set() # The currently loaded entities

        self.create_initial_chunks()

    def create_initial_chunks(self):
        def func(_):
            pass
        generate = Chunk.generate
        setattr(Chunk, "generate", func)
        for y in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
            for x in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
                chunk = Chunk(Vector(x, y))
                self.list[(x, y)] = chunk
        setattr(Chunk, "generate", generate)

    def update(self, player):
        
        # Turn coordinates into chunk coordinates
        chunk_coords = player.position // CHUNK_SIZE

        # Unload all entities
        original_entities = self.entities
        self.entities = set()

        # Loop through chunks in square around player's position
        for y in range(chunk_coords.y - LOAD_DISTANCE, chunk_coords.y + LOAD_DISTANCE + 1):
            for x in range(chunk_coords.x - LOAD_DISTANCE, chunk_coords.x + LOAD_DISTANCE + 1):
                
                # If chunk hasn't been created, then create a new chunk
                position = (x, y)
                if position not in self.list:
                    self.list[position] = Chunk(Vector(x, y))

                # Load entities in loaded chunks
                self.entities.update(self.get_chunk(position).entities)

        for entity in original_entities.difference(self.entities):
            if hasattr(entity, "unload"):
                entity.unload()

    def get_chunk(self, arg: tuple[int, int] or Object) -> "Chunk":
        """Returns the chunk, arg can be a chunk_coord or an object"""

        # Check if arg is chunk_coord or an entity
        if type(arg) == tuple:
            position = arg
        else:
            position = (arg.position // CHUNK_SIZE).to_tuple()

        # Create chunk, if chunk hasn't been generated
        if position not in self.list:
            self.list[position] = Chunk(Vector(position[0], position[1]))

        return self.list[position]

    def add_entity(self, entity: Object):

        self.get_chunk(entity).entities.add(entity)

    def remove_entity(self, entity: Object):

        self.get_chunk(entity).entities.remove(entity)
        
        if entity in self.entities:
            self.entities.remove(entity)

    # optomized
    def move_entity(self, entity: Entity, delta_time):
        
        original_chunk_pos = (int(entity.position.x // CHUNK_SIZE), int(entity.position.y // CHUNK_SIZE))
        entity.position += entity.velocity * delta_time
        new_chunk_pos = (int(entity.position.x // CHUNK_SIZE), int(entity.position.y // CHUNK_SIZE))

        if new_chunk_pos != original_chunk_pos:
            self.get_chunk(original_chunk_pos).entities.remove(entity)
            self.get_chunk(new_chunk_pos).entities.add(entity)



class Chunk():
    def __init__(self, position) -> None:
        self.position = position
        self.entities = set()
        self.generate()

    def generate(self):

        # elif is used so that ships don't spawn in an asteroid chunk
        # the ships make sure they don't spawn inside a chunk by
        # checking if this chunk is adjoining a chunk with an asteroid in

        if self.adjoining_asteroid_chunk():
            return


        # Health Pickup
        # elif random.random() < 0.1:

        #     self.entities.add(
        #         HealthPickup(self.random_position())
        #     )

        # Asteroid
        elif random.random() < 0.1 and self.adjoining_empty_chunks():
            self.entities.add(

                Asteroid(self.random_position())
            )

        # Enemy Station
        elif random.random() < 0.04 and self.adjoining_empty_chunks():
            self.entities.add(

                EnemyStation(self.random_position())
            )

        # Friendly Station
        elif random.random() < 0.03 and self.adjoining_empty_chunks():
            self.entities.add(

                FriendlyStation(self.random_position())
            )


    def adjoining_asteroid_chunk(self):

        for y in range(self.position.y-1, self.position.y+2):
            for x in range(self.position.x-1, self.position.x+2):

                if (x, y) not in game.CHUNKS.list:
                    continue

                for entity in game.CHUNKS.get_chunk((x, y)).entities:
                    if isinstance(entity, Asteroid):
                        return True

        return False

    def adjoining_empty_chunks(self):

        for y in range(self.position.y-1, self.position.y+2):
            for x in range(self.position.x-1, self.position.x+2):

                if (x, y) not in game.CHUNKS.list:
                    continue

                if len(game.CHUNKS.get_chunk((x, y)).entities) > 0: # check if there are any entities in the chunk
                    return False

        return True

    def random_position(self):
        return Vector(random.randint(self.position.x * CHUNK_SIZE, self.position.x * CHUNK_SIZE + CHUNK_SIZE - 1),
            random.randint(self.position.y * CHUNK_SIZE, self.position.y * CHUNK_SIZE + CHUNK_SIZE - 1))