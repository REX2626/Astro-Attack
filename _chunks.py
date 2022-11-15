from objects import Vector, Object
import random



class Chunks():
    def __init__(self) -> None:
        global CHUNK_DISTANCE, CHUNK_SIZE
        from main import CHUNK_DISTANCE, CHUNK_SIZE
        self.list = {}
        self.entities: set[Object] = set() # The currently loaded entities

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
                    self.list[position] = Chunk(Vector(position[0], position[1]))

                # Load entities in loaded chunks
                self.entities.update(self.get_chunk(position).entities)

    def get_chunk(self, position: tuple[float, float]) -> "Chunk":

        # Create chunk, if chunk hasn't been generated
        if position not in self.list:
            self.list[position] = Chunk(Vector(position[0], position[1]))

        return self.list[position]

    def add_entity(self, entity: Object):

        chunk_coords = entity.position // CHUNK_SIZE

        self.get_chunk(chunk_coords.to_tuple()).entities.add(entity)



class Chunk():
    def __init__(self, position) -> None:
        self.position = position
        self.entities = set()
        self.generate()

    def generate(self):
        
        for _ in range(3):

            random_position = Vector(random.randint(self.position.x * CHUNK_SIZE, self.position.x * CHUNK_SIZE + CHUNK_SIZE - 1), random.randint(self.position.y * CHUNK_SIZE, self.position.y * CHUNK_SIZE + CHUNK_SIZE - 1))
            size = Vector(36, 40)
            self.entities.add(

                # Alien
                Object(random_position, size, image="assets/alien.png")
            )

    def in_chunk(self, entity: Object):
        return self.position * CHUNK_DISTANCE <= entity.position and self.position * CHUNK_DISTANCE + CHUNK_DISTANCE >= entity.position