from objects import Vector
from entities import Asteroid, Scrap
from station import Station, EnemyStation, FriendlyStation
import aiship
from aiship import Neutral_Ship_Cargo, Enemy_Ship, Drone_Enemy, Missile_Ship,  Mother_Ship, Neutral_Ship_Fighter # For commands
import images
import game
import commands
import math
import time
import psutil
from pygame import freetype
import pygame



class Bar():
    """
    x, y are functions

    width and height are for the outline
    """
    def __init__(self, x, y, width, height, colour, outline_width=0, outline_colour=game.WHITE, curve=0, flatten_left=False, flatten_right=False) -> None:
        self.x = x
        self.y = y
        self.width = width-outline_width*2
        self.height = height
        self.original_width = width
        self.colour = colour
        self.outline_width = outline_width
        self.outline_colour = outline_colour
        self.left_curve = -1 if flatten_left else curve
        self.right_curve = -1 if flatten_right else curve

    def update(self, new_percent):
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = (self.original_width-self.outline_width*2) * min(1, new_percent)

    def draw(self):
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.x()+self.outline_width, self.y() - self.height/2 + self.outline_width, # bar position is middle left
                              self.width, self.height-self.outline_width*2),

                        border_top_left_radius=self.left_curve-self.outline_width, # - self.outline_width to be the same curve as the inside curve of the outline
                        border_bottom_left_radius=self.left_curve-self.outline_width,
                        border_top_right_radius=self.right_curve-self.outline_width,
                        border_bottom_right_radius=self.right_curve-self.outline_width
                        )

        if self.outline_width:
            pygame.draw.rect(game.WIN, self.outline_colour,
                        rect=(self.x()           , self.y() - self.height/2, # bar position is middle left
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
        self.x, self.y = position
        self.width = width
        self.height = height

        self.border_width = 7
        self.draw_width = width - 2*self.border_width
        self.draw_height = height - 2*self.border_width

        self.player_colour = (255, 255, 255)
        self.neutral_colour = (5, 230, 20)
        self.enemy_colour = (230, 0, 0)
        self.asteroid_colour = game.LIGHT_GREY
        self.scrap_colour = (255, 255, 0)
        self.entity_size = 3
        self.player_image = images.PLAYER_MINIMAP_IMAGE

    def draw_entity(self, colour, entity, surf):
        if colour:
            pos = (((entity.position.x - game.player.position.x) / (game.LOAD_DISTANCE-1) / game.CHUNK_SIZE / 2 * self.draw_width) + (self.draw_width / 2),
                   ((entity.position.y - game.player.position.y) / (game.LOAD_DISTANCE-1) / game.CHUNK_SIZE / 2 * self.draw_height) + (self.draw_height / 2))

            pygame.draw.circle(surf, colour, pos, self.entity_size)

    def get_entity_colour(self, entity):

        # Changes colour based on type
        if isinstance(entity, aiship.Enemy_Ship):
            self.entity_size = 3
            return self.enemy_colour
        elif isinstance(entity, aiship.Neutral_Ship):
            self.entity_size = 3
            return self.neutral_colour
        elif isinstance(entity, Asteroid):
            self.entity_size = 10
            return self.asteroid_colour
        elif isinstance(entity, Scrap):
            self.entity_size = 2
            return self.scrap_colour

    def draw(self):
        # Draws enemies in chunks
        surf = pygame.Surface((self.draw_width, self.draw_height))

        for entity in filter(lambda entity: isinstance(entity, Station), game.CHUNKS.entities):
            # Blits station image, (game.LOAD_DISTANCE-1) so that entities do not vanish if near minimap edge
            station_image = images.ENEMY_STATION_ICON if isinstance(entity, EnemyStation) else images.FRIENDLY_STATION_ICON
            surf.blit(station_image, (((entity.position.x - entity.width/2 - game.player.position.x) / (game.LOAD_DISTANCE-1) / game.CHUNK_SIZE / 2 * self.draw_width) + (self.draw_width / 2),
                                      ((entity.position.y - entity.height/2 - game.player.position.y) / (game.LOAD_DISTANCE-1) / game.CHUNK_SIZE / 2 * self.draw_height) + (self.draw_height / 2)))

        for entity in filter(lambda entity: not isinstance(entity, Station), game.CHUNKS.entities):
            self.draw_entity(self.get_entity_colour(entity), entity, surf)

        game.WIN.blit(surf, (self.border_width, self.border_width))

        # Draws border
        pygame.draw.rect(game.WIN, color=game.DARK_GREY, rect=(
            self.x, self.y, self.width, self.height
        ), width=self.border_width, border_radius=5)

        # Draws player image
        image = pygame.transform.rotate(self.player_image, game.player.rotation / math.pi * 180)
        game.WIN.blit(image, ((self.width / 2) - (image.get_width() / 2), (self.height / 2) - (image.get_height() / 2)))



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

            if i == game.WEAPON_SELECTED:
                colour = (255, 125, 0)

            else:
                colour = game.DARK_GREY

            x = game.CENTRE_POINT.x + self.gap/2 + (i-self.number/2)*(self.size+self.gap)
            y = game.HEIGHT - self.height
            pygame.draw.rect(game.WIN, colour, (x, y, self.size, self.size), width=6, border_radius=7)

            image = self.images[i]
            game.WIN.blit(image, (x+self.size/2-image.get_width()/2, y+self.size/2-image.get_height()/2))



class Console():
    def __init__(self) -> None:
        self.left_text_padding = 20
        self.text_input_height = 50
        self.chat_history_gap = 45

        self.input_text = ""
        self.chat_history = []

        self.text_input_font = pygame.font.SysFont("consolas", 50)
        self.chat_history_font = pygame.font.SysFont("consolas", 35)

        self.commands_colour = (255, 204, 0)
        self.old_commands_colour = (105, 89, 26)
        self.output_colour = (30, 80, 240)
        self.miscellaneous_colour = (186, 186, 186)
        self.entity_list_colour = (100, 180, 180)
        self.error_colour = (199, 46, 12)

        self.commands = {"godmode": commands.god_mode,
                         "kill": commands.kill,
                         "score": commands.add_score,
                         "spawnentity": commands.spawn_entity,
                         "tp": commands.teleport,
                         "zoom": commands.change_max_zoom}

        # console_commands mean that the command is written in this class
        self.console_commands = {"log": self.log}

        self.commands_to_run = []

        self.help_message = ["/entitylist - prints entities that can be spawned",
                             "/godmode (max_health) (max_boost) - boosts stats",
                             "/kill - removes all entities apart from player",
                             "/log (argument) - prints argument to console",
                             "/score (score) - adds score to current score",
                             "/spawnentity (entity_class) (frequency) - spawns entity at current location",
                             "/tp (x) (y) - teleports player to coordinates (x, y)",
                             "/zoom (zoom_level) - changes how far you can zoom out"]

        self.entity_list_message = ["EnemyStation, FriendlyStation, Neutral_Ship_Cargo, Enemy_Ship,",
                                    "Drone_Enemy, Missile_Ship,  Mother_Ship, Neutral_Ship_Fighter, Scrap"]

        self.current_selected_command = 0

        self.previous_commands = []

        self.cursor_pos = 0

    def check_for_inputs(self):
        # Take an image of the current playing screen, then darken it, and save to be used for drawing
        surf = pygame.Surface((game.WIN.get_size()), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 200), (0, 0, game.WIDTH, game.HEIGHT))
        game.WIN.blit(surf, (0, 0))
        self.playing_background = game.WIN.copy()

        # If a button is held for more than 0.5 second, spam it every 0.08 seconds
        button_spam_time = math.inf
        button_pressed_event = None

        # while loop to pause the game and check for inputs
        while game.CONSOLE_SCREEN == True:
            events = pygame.event.get()

            if time.perf_counter() - button_spam_time > 0.08:
                events.append(button_pressed_event)
                button_spam_time = time.perf_counter()

            for event in events:
                if event.type == pygame.QUIT:
                    game.quit()

                elif event.type == pygame.KEYDOWN:

                    if button_pressed_event != event:
                        button_spam_time = time.perf_counter() + 0.42
                        button_pressed_event = event

                    if event.key == pygame.K_ESCAPE:
                        game.CONSOLE_SCREEN = False

                    elif event.key == pygame.K_RETURN:
                        self.enter_text()

                    elif event.key == pygame.K_UP:
                        self.up_pressed()

                    elif event.key == pygame.K_DOWN:
                        self.down_pressed()

                    elif event.key == pygame.K_LEFT:
                        if event.mod & pygame.KMOD_CTRL:
                            self.ctrl_left_pressed()
                        else:
                            self.left_pressed()

                    elif event.key == pygame.K_RIGHT:
                        if event.mod & pygame.KMOD_CTRL:
                            self.ctrl_right_pressed()
                        else:
                            self.right_pressed()

                    # removes last item from input_text string when backspace is pressed
                    elif event.key == pygame.K_BACKSPACE:
                        if self.cursor_pos > 0:
                            self.cursor_pos -= 1
                            self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos+1:]

                    elif event.key == pygame.K_DELETE:
                        self.input_text = self.input_text[:self.cursor_pos+1] + self.input_text[self.cursor_pos+2:]

                    # ctrl + x copies text to clipboard then deletes text
                    elif event.key == pygame.K_x and event.mod & pygame.KMOD_CTRL:
                        pygame.scrap.put_text(self.input_text)
                        self.input_text = ""
                        self.cursor_pos = 0

                    # ctrl + c copies text to clipboard
                    elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                        pygame.scrap.put_text(self.input_text)

                    # ctrl + v pastes clipboard
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                        clipboard_text = pygame.scrap.get_text()
                        self.input_text = self.input_text[:self.cursor_pos] + clipboard_text + self.input_text[self.cursor_pos:]
                        self.cursor_pos += len(clipboard_text)

                    # add pressed character to input_text
                    else:
                        start_len = len(self.input_text)
                        self.input_text = self.input_text[:self.cursor_pos] + event.unicode + self.input_text[self.cursor_pos:]
                        end_len = len(self.input_text)
                        if start_len != end_len:
                            self.cursor_pos += 1

                elif event.type == pygame.KEYUP:
                    button_spam_time = math.inf
                    button_pressed_event = None

            # must draw here since this is the only game loop running
            self.draw()

    def enter_text(self):
        self.current_selected_command = 0

        if self.input_text != "":
            self.input_text = self.input_text.replace("|", "")

            split_text = self.input_text.split()
            if split_text: input_command = split_text[0]
            else: input_command = ""
            arguments = split_text[1:]

            if self.input_text == "help":
                self.previous_commands.insert(0, self.input_text)

                # displays all of the help messages on separate lines
                for message in self.help_message:
                    self.chat_history.insert(0, [message, self.miscellaneous_colour])

            elif self.input_text == "entitylist":
                self.previous_commands.insert(0, self.input_text)

                for message in self.entity_list_message:
                    self.chat_history.insert(0, [message, self.entity_list_colour])

            elif input_command in self.console_commands:
                self.previous_commands.insert(0, self.input_text)

                try:
                    self.console_commands[input_command](eval(",".join(arguments)))
                except Exception as exception:
                    self.chat_history.insert(0, [str(exception), self.error_colour])


            elif input_command in self.commands:
                # must insert at start since when drawing text in draw() it renders text from newest to oldest command entered
                self.chat_history.insert(0, ["/" + self.input_text, self.commands_colour])
                self.previous_commands.insert(0, self.input_text)

                self.commands_to_run.append((input_command, arguments))

            else:
                try:
                    exec(self.input_text)
                    self.chat_history.insert(0, ["/" + self.input_text, self.commands_colour])
                    self.previous_commands.insert(0, self.input_text)
                except:
                    # just returns what you wrote into the command history
                    self.chat_history.insert(0, [self.input_text, self.miscellaneous_colour])
                    self.previous_commands.insert(0, self.input_text)

        # resets the input_text
        self.input_text = ""

        self.cursor_pos = 0

    def up_pressed(self):
        if self.current_selected_command < len(self.previous_commands):
            self.current_selected_command += 1

            command = self.previous_commands[self.current_selected_command - 1]
            self.input_text = command

    def down_pressed(self):
        if self.current_selected_command > 1:
            self.current_selected_command -= 1

            command = self.previous_commands[self.current_selected_command - 1]
            self.input_text = command
        else:
            self.current_selected_command = 0
            self.input_text = ""
            self.cursor_pos = 0

    def left_pressed(self) -> None:
        self.input_text = self.input_text.replace("|", "")
        if self.cursor_pos == 0:
            self.cursor_pos = len(self.input_text)
            self.input_text = self.input_text[:self.cursor_pos] + "|"
        else:
            self.cursor_pos -= 1
            self.input_text = self.input_text[:self.cursor_pos] + "|" + self.input_text[self.cursor_pos:]

    def right_pressed(self) -> None:
        self.input_text = self.input_text.replace("|", "")
        if self.cursor_pos == len(self.input_text):
            self.cursor_pos = 0
            self.input_text = "|" + self.input_text[self.cursor_pos:]
        else:
            self.cursor_pos += 1
            self.input_text = self.input_text[:self.cursor_pos] + "|" + self.input_text[self.cursor_pos:]

    def ctrl_left_pressed(self) -> None:
        self.input_text = self.input_text.replace("|", "")
        if self.cursor_pos == 0:
            self.cursor_pos = len(self.input_text)
            self.input_text = self.input_text + "|"
        else:
            self.cursor_pos = 0
            self.input_text = "|" + self.input_text

    def ctrl_right_pressed(self) -> None:
        self.input_text = self.input_text.replace("|", "")
        if self.cursor_pos == len(self.input_text):
            self.cursor_pos = 0
            self.input_text = "|" + self.input_text
        else:
            self.cursor_pos = len(self.input_text)
            self.input_text = self.input_text + "|"

    def run_commands(self):
        # loops through the dictionary
        for command, args in self.commands_to_run:
            # runs command corresponding to the key (in this case, the array of keys are in self.commands_to_run)

            # if there are arguments eval the list of arguments
            if args:
                try:
                    self.commands[command](eval(",".join(args)))
                except Exception as exception:
                    self.chat_history.insert(0, [str(exception), self.error_colour])

            # if there is no argument then just run the function
            else:
                try:
                    self.commands[command]()
                except Exception as exception:
                    self.chat_history.insert(0, [str(exception), self.error_colour])

        self.commands_to_run.clear()

        # Change colour of previously run commands
        for command in self.chat_history:
            if command[1] == self.commands_colour:
                command[1] = self.old_commands_colour

    def log(self, argument):
        self.chat_history.insert(0, ["/" + self.input_text, self.commands_colour])
        self.chat_history.insert(0, [f"{argument}", self.output_colour])

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
            text_surface = self.text_input_font.render("/" + self.input_text, True, game.BLACK)
            game.WIN.blit(text_surface, (self.left_text_padding, height - self.text_input_height + (0 if "|" in self.input_text else 2)))

            # Loops through all previous commands and displays them above
            for i, command in enumerate(self.chat_history):
                text_surface = self.chat_history_font.render(command[0], True, command[1])
                game.WIN.blit(text_surface, (self.left_text_padding, height - self.text_input_height - ((i + 1) * self.chat_history_gap)))

            # Needed since draw() is called in the while loop
            pygame.display.update()



class AdjustableText():
    def __init__(self, top_x, top_y, bottom_x, bottom_y, font, default_font_size, colour, text="Text") -> None:
        self.top_x = top_x
        self.top_y = top_y
        self.bottom_x = bottom_x
        self.bottom_y = bottom_y

        self.words = text.split()
        self.font_type = font
        self.default_font_size = default_font_size
        self.colour = colour

        self.font = freetype.SysFont(self.font_type, self.default_font_size)

        self.line_spacing = self.font.get_sized_height()

        self.low_letters = ["g", "j", "q", "p", "y"]

    def render_words(self):
        low_letter_difference = self.font.get_rect("y").height - self.font.get_rect("u").height
        low_letter = False
        x, y = self.top_x, self.top_y
        space = self.font.get_rect(' ')

        render_list = []

        for word in self.words:
            bounds = self.font.get_rect(word)

            for letter in self.low_letters:
                if letter in word:
                    low_letter = True
                    break

            if x + bounds.width >= self.bottom_x:
                x, y = self.top_x, y + self.line_spacing

            if x + bounds.width >= self.bottom_x or y + self.line_spacing >= self.bottom_y:
                break

            if low_letter:
                render_list.append((x, y + (self.line_spacing - bounds.height), word))
                low_letter = False
            else:
                render_list.append((x, y + (self.line_spacing - bounds.height) - low_letter_difference, word))
            x += bounds.width + space.width

        return render_list

    def draw(self):
        # pygame.draw.rect(game.WIN, (0, 0, 0), (self.top_x, self.top_y, self.bottom_x - self.top_x, self.bottom_y-self.top_y), width=2)

        render_list = self.render_words()

        while len(render_list) < len(self.words):
            self.default_font_size -= 1
            self.font = freetype.SysFont(self.font_type, self.default_font_size)
            self.line_spacing = self.font.get_sized_height()
            render_list = self.render_words()

        for element in render_list:
            self.font.render_to(game.WIN, (element[0], element[1]), text=element[2], fgcolor=self.colour)



class MissionOverview():
    def __init__(self, x, y, width, height) -> None:
        # Coordinates are from right side of MissionOverview ui to make it easier
        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.font = freetype.SysFont("bahnschrift", 30)

        self.claim_reward_label, (*_, self.claim_reward_label_width, self.claim_reward_label_height) = self.font.render("Claim Reward", (255, 182, 36))
        self.mission_label = self.font.render("Mission", (255, 255, 255))[0]
        self.kill_mission_label = self.font.render("Kill Mission", (255, 255, 255))[0]

        self.title_label = self.mission_label

        self.info = "You do not have a mission currently"
        self.info_text = AdjustableText(self.x() - self.width + 10, self.y() - self.height/4 - 50, self.x() - 10, self.y() + self.height/4 - 40, "bahnschrift", 30, (255, 255, 255), self.info)

        self.progress_text = "0/0"
        self.progress_label = self.font.render(self.progress_text, (255, 255, 255))[0]
        self.progress_bar = Bar(lambda: self.x() - self.width + 10, lambda: self.y() + self.height/3 + 20, self.width - 20, 50, (0, 0, 255), 2, (0, 0, 0), 5)

    def draw(self):
        pygame.draw.rect(game.WIN, game.DARK_GREY, (self.x() - self.width, self.y() - (self.height/2), self.width, self.height), border_radius=7)

        if game.CURRENT_MISSION:
            if game.CURRENT_MISSION[0] >= game.CURRENT_MISSION[1]:  # If reward completed: draw "Claim Reward"
                game.WIN.blit(self.claim_reward_label, (self.x()-self.claim_reward_label_width/2-self.width/2, self.y()+self.height/4-self.claim_reward_label_height/2))
            else:
                progress_text = f"{game.CURRENT_MISSION[0]}/{game.CURRENT_MISSION[1]}"
                if progress_text != self.progress_text:
                    self.progress_text = progress_text
                    self.progress_label = self.font.render(self.progress_text, (255, 255, 255))[0]
                game.WIN.blit(self.progress_label, (self.x()-self.progress_label.get_width()/2-self.width/2, self.y()+self.height/4-self.progress_label.get_height()/2))

                self.progress_bar.update(game.CURRENT_MISSION[0]/game.CURRENT_MISSION[1])
                self.progress_bar.draw()

            if game.CURRENT_MISSION[3] == game.KILL:
                self.title_label = self.kill_mission_label
                self.info = f"Kill {game.CURRENT_MISSION[1]} {game.ENTITY_DICT.get(game.CURRENT_MISSION[2])}s"

        else:
            self.title_label = self.mission_label
            self.info = "You do not have a mission currently"

        game.WIN.blit(self.title_label, (self.x()-self.title_label.get_width()/2-self.width/2, self.y()-self.height/2+self.title_label.get_height()/2))

        self.info_text.words = self.info.split()
        self.info_text.top_x = self.x() - self.width + 10
        self.info_text.top_y = self.y() - self.height/4 - 50
        self.info_text.bottom_x = self.x() - 10
        self.info_text.bottom_y = self.y() + self.height/4 - 40
        self.info_text.draw()



class Canvas():
    def __init__(self) -> None:
        self.elements = []

        self.add("health_bar", Bar(lambda: game.WIDTH/2-204, lambda: game.HEIGHT-100, width=206, height=46, colour=(255, 0, 0), outline_width=3, curve=7, flatten_right=True))
        self.add("armour_bar", Bar(lambda: game.WIDTH/2-1, lambda: game.HEIGHT-100, width=206, height=46, colour=(185, 185, 185), outline_width=3, curve=7, flatten_left=True))
        self.add("shield_bar", Bar(lambda: 97, lambda: game.HEIGHT-212 , width=206, height=46, colour=(34, 130, 240), outline_width=3, curve=7))
        self.add("boost_bar" , Bar(lambda: 97, lambda: game.HEIGHT-156, width=206, height=46, colour=(217, 87, 27), outline_width=3, curve=7))
        self.add("speed_bar" , Bar(lambda: 97, lambda: game.HEIGHT-100, width=206, height=46, colour=(30, 190, 190), outline_width=3, curve=7))
        self.add("mini_map"  , MiniMap((0, 0), width=350, height=350))
        self.add("hotbar"    , Hotbar(height=195, number=4, size=52, gap=26))
        self.add("mission_overview", MissionOverview(lambda: game.WIDTH, lambda: game.HEIGHT/2, 200, 400))
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


def update_closest_station():
    """Updates the current closest station"""
    closest_station = None
    distance = math.inf
    chunk_pos = game.player.position // game.CHUNK_SIZE
    for cy in range(chunk_pos.y-1, chunk_pos.y+2):
        for cx in range(chunk_pos.x-1, chunk_pos.x+2):
            for entity in game.CHUNKS.get_chunk((cx, cy)).entities:
                if isinstance(entity, FriendlyStation):
                    dist = game.player.distance_to(entity)
                    if dist < 500 and dist < distance:
                        distance = dist
                        closest_station = entity

    if closest_station:
        # Draw E popup
        size = 50
        x = 0
        y = 360
        border = 7

        # Draw background
        pygame.draw.rect(game.WIN, game.MEDIUM_GREY, (x+border, y+border, size-2*border, size-2*border))

        # Draw outline
        pygame.draw.rect(game.WIN, game.DARK_GREY, (x, y, size, size), width=border, border_radius=5)

        # Draw letter E
        label = font.render("E", True, (255, 255, 255))
        game.WIN.blit(label, (x+size/2-label.get_width()/2, y+size/2-font.get_height()/2))

    game.player.closest_station = closest_station


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
        min_fps = 1 / delta_time

    return showing_min_fps


average_fps_elapsed_time = 0
average_fps = 0
n_fps = 1
showing_average_fps = 0
def get_average_fps(delta_time):

    global average_fps_elapsed_time, average_fps, n_fps, showing_average_fps
    average_fps_elapsed_time += delta_time
    if average_fps_elapsed_time > 1:

        average_fps_elapsed_time = 0
        showing_average_fps = average_fps
        average_fps = 1 / delta_time
        n_fps = 1

    else:
        average_fps = (1 / delta_time + n_fps * average_fps) / (n_fps + 1)
        n_fps += 1

    return showing_average_fps


def draw(delta_time):
    pygame.mouse.set_visible(False)


    canvas.health_bar.update(game.player.health/game.MAX_PLAYER_HEALTH)
    canvas.armour_bar.update(game.player.armour/game.MAX_PLAYER_ARMOUR)
    canvas.shield_bar.update(game.player.shield/game.player.max_shield)
    canvas.boost_bar.update(game.player.boost_amount/game.MAX_BOOST_AMOUNT)
    canvas.speed_bar.update(game.player.velocity.magnitude()/(game.MAX_PLAYER_SPEED*2))

    canvas.cursor_image.update(pygame.mouse.get_pos())

    cursor_highlighting()

    update_closest_station()

    canvas.draw()

    label = font.render(f"FPS: {round(get_average_fps(delta_time))}", True, (255, 255, 255))
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

        label = font3.render(f"Difficulty: {game.CURRENT_SHIP_LEVEL}", True, (255, 255, 255))
        WIN.blit(label, (8, 278))

    label = font.render(f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH/2-193, game.HEIGHT-114))

    label = font.render(f"{round(game.player.armour)}", True, (255, 255, 255))
    WIN.blit(label, (game.WIDTH/2+10, game.HEIGHT-114))

    label = font.render(f"{round(game.player.shield)} | {round(game.player.max_shield)}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-226))

    label = font.render(f"{round(game.player.boost_amount)} | {game.MAX_BOOST_AMOUNT}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-170))

    label = font.render(f"{round(game.player.velocity.magnitude())}", True, (255, 255, 255))
    WIN.blit(label, (108, game.HEIGHT-114))
