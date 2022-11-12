import pygame
import os
import sys
import math



def get_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)




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
        self.x = y1*math.sin(angle) - x1*math.cos(angle)
        self.y = y1*math.cos(angle) - x1*math.sin(angle)
    
    def to_tuple(self):
        return (self.x, self.y)



class Object():
    def __init__(self, position, width, height, image="assets/default_image.png") -> None:
        
        # Make position a vector
        if type(position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position = position

        self.width = width
        self.height = height
        self.size = Vector(width, height)
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height)).convert()

    def draw(self, win: pygame.Surface, focus_point, centre_point):
        win.blit(self.image, (round(self.position - focus_point + centre_point - self.size * 0.5)).to_tuple())
        pygame.draw.rect(win, (255, 0, 0), (self.image.get_rect()))



class MoveableObject(Object):
    def __init__(self, position, velocity, width, height, image="assets/default_image.png") -> None:
        super().__init__(position, width, height, image)

        # Make velocity a vector
        if type(velocity) != Vector:
            self.velocity = Vector(velocity[0], velocity[1])
        else:
            self.velocity: Vector = velocity

    def update_pos(self, delta_time):
        self.position += self.velocity * delta_time



class Ship(MoveableObject):
    def __init__(self, position: Vector, velocity: Vector, width, height, rotation=0, image="assets/default_image.png") -> None:
        super().__init__(position, velocity, width, height, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.original_image = self.image

    def set_rotation(self, rotation):
        self.rotation = rotation

        # pygame.transform.rotate uses degrees NOT radians
        # so rotation needs to be converted to degrees
        self.image = pygame.transform.rotate(self.original_image, rotation / math.pi * 180)
        self.width = self.image.get_width()
        self.height = self.image.get_height()



class Player_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, width, height, max_speed, rotation=0, image="assets/default_image.png") -> None:
        super().__init__(position, velocity, width, height, rotation, image)
        self.max_speed = max_speed

    def accelerate(self, acceleration: Vector):
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)

    def accelerate_relative(self, acceleration: Vector):
        acceleration.rotate(self.rotation)
        self.velocity += acceleration
        self.velocity.clamp(self.max_speed)
    
    def update_pos(self, delta_time):
        super().update_pos(delta_time)

        # Inertial Dampening
        """
        -> velocity is added with the inverse velocity, making velocity 0
        -> but inverse velocity is clamped so it doesn't go to 0 velocity instantly
        -> 200 is a constant
        -> the bigger the constant, the faster the dampening
        """
        self.velocity -= self.velocity.get_clamp(200 * delta_time)