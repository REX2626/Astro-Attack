# Import all objects in case they are used in a command
from aiship import Neutral_Ship_Cargo, Enemy_Ship, Drone_Enemy, Missile_Ship,  Mother_Ship, Neutral_Ship_Fighter
from station import FriendlyStation, EnemyStation
from objects import Vector
from entities import Entity, Scrap, Asteroid
import game
import random
import pygame


# Spawns entity
def spawn_entity(arguments):

    entity_class, frequency = arguments

    for _ in range(frequency):
        entity = entity_class(game.player.position + Vector(random.random() - 0.5, random.random() - 0.5))

        game.CHUNKS.add_entity(entity)


# boosts stats by a lot
def god_mode(arguments=(10_000, 10_000)):
    print(arguments)
    max_hp, max_boost = arguments

    game.MAX_PLAYER_HEALTH = max_hp
    game.player.health = max_hp

    game.MAX_BOOST_AMOUNT = max_boost
    game.player.boost_amount = max_boost


def change_max_zoom(zoom=0.1):
    game.CURRENT_MIN_ZOOM = zoom

def add_score(score=100):
    game.SCORE += score
