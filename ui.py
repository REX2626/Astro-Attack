import game
import images
from objects import Vector
import pygame



class Bar():
    def __init__(self, position, width, height, colour) -> None:
        self.position = position
        self.width = width
        self.height = height
        self.original_width = width
        self.colour = colour

    def update(self, new_percent):
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = self.original_width * new_percent

    def draw(self):
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.position.x, self.position.y - self.height*0.5, # bar position is middle left
                              self.width, self.height)
                        )


class Image():
    def __init__(self, position, image=images.DEFAULT) -> None:
        self.position = position
        self.x, self.y = self.position
        self.width = image.get_width()
        self.height = image.get_height()
        self.image = image

    def update(self, new_position):
        """Updates position of the image"""
        self.position = new_position
        self.x, self.y = self.position

    def draw(self):
        game.WIN.blit(self.image, (self.x - self.width*0.5, self.y - self.height*0.5))



class Canvas():
    def __init__(self) -> None:
        self.elements = set()

        self.add("health_bar", Bar(Vector(100, game.HEIGHT-200), width=200, height=40, colour=(255, 0, 0)))
        self.add("boost_bar", Bar(Vector(100, game.HEIGHT-150), width=200, height=40, colour=(0, 0, 255)))
        self.add("speed_bar", Bar(Vector(100, game.HEIGHT-100), width=200, height=40, colour=(30, 190, 190)))
        self.add("cursor_image", Image(pygame.mouse.get_pos(), image=images.CURSOR1))

    def add(self, name, element):
        self.__setattr__(name, element)
        self.elements.add(element)

    def draw(self):
        for element in self.elements:
            element.draw()

canvas = Canvas()