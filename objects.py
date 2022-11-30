import pygame
import os
import sys
import math
import images
import game
import random



def get_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



class Vector1D():
    def __init__(self, x) -> None:
        self.x = x

    def __add__(self, arg):

        # Adding Vectors
        if type(arg) == Vector1D:
            return Vector1D(self.x + arg.x)

        # Adding Vector and number
        else:
            return Vector1D(self.x + arg)

    def __radd__(self, arg):
        return self.x + arg

    def __sub__(self, arg):
        return Vector1D(self.x - arg.x)

    def __mul__(self, arg):

        # Multiplying Vectors
        if type(arg) == Vector1D:
            return Vector1D(self.x * arg.x)

        # Multiplying Vector by int
        else:
            return Vector1D(self.x * arg)

    def __truediv__(self, arg):

        # Vector divided by Vector
        if type(arg) == Vector1D:
            return Vector1D(self.x / arg.x)

        # Vector divided by number
        else:
            return Vector1D(self.x / arg)

    def magnitude(self):
        return abs(self.x)

    def set_magnitude(self, magnitude):
        new_vector = self * magnitude / self.magnitude()
        self.x = new_vector.x

    def clamp(self, maximum):
        if self.magnitude() > maximum:
            self.set_magnitude(maximum)

    def get_clamp(self, maximum):
        if self.magnitude() > maximum:
            # Set magnitude to maximum
            return self * maximum / self.magnitude()
        return self



class Vector():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, arg):

        # Adding Vectors
        if type(arg) == Vector:
            return Vector(self.x + arg.x, self.y + arg.y)

        # Adding Vector to Scalar
        else:
            return Vector(self.x + arg, self.y + arg)

    def __truediv__(self, arg):

        # Dividing Vectors
        if type(arg) == Vector:
            return Vector(self.x / arg.x, self.y / arg.y)
        
        # Dividing Vector by Scalar
        else:
            return Vector(self.x / arg, self.y / arg)

    def __floordiv__(self, arg):

        # Dividing Vectors
        if type(arg) == Vector:
            return Vector(int(self.x // arg.x), int(self.y // arg.y))
        
        # Dividing Vector by Scalar
        else:
            return Vector(int(self.x // arg), int(self.y // arg))
    
    def __sub__(self, arg):

        # Subtracting Vectors
        if type(arg) == Vector:
            return Vector(self.x - arg.x, self.y - arg.y)
        
        # Subtracting Scalar from Vector
        else:
            return Vector(self.x - arg, self.y - arg)

    def __mul__(self, arg):

        # Multiplying Vectors
        if type(arg) == Vector:
            return Vector(self.x * arg.x, self.y * arg.y)

        # Multiplying Vector with Scalar
        else:
            return Vector(self.x * arg, self.y * arg)

    def __rmul__(self, arg):

        # Multiplying Vectors with dot product
        if type(arg) == Vector:
            return Vector(self.x * arg.x, self.y * arg.y)

        # Multiplying Vector with Scalar
        else:
            return Vector(self.x * arg, self.y * arg)

    def __mod__(self, arg):
        return Vector(int(self.x) % arg, int(self.y) % arg)

    def __repr__(self):
        return str((self.x, self.y))

    def __round__(self):
        return Vector(round(self.x), round(self.y))

    def clamp(self, maximum):
        if self.magnitude() > maximum:
            self.set_magnitude(maximum)

    def get_clamp(self, maximum):
        if self.magnitude() > maximum:
            # Set magnitude to maximum
            return self * maximum / self.magnitude()
        return self

    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5

    def set_magnitude(self, magnitude):
        # cringe way of updating self
        # can't do "self = new_vector" as self is just a variable
        new_vector = self * magnitude / self.magnitude()
        self.x = new_vector.x
        self.y = new_vector.y

    def get_angle(self, position):
        angle = math.atan((-position.y + self.y) / (position.x - self.x))
        return angle - math.pi/2 if self.x < position.x else angle + math.pi/2

    def rotate(self, angle):
        x1, y1 = self.x, self.y
        # The positive and negative signs are different
        # Because y increases downwards (for our coord system)
        self.x = y1*math.sin(angle) + x1*math.cos(angle)
        self.y = y1*math.cos(angle) - x1*math.sin(angle)

    def rotate_about(self, angle, position):
        self.x -= position.x
        self.y -= position.y
        self.rotate(angle)
        self.x += position.x
        self.y += position.y

    def in_range(self, x, y, width, height):
        return self.x >= x and self.x <= x + width and self.y >= y and self.y <= y + height
    
    def to_tuple(self):
        return (self.x, self.y)




def random_vector(magnitude: float) -> Vector:
    """Returns a vector with random direction and given magnitude"""
    random_direction = random.random() * 2 * math.pi    # Get random direction

    random_vector = Vector(magnitude * math.cos(random_direction), magnitude * math.sin(random_direction))  # Get random vector with magnitude
    
    return random_vector



class Object():
    def __init__(self, position, image=images.DEFAULT) -> None:
        
        # Make position a vector
        if type(position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position: Vector = position

        # Set the size (dimensions), original size of image, doesn't change when rotating
        self.size = Vector(image.get_width(), image.get_height())

        self.image = image
    def update(self, delta_time):
        pass

    def distance_to(self, object):
        return (self.position - object.position).magnitude()

    def get_zoomed_image(self):
        return pygame.transform.scale(self.image, (game.ZOOM * self.size).to_tuple())

    def draw(self, win: pygame.Surface, focus_point):
        image = self.get_zoomed_image()
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())
        # old code
        # win.blit(self.image, (round(self.position - focus_point + self.offset)).to_tuple())



class MoveableObject(Object):
    def __init__(self, position, velocity, image=images.DEFAULT) -> None:
        super().__init__(position, image)

        # Make velocity a vector
        if type(velocity) != Vector:
            self.velocity = Vector(velocity[0], velocity[1])
        else:
            self.velocity: Vector = velocity

    def update(self, delta_time):

        # Remove self from current chunk
        original_chunk = game.CHUNKS.get_chunk(self)
        original_chunk.entities.remove(self)

        # Move self
        self.position += self.velocity * delta_time

        # Add self to the chunk it should now be in
        new_chunk = game.CHUNKS.get_chunk(self)
        new_chunk.entities.add(self)

    def move_towards(self, target_position, speed):
        v: "Vector" = target_position - self.position
        v.set_magnitude(speed)
        self.velocity = v


class Entity(MoveableObject):
    def __init__(self, position, velocity, rotation=0, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.original_image = self.image
        self.set_rotation(rotation) 

    def set_rotation(self, rotation):
        self.rotation = rotation

    def draw(self, win: pygame.Surface, focus_point):
        image = self.get_zoomed_image()
        image = pygame.transform.rotate(image, self.rotation / math.pi * 180)
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())



class Ship(Entity):
    def __init__(self, position: Vector, velocity: Vector, max_speed, rotation=0, fire_rate=1, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, rotation, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.reload_time = 1 / fire_rate
        self.original_image = self.image
        self.max_speed = max_speed
        
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
        -> 10 is the size of the dampening
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
            bullet_velocity = Vector(0, -450)
            bullet_velocity.rotate(self.rotation)
            bullet = Bullet(

                position=bullet_position,
                velocity=bullet_velocity + self.velocity,
                rotation=self.rotation
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


from enemy import Enemy_Ship # Has to be done after defining Vector and Ship, used for Bullet
import particles

class Bullet(Entity):
    def __init__(self, position, velocity, rotation=0, image=images.BULLET) -> None:
        super().__init__(position, velocity, rotation, image)
        global player
        import player
        
    def update(self, delta_time):
        super().update(delta_time)

        # Check if bullet is near to any aliens in it's chunk
        # If it is, then destroy alien and bullet
        for entity in game.CHUNKS.get_chunk(self).entities:
            if isinstance(entity, Enemy_Ship) and self.distance_to(entity) < 30:
                game.CHUNKS.remove_entity(entity)
                game.CHUNKS.remove_entity(self)
                game.SCORE += 1
                particles.ParticleSystem(entity.position, size=3, colour=(0, 255, 0), duration=0.2, lifetime=0.5, frequency=250, speed=500, speed_variance=100)
                particles.ParticleSystem(entity.position, size=3, colour=(255, 120, 0), duration=0.2, lifetime=0.5, frequency=250, speed=500, speed_variance=100)
                break

            elif type(entity) == player.Player_Ship and self.distance_to(entity) < 30:
                entity.health -= 1
                game.CHUNKS.remove_entity(self)
                particles.ParticleSystem(entity.position, size=3, colour=(255, 0, 0), duration=0.2, lifetime=0.5, frequency=500, speed=500, speed_variance=100)
                break

    def unload(self):
        game.CHUNKS.remove_entity(self)



class Asteroid(Object):
    def __init__(self, position, image=images.ASTEROID) -> None:
        
        # Set Asteroid to random rotation
        image = pygame.transform.rotate(image, random.random() * 360)
        super().__init__(position, image)