from aiship import Neutral_Ship
from objects import Vector
import game
import pygame
pygame.init()



# spawns neutral ship at current player position
def spawn_netral_ship():
    neutral = Neutral_Ship(game.player.position, Vector(0, 0))
            
    game.CHUNKS.add_entity(neutral)


# boosts stats by a lot
def god_mode():
    game.MAX_PLAYER_HEALTH = 1000
    game.player.health = 1000

    game.MAX_BOOST_AMOUNT = 1000
    game.player.boost_amount = 1000

    game.MAX_PLAYER_SPEED = 5000