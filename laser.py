from objects import Object, Vector
import entities
import station
import game
import math
import pygame



class Laser():
    def __init__(self, ship: entities.Ship, damage: float = game.PLAYER_LASER_DAMAGE, charge: float = 10, recharge: float = 1, range: float = game.PLAYER_LASER_RANGE) -> None:
        self.ship = ship
        self.damage = damage
        self.charge = charge
        self.recharge = recharge
        self.max_range = range

        self.range = self.max_range
        self.shooting = False
        self.delta_time = 0  # used for shoot

    def update(self, delta_time: float) -> None:
        self.charge += self.recharge * delta_time
        self.delta_time = delta_time

    def shoot(self) -> None:
        self.shooting = True
        self.range, entity = self.raycast()
        self.damage = game.PLAYER_LASER_DAMAGE  # assuming only player has a laser

        if hasattr(entity, "damage") and callable(entity.damage):
            entity.damage(self.damage*self.delta_time, self.ship)

    def raycast(self) -> tuple[int, Object | None]:
        self.max_range = game.PLAYER_LASER_RANGE  # assuming only player has a laser
        sin_rotation = math.sin(self.ship.rotation)
        cos_rotation = math.cos(self.ship.rotation)
        x = self.ship.position.x - self.ship.image.get_height()/2 * sin_rotation
        y = self.ship.position.y - self.ship.image.get_height()/2 * cos_rotation
        chunk_x = None
        chunk_y = None

        for step in range(self.max_range):
            x, y = x - sin_rotation, y - cos_rotation

            if chunk_x != int(x // game.CHUNK_SIZE) or chunk_y != int(y // game.CHUNK_SIZE):
                chunk_x = int(x // game.CHUNK_SIZE)
                chunk_y = int(y // game.CHUNK_SIZE)

                total_entities = []
                nearby_entities: dict[Object, tuple[pygame.Surface, pygame.Rect]] = {}

                for cy in range(chunk_y - 1, chunk_y + 2):
                    for cx in range(chunk_x - 1, chunk_x + 2):
                        total_entities.extend(game.CHUNKS.get_chunk_from_coord((cx, cy)).entities)

                if self.ship in total_entities:
                    total_entities.remove(self.ship)

                for entity in total_entities:
                    if (isinstance(entity, entities.Ship) or
                    isinstance(entity, entities.Asteroid) or
                    isinstance(entity, entities.Missile) or
                    isinstance(entity, station.StationCannon)
                    ):

                        if isinstance(entity, entities.Asteroid):
                            image = entity.image
                        else:
                            image = entity.rotated_image

                        nearby_entities[entity] = image, image.get_rect()

            # pos is a vector from entity to laser point
            # it is then adjusted so the top left corner is (0, 0)
            for entity, (image, rect) in nearby_entities.items():
                pos = round(x - entity.position.x + rect[2]/2), round(y - entity.position.y + rect[3]/2)

                if rect.collidepoint(pos) and image.get_at(pos)[3] == 255:  # Check for pixel at pos
                    return step, entity

        return step, None

    def draw_beam(self) -> pygame.Surface:
        beam_width = 10*game.ZOOM
        glow_radius = 100*game.ZOOM
        width, height = beam_width+glow_radius, self.range*game.ZOOM+glow_radius
        surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)

        # Draw beam glow
        for step in range(int(glow_radius/4)+1):
            step=step*2
            pygame.draw.rect(surf, (40, 100, 150, (step/width)**1.3*510), (step, step, width-step*2, height-step*2), border_radius=round(width-step), width=3)

        # Draw light beam
        pygame.draw.rect(surf, (81, 200, 252), (glow_radius/2, glow_radius/2, beam_width, self.range*game.ZOOM), border_radius=round(beam_width))

        surf = pygame.transform.rotozoom(surf, math.degrees(self.ship.rotation), 1)
        return surf

    def draw(self, win: pygame.Surface, focus_point: Vector) -> None:
        if not self.shooting:
            return
        self.shooting = False

        # If laser extends outside of view, then don't draw it
        self.range = min(self.range, math.hypot(game.WIDTH/2, game.HEIGHT/2)/game.ZOOM)

        ship = self.ship
        centre = ship.position + Vector(0, -ship.image.get_height()/2 - self.range/2)  # centre of laser
        centre.rotate_about(ship.rotation, ship.position)

        surf = self.draw_beam()

        win.blit(surf, ((centre - focus_point) * game.ZOOM + game.CENTRE_POINT - Vector(surf.get_width()/2, surf.get_height()/2)).to_tuple())
