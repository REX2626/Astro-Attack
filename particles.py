from objects import Entity, Vector, random_vector
import game
import random
import pygame



draw_circle = pygame.draw.circle
class Particle():
    __slots__ = ("position", "velocity", "start_size", "end_size", "colour", "lifetime", "time_alive", "current_size", "size_difference")

    def __init__(self, position: Vector, velocity: Vector, start_size: float, end_size: float, colour: tuple, lifetime: float, **kwargs) -> None:
        self.position = position
        self.velocity = velocity
        self.start_size = start_size
        self.end_size = end_size
        self.colour = colour
        self.lifetime = lifetime
        self.time_alive = 0
        self.current_size = start_size
        self.size_difference = end_size - start_size

    def update_time(self, delta_time: float, system: "ParticleSystem") -> None:
        self.time_alive += delta_time

        self.current_size += self.size_difference * (delta_time / self.lifetime)

        if self.time_alive > self.lifetime:
            system.particles.remove(self)

    def update(self, delta_time: float, system: "ParticleSystem") -> None:
        # optimized
        self.position = Vector(self.position.x + self.velocity.x * delta_time, self.position.y + self.velocity.y * delta_time)
        self.update_time(delta_time, system)

    def draw(self, WIN: pygame.Surface, focus_point: Vector) -> None:
        ZOOM = game.ZOOM
        draw_circle(WIN, self.colour,
                    ((self.position.x - focus_point.x) * ZOOM + game.CENTRE_POINT.x,
                     (self.position.y - focus_point.y) * ZOOM + game.CENTRE_POINT.y),
                      max(1, self.current_size * ZOOM))



class BloomParticle(Particle):
    __slots__ = ("bloom")

    def __init__(self, position: Vector, velocity: Vector, start_size: float, end_size: float, colour: tuple, lifetime: float, bloom: float) -> None:
        super().__init__(position, velocity, start_size, end_size, colour, lifetime)
        self.bloom = bloom

    def draw(self, WIN: pygame.Surface, focus_point: Vector) -> None:
        ZOOM = game.ZOOM
        CENTRE_POINT_X = game.CENTRE_POINT.x
        CENTRE_POINT_Y = game.CENTRE_POINT.y
        radius = max(1, self.current_size*ZOOM*self.bloom)
        surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        max_radius = int(self.current_size*ZOOM*self.bloom)
        min_radius = int(self.current_size*ZOOM)

        # draw circle going from out to in
        for radius1 in range(max_radius, min_radius, -1):  # e.g. range(15, 10, -1)
            amount_done = (max_radius-radius1) / (max_radius-min_radius)
            draw_circle(surface, (*self.colour, amount_done*255), (radius, radius), radius1, width=2)

        WIN.blit(surface, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X - radius, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y - radius))

        draw_circle(WIN, self.colour, ((self.position.x - focus_point.x) * ZOOM + CENTRE_POINT_X, (self.position.y - focus_point.y) * ZOOM + CENTRE_POINT_Y), max(1, self.current_size * ZOOM))



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
    def __init__(self, position: Vector | Entity, entity_offset=lambda x: Vector(0, 0), z: int = 1,
                 start_size: float = 5, max_start_size: float | None = None, end_size: float = 0,
                 colour: tuple[int, int, int] = (255, 255, 255), max_colour: tuple[int, int, int] | None = None, bloom: float = 0,
                 duration: float | None = 5, lifetime: float = 2, frequency: float = 2,
                 speed: float = 20, speed_variance: float | None = None, initial_velocity: Vector = Vector(0, 0)) -> None:

        self.entity_offset = entity_offset
        self.z = z

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

        self.particle = Particle if not bloom else BloomParticle
        self.bloom = bloom + 1

        self.duration = duration
        self.lifetime = lifetime
        self.time_alive = 0
        self.period = 1 / frequency
        self.delay = 0

        if not isinstance(position, Vector):  # if position is an Entity
            self.entity = position
            self.position = self.entity.position
            self.active = False
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

        self.particles: list[Particle] = []

        game.CHUNKS.add_entity(self)

        if not duration:
            self.duration = 0
            if not self.entity:
                self.burst()

    def update(self, delta_time: float) -> None:
        self.delay += delta_time
        self.time_alive += delta_time

        for particle in self.particles:
            particle.update(delta_time, self)

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

    def draw(self, WIN: pygame.Surface, player_pos: Vector) -> None:
        for particle in self.particles:
            particle.draw(WIN, player_pos)

    def burst(self) -> None:
        for _ in range(int(1/self.period)):
            self.spawn(self.position, self.get_velocity(), self.get_start_size())

    def spawn(self, position: Vector, velocity: Vector, start_size: float) -> None:

        self.particles.append(
            self.particle(position, velocity, start_size=start_size, end_size=self.end_size, colour=self.get_colour(), lifetime=self.lifetime, bloom=self.bloom)
            )
