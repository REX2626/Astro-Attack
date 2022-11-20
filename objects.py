import pygame
import os
import sys
import math
import images



def get_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



def init_chunks(chunks: "_chunks.Chunks"):
    global CHUNKS
    CHUNKS = chunks




class Vector_1D():
    def __init__(self, x) -> None:
        self.x = x

    def __add__(self, arg):

        # Adding Vectors
        if type(arg) == Vector_1D:
            return Vector_1D(self.x + arg.x)

        # Adding Vector and number
        else:
            return Vector_1D(self.x + arg)

    def __radd__(self, arg):
        return self.x + arg

    def __sub__(self, arg):
        return Vector_1D(self.x - arg.x)

    def __mul__(self, arg):

        # Multiplying Vectors
        if type(arg) == Vector_1D:
            return Vector_1D(self.x * arg.x)

        # Multiplying Vector by int
        else:
            return Vector_1D(self.x * arg)

    def __truediv__(self, arg):

        # Vector divided by Vector
        if type(arg) == Vector_1D:
            return Vector_1D(self.x / arg.x)

        # Vector divided by number
        else:
            return Vector_1D(self.x / arg)

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

        # Multiplying Vectors
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
    
    def to_tuple(self):
        return (self.x, self.y)



class Object():
    def __init__(self, position, scale=1, image=images.DEFAULT) -> None:
        
        # Make position a vector
        if type(position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position = position

        # Set the size (dimensions)
        self.size = Vector(image.get_width(), image.get_height()) * scale

        self.image = pygame.transform.scale(image, (self.size.to_tuple())).convert_alpha()

    def update(self, delta_time):
        pass

    def draw(self, win: pygame.Surface, focus_point, centre_point):
        win.blit(self.image, (round(self.position - focus_point + centre_point - self.size * 0.5)).to_tuple())



class MoveableObject(Object):
    def __init__(self, position, velocity, scale=1, image=images.DEFAULT) -> None:
        super().__init__(position, scale, image)

        # Make velocity a vector
        if type(velocity) != Vector:
            self.velocity = Vector(velocity[0], velocity[1])
        else:
            self.velocity: Vector = velocity

    def update(self, delta_time):

        # Remove self from current chunk
        original_chunk = CHUNKS.get_chunk(self)
        original_chunk.entities.remove(self)

        # Move self
        self.position += self.velocity * delta_time

        # Add self to the chunk it should now be in
        new_chunk = CHUNKS.get_chunk(self)
        new_chunk.entities.add(self)



class Entity(MoveableObject):
    def __init__(self, position, velocity, scale=1, rotation=0, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, scale, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.original_image = self.image
        self.set_rotation(rotation) 

    def set_rotation(self, rotation):
        self.rotation = rotation

        # pygame.transform.rotate uses degrees NOT radians
        # so rotation needs to be converted to degrees
        self.image = pygame.transform.rotate(self.original_image, rotation / math.pi * 180)
        self.size = Vector(self.image.get_width(), self.image.get_height())



class Ship(Entity):
    def __init__(self, position: Vector, velocity: Vector, scale=1, rotation=0, fire_rate=1, image=images.DEFAULT) -> None:
        super().__init__(position, velocity, scale, rotation, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.reload_time = 1 / fire_rate
        self.original_image = self.image
        
        self.time_reloading = 0



class Player_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, max_speed, scale=1, rotation=0, max_rotation_speed=3, fire_rate=1, image=images.RED_SHIP) -> None:
        super().__init__(position, velocity, scale, rotation, fire_rate, image)
        self.max_speed = max_speed
        self.max_rotation_speed = max_rotation_speed
        self.rotation_speed = Vector_1D(0)

    def accelerate(self, acceleration: Vector):
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_rotation(self, acceleration):
        self.rotation_speed += acceleration
        self.rotation_speed.clamp(self.max_rotation_speed)
    
    def update(self, delta_time):
        super().update(delta_time)

        # Inertial Dampening
        """
        -> velocity is added with the inverse velocity, making velocity 0
        -> but inverse velocity is clamped so it doesn't go to 0 velocity instantly
        -> 200 is a constant
        -> the bigger the constant, the faster the dampening
        """
        self.velocity -= self.velocity.get_clamp(200 * delta_time)

        # Change rotation by rotation speed
        self.set_rotation(self.rotation + self.rotation_speed * delta_time)

        # Rotation Dampening
        """
        -> See above definition of dampening
        -> 10 is the size of the dampening
        """
        self.rotation_speed -= self.rotation_speed.get_clamp(3 * delta_time)

        # Increase reload time
        self.time_reloading += delta_time

    def move_forward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, -1000))

    def move_backward(self, delta_time):
        self.accelerate_relative(delta_time * Vector(0, 800))

    def move_left(self, delta_time):
        self.accelerate_relative(delta_time * Vector(-500, 0))

    def move_right(self, delta_time):
        self.accelerate_relative(delta_time * Vector(500, 0))

    def turn_left(self, delta_time):
        self.accelerate_rotation(delta_time * 8)

    def turn_right(self, delta_time):
        self.accelerate_rotation(delta_time * -8)

    def shoot(self):

        # Check if reloaded
        if self.time_reloading >= self.reload_time:
            
            bullet_position = self.position + Vector(0, -71) # spawns bullet at ship's gun, ship's height/2 + bullet's height/2
            bullet_position.rotate_about(self.rotation, self.position)
            bullet_velocity = Vector(0, -500)
            bullet_velocity.rotate(self.rotation)
            bullet = Bullet(

                position=bullet_position,
                velocity=bullet_velocity + self.velocity,
                scale=3,
                rotation=self.rotation
                )

            CHUNKS.add_entity(bullet)
            self.time_reloading = 0



class Bullet(Entity):
    def __init__(self, position, velocity, scale=1, rotation=0, image=images.BULLET) -> None:
        super().__init__(position, velocity, scale, rotation, image)
        
    def update(self, delta_time):
        super().update(delta_time)

        # Check if bullet is near to any aliens in it's chunk
        # If it is, then destroy alien and bullet
        for entity in CHUNKS.get_chunk(self).entities:
            if type(entity) == Object and (entity.position - self.position).magnitude() < 20:
                CHUNKS.remove_entity(entity)
                CHUNKS.remove_entity(self)
                break



class Asteroid(Object):
    def __init__(self, position, scale=1, image=images.ASTEROID) -> None:
        super().__init__(position, scale, image)
        


# _chunks has to be imported last, so that all objects can be initialized
import _chunks