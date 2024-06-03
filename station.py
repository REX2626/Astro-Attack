from objects import Entity, Object, Vector, random_vector
from aiship import Mother_Ship, Neutral_Ship_Cargo
from weapons import DefaultGun
import effects
import images
import game
import random
import pygame



class Station(Object):
    def __init__(self, position, max_entities=1, max_spawns=3, spawn_cooldown=5, entity_type=Neutral_Ship_Cargo, selected_image=lambda: images.SELECTED_STATION, image=lambda: images.FRIENDLY_STATION) -> None:
        super().__init__(position, image)
        self.max_entities = max_entities
        self.max_spawns = max_spawns
        self.spawn_cooldown = spawn_cooldown
        self.current_time = spawn_cooldown  # Entities are spawned in straight away
        self.entity_type = entity_type

        self.spawns_occurred = 0
        self.entities_to_spawn = random.randint(1, max_entities)

        self.default_image = image()
        self.selected_image = selected_image()
        self.load_default_image = image
        self.load_selected_image = selected_image
        self.default_scale = game.ZOOM
        self.selected_scale = game.ZOOM
        self.scaled_default_image = pygame.transform.scale_by(self.default_image, game.ZOOM)
        self.scaled_selected_image = pygame.transform.scale_by(self.selected_image, game.ZOOM)

        self.mask = pygame.mask.from_surface(self.image)

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.z = -1

    def __setstate__(self, state):
        super().__setstate__(state)
        self.default_image = self.load_default_image()
        self.selected_image = self.load_selected_image()
        self.scaled_default_image = pygame.transform.scale_by(self.default_image, self.default_scale)
        self.scaled_selected_image = pygame.transform.scale_by(self.selected_image, self.selected_scale)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        super().update(delta_time)

        if self.spawns_occurred < self.max_spawns:

            # Spawn entities after cooldown
            if self.entities_to_spawn > 0:
                self.current_time += delta_time

                if self.current_time >= self.spawn_cooldown:
                    for _ in range(self.entities_to_spawn):
                        self.spawn_entity(self.entity_type)
                    self.current_time = 0
                    self.entities_to_spawn = 0
                    self.spawns_occurred += 1


    def spawn_entity(self, entity_type):
        random_position = self.position + random_vector(game.CHUNK_SIZE/3)

        entity = entity_type(random_position, Vector(0, 0), level=game.CURRENT_SHIP_LEVEL, current_station=self)

        game.CHUNKS.add_entity(entity)


    def get_zoomed_image(self):
        if game.player.closest_station == self:
            if self.selected_scale != game.ZOOM:
                # if self.scaled_image isn't the right scale -> recalculate the scaled_image
                self.selected_scale = game.ZOOM
                self.scaled_selected_image = pygame.transform.scale_by(self.selected_image, game.ZOOM)
            return self.scaled_selected_image
        else:
            if self.default_scale != game.ZOOM:
                # if self.scaled_image isn't the right scale -> recalculate the scaled_image
                self.default_scale = game.ZOOM
                self.scaled_default_image = pygame.transform.scale_by(self.default_image, game.ZOOM)
            return self.scaled_default_image



class FriendlyStation(Station):
    def __init__(self, position, max_entities=3, max_spawns=3, spawn_cooldown=5, entity_type=Neutral_Ship_Cargo, selected_image=lambda: images.SELECTED_STATION, image=lambda: images.FRIENDLY_STATION) -> None:
        super().__init__(position, max_entities, max_spawns, spawn_cooldown, entity_type, selected_image, image)

    def update(self, delta_time):
        super().update(delta_time)
        if self.distance_to(game.player) < 500:
            game.player.health = min(game.MAX_PLAYER_HEALTH, game.player.health + 2*delta_time)



class EnemyStation(Station):
    def __init__(self, position, max_entities=2, max_spawns=3, spawn_cooldown=10, entity_type=Mother_Ship, selected_image=lambda: images.SELECTED_STATION, image=lambda: images.ENEMY_STATION) -> None:
        super().__init__(position, max_entities, max_spawns, spawn_cooldown, entity_type, selected_image, image)

        # Spawn in 2 cannons
        pos1 = position - Vector(self.width/2 - 20, 0)
        pos2 = position + Vector(self.width/2 - 20, 0)

        game.CHUNKS.add_entity(StationCannon(pos1, level=game.CURRENT_SHIP_LEVEL))
        game.CHUNKS.add_entity(StationCannon(pos2, level=game.CURRENT_SHIP_LEVEL))



class StationCannon(Entity):
    def __init__(self, position: Vector, health: int = 20, damage: int = 2, range: int = 800, level: int = 0, image=lambda: images.STATION_CANNON) -> None:
        super().__init__(position, velocity=Vector(0, 0), image=image)
        self.range = range

        # Adds 5 hp for every level
        self.health = health + 5*level

        # Adds 0.4 damage per level
        damage += 0.4*level

        self.cannon = DefaultGun(self, damage, fire_rate=0.5, speed=400, image=lambda: images.STATION_CANNON_BULLET)

    def damage(self, damage: int, entity=None) -> None:
        self.health -= damage
        effects.damage(self.position, damage)

        if self.health <= 0:
            game.CHUNKS.remove_entity(self)
            effects.explosion(self.position)

    def update(self, delta_time: float) -> None:
        self.cannon.update(delta_time)
        self.rotation = self.position.get_angle_to(game.player.position)
        if self.position.dist_to(game.player.position) <= self.range:
            self.cannon.shoot()
