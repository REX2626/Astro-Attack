import random
import game

def retrieve_chunk_value(x, y):
    random.seed(game.SEED1 + x + ((game.SEED2 + y) * 1000))
    return random.random()