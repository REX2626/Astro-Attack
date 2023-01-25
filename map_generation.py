import random
import game
import math

def retrieve_chunk_value(x, y):
    f = math.floor
    frac = lambda x: x - f(x)
    random.seed(
        f( math.pi * 190000 * 
        x * y * frac(
            game.SEED * math.pi
            + frac(
                x - y * math.e - 79070.91433
            ) * f(
                math.pi * 420 * game.SEED
            )
        )
        )
    )
    return random.random()