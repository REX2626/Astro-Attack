from objects import Vector, random_vector
import game
import pygame
import random



draw_circle = pygame.draw.circle
class Particle():
    def __init__(self, position: Vector, velocity: Vector, start_size: float, end_size: float, colour: tuple, bloom: int, lifetime: float) -> None:
        self.position = position
        self.velocity = velocity
        self.start_size = start_size
        self.end_size = end_size
        self.colour = colour
        self.bloom = bloom
        self.lifetime = lifetime
        self.time_alive = 0
        self.current_size = start_size
        self.size_difference = end_size - start_size

    def update_time(self, delta_time, system: "ParticleSystem"):
        self.time_alive += delta_time

        self.current_size += self.size_difference * (delta_time / self.lifetime)

        if self.time_alive > self.lifetime:
            system.particles.remove(self)

    def update(self, delta_time, system):
        # optomized
        self.position = Vector(self.position.x + self.velocity.x * delta_time, self.position.y + self.velocity.y * delta_time)
        self.update_time(delta_time, system)

    def draw(self, WIN, focus_point):
        radius = max(1, self.current_size * ZOOM*self.bloom)
        surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        max_radius = int(self.current_size*ZOOM*self.bloom)
        min_radius = int(self.current_size*ZOOM)

        # draw circle going from out to in
        for radius1 in range(max_radius*2, min_radius*2, -1): # e.g. range(15, 10, -1), radius*2 so that it can be x.5
            radius1 = radius1/2
            amount_done = (max_radius-radius1) / (max_radius-min_radius)
            draw_circle(surface, (*self.colour, amount_done*255), (radius, radius), radius1, width=2)

        WIN.blit(surface, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X - radius, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y - radius))

        draw_circle(WIN, self.colour, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y), max(1, self.current_size * ZOOM))



class ParticleSystem():
    def __init__(self, position, start_size=5, max_start_size=None, end_size=0, colour=(255, 255, 255), max_colour=None, bloom=0, duration=5, lifetime=2, frequency=2, speed=20, speed_variance=None, initial_velocity=Vector(0, 0)) -> None:
        self.position = position
        if not max_start_size: max_start_size = start_size
        self.start_size = start_size
        self.max_start_size = max_start_size
        self.end_size = end_size
        if not max_colour: max_colour = colour
        self.max_colour = max_colour
        self.min_colour = colour
        self.bloom = bloom
        self.duration = duration
        self.lifetime = lifetime
        self.time_alive = 0
        self.period = 1 / frequency
        self.speed = speed
        self.delay = 0
        self.speed_variance = speed_variance
        self.initial_velocity = initial_velocity

        self.particles: list[Particle] = []

        game.CHUNKS.add_entity(self)

        global ZOOM
        ZOOM = game.ZOOM

        global CENTRE_POINT_X, CENTRE_POINT_Y
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y

        if not duration:
            self.duration = 0
            self.burst()

    def update(self, delta_time):
        self.delay += delta_time
        self.time_alive += delta_time

        for particle in self.particles:
            particle.update(delta_time, self)

        if self.time_alive > self.duration: # check if the System's life time is over

            if not self.particles: # if there are no more particles, then the System can be destroyed
                game.CHUNKS.remove_entity(self)

        elif self.delay > self.period: # if the System should stil be alive AND the spawning delay is over, then spawn in more particles

            count = self.delay // self.period

            self.delay -= self.period * count

            for _ in range(int(count)):
                self.spawn()

    def draw(self, WIN, player_pos):
        
        for particle in self.particles:
            particle.draw(WIN, player_pos)

    def burst(self):
        for _ in range(int(1/self.period)):
            self.spawn()

    def spawn(self):
        if self.speed_variance:
            speed = self.speed + (random.random()*2-1) * self.speed_variance
        else:
            speed = self.speed

        start_size = random.randint(self.start_size, self.max_start_size)

        r1, r2 = self.min_colour[0], self.max_colour[0]
        g1, g2 = self.min_colour[1], self.max_colour[1]
        b1, b2 = self.min_colour[2], self.max_colour[2]
        colour = (random.randint(r1, r2), random.randint(g1, g2), random.randint(b1, b2))

        self.particles.append(
            Particle(self.position, random_vector(speed) + self.initial_velocity, start_size=start_size, end_size=self.end_size, colour=colour, bloom=self.bloom, lifetime=self.lifetime)
            )