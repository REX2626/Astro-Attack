from objects import Vector, Object, Asteroid, Enemy_Ship
import random
import game



class Chunks():
    def __init__(self) -> None:
        global CHUNK_DISTANCE, CHUNK_SIZE
        CHUNK_DISTANCE, CHUNK_SIZE = game.CHUNK_DISTANCE, game.CHUNK_SIZE
        self.list = {}
        self.entities: set[Object] = set() # The currently loaded entities

        self.create_initial_chunks()

    def create_initial_chunks(self):
        for y in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
            for x in range(-game.SPAWN_SIZE, game.SPAWN_SIZE):
                chunk = Chunk(Vector(x, y))
                chunk.entities.clear()
                self.list[(x, y)] = chunk

    def update(self, player):
        
        # Turn coordinates into chunk coordinates
        chunk_coords = player.position // CHUNK_SIZE

        # Unload all entities
        self.entities = set()

        # Loop through chunks in square around player's position
        for y in range(chunk_coords.y - CHUNK_DISTANCE, chunk_coords.y + CHUNK_DISTANCE + 1):
            for x in range(chunk_coords.x - CHUNK_DISTANCE, chunk_coords.x + CHUNK_DISTANCE + 1):
                
                # If chunk hasn't been created, then create a new chunk
                position = (x, y)
                if position not in self.list:
                    self.list[position] = Chunk(Vector(x, y))

                # Load entities in loaded chunks
                self.entities.update(self.get_chunk(position).entities)

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



class Chunk():
    def __init__(self, position) -> None:
        self.position = position
        self.entities = set()
        self.generate()

    def generate(self):
        
        # Enemy Ship
        # 20% chance of spawning
        if random.random() < 0.2:

            random_position = Vector(random.randint(self.position.x * CHUNK_SIZE, self.position.x * CHUNK_SIZE + CHUNK_SIZE - 1), random.randint(self.position.y * CHUNK_SIZE, self.position.y * CHUNK_SIZE + CHUNK_SIZE - 1))
            self.entities.add(

                # Enemy_Ship
                Enemy_Ship(random_position, Vector(0, 0))
            )

        # Asteroid
        # 10% chance of spawning
        if random.random() < 0.1:

            random_position = Vector(random.randint(self.position.x * CHUNK_SIZE, self.position.x * CHUNK_SIZE + CHUNK_SIZE - 1), random.randint(self.position.y * CHUNK_SIZE, self.position.y * CHUNK_SIZE + CHUNK_SIZE - 1))
            self.entities.add(

                Asteroid(random_position)
            )