import game
import images
from objects import Vector
from aiship import AI_Ship
import math
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
        self.add("cursor_image", Image(pygame.mouse.get_pos(), image=images.CURSOR))

    def add(self, name, element):
        self.__setattr__(name, element)
        self.elements.add(element)

    def draw(self):
        for element in self.elements:
            element.draw()

canvas = Canvas()


WIN = game.WIN
font = pygame.font.SysFont("bahnschrift", 30)
font2 = pygame.font.SysFont("bahnschrift", 50)


def cursor_highlighting():
        x, y = pygame.mouse.get_pos()
        cursor_pos = (Vector(x, y) - game.CENTRE_POINT) / game.ZOOM + game.player.position
        canvas.cursor_image.image = images.CURSOR
        game.player.cursor_highlighted = False
        for entity in game.CHUNKS.get_chunk((cursor_pos // game.CHUNK_SIZE).to_tuple()).entities:
            if isinstance(entity, AI_Ship) and (cursor_pos - entity.position).magnitude() < 32:
                canvas.cursor_image.image = images.CURSOR_HIGHLIGHTED
                game.player.cursor_highlighted = True
                game.player.current_enemy_aiming = entity
                break


def draw(delta_time):
    pygame.mouse.set_visible(False)


    canvas.health_bar.update(game.player.health/game.MAX_PLAYER_HEALTH)
    canvas.boost_bar.update(game.player.boost_amount/game.MAX_BOOST_AMOUNT)
    canvas.speed_bar.update(game.player.velocity.magnitude()/1000)

    canvas.cursor_image.update(pygame.mouse.get_pos())

    cursor_highlighting()
    
    canvas.draw()

    # NOTE: Fonts are rendered differently in pygame 2.1.2 and 2.1.3, use 2.1.3 for best results

    label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH - 300, 8))

    label = font.render(f"Angle: {round(game.player.rotation / math.pi * 180 - 180) % 360 - 180}", True, (255, 255, 255))
    WIN.blit(label, (200, 8))

    label = font2.render(f"SCORE: {game.SCORE}", True, (255, 10, 10))
    WIN.blit(label, (game.WIDTH/2 - label.get_width()/2, 100))

    label = font.render(f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-214))

    label = font.render(f"{round(game.player.boost_amount)} | {game.MAX_BOOST_AMOUNT}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-164))

    label = font.render(f"{round(game.player.velocity.magnitude())}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-114))