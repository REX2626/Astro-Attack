from aiship import Neutral_Ship_Cargo
from station import FriendlyStation
from objects import Vector
import game
import pygame




# spawns neutral ship at current player position
def spawn_netral_ship(number):

    for i in range(number):
        neutral = Neutral_Ship_Cargo(game.player.position, Vector(0, 0))
                
        game.CHUNKS.add_entity(neutral)


def spawn_station():

    station = FriendlyStation(game.player.position)

    game.CHUNKS.add_entity(station)


# boosts stats by a lot
def god_mode(arguments):

    max_hp, max_boost = arguments

    game.MAX_PLAYER_HEALTH = max_hp
    game.player.health = max_hp

    game.MAX_BOOST_AMOUNT = max_boost
    game.player.boost_amount = max_boost


def change_max_zoom(zoom):
    game.CURRENT_MIN_ZOOM = zoom