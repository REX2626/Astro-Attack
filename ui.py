import game
import images
from objects import Vector
import aiship
from entities import Asteroid, HealthPickup
from station import Station
import math
import pygame
import psutil
import commands



class Bar():
    """x, y are functions"""
    def __init__(self, x, y, width, height, colour, outline_width=0, outline_colour=(250, 250, 255), curve=0, flatten_left=False, flatten_right=False) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.original_width = width
        self.colour = colour
        self.outline_width = outline_width
        self.outline_colour = outline_colour
        self.left_curve = -1 if flatten_left else curve
        self.right_curve = -1 if flatten_right else curve

    def update(self, new_percent):
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = self.original_width * new_percent

    def draw(self):
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.x(), self.y() - self.height/2, # bar position is middle left
                              self.width, self.height),
                        border_top_left_radius=self.left_curve,
                        border_bottom_left_radius=self.left_curve,
                        border_top_right_radius=self.right_curve+self.outline_width, # + self.outline_width to be the same curve as outline
                        border_bottom_right_radius=self.right_curve+self.outline_width
                        )
        if self.outline_width:
            pygame.draw.rect(game.WIN, self.outline_colour,
                        rect=(self.x(), self.y() - self.height/2, # bar position is middle left
                              self.original_width, self.height),
                        width=self.outline_width,
                        border_top_left_radius=self.left_curve,
                        border_bottom_left_radius=self.left_curve,
                        border_top_right_radius=self.right_curve,
                        border_bottom_right_radius=self.right_curve
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
        game.WIN.blit(self.image, (self.x - self.width/2, self.y - self.height/2))



class MiniMap():
    def __init__(self, position, width, height) -> None:
        self.position = position
        self.x, self.y = self.position
        self.width = width
        self.height = height
        self.enemy_colour = (255, 0, 0)
        self.asteroid_colour = game.LIGHT_GREY
        self.player_colour = (255, 255, 255)
        self.neutral_colour = (0, 255, 0)
        self.health_pickup_colour = (0, 0, 255)
        self.entity_size = 3
        self.player_image = images.PLAYER_MINIMAP_IMAGE

    def draw_entity(self, colour, entity, surf):
        if colour:
            pos = (((entity.position.x - game.player.position.x) / game.LOAD_DISTANCE / game.CHUNK_SIZE / 2 * self.width) + (self.width / 2),
                   ((entity.position.y - game.player.position.y) / game.LOAD_DISTANCE / game.CHUNK_SIZE / 2 * self.height) + (self.height / 2))
            
            pygame.draw.circle(surf, colour, pos, self.entity_size)

    def get_entity_colour(self, entity):

        # Changes colour based on type of 
        if isinstance(entity, aiship.Enemy_Ship):
            self.entity_size = 3
            return self.enemy_colour
        elif isinstance(entity, aiship.Neutral_Ship):
            self.entity_size = 3
            return self.neutral_colour
        elif isinstance(entity, Asteroid):
            self.entity_size = 10
            return self.asteroid_colour
        elif isinstance(entity, HealthPickup):
            self.entity_size = 2
            return self.health_pickup_colour

    def draw(self):
        # Draws black background
        pygame.draw.rect(game.WIN, color=game.BLACK, rect=(
            self.x, self.y, self.width, self.height
        ), border_radius=5)

        # Draws enemies in chunks
        surf = pygame.Surface((self.width, self.height))
        for entity in game.CHUNKS.entities:
            if isinstance(entity, Station):
                # Blits station image
                station_image = images.STATION_ICON
                surf.blit(station_image, (((entity.position.x - entity.width/2 - game.player.position.x) / game.LOAD_DISTANCE / game.CHUNK_SIZE / 2 * self.width) + (self.width / 2),
                                          ((entity.position.y - entity.height/2 - game.player.position.y) / game.LOAD_DISTANCE / game.CHUNK_SIZE / 2 * self.height) + (self.height / 2)))
            else:
                self.draw_entity(self.get_entity_colour(entity), entity, surf)

        game.WIN.blit(surf, (0, 0))

        # Draws border
        pygame.draw.rect(game.WIN, color=game.DARK_GREY, rect=(
            self.x, self.y, self.width, self.height
        ), width=7, border_radius=5)

        # Draws player image
        image = pygame.transform.rotate(self.player_image, game.player.rotation / math.pi * 180)
        game.WIN.blit(image, ((self.width / 2) - (image.get_width() / 2), (self.height / 2) - (image.get_height() / 2)))



weapon_selected = 0
class Hotbar():
    def __init__(self, height, number, size, gap) -> None:
        self.height = height
        self.number = number
        self.size = size
        self.gap = gap

        self.images = [pygame.transform.scale_by(images.BULLET, 2), pygame.transform.scale_by(images.GATLING_BULLET, 2), pygame.transform.scale_by(images.SNIPER_BULLET, 2), self.get_laser_image()]

    def get_laser_image(self):
        image = pygame.Surface((20, 36), flags=pygame.SRCALPHA)
        for step in range(6):
            pygame.draw.rect(image, (40, 100, 150, (step+1)/6*255), (step, step, 20-step*2, 36-step*2), border_radius=round(20-step))
        pygame.draw.rect(image, (81, 200, 252), (6, 5, 8, 26), border_radius=4)
        return image

    def draw(self):
        for i in range(self.number):

            if i == weapon_selected:
                colour = (255, 125, 0)

            else:
                colour = (30, 30, 30)

            x = game.CENTRE_POINT.x + self.gap/2 + (i-self.number/2)*(self.size+self.gap)
            y = game.HEIGHT - self.height
            pygame.draw.rect(game.WIN, colour, (x, y, self.size, self.size), width=6, border_radius=7)
            
            image = self.images[i]
            game.WIN.blit(image, (x+self.size/2-image.get_width()/2, y+self.size/2-image.get_height()/2))



class Console():
    def __init__(self) -> None:
        self.left_text_padding = 20
        self.text_input_height = 50
        self.previous_command_gap = 45

        self.input_text = ""
        self.previous_commands = []

        self.text_input_font = pygame.font.Font(None, 64)
        self.previous_commands_font = pygame.font.Font(None, 40)

        self.commands_colour = (255, 204, 0)

        self.commands = {"spawnneutral": commands.spawn_netral_ship,
                         "godmode": commands.god_mode}
        
        self.commands_to_run = []

        self.help_message = ["/spawnneutral(frequency) - spawns in neutral ship at current location",
                             "/godmode(max_health, max_boost) - boosts stats"]

        self.arguements = []

    def check_for_inputs(self):
        # Take an image of the current playing screen, then darken it, and save to be used for drawing
        surf = pygame.Surface((game.WIN.get_size()), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 120), (0, 0, game.WIDTH, game.HEIGHT))
        game.WIN.blit(surf, (0, 0))
        self.playing_background = game.WIN.copy()
        
        # while loop to pause the game and check for inputs
        while game.CONSOLE_SCREEN == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.quit()

                elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                    game.CONSOLE_SCREEN = False
                
                elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_RETURN:
                    self.enter_text()

                elif event.type == pygame.KEYDOWN:
                    # removes last item from input_text string when backspace is pressed
                    if event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]

                    # add pressed character to input_text
                    else:
                        self.input_text += event.unicode

            # must draw here since this is the only game loop running
            self.draw()

    def enter_text(self):
        if self.input_text != "":
            
            # Checks if this is a function which will take in arguements
            if "(" in self.input_text:
                # splits input into the name of the function (in input_command) and a list of the arguements (in self.arguements)
                split_text = self.input_text.split("(")
                input_command = split_text[0]
                split_text[1] = split_text[1][:-1]
                self.arguements = split_text[1].split(", ")
            
            if self.input_text == "help":
                # displays all of the help messages on separate lines
                for message in self.help_message:
                    self.previous_commands.insert(0, message)

            elif input_command in self.commands.keys():
                # must insert at start since when drawing text in draw() it renders text from newest to oldes command entered
                self.previous_commands.insert(0, "/" + self.input_text)

                self.commands_to_run.append(split_text)

            else:
                try:
                    eval(self.input_text)
                    self.previous_commands.insert(0, "/" + self.input_text)
                except:
                    # just returns what you wrote into the command history
                    self.previous_commands.insert(0, self.input_text)

        # resets the input_text
        self.input_text = ""

    def run_commands(self):
        # loops through the dictionary
        for command in self.commands_to_run:
            # runs command corresponding to the key (in this case, the array of keys are in self.commands_to_run)

            # if there is no arguement then just run the function
            if command[1] == "":
                self.commands[command[0]]()

            # if there are arguements input the list of arguements (they are as strings sadly)
            else:
                self.commands[command[0]](self.arguements)
        
        self.commands_to_run.clear()
        
    def draw(self):
        # the if game.CONSOLE_SCREEN: is run to ensure that this draw method is not run when canvas.draw() is run
        if game.CONSOLE_SCREEN:
            # Not defined in __init__ since the game.width and game.height could change mid game
            width = game.WIDTH
            height = game.HEIGHT

            # Darkened playing background and white box
            game.WIN.blit(self.playing_background, (0, 0))
            pygame.draw.rect(game.WIN, game.WHITE, (0, height - self.text_input_height, width, self.text_input_height))

            # Renders input text
            text_surface = self.text_input_font.render("/ " + self.input_text, True, game.BLACK)
            game.WIN.blit(text_surface, (self.left_text_padding, height - self.text_input_height))

            # Loops through all previous commands and displays them above
            for i, command in enumerate(self.previous_commands):
                text_surface = self.previous_commands_font.render(command, True, self.commands_colour)
                game.WIN.blit(text_surface, (self.left_text_padding, height - self.text_input_height - ((i + 1) * self.previous_command_gap)))
            
            # Needed since draw() is called in the while loop
            pygame.display.update()


class Canvas():
    def __init__(self) -> None:
        self.elements = []

        self.add("health_bar", Bar(lambda: game.WIDTH/2-204, lambda: game.HEIGHT-100, width=206, height=46, colour=(255, 0, 0), outline_width=3, curve=7, flatten_right=True))
        self.add("armour_bar", Bar(lambda: game.WIDTH/2-1, lambda: game.HEIGHT-100, width=206, height=46, colour=(255, 160, 30), outline_width=3, curve=7, flatten_left=True))
        self.add("shield_bar", Bar(lambda: 100, lambda: game.HEIGHT-200 , width=200, height=40, colour=(34, 130, 240)))
        self.add("boost_bar" , Bar(lambda: 100, lambda: game.HEIGHT-150, width=200, height=40, colour=(207, 77, 17)))
        self.add("speed_bar" , Bar(lambda: 100, lambda: game.HEIGHT-100, width=200, height=40, colour=(30, 190, 190)))
        self.add("mini_map"  , MiniMap((0, 0), width=350, height=350))
        self.add("hotbar"    , Hotbar(height=195, number=4, size=52, gap=26))
        self.add("cursor_image", Image(pygame.mouse.get_pos(), image=images.CURSOR))
        self.add("console_panel", Console())

    def add(self, name, element):
        self.__setattr__(name, element)
        self.elements.append(element)

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
        if isinstance(entity, aiship.AI_Ship) and (cursor_pos - entity.position).magnitude() < 32:
            canvas.cursor_image.image = images.CURSOR_HIGHLIGHTED
            game.player.cursor_highlighted = True
            game.player.aiming_enemy = entity
            break


def highlight_station():
    x, y = pygame.mouse.get_pos()
    cursor_pos = (Vector(x, y) - game.CENTRE_POINT) / game.ZOOM + game.player.position
    chunk_pos = cursor_pos // game.CHUNK_SIZE
    for cy in range(chunk_pos.y-1, chunk_pos.y+2):
        for cx in range(chunk_pos.x-1, chunk_pos.x+2):
            for entity in game.CHUNKS.get_chunk((cx, cy)).entities:
                if isinstance(entity, Station):
                    x, y = cursor_pos.x, cursor_pos.y
                    if entity.position.x - entity.width/2 <= x <= entity.position.x + entity.width/2 and entity.position.y - entity.height/2 <= y <= entity.position.y + entity.height/2:
                        if entity.mask.get_at((x-entity.position.x+entity.width/2, y-entity.position.y+entity.height/2)):
                            game.player.station_highlighted = entity
                            outline = entity.mask.outline()
                            for i in range(len(outline)):
                                outline[i] = outline[i][0] + entity.position.x - entity.width/2, outline[i][1] + entity.position.y - entity.height/2
                                outline[i] = outline[i][0] - game.player.position.x, outline[i][1] - game.player.position.y
                                outline[i] = outline[i][0] * game.ZOOM, outline[i][1] * game.ZOOM
                                outline[i] = outline[i][0] + game.CENTRE_POINT.x, outline[i][1] + game.CENTRE_POINT.y
                            pygame.draw.polygon(game.WIN, (255, 0, 0), outline, width=round(3*game.ZOOM))
                            return
    game.player.station_highlighted = None

bars = 20
time_elapsed = 0
last_cpu_percent = 0
last_mem_percent = 0
last_cpu_bar = ""
last_mem_bar = ""
def get_usage(delta_time):

    global time_elapsed
    time_elapsed += delta_time
    if time_elapsed > 0.1: # updates 10 times a second

        global last_cpu_percent, last_mem_percent, last_cpu_bar, last_mem_bar
        cpu_percent = psutil.cpu_percent()
        if cpu_percent == 0:
            cpu_percent = last_cpu_percent
        else:
            last_cpu_percent = cpu_percent
        cpu_bar = "█" * int((cpu_percent/100) * bars) + "-" * (bars - int((cpu_percent/100) * bars)) # Turns percent into bar visual
        
        mem_percent = psutil.virtual_memory().percent
        mem_bar = "█" * int((mem_percent/100) * bars) + "-" * (bars - int((mem_percent/100) * bars))

        time_elapsed = 0
        last_cpu_percent, last_mem_percent, last_cpu_bar, last_mem_bar = cpu_percent, mem_percent, cpu_bar, mem_bar

    else:
        cpu_percent, mem_percent, cpu_bar, mem_bar = last_cpu_percent, last_mem_percent, last_cpu_bar, last_mem_bar

    return cpu_percent, mem_percent, cpu_bar, mem_bar


min_fps_elapsed_time = 0
min_fps = math.inf
showing_min_fps = 0
def get_minimum_fps(delta_time):

    global min_fps_elapsed_time, min_fps, showing_min_fps
    min_fps_elapsed_time += delta_time
    if min_fps_elapsed_time > 1:

        min_fps_elapsed_time = 0
        showing_min_fps = min_fps
        min_fps = math.inf

    if 1/delta_time < min_fps:
        min_fps = 1/delta_time

    return showing_min_fps


def draw(delta_time):
    pygame.mouse.set_visible(False)


    canvas.health_bar.update(game.player.health/game.MAX_PLAYER_HEALTH)
    canvas.armour_bar.update(game.player.armour/game.MAX_PLAYER_ARMOUR)
    canvas.shield_bar.update(game.player.shield/game.player.max_shield)
    canvas.boost_bar.update(game.player.boost_amount/game.MAX_BOOST_AMOUNT)
    canvas.speed_bar.update(game.player.velocity.magnitude()/(game.MAX_PLAYER_SPEED*2))

    canvas.cursor_image.update(pygame.mouse.get_pos())

    cursor_highlighting()

    highlight_station()
    
    canvas.draw()

    # NOTE: Fonts are rendered differently in pygame 2.1.2 and 2.1.3, use 2.1.3 for best results

    label = font.render(f"FPS: {round(1 / delta_time)}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH - 300, 8))

    label = font2.render(f"SCORE: {game.SCORE}", True, (255, 10, 10))
    WIN.blit(label, (game.WIDTH/2 - label.get_width()/2, 100))

    if game.DEBUG_SCREEN:
        label = font3.render(f"Position: {round(game.LAST_PLAYER_POS)}", True, (255, 255, 255))
        WIN.blit(label, (8, 8))

        label = font3.render(f"Chunk Position: {game.LAST_PLAYER_POS // game.CHUNK_SIZE}", True, (255, 255, 255))
        WIN.blit(label, (8, 38))

        label = font3.render(f"Angle: {round(game.player.rotation / math.pi * 180 - 180) % 360 - 180}", True, (255, 255, 255))
        WIN.blit(label, (8, 68))

        label = font3.render(f"Zoom: {round(game.ZOOM, 3)}", True, (255, 255, 255))
        WIN.blit(label, (8, 98))

        label = font3.render(f"Mouse Pos: {pygame.mouse.get_pos()}", True, (255, 255, 255))
        WIN.blit(label, (8, 128))

        cpu_usage, memory_usage, cpu_bar, memory_bar = get_usage(delta_time)

        label = font3.render(f"CPU Usage: |{cpu_bar}| {cpu_usage:.1f}%", True, (255, 255, 255))
        WIN.blit(label, (8, 158))

        label = font3.render(f"Memory Usage: |{memory_bar}| {memory_usage:.1f}%", True, (255, 255, 255))
        WIN.blit(label, (8, 188))

        minimum = get_minimum_fps(delta_time)

        label = font3.render(f"Minimum FPS: {round(minimum)}", True, (255, 255, 255))
        WIN.blit(label, (8, 218))

        label = font3.render(f"Seed: {game.SEED}", True, (255, 255, 255))
        WIN.blit(label, (8, 248))

    label = font.render(f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH/2-193, game.HEIGHT-114))

    label = font.render(f"{round(game.player.armour)}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH/2+10, game.HEIGHT-114))

    label = font.render(f"{round(game.player.shield)} | {round(game.player.max_shield)}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-214))

    label = font.render(f"{round(game.player.boost_amount)} | {game.MAX_BOOST_AMOUNT}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-164))

    label = font.render(f"{round(game.player.velocity.magnitude())}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-114))