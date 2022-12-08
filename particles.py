from objects import Vector, random_vector
import game
import pygame
import random



draw_circle = pygame.draw.circle
class Particle():
    def __init__(self, position: Vector, velocity: Vector, start_size: float, end_size: float, colour: tuple, lifetime: float) -> None:
        self.position = position
        self.velocity = velocity
        self.start_size = start_size
        self.end_size = end_size
        self.colour = colour
        self.lifetime = lifetime
        self.time_alive = 0
        self.current_size = start_size
        self.size_difference = end_size - start_size

    def move(self, delta_time):
        # Remove self from current chunk
        original_chunk = game.CHUNKS.get_chunk(self)

        # Move self
        self.position += self.velocity * delta_time

        # Add self to the chunk it should now be in
        new_chunk = game.CHUNKS.get_chunk(self)

        if original_chunk != new_chunk:
            original_chunk.entities.remove(self)
            new_chunk.entities.add(self)

    def update_time(self, delta_time):
        self.time_alive += delta_time

        self.current_size += self.size_difference * (delta_time / self.lifetime)

        if self.time_alive > self.lifetime:
            game.CHUNKS.remove_entity(self)

    def update(self, delta_time):
        self.move(delta_time)
        self.update_time(delta_time)

    def draw(self, WIN, focus_point):
        draw_circle(WIN, self.colour, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y), max(1, self.current_size * ZOOM))

    def unload(self):
        game.CHUNKS.remove_entity(self)



class ParticleSystem():
    def __init__(self, position, start_size=5, end_size=0, colour=(255, 255, 255), max_colour=None, duration=5, lifetime=2, frequency=2, speed=20, speed_variance=None) -> None:
        self.position = position
        self.start_size = start_size
        self.end_size = end_size
        if not max_colour: max_colour = colour
        self.max_colour = max_colour
        self.min_colour = colour
        self.duration = duration
        self.lifetime = lifetime
        self.time_alive = 0
        self.period = 1 / frequency
        self.speed = speed
        self.delay = 0
        self.speed_variance = speed_variance

        game.CHUNKS.add_entity(self)

        global ZOOM
        ZOOM = game.ZOOM

        global CENTRE_POINT_X, CENTRE_POINT_Y
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y

        if not duration:
            self.burst()

    def update(self, delta_time):
        self.delay += delta_time
        self.time_alive += delta_time

        if self.delay > self.period:

            count = self.delay // self.period

            self.delay -= self.period * count

            for _ in range(int(count)):
                self.spawn()

        if self.time_alive > self.duration:
            game.CHUNKS.remove_entity(self)

    def draw(self, WIN, red_ship_pos):
        pass

    def burst(self):
        for _ in range(int(1/self.period)):
            self.spawn()
        game.CHUNKS.remove_entity(self)

    def spawn(self):
        if self.speed_variance:
            speed = self.speed + (random.random()*2-1) * self.speed_variance
        else:
            speed = self.speed

        r1, r2 = self.min_colour[0], self.max_colour[0]
        g1, g2 = self.min_colour[1], self.max_colour[1]
        b1, b2 = self.min_colour[2], self.max_colour[2]
        colour = (random.randint(r1, r2), random.randint(g1, g2), random.randint(b1, b2))

        game.CHUNKS.add_entity(
            Particle(self.position, random_vector(speed), start_size=self.start_size, end_size=self.end_size, colour=colour, lifetime=self.lifetime)
            )