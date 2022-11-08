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



class Object():
    def __init__(self, x, y, width, height, image) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = pygame.transform.scale(pygame.image.load(image), (width, height)).convert()

    def draw(self, win: pygame.Surface):
        print(self.x, self.y)
        win.blit(self.image, (round(self.x), round(self.y)))



class MoveableObject(Object):
    def __init__(self, x, y, vx, vy, width, height, image) -> None:
        super().__init__(x, y, width, height, image)
        self.vx = vx
        self.vy = vy

    def update_posx(self, delta_time):
        self.x += self.vx * delta_time
    
    def update_posy(self, delta_time):
        self.y += self.vy * delta_time

    def update_pos(self, delta_time):
        self.update_posx(delta_time)
        self.update_posy(delta_time)

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