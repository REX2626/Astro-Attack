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

    def __repr__(self):
        return str((self.x, self.y))

    def __round__(self):
        self.x = round(self.x)
        self.y = round(self.y)



class Object():
    def __init__(self, position, width, height, image) -> None:
        
        # Make position a vector
        if type(self.position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position = position

        self.width = width
        self.height = height
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height)).convert()

    def draw(self, win: pygame.Surface, focus_point):
        win.blit(self.image, (round(self.position - focus_point)))



class MoveableObject(Object):
    def __init__(self, position, velocity, width, height, image) -> None:
        super().__init__(position, width, height, image)
        self.vx = vx
        self.vy = vy

    def update_posx(self, delta_time):
        self.position.x += self.vx * delta_time
    
    def update_posy(self, delta_time):
        self.position.y += self.vy * delta_time

    def update_pos(self, delta_time):
        self.update_posx(delta_time)
        self.update_posy(delta_time)
        self.position += self.velocity * delta_time

    def change_vel(self, ax, ay):
        self.vx += ax
        self.vy += ay

    def get_mag(self, a, b):
        return (a**2 + b**2) ** 0.5

    def vel_mag(self):
        return self.get_mag(self.vx, self.vy)

    def set_vel_mag(self, mag):
        k = mag / self.vel_mag()
        self.vx *= k
        self.vy *= k

    def clamp_vel(self, max_speed):
        if self.vel_mag() > max_speed:
            self.set_vel_mag(max_speed)



class Ship(MoveableObject):
    def __init__(self, x, y, vx, vy, width, height, image) -> None:
        super().__init__(x, y, vx, vy, width, height, image)



class Player_Ship(Ship):
    def __init__(self, x, y, vx, vy, width, height, max_speed, image) -> None:
        super().__init__(x, y, vx, vy, width, height, image)
        self.max_speed = max_speed

    def change_vel(self, ax, ay):
        self.vx += ax
        self.vy += ay
        self.clamp_vel(self.max_speed)