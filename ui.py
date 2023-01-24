import game
import images
from objects import Vector
from aiship import AI_Ship
import math
import pygame
import psutil



class Bar():
    """x, y are functions"""
    def __init__(self, x, y, width, height, colour) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.original_width = width
        self.colour = colour

    def update(self, new_percent):
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = self.original_width * new_percent

    def draw(self):
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.x(), self.y() - self.height*0.5, # bar position is middle left
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

        self.add("health_bar", Bar(lambda: 100, lambda: game.HEIGHT-200, width=200, height=40, colour=(255, 0, 0)))
        self.add("boost_bar" , Bar(lambda: 100, lambda: game.HEIGHT-150, width=200, height=40, colour=(0, 0, 255)))
        self.add("speed_bar" , Bar(lambda: 100, lambda: game.HEIGHT-100, width=200, height=40, colour=(30, 190, 190)))
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
font3 = pygame.font.SysFont("consolas", 20)


def cursor_highlighting():
    x, y = pygame.mouse.get_pos()
    cursor_pos = (Vector(x, y) - game.CENTRE_POINT) / game.ZOOM + game.player.position
    canvas.cursor_image.image = images.CURSOR
    game.player.cursor_highlighted = False
    for entity in game.CHUNKS.get_chunk((cursor_pos // game.CHUNK_SIZE).to_tuple()).entities:
        if isinstance(entity, AI_Ship) and (cursor_pos - entity.position).magnitude() < 32:
            canvas.cursor_image.image = images.CURSOR_HIGHLIGHTED
            game.player.cursor_highlighted = True
            game.player.aiming_enemy = entity
            break


bars = 20
last_cpu_usage = 0
def get_usage():
    global last_cpu_usage
    cpu_percent = psutil.cpu_percent()
    if cpu_percent == 0:
        cpu_percent = last_cpu_usage
    else:
        last_cpu_usage = cpu_percent
    cpu_bar = "█" * int((cpu_percent/100) * bars) + "-" * (bars - int((cpu_percent/100) * bars)) # Turns percent into bar visual
    
    mem_percent = psutil.virtual_memory().percent
    mem_bar = "█" * int((mem_percent/100) * bars) + "-" * (bars - int((mem_percent/100) * bars))

    return cpu_percent, mem_percent, cpu_bar, mem_bar


def draw(delta_time):
    pygame.mouse.set_visible(False)


    canvas.health_bar.update(game.player.health/game.MAX_PLAYER_HEALTH)
    canvas.boost_bar.update(game.player.boost_amount/game.MAX_BOOST_AMOUNT)
    canvas.speed_bar.update(game.player.velocity.magnitude()/(game.MAX_PLAYER_SPEED*2))

    canvas.cursor_image.update(pygame.mouse.get_pos())

    cursor_highlighting()
    
    canvas.draw()

    # NOTE: Fonts are rendered differently in pygame 2.1.2 and 2.1.3, use 2.1.3 for best results

    label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH - 300, 8))

    label = font2.render(f"SCORE: {game.SCORE}", True, (255, 10, 10))
    WIN.blit(label, (game.WIDTH/2 - label.get_width()/2, 100))

    if game.DEBUG_SCREEN:
        label = font3.render(f"Position: {round(game.LAST_PLAYER_POS)}", True, (255, 255, 255))
        WIN.blit(label, (0, 8))

        label = font3.render(f"Chunk Position: {game.LAST_PLAYER_POS // game.CHUNK_SIZE}", True, (255, 255, 255))
        WIN.blit(label, (0, 38))

        label = font3.render(f"Angle: {round(game.player.rotation / math.pi * 180 - 180) % 360 - 180}", True, (255, 255, 255))
        WIN.blit(label, (0, 68))

        label = font3.render(f"Zoom: {round(game.ZOOM, 3)}", True, (255, 255, 255))
        WIN.blit(label, (0, 98))

        label = font3.render(f"Mouse Pos: {pygame.mouse.get_pos()}", True, (255, 255, 255))
        WIN.blit(label, (0, 128))

        cpu_usage, memory_usage, cpu_bar, memory_bar = get_usage()

        label = font3.render(f"CPU Usage: |{cpu_bar}| {cpu_usage:.1f}%", True, (255, 255, 255))
        WIN.blit(label, (0, 158))

        label = font3.render(f"Memory Usage: |{memory_bar}| {memory_usage:.1f}%", True, (255, 255, 255))
        WIN.blit(label, (0, 188))

    label = font.render(f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-214))

    label = font.render(f"{round(game.player.boost_amount)} | {game.MAX_BOOST_AMOUNT}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-164))

    label = font.render(f"{round(game.player.velocity.magnitude())}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-114))