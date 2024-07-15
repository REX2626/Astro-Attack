"""
Main file for the interior of stations and ships
Displays graphics of rooms and corridors
Controls character and enemies

There is no zoom, so the coordinates are equal to pixels
"""
from __future__ import annotations
from objects import Vector
import game
from time import perf_counter
import pygame



def main() -> None:
    """
    Main loop for interior
    """
    delta_time = 1
    character = Character(Vector(0, 0))
    people = [character]
    while True:
        time1 = perf_counter()

        handle_player_input(character, delta_time)

        update_people(people, delta_time)

        draw_window(people)

        handle_events()

        time2 = perf_counter()
        delta_time = time2 - time1


def handle_player_input(character: Character, delta_time: float) -> None:
    """
    Handle inputs from user to control character
    """
    keys_pressed = pygame.key.get_pressed()

    if keys_pressed[pygame.K_w]:
        character.move_up()

    if keys_pressed[pygame.K_s]:
        character.move_down()

    if keys_pressed[pygame.K_a]:
        character.move_left()

    if keys_pressed[pygame.K_d]:
        character.move_right()


def update_people(people: list[Character], delta_time: float) -> None:
    for person in people:
        person.update(delta_time)


def draw_window(people: list[Character]) -> None:
    """
    Draw window
    """
    game.WIN.fill(game.BLACK)

    for person in people:
        person.draw()

    pygame.display.update()


def handle_events() -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()


class Character():
    def __init__(self, position: Vector) -> None:
        self.position = position

        self.velocity = Vector(0, 0)
        self.speed = 200

    def move(self, velocity: Vector) -> None:
        self.velocity += velocity

    def move_up(self) -> None:
        self.move(Vector(0, -1))

    def move_down(self) -> None:
        self.move(Vector(0, 1))

    def move_left(self) -> None:
        self.move(Vector(-1, 0))

    def move_right(self) -> None:
        self.move(Vector(1, 0))

    def update(self, delta_time: float) -> None:
        self.position += self.velocity.with_magnitude(self.speed) * delta_time
        self.velocity = Vector(0, 0)

    def draw(self) -> None:
        pygame.draw.circle(game.WIN, (60, 60, 60), self.position.to_tuple(), 20)
