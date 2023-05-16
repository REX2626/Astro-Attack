from objects import Vector, Object, Entity
from weapons import DefaultGun
import effects
import images
import game
import random
import math
import pygame



class Ship(Entity):
    def __init__(self, position: Vector, velocity: Vector, max_speed, rotation=0, weapon=DefaultGun, health=1, shield=0, armour=0, shield_delay=1, shield_recharge=1, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, velocity, rotation, image)

        self.weapon = weapon(self)
        self.max_speed = max_speed
        self.health = health
        self.max_shield = shield
        self.shield = shield
        self.armour = armour
        self.shield_delay = shield_delay
        self.shield_recharge = shield_recharge

        self.shield_delay_elapsed = 0

    def update(self, delta_time):

        # Move the ship by it's velocity
        super().update(delta_time)

        # Inertial Dampening
        """
        -> velocity is added with the inverse velocity, making velocity 0
        -> but inverse velocity is clamped so it doesn't go to 0 velocity instantly
        -> 200 is a constant
        -> the bigger the constant, the faster the dampening
        """
        self.velocity -= self.velocity.get_clamp(200 * delta_time)

        # Update weapon
        self.weapon.update(delta_time)

        # Increase shield delay time elapsed
        self.shield_delay_elapsed += delta_time

        # Check if shield should be increased
        if self.shield_delay_elapsed > self.shield_delay:
            self.shield += self.shield_recharge * delta_time

            if self.shield > self.max_shield:
                self.shield = self.max_shield

    def shoot(self):
        self.weapon.shoot()

    def accelerate(self, acceleration: Vector):
        super().accelerate(acceleration)
        self.velocity.clamp(self.max_speed)

    def damage(self, damage, entity=None):
        """entity is the object which is damaging this ship, DON'T REMOVE"""
        self.shield_delay_elapsed = 0

        # Shield takes damage, and if shield is now 0 then damage to ship is reduced
        new_shield = max(0, self.shield - damage)
        damage -= self.shield - new_shield
        self.shield = new_shield

        # If no shield, then damage ship
        if self.shield == 0:
            effects.damage(self.position, damage)

            # Armour takes damage
            new_armour = max(0, self.armour - damage)
            damage -= self.armour - new_armour
            self.armour = new_armour

            # Health takes damage
            self.health -= damage
            if self.health <= 0:
                self.destroy()

    def destroy(self):
        # If ship dies and it is a target of a kill mission, then the progress of that mission increases
        if game.CURRENT_MISSION:
            if game.CURRENT_MISSION[3] == game.KILL and game.CURRENT_MISSION[2] == self.__class__.__name__:
                game.CURRENT_MISSION[0] += 1

        game.CHUNKS.remove_entity(self)
        effects.explosion(self.position)

    def draw(self, win, focus_point):
        super().draw(win, focus_point)

        # Draw shield around ship
        if self.shield:
            surf = pygame.Surface((60*game.ZOOM, 60*game.ZOOM), flags=pygame.SRCALPHA)
            alpha = (self.shield / self.max_shield) * 255 # alpha value depends on current shield percentage
            pygame.draw.circle(surf, (34, 130, 240, alpha), (30*game.ZOOM, 30*game.ZOOM), 30*game.ZOOM, width=round(2*game.ZOOM))
            pos = ((self.position - focus_point) * game.ZOOM + game.CENTRE_POINT) - 30*game.ZOOM
            win.blit(surf, pos.to_tuple())



class Asteroid(Object):
    def __init__(self, position, image=None) -> None:

        # Generate random asteroid image
        if not image:
            number = random.randint(0, len(images.ASTEROIDS)-1)
        super().__init__(position, lambda: images.ASTEROIDS[number])

        # Set Asteroid to random rotation
        self.rotation = random.random() * 360
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.mask = pygame.mask.from_surface(self.image)

        self.previous_delta_time = 1

    def __setstate__(self, state):
        super().__setstate__(state)
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, delta_time):
        super().update(delta_time)

        chunk_pos = self.position // game.CHUNK_SIZE

        for y in range(chunk_pos.y-1, chunk_pos.y+2):
            for x in range(chunk_pos.x-1, chunk_pos.x+2):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():

                    if isinstance(entity, Ship):
                        asteroid_collision(self, entity)

                    elif isinstance(entity, Bullet):
                        entity_mask = pygame.mask.from_surface(entity.image)

                        x_offset = (entity.position.x - entity.image.get_width()/2) - (self.position.x - self.image.get_width()/2)
                        y_offset = (entity.position.y - entity.image.get_height()/2) - (self.position.y - self.image.get_height()/2)

                        if self.mask.overlap(entity_mask, (x_offset, y_offset)):
                            entity.unload() # if bullet collides with asteroid then destroy bullet
                            effects.damage(entity.position, entity.damage)

        self.previous_delta_time = delta_time



def asteroid_collision(asteroid: Asteroid, entity: Entity):
    """
    Check if entity overlapping with asteroid
    If overlapping:
        Move entity backwards
        If still overlapping:
            Move the entity out 1 unit at a time until not overlapping
        Rotate entity velocity so that it is reflected off the tangent to the asteroid
        Damage entity and create damage particle effect
    """
    entity_mask = pygame.mask.from_surface(entity.image)

    x_offset = (entity.position.x - entity.image.get_width()/2) - (asteroid.position.x - asteroid.image.get_width()/2)
    y_offset = (entity.position.y - entity.image.get_height()/2) - (asteroid.position.y - asteroid.image.get_height()/2)

    if asteroid.mask.overlap(entity_mask, (x_offset, y_offset)):

        game.CHUNKS.move_entity(entity, -asteroid.previous_delta_time)  # Move the entity backwards out of the asteroid

        # Check if entity still in asteroid
        x_offset = (entity.position.x - entity.image.get_width()/2) - (asteroid.position.x - asteroid.image.get_width()/2)
        y_offset = (entity.position.y - entity.image.get_height()/2) - (asteroid.position.y - asteroid.image.get_height()/2)

        if asteroid.mask.overlap(entity_mask, (x_offset, y_offset)):
            # Move entity out of Asteroid if entity is still in Asteroid
            # This ensures that the entity is definitly outside of the asteroid by moving the entity 1 game unit at a time

            escape_vector = entity.position - asteroid.position
            escape_vector.set_magnitude(1)  # Normalize vector
            original_velocity = entity.velocity.copy()
            entity.velocity = escape_vector

            while True:
                game.CHUNKS.move_entity(entity, 1)

                x_offset = (entity.position.x - entity.image.get_width()/2) - (asteroid.position.x - asteroid.image.get_width()/2)
                y_offset = (entity.position.y - entity.image.get_height()/2) - (asteroid.position.y - asteroid.image.get_height()/2)

                if not asteroid.mask.overlap(entity_mask, (x_offset, y_offset)):
                    break

            entity.velocity = original_velocity

        vector_to_asteroid = asteroid.position - entity.position
        tangent_to_asteroid = vector_to_asteroid.get_rotate(math.pi/2)  # Rotate 90 degrees
        tangent_angle = tangent_to_asteroid.get_angle()
        entity_angle = entity.velocity.get_angle()
        angle_difference = entity_angle - tangent_angle
        entity_rotation = 2 * angle_difference  # 1 angle difference makes it go along normal, another difference reflects it through normal
        entity.velocity.rotate(entity_rotation)

        entity.velocity.set_magnitude(entity.velocity.magnitude()*0.8)  # Set speed to 80%

        entity.damage(entity.velocity.magnitude()**2/100_000)

        if hasattr(entity, "make_new_patrol_point"):
            entity.make_new_patrol_point(400, 500, entity.position)
            entity.state = 0  # Patrol state

        effects.asteroid_debris(entity.position)



class Pickup(Entity):
    def __init__(self, position, velocity=Vector(0, 0), max_speed=200, rotation=0, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, velocity, rotation, image)
        self.max_speed = max_speed

    def update(self, delta_time):
        super().update(delta_time)

        # Inertial Dampening
        self.velocity -= self.velocity.get_clamp(1500 * delta_time)

        if game.player.distance_to(self) < game.PICKUP_DISTANCE:
            self.move_to_player(delta_time)

        if game.player.distance_to(self) < 13 + game.player.size.x/2:
            self.activate()

    def accelerate(self, acceleration: Vector):
        super().accelerate(acceleration)
        self.velocity.clamp(self.max_speed)

    def move_to_player(self, delta_time):
        self.accelerate_to(game.player.position, 3000 * delta_time)

    def activate(self):
        # Have set function for each pickup
        return

    def destroy(self):
        game.CHUNKS.remove_entity(self)



class Scrap(Pickup):
    def __init__(self, position, velocity=Vector(0, 0), max_speed=600, rotation=0, image=lambda: images.SCRAP) -> None:
        super().__init__(position, velocity, max_speed, rotation, image)

    def activate(self):
        game.SCRAP_COUNT += 1

        game.CHUNKS.remove_entity(self)



from aiship import Enemy_Ship



class Bullet(Entity):
    def __init__(self, position, velocity, rotation=0, ship=None, damage=1, lifetime=5, image=lambda: images.BULLET) -> None:
        super().__init__(position, velocity, rotation, image)
        self.ship = ship
        self.damage = damage
        self.lifetime = lifetime
        self.start_time = 0

    def update(self, delta_time):
        super().update(delta_time)

        self.start_time += delta_time

        if self.start_time > self.lifetime:
            game.CHUNKS.remove_entity(self)
        else:
            # Check if bullet is near to any aliens in it's chunk
            # If it is, then destroy alien and bullet
            for entity in game.CHUNKS.get_chunk(self).entities:

                if isinstance(entity, Ship) and entity != self.ship:
                    if not (isinstance(entity, Enemy_Ship) and isinstance(self.ship, Enemy_Ship)):
                        if (entity.shield and self.distance_to(entity) < 35) or (not entity.shield and self.distance_to(entity) < 29):
                            entity.damage(self.damage, self.ship)
                            game.CHUNKS.remove_entity(self)
                            break

                elif isinstance(entity, Missile):
                    if not isinstance(self.ship, Enemy_Ship):
                        if self.distance_to(entity) < 20:
                            entity.explode(entity.explode_radius)
                            game.CHUNKS.remove_entity(self)
                            break

    def unload(self):
        game.CHUNKS.remove_entity(self)



class Missile(Entity):
    def __init__(self, position, velocity, rotation=0, max_speed=1000, max_rotation_speed=3, explode_distance=100, explode_radius=150, explode_damage=5, explode_countdown=0.1, image=lambda: images.MISSILE) -> None:
        super().__init__(position, velocity, rotation, image)

        self.max_speed = max_speed
        self.max_rotation_speed = max_rotation_speed
        self.explode_distance = explode_distance
        self.explode_radius = explode_radius
        self.explode_damage = explode_damage
        self.explode_countdown = explode_countdown
        self.time_to_explode = 0
        self.exploding = False

        self.particles = effects.missile_trail(self)
        self.particles.active = True

    def update(self, delta_time):
        super().update(delta_time)

        # Inertial Dampening - improves missile stability
        self.velocity -= self.velocity.get_clamp(1500 * delta_time)

        # Rotation
        self.rotate_to(delta_time, self.position.get_angle_to(game.player.position), self.max_rotation_speed)

        # Movement
        self.accelerate_in_direction(self.rotation, 2000 * delta_time)

        if self.distance_to(game.player) < self.explode_distance:
            self.exploding = True

        if self.exploding:
            self.time_to_explode += delta_time
            if self.time_to_explode > self.explode_countdown:
                self.explode(self.explode_radius)

    def accelerate(self, acceleration: Vector):
        super().accelerate(acceleration)
        self.velocity.clamp(self.max_speed)

    def unload(self):
        game.CHUNKS.remove_entity(self)
        self.particles.entity = None

    def damage(self, damage, entity=None):
        self.explode(self.explode_radius)

    def explode(self, radius):
        entity_list = game.CHUNKS.entities

        # Have to create separate list otherwise the set game.CHUNKS.entities will change size while iterating though it
        entities_to_damage = []
        damage_values = []

        for entity in entity_list:
            if isinstance(entity, Ship):
                distance = entity.distance_to(self)
                if distance < radius:
                    entities_to_damage.append(entity)
                    damage_values.append(1 - distance / self.explode_radius)

        for i, entity in enumerate(entities_to_damage):
            entity.damage(self.explode_damage * damage_values[i])

        self.destroy()

    def destroy(self):
        game.CHUNKS.remove_entity(self)
        self.particles.entity = None
        effects.explosion(self.position)
