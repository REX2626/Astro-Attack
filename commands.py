from aiship import Neutral_Ship, Enemy_Ship
from objects import Vector
from entities import Entity
from player import Player_Ship
import game
import random


# Spawns entity
def spawn_entity(arguments):
    entity_class, frequency = arguments

    for _ in range(frequency):
        entity = entity_class(game.player.position + Vector(random.random() - 0.5, random.random() - 0.5))

        game.CHUNKS.add_entity(entity)


# boosts stats by a lot
def god_mode(arguments=(10_000, 10_000)):

    max_hp, max_boost = arguments

    game.MAX_PLAYER_HEALTH = max_hp
    game.player.health = max_hp

    game.MAX_BOOST_AMOUNT = max_boost
    game.player.boost_amount = max_boost


def change_max_zoom(zoom=0.1):
    game.CURRENT_MIN_ZOOM = zoom


def add_score(score=100):
    game.SCORE += score


def kill(type: str = ""):
    if type == "":
        for entity in game.CHUNKS.entities.copy():
            if isinstance(entity, Entity) and not isinstance(entity, Player_Ship):
                game.CHUNKS.remove_entity(entity)

    elif type == "neutral":
        for entity in game.CHUNKS.entities.copy():
            if isinstance(entity, Neutral_Ship):
                game.CHUNKS.remove_entity(entity)

    elif type == "enemy":
        for entity in game.CHUNKS.entities.copy():
            if isinstance(entity, Enemy_Ship):
                game.CHUNKS.remove_entity(entity)


def teleport(position: tuple[float, float]):
    game.CHUNKS.set_position(game.player, Vector(*position))
