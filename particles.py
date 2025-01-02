import random
from typing import Callable, List, Optional, Tuple, Union

import pygame

import game
from game import CHUNKS, ZOOM, CENTRE_POINT
from objects import Entity, Vector, random_vector

# For convenience
draw_circle = pygame.draw.circle


class ParticleSystem:
    """
    A Particle System that spawns and manages particles. Particles can be
    stationary or follow an entity; they can be either short-lifetime bursts
    or continuous emission.

    Parameters
    ----------
    position : Union[Vector, Entity]
        If a Vector, the system remains stationary at that point. If an Entity,
        the system follows the entity's position. If the entity is destroyed,
        you can set `self.entity = None`.
    entity_offset : Callable[[Entity], Vector], optional
        A function that given the entity returns the offset from its position
        where particles should spawn. Defaults to a zero vector.
    z : int
        Z-layer for rendering order. Entities/ParticleSystems with higher z
        appear in front of those with lower z.
    start_size : float
        The initial radius for newly spawned particles.
    max_start_size : float, optional
        If given, the system randomly chooses an initial radius in range
        [start_size, max_start_size]. If None, all start at exactly `start_size`.
    end_size : float
        The final radius for a particle at the end of its lifetime.
    colour : tuple[int, int, int]
        The base RGB color that each particle can start with if `max_colour` is None.
    max_colour : tuple[int, int, int], optional
        If provided, a random color is chosen between `colour` and `max_colour`.
        E.g. randomizing the color range for each particle.
    bloom : float
        Bloom factor for drawing. If bloom <= 0, uses a normal circle. If bloom > 0,
        draws a multi-radius circle with partial transparency. Typically small, e.g. 1.2, 1.5, etc.
    duration : float, optional
        The total time the system spawns particles. If None or 0, spawns all at once
        (like an explosion). If > 0, it spawns continuously for that many seconds.
    lifetime : float
        The number of seconds each particle remains alive. After that, the particle is removed.
    frequency : float
        The number of particles per second to spawn.
    speed : float
        The base linear velocity of new particles in random directions, unless `initial_velocity`
        modifies it further.
    speed_variance : float, optional
        If set, the actual speed is `speed +- speed_variance * random()`.
    initial_velocity : Union[Vector, Callable[[Entity], Vector]]
        Additional velocity each particle receives upon spawning. If the system is
        entity-based, you can pass a function that returns a velocity based on that entity.
        Otherwise, a simple Vector is added to the random velocity.

    Usage
    -----
    system = ParticleSystem(position=some_vector, ... )
    CHUNKS.add_entity(system)
    Then in the main update loop: system.update(delta_time)
    Then in the main draw: system.draw_particles(WIN, camera_focus)

    For an entity-based system:
    system = ParticleSystem(position=some_entity, active=True, ...)
    system.entity_offset = lambda ent: Vector(0, -10)
    """

    __slots__ = (
        "entity_offset",
        "previous_position",
        "z",
        "draw",  # either draw_particles or draw_bloom_particles
        "bloom",
        "duration",
        "lifetime",
        "time_alive",
        "period",
        "delay",
        "get_start_size",
        "end_size",
        "get_colour",
        "entity",
        "position",
        "active",
        "get_velocity",
        "particles",
        "acceleration",
        "color_fade",  # optional color fade
    )

    def __init__(
        self,
        position: Union[Vector, Entity],
        entity_offset: Callable[[Entity], Vector] = lambda ent: Vector(0, 0),
        z: int = 1,
        start_size: float = 5.0,
        max_start_size: Optional[float] = None,
        end_size: float = 0.0,
        colour: Tuple[int, int, int] = (255, 255, 255),
        max_colour: Optional[Tuple[int, int, int]] = None,
        bloom: float = 0.0,
        duration: Optional[float] = 5.0,
        lifetime: float = 2.0,
        frequency: float = 2.0,
        speed: float = 20.0,
        speed_variance: Optional[float] = None,
        initial_velocity: Union[Vector, Callable[[Entity], Vector]] = Vector(0, 0),
        # new optional features
        acceleration: Vector = Vector(0, 0),
        color_fade: bool = False,
    ) -> None:

        self.entity_offset = entity_offset
        self.previous_position = position
        self.z = z

        # Choose the drawing method
        if bloom > 0.0:
            self.bloom = bloom + 1.0  # offset
            self.draw = self.draw_bloom_particles
        else:
            self.bloom = 1.0
            self.draw = self.draw_particles

        self.duration = duration if duration else 0.0  # if None or 0 => immediate burst
        self.lifetime = lifetime
        self.time_alive = 0.0
        self.period = 1.0 / frequency if frequency > 0.0 else 9999999.0
        self.delay = 0.0

        # Start size can be random in [start_size, max_start_size]
        if max_start_size:
            def get_sz() -> float:
                return start_size + random.random() * (max_start_size - start_size)
            self.get_start_size = get_sz
        else:
            self.get_start_size = lambda: start_size
        self.end_size = end_size

        # Possibly random color
        if max_colour:
            def get_clr() -> Tuple[int, int, int]:
                return (
                    random.randint(colour[0], max_colour[0]),
                    random.randint(colour[1], max_colour[1]),
                    random.randint(colour[2], max_colour[2])
                )
            self.get_colour = get_clr
        else:
            self.get_colour = lambda: colour

        self.active = True  # if entity-based, set to True for continuous spawn
        self.color_fade = color_fade

        # Setup position
        if isinstance(position, Vector):
            self.position = position
            self.entity = None
        else:
            self.entity = position
            self.position = self.entity.position

        # Build velocity function
        if callable(initial_velocity):
            # We have a function that returns velocity
            if speed_variance:
                def get_vel():
                    spd = speed + (random.random() * 2 - 1.0) * speed_variance
                    return random_vector(spd) + initial_velocity(self.entity)  # type: ignore
            else:
                def get_vel():
                    return random_vector(speed) + initial_velocity(self.entity)  # type: ignore
        else:
            # initial_velocity is a plain Vector
            if speed_variance:
                def get_vel():
                    spd = speed + (random.random() * 2 - 1.0) * speed_variance
                    return random_vector(spd) + initial_velocity
            else:
                def get_vel():
                    return random_vector(speed) + initial_velocity

        self.get_velocity = get_vel

        # Each particle: [pos, vel, color, time_alive, size_diff, start_size, optional color fade factor]
        self.particles: List[
            [
                List[float],  # pos [x, y]
                List[float],  # vel [x, y]
                Tuple[int, int, int],  # color (r, g, b)
                float,  # time_alive
                float,  # size_difference
                float,  # start_size
            ]
        ] = []

        # Additional features:
        self.acceleration = [acceleration.x, acceleration.y]

        # Register system with chunk manager
        CHUNKS.add_entity(self)

        # If the system is an immediate burst (duration=0), spawn them right away
        if self.duration <= 0 and not self.entity:
            self.burst()

    def update(self, delta_time: float) -> None:
        """
        Called every frame to update the particle system's logic, including spawning
        new particles and updating existing ones.
        """
        self.delay += delta_time
        self.time_alive += delta_time

        # If we have an entity, update our own position to track it
        if self.entity and self.entity in CHUNKS.entities:
            self.previous_position = self.position
            offset_pos = self.entity_offset(self.entity)
            new_pos = self.entity.position + offset_pos
            CHUNKS.set_position(self, new_pos)
            self.position = new_pos

        # Update existing particles
        self._update_particles(delta_time)

        # If no entity and system is short-lived, we remove it after duration + after all particles die
        if not self.entity and self.time_alive > self.duration > 0:
            # Once all particles are gone, remove the system
            if not self.particles:
                CHUNKS.remove_entity(self)
            return

        # If the system is attached to an entity but we set self.active=False, skip new spawns
        if self.entity and not self.active:
            self.delay = 0.0
            return

        # Spawn new particles if time has passed
        if self.delay >= self.period and (self.entity or self.time_alive < self.duration):
            # see how many steps we can do
            steps = int(self.delay / self.period)
            self.delay -= self.period * steps

            vec_diff = self.position - self.previous_position
            for i in range(1, steps + 1):
                # fraction for sub-step
                fraction = i / float(steps)

                velocity = self.get_velocity()
                sub_pos = self.previous_position + fraction * vec_diff + (1.0 - fraction) * velocity * delta_time
                start_size = self.get_start_size()

                # We do partial interpolation on start_size as well
                size_progress = (1.0 - fraction) * self.period
                start_size += (self.end_size - start_size) * size_progress

                self._spawn(sub_pos, velocity, start_size)

    def _update_particles(self, delta_time: float) -> None:
        """
        Move each particle based on velocity & optional acceleration, remove old ones.
        """
        # We do a forward iteration but remove afterwards
        # If there's a performance concern, maintain a separate remove list
        # [pos, vel, color, time_alive, size_diff, start_size]
        for i in range(len(self.particles) - 1, -1, -1):
            part = self.particles[i]
            part[0][0] += part[1][0] * delta_time
            part[0][1] += part[1][1] * delta_time
            # apply acceleration if not zero
            part[1][0] += self.acceleration[0] * delta_time
            part[1][1] += self.acceleration[1] * delta_time

            # increment time
            part[3] += delta_time

            # if exceeded lifetime, remove
            if part[3] > self.lifetime:
                self.particles.pop(i)

    def draw_particles(self, surface: pygame.Surface, focus_point: Vector) -> None:
        """
        Draw the system's particles as normal circles, no bloom effect.
        """
        # [pos, vel, color, time_alive, size_diff, start_size]
        for (px, py), vel, color, t_alive, size_diff, start_size in self.particles:
            # compute final radius
            # ratio in [0..1]
            ratio = t_alive / self.lifetime
            final_size = start_size + size_diff * ratio
            radius = max(1, final_size * ZOOM)

            sx = (px - focus_point.x) * ZOOM + CENTRE_POINT.x
            sy = (py - focus_point.y) * ZOOM + CENTRE_POINT.y

            draw_circle(surface, color, (sx, sy), radius)

    def draw_bloom_particles(self, surface: pygame.Surface, focus_point: Vector) -> None:
        """
        Draw the system's particles with a bloom effect, meaning bigger
        partially transparent circles that fade outward.
        """
        # [pos, vel, color, time_alive, size_diff, start_size]
        for (px, py), vel, color, t_alive, size_diff, start_size in self.particles:
            ratio = t_alive / self.lifetime
            final_size = start_size + size_diff * ratio

            # The smaller "core" radius
            radius_core = max(1, final_size * ZOOM)

            # The bigger bloom radius
            bloom_radius = max(1, radius_core * self.bloom)

            sx = (px - focus_point.x) * ZOOM + CENTRE_POINT.x - bloom_radius
            sy = (py - focus_point.y) * ZOOM + CENTRE_POINT.y - bloom_radius

            # Prepare a surface to draw the gradient bloom
            size_bloom = int(bloom_radius * 2)
            alpha_surf = pygame.Surface((size_bloom, size_bloom), pygame.SRCALPHA)

            # We'll do a radial alpha fill
            for r in range(int(radius_core), int(bloom_radius)):
                alpha_factor = int((bloom_radius - r) / (bloom_radius - radius_core + 1) * 255)
                # color + alpha
                c = (*color, alpha_factor)
                draw_circle(alpha_surf, c, (bloom_radius, bloom_radius), r, width=1)

            surface.blit(alpha_surf, (sx, sy))

            # Draw smaller core circle on main surface
            core_x = (px - focus_point.x) * ZOOM + CENTRE_POINT.x
            core_y = (py - focus_point.y) * ZOOM + CENTRE_POINT.y
            draw_circle(surface, color, (core_x, core_y), radius_core)

    def burst(self) -> None:
        """
        Create a one-time burst of particles (like an explosion),
        if the system has no duration (duration=0).
        """
        # Let's spawn ~ 1 / self.period worth of particles
        # or an arbitrary number
        num = int(1.0 / self.period) if self.period != 0 else 10
        for _ in range(num):
            velocity = self.get_velocity()
            size = self.get_start_size()
            self._spawn(self.position, velocity, size)

    def _spawn(self, pos: Vector, vel: Vector, start_size: float) -> None:
        """
        Internal function to add a new particle.
        """
        # color, lifetime mgmt
        c = self.get_colour()

        # particle data
        # [ position: [float, float], velocity: [float, float],
        #   color: (r, g, b), time_alive: float,
        #   size_diff: float, start_size: float]
        p = [
            [pos.x, pos.y],
            [vel.x, vel.y],
            c,
            0.0,                       # time_alive
            (self.end_size - start_size),
            start_size
        ]
        self.particles.append(p)

