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

    def __repr__(self):
        return str((self.x, self.y))

    def __round__(self):
        return Vector(round(self.x), round(self.y))

    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5
    
    def to_tuple(self):
        return (self.x, self.y)



class Object():
    def __init__(self, position, width, height, image) -> None:
        
        # Make position a vector
        if type(position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position = position

        self.width = width
        self.height = height
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height)).convert()

    def draw(self, win: pygame.Surface, focus_point, centre_point):
        win.blit(self.image, (round(self.position - focus_point + centre_point)).to_tuple())



class MoveableObject(Object):
    def __init__(self, position, velocity, width, height, image) -> None:
        super().__init__(position, width, height, image)

        # Make velocity a vector
        if type(velocity) != Vector:
            self.velocity = Vector(velocity[0], velocity[1])
        else:
            self.velocity = velocity

    def update_pos(self, delta_time):
        self.position += self.velocity * delta_time

    def set_vel_mag(self, mag):
        k = mag / self.velocity.magnitude()
        self.velocity *= k

    def clamp_vel(self, max_speed):
        if self.velocity.magnitude() > max_speed:
            self.set_vel_mag(max_speed)



class Ship(MoveableObject):
    def __init__(self, position, velocity, width, height, image) -> None:
        super().__init__(position, velocity, width, height, image)



class Player_Ship(Ship):
    def __init__(self, position, velocity, width, height, max_speed, image) -> None:
        super().__init__(position, velocity, width, height, image)
        self.max_speed = max_speed

    def change_vel(self, acceleration):
        self.velocity + acceleration
        self.clamp_vel(self.max_speed)