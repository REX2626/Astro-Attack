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
        ZOOM = game.ZOOM
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y
        radius = max(1, self.current_size * ZOOM*self.bloom)
        surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        max_radius = int(self.current_size*ZOOM*self.bloom)
        min_radius = int(self.current_size*ZOOM)

        # draw circle going from out to in
        for radius1 in range(max_radius, min_radius, -1): # e.g. range(15, 10, -1)
            amount_done = (max_radius-radius1) / (max_radius-min_radius)
            draw_circle(surface, (*self.colour, amount_done*255), (radius, radius), radius1, width=2)

        WIN.blit(surface, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X - radius, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y - radius))

        draw_circle(WIN, self.colour, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y), max(1, self.current_size * ZOOM))



class ParticleSystem():
    """
    position can be a Vector or an Entity
    if entity: the ParticleSystem can be turned on and off by setting the active attribute to True or False
    entity_offset is a function that takes in the Entity and returns a Vector
    if entity: initial_velocity is a function that is called with the entity as an input
    NOTE: if entity: when entity is destroyed - set ParticleSystem.entity = None
    """
    def __init__(self, position, entity_offset=lambda x: Vector(0, 0), z=1, start_size=5, max_start_size=None, end_size=0, colour=(255, 255, 255), max_colour=None, bloom=0, duration=5, lifetime=2, frequency=2, speed=20, speed_variance=None, initial_velocity=Vector(0, 0)) -> None:
        self.entity_offset = entity_offset
        self.z = z
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

        if not isinstance(position, Vector): # if position is an Entity
            self.entity = position
            self.position = self.entity.position
            self.active = False
        else:
            self.position = position
            self.entity = None

        self.particles: list[Particle] = []

        game.CHUNKS.add_entity(self)

        if not duration:
            self.duration = 0
            if not self.entity:
                self.burst()

    def update(self, delta_time):
        self.delay += delta_time
        self.time_alive += delta_time

        for particle in self.particles:
            particle.update(delta_time, self)
        
        if self.entity and self.entity in game.CHUNKS.entities:
            self.previous_position = self.position
            game.CHUNKS.remove_entity(self)
            self.position = self.entity.position + self.entity_offset(self.entity)
            game.CHUNKS.add_entity(self)

        if not self.entity and self.time_alive > self.duration: # check if the System's life time is over

            if not self.particles: # if there are no more particles, then the System can be destroyed
                game.CHUNKS.remove_entity(self)
            return
        
        if self.entity and not self.active: # if not active: don't spawn particles
            self.delay = 0
            return

        if self.delay > self.period: # if the System should stil be alive AND the spawning delay is over, then spawn in more particles

            count = self.delay // self.period

            self.delay -= self.period * count

            if self.entity:
                vec = self.position - self.previous_position
                for i in range(1, int(count)+1):
                    position = self.previous_position + (i/count) * vec + (1-i/count) * self.initial_velocity(self.entity) * delta_time
                    start_size = self.start_size + (self.end_size - self.start_size) * (delta_time / self.lifetime)
                    self.spawn(position, start_size)

            else:
                for _ in range(int(count)):
                    self.spawn(self.position, self.start_size)

    def draw(self, WIN, player_pos):
        
        for particle in self.particles:
            particle.draw(WIN, player_pos)

    def burst(self):
        for _ in range(int(1/self.period)):
            self.spawn(self.position, self.start_size)

    def spawn(self, position, start_size):
        if self.speed_variance:
            speed = self.speed + (random.random()*2-1) * self.speed_variance
        else:
            speed = self.speed

        start_size = random.random() * (self.max_start_size - start_size) + start_size

        r1, r2 = self.min_colour[0], self.max_colour[0]
        g1, g2 = self.min_colour[1], self.max_colour[1]
        b1, b2 = self.min_colour[2], self.max_colour[2]
        colour = (random.randint(r1, r2), random.randint(g1, g2), random.randint(b1, b2))
        if self.entity:
            initial_velocity = self.initial_velocity(self.entity)
        else:
            initial_velocity = self.initial_velocity

        self.particles.append(
            Particle(position, random_vector(speed) + initial_velocity, start_size=start_size, end_size=self.end_size, colour=colour, bloom=self.bloom, lifetime=self.lifetime)
            )