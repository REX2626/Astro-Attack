import game
import random
import math

def set_seed(x, y):
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
