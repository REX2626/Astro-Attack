from objects import Vector1D, Vector, Object, Entity
import particles
import images
import game
import random
import math
import pygame



class Asteroid(Object):
    def __init__(self, position, image=None) -> None:

        # Generate random asteroid image
        if not image:
            image = random.choice(images.ASTEROIDS)
        
        # Set Asteroid to random rotation
        image = pygame.transform.rotate(image, random.random() * 360)
        self.mask = pygame.mask.from_surface(image)
        super().__init__(position, image)

    def update(self, delta_time):
        super().update(delta_time)

        chunk_pos = self.position // game.CHUNK_SIZE

        for y in range(chunk_pos.y-2, chunk_pos.y+3):
            for x in range(chunk_pos.x-2, chunk_pos.x+3):

                for entity in game.CHUNKS.get_chunk((x, y)).entities.copy():

                    if isinstance(entity, Ship):
                        entity_mask = pygame.mask.from_surface(entity.image)

                        x_offset = (entity.position.x - entity.image.get_width()/2) - (self.position.x - self.image.get_width()/2)
                        y_offset = (entity.position.y - entity.image.get_height()/2) - (self.position.y - self.image.get_height()/2)

                        if self.mask.overlap(entity_mask, (x_offset, y_offset)):

                            vector_to_asteroid = self.position - entity.position

                            game.CHUNKS.move_entity(entity, -delta_time) # Move entity backwards, so outside of asteroid

                            tangent_to_asteroid = vector_to_asteroid.get_rotate(math.pi/2) # Rotate 90 degrees
                            tangent_angle = tangent_to_asteroid.get_angle()
                            entity_angle = entity.velocity.get_angle()
                            angle_difference = entity_angle - tangent_angle
                            entity_rotation = 2 * angle_difference # 1 angle difference makes it go along normal, another difference reflects it through normal
                            entity.velocity.rotate(entity_rotation)

                            entity.damage(entity.velocity.magnitude()**2/100_000)
                            particles.ParticleSystem(entity.position, start_size=10, end_size=0, colour=game.DARK_GREY, duration=None, lifetime=0.5, frequency=20, speed=100, speed_variance=20)



class Ship(Entity):
    def __init__(self, position: Vector, velocity: Vector, max_speed, rotation=0, fire_rate=1, health=1, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, rotation, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.reload_time = 1 / fire_rate
        self.original_image = self.image
        self.max_speed = max_speed
        self.health = health
        
        self.time_reloading = 0
        self.rotation_speed = Vector1D(0)

    def update(self, delta_time):

        # Inertial Dampening
        """
        -> velocity is added with the inverse velocity, making velocity 0
        -> but inverse velocity is clamped so it doesn't go to 0 velocity instantly
        -> 200 is a constant
        -> the bigger the constant, the faster the dampening
        """
        self.velocity -= self.velocity.get_clamp(200 * delta_time)

        # Rotation Dampening
        """
        -> See above definition of dampening
        -> 3 is the size of the dampening
        """
        self.rotation_speed -= self.rotation_speed.get_clamp(3 * delta_time)

        # Move the ship by it's velocity
        super().update(delta_time)

        # Change rotation by rotation speed
        self.set_rotation(self.rotation + self.rotation_speed * delta_time)

        # Increase reload time
        self.time_reloading += delta_time

    def shoot(self):
        # Check if reloaded
        if self.time_reloading >= self.reload_time:
            
            bullet_position = self.position + Vector(0, -self.original_image.get_height()/2 - images.BULLET.get_height()/2) # spawns bullet at ship's gun
            bullet_position.rotate_about(self.rotation, self.position)
            bullet_velocity = Vector(0, -750)
            bullet_velocity.rotate(self.rotation)
            bullet = Bullet(

                position=bullet_position,
                velocity=bullet_velocity + self.velocity,
                rotation=self.rotation,
                ship=self,
                lifetime=3
                )

            game.CHUNKS.add_entity(bullet)
            self.time_reloading = 0
    
    def accelerate(self, acceleration: Vector):
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)
    
    def accelerate_in_direction(self, target_position: Vector, magnitude: float):
        acceleration = target_position - self.position
        acceleration.set_magnitude(magnitude)
        self.accelerate(acceleration)
    
    def damage(self, damage):
        self.health -= damage
        particles.ParticleSystem(self.position, start_size=3, max_start_size=5, end_size=1, colour=(200, 0, 0), max_colour=(255, 160, 0), duration=None, lifetime=0.6, frequency=30, speed=120, speed_variance=40)
        if self.health <= 0:
            self.destroy()

    def destroy(self):
        game.CHUNKS.remove_entity(self)
        particles.ParticleSystem(self.position, start_size=10, max_start_size=35, end_size=2, colour=(200, 0, 0), max_colour=(255, 160, 0), bloom=1.5, duration=None, lifetime=0.8, frequency=20, speed=100, speed_variance=50)
        particles.ParticleSystem(self.position, start_size=15, max_start_size=25, end_size=1, colour=game.DARK_GREY, bloom=1.2, duration=None, lifetime=0.6, frequency=10, speed=60, speed_variance=30)


from aiship import Enemy_Ship, Neutral_Ship # Has to be done after defining Ship, used for Bullet

class Bullet(Entity):
    def __init__(self, position, velocity, rotation=0, ship=None, lifetime=5, image=images.BULLET) -> None:
        super().__init__(position, velocity, rotation, image)
        self.ship = ship
        self.lifetime = lifetime
        self.start_time = 0
        global player
        import player
        
    def update(self, delta_time):
        super().update(delta_time)

        self.start_time += delta_time

        if self.start_time > self.lifetime:
            game.CHUNKS.remove_entity(self)
        else:
            # Check if bullet is near to any aliens in it's chunk
            # If it is, then destroy alien and bullet
            for entity in game.CHUNKS.get_chunk(self).entities:
                if isinstance(entity, Enemy_Ship) and self.distance_to(entity) < 30:
                    entity.damage(1)
                    if isinstance(self.ship, player.Player_Ship):
                        entity.enemy_spotted()
                    game.CHUNKS.remove_entity(self)
                    game.SCORE += 1
                    break


                elif type(entity) == player.Player_Ship and self.distance_to(entity) < 30:
                    entity.damage(1)
                    game.CHUNKS.remove_entity(self)
                    break

                elif type(entity) == Neutral_Ship and self.distance_to(entity) < 30:
                    entity.damage(1)
                    if isinstance(self.ship, player.Player_Ship):
                        entity.state = 1
                    elif isinstance(self.ship, Enemy_Ship):
                        entity.state = 2
                        entity.recent_enemy = self.ship
                    game.CHUNKS.remove_entity(self)
                    break

    def unload(self):
        game.CHUNKS.remove_entity(self)