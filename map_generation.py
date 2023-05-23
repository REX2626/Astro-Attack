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

offset = 0

def reset_chance(pos):
    global offset, x, y
    offset = 0
    x, y = pos.x, pos.y
    if not x: x = 1

def chance(chance):
    global offset
    offset += chance
    random.seed(game.SEED + x*374761393 + y*668265263)
    return offset > random.random()
