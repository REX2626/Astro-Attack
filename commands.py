from aiship import Neutral_Ship
from objects import Vector
import game
import pygame
pygame.init()


"""
HOW TO SET UP COMMAND:
Make a function. If it has any arguements then type in the arguements variable into the function.
Then to initialise the arguements you must set your arguements equal to the list (if one arguement
is needed then set it to the first element). After you must set each variable to the type of variable
that you want it to be.
THIS SOLUTION IS SHIT AND I HOPE TO MAKE IT BETTER IN THE NEAR FUTURE!
"""


# spawns neutral ship at current player position
def spawn_netral_ship(arguements):
    number = arguements[0]

    number = int(number)

    for i in range(number):
        neutral = Neutral_Ship(game.player.position, Vector(0, 0))
                
        game.CHUNKS.add_entity(neutral)


# boosts stats by a lot
def god_mode(arguements):

    max_hp, max_boost = arguements
    max_hp = int(max_hp)
    max_boost = int(max_boost)

    game.MAX_PLAYER_HEALTH = max_hp
    game.player.health = max_hp

    game.MAX_BOOST_AMOUNT = max_boost
    game.player.boost_amount = max_boost