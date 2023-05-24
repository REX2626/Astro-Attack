from objects import Entity, Vector, random_vector
import game
import random
import pygame



draw_circle = pygame.draw.circle

class ParticleSystem():
    """
    Creates a controller to spawn particles

    NOTE: Automatically adds this system to game.CHUNKS

    Parameters:

        `position` (Vector | Entity): If Vector then System is stationary, if Entity then System follows the entity\
                                      and can be turned on/off by setting the active attribute to True/False.\
                                      NOTE: when the entity is destroyed, set ParticleSystem.entity = None

        `entity_offset` (Function): Input - entity, Returns - Vector from the position

        `z` (int): The z layer of the entity, for entity overlapping

        `start_size` (float): The starting radius of the particles (without bloom)

        `max_start_size` (float | None): Optional, if given the actual start size will be between start_size and max_start_size

        `end_size` (float): The final radius of the particles

        `colour` (tuple[int, int, int]): RGB colour of the particles

        `max_colour` (tuple[int, int, int] | None): RGB colour, optional, if given the actual start colour will be between colour and max_colour

        `bloom` (float): bloom > 0 for any bloom, bloom == 0 for no bloom

        `duration` (float | None): None or 0 for explosion, else duration is the time in seconds the system will be active for

        `lifetime` (float): Time in seconds that the particles will be alive for

        `frequency` (float): Number of particles that will be spawned per second

        `speed` (float): The speed of the particles

        `speed_variance` (float | None): Optional, if given the speed will be up to +- speed_variance

        `initial_velocity` (Vector | Function): Initial speed of particle,\
                                                if entity then initial_velocity will be called,\
                                                Input - entity, Returns - Vector
    """

    __slots__ = ("entity_offset", "previous_position", "z", "draw", "bloom", "duration", "lifetime", "time_alive", "period", "delay",
                 "get_start_size", "end_size", "get_colour", "entity", "position", "active", "get_velocity", "particles")

    def __init__(self, position: Vector | Entity, entity_offset=lambda x: Vector(0, 0), z: int = 1,
                 start_size: float = 5, max_start_size: float | None = None, end_size: float = 0,
                 colour: tuple[int, int, int] = (255, 255, 255), max_colour: tuple[int, int, int] | None = None, bloom: float = 0,
                 duration: float | None = 5, lifetime: float = 2, frequency: float = 2,
                 speed: float = 20, speed_variance: float | None = None, initial_velocity: Vector = Vector(0, 0)) -> None:

        self.entity_offset = entity_offset
        self.previous_position = position
        self.z = z

        self.draw = self.draw_particles if not bloom else self.draw_bloom_particles
        self.bloom = bloom + 1

        self.duration = duration
        self.lifetime = lifetime
        self.time_alive = 0
        self.period = 1 / frequency
        self.delay = 0

        if max_start_size:
            self.get_start_size = lambda: start_size + random.random() * (max_start_size - start_size)
        else:
            self.get_start_size = lambda: start_size
        self.end_size = end_size

        if max_colour:
            self.get_colour = lambda: (random.randint(colour[0], max_colour[0]),
                                       random.randint(colour[1], max_colour[1]),
                                       random.randint(colour[2], max_colour[2]))
        else:
            self.get_colour = lambda: colour

        self.active = False
        if not isinstance(position, Vector):  # if position is an Entity
            self.entity = position
            self.position = self.entity.position
        else:
            self.position = position
            self.entity = None

        if speed_variance:
            if self.entity:
                self.get_velocity = lambda: random_vector(speed + (random.random()*2-1) * speed_variance) + initial_velocity(self.entity)
            else:
                self.get_velocity = lambda: random_vector(speed + (random.random()*2-1) * speed_variance) + initial_velocity
        else:
            if self.entity:
                self.get_velocity = lambda: random_vector(speed) + initial_velocity(self.entity)
            else:
                self.get_velocity = lambda: random_vector(speed) + initial_velocity

        # [position, velocity, colour, time_alive, size_difference, start_size]
        self.particles: list[list[list, list, tuple[int, int, int], float, float, float]] = []

        game.CHUNKS.add_entity(self)

        if not duration:
            self.duration = 0
            if not self.entity:
                self.burst()


    def update(self, delta_time: float) -> None:
        self.delay += delta_time
        self.time_alive += delta_time

        self.update_particles(delta_time)

        if self.entity and self.entity in game.CHUNKS.entities:
            self.previous_position = self.position
            game.CHUNKS.set_position(self, self.entity.position + self.entity_offset(self.entity))

        if not self.entity and self.time_alive > self.duration:  # check if the System's life time is over

            if not self.particles:  # if there are no more particles, then the System can be destroyed
                game.CHUNKS.remove_entity(self)
            return

        if self.entity and not self.active:  # if not active: don't spawn particles
            self.delay = 0
            return

        if self.delay > self.period:  # if the System should stil be alive AND the spawning delay is over, then spawn in more particles

            count = int(self.delay / self.period)

            self.delay -= self.period * count

            if self.entity:
                vec = self.position - self.previous_position
                for i in range(1, count+1):
                    velocity = self.get_velocity()
                    position = self.previous_position + (i/count) * vec + (1-i/count) * velocity * delta_time
                    start_size = self.get_start_size()
                    start_size = start_size + (self.end_size - start_size) * (1-i/count) * self.period
                    self.spawn(position, velocity, start_size)

            else:
                for i in range(1, count+1):
                    velocity = self.get_velocity()
                    position = self.position + (1-i/count) * velocity * delta_time
                    start_size = self.get_start_size()
                    start_size = start_size + (self.end_size - start_size) * (1-i/count) * self.period
                    self.spawn(position, velocity, start_size)

    def update_particles(self, delta_time: float) -> None:
        # [position, velocity, colour, time_alive, size_difference, start_size]
        for particle in self.particles:
            # Move particle
            particle[0][0] += particle[1][0] * delta_time
            particle[0][1] += particle[1][1] * delta_time
            particle[3] += delta_time  # Add time to time_alive

        # self.particles is sorted from oldest to newest, so when we reach a particle
        # that hasn't expired we can stop looking through the list
        for particle in self.particles:
            if particle[3] > self.lifetime:  # If particle's time_alive expires, then destroy particle
                self.particles.remove(particle)
            else:
                break


    def draw_particles(self, WIN: pygame.Surface, focus_point: Vector) -> None:
        ZOOM = game.ZOOM
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y
        FOCUS_POINT_X = focus_point.x
        FOCUS_POINT_Y = focus_point.y

        # [position, velocity, colour, time_alive, size_difference, start_size]
        for particle in self.particles:
            draw_circle(WIN, particle[2],
                           ((particle[0][0] - FOCUS_POINT_X) * ZOOM + CENTRE_POINT_X,
                            (particle[0][1] - FOCUS_POINT_Y) * ZOOM + CENTRE_POINT_Y),
                             max(1, (particle[5] + particle[4] * particle[3] / self.lifetime) * ZOOM))  # radius is start_size + (size_difference * time_alive/life_time)

    def draw_bloom_particles(self, WIN: pygame.Surface, focus_point: Vector) -> None:
        ZOOM = game.ZOOM
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y
        FOCUS_POINT_X = focus_point.x
        FOCUS_POINT_Y = focus_point.y

        # [position, velocity, colour, time_alive, size_difference, start_size]
        for position, velocity, colour, time_alive, size_difference, start_size in self.particles:
            SIZE = (start_size + size_difference * time_alive / self.lifetime) * ZOOM
            radius = max(1, SIZE*self.bloom)
            surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

            max_radius = int(SIZE*self.bloom)
            min_radius = int(SIZE)

            # draw circle going from in to out
            spread = (max_radius - min_radius) / 255  # 255 is max opaque
            for radius1 in range(min_radius, max_radius):  # e.g. range(10, 15)
                draw_circle(surface, (*colour, (max_radius-radius1) / spread), (radius, radius), radius1, width=2)

            WIN.blit(surface, ((position[0] - FOCUS_POINT_X) * ZOOM + CENTRE_POINT_X - radius, (position[1] - FOCUS_POINT_Y) * ZOOM + CENTRE_POINT_Y - radius))

            draw_circle(WIN, colour, ((position[0] - FOCUS_POINT_X) * ZOOM + CENTRE_POINT_X, (position[1] - FOCUS_POINT_Y) * ZOOM + CENTRE_POINT_Y), max(1, SIZE))


    def burst(self) -> None:
        for _ in range(int(1/self.period)):
            self.spawn(self.position, self.get_velocity(), self.get_start_size())

    def spawn(self, position: Vector, velocity: Vector, start_size: float) -> None:

        # [position, velocity, colour, time_alive, size_difference, start_size]
        self.particles.append(
            [[position.x, position.y], [velocity.x, velocity.y], self.get_colour(), 0, self.end_size - start_size, start_size]
        )
