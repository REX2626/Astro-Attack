from objects import Vector, Object
import random



class Chunks():
    def __init__(self) -> None:
        global CHUNK_DISTANCE, CHUNK_SIZE
        from main import CHUNK_DISTANCE, CHUNK_SIZE
        self.list = {}
        self.entities = set()

    def update(self, player):
        
        # Turn coordinates into chunk coordinates
        chunk_coords = round(player.position // CHUNK_SIZE)

        # Loop through chunks in square around player's position
        for y in range(chunk_coords.y - CHUNK_DISTANCE, chunk_coords.y + CHUNK_DISTANCE + 1):
            for x in range(chunk_coords.x - CHUNK_DISTANCE, chunk_coords.x + CHUNK_DISTANCE + 1):
                
                # If chunk hasn't been created, then create a new chunk
                position = (x, y)
                if position not in self.list:
                    self.list[position] = self.create_chunk(Vector(position[0], position[1]))

    def create_chunk(self, position):
        new_chunk = Chunk(position)
        self.entities.update(new_chunk.entities)
        return new_chunk



class Chunk():
    def __init__(self, position) -> None:
        self.position = position
        self.entities = []
        self.generate()

    def generate(self):
        
        for _ in range(3):

            random_position = Vector(random.randint(self.position.x * CHUNK_SIZE, self.position.x * CHUNK_SIZE + CHUNK_SIZE), random.randint(self.position.y * CHUNK_SIZE, self.position.y * CHUNK_SIZE + CHUNK_SIZE))
            size = Vector(36, 40)
            self.entities.append(

                # Alien
                Object(random_position, size, image="assets/alien.png")
            )