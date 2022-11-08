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
        self.image = image

    def draw(self, win: pygame.Surface):
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