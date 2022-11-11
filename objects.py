import pygame
import os
import sys



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
        self.rotation = rotation

    def set_rotation(self, rotation):
        self.rotation = rotation
        self.image = pygame.transform.rotate(self.image, rotation)



class Player_Ship(Ship):
    def __init__(self, position: Vector, velocity: Vector, width, height, max_speed, rotation=0, image="assets/default_image.png") -> None:
        super().__init__(position, velocity, width, height, rotation, image)
        self.max_speed = max_speed

    def change_vel(self, acceleration: Vector):
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