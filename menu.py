import pygame
from pygame import freetype
import random
from player import get_player
from ui import Bar as UIBar
import game
import images
import main
# menu v2



class Menu():
    """Menu controls the current page and checks for mouse clicks"""

    running = False

    DEFAULT_BACKGROUND_COLOUR = game.DARK_GREY
    DEFAULT_BOX_COLOUR = game.MEDIUM_GREY
    DEFAULT_FONT = "bahnschrift"
    DEFAULT_FONT_SIZE = 40
    DEFAULT_COLOUR = game.WHITE
    DEFAULT_PADX = 16
    DEFAULT_PADY = 12
    DEFAULT_OUTLINE_COLOUR = (20, 20, 20)
    DEFAULT_HOVER_COLOUR = game.LIGHT_GREY
    DEFAULT_CLICK_OUTLINE_COLOUR = (190, 190, 190)
    DEFAULT_TEXT_SPACING = 0.003
    SLIDER_WIDTH = 0.02 # percentage (0 to 1) of screen width
    SLIDER_COLOUR = (*game.LIGHT_GREY, 150)
    SLIDER_OUTLINE = (30, 30, 30, 150)

    def __init__(self) -> None:
        """On start up, the default page is main_menu"""
        Menu.change_page(main_menu)

    def change_page(page: "Page"):
        """Draw the new page, and then wait for a mouse click"""
        pygame.mouse.set_visible(True)
        Menu.current_page = page
        page.draw()

        if not Menu.running:
            Menu.running = True
            Menu.run()

    def run():
        while Menu.running:
            if Menu.check_for_inputs(): # if check_for_inputs() returns True, then break out of Menu control
                Menu.running = False

    def update():
        """Re-draw the current_page"""
        Menu.current_page.draw()

    def resize():
        """Re-draw the current_page but with the updated screen dimensions"""
        game.update_screen_size()
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "resize"):
                widget.resize()
        Menu.update()

    def check_for_inputs():
        """Go through pygame.event and do the corresponding functions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit()

            elif event.type == pygame.VIDEORESIZE:
                Menu.resize()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # 1 is left click
                mouse = pygame.mouse.get_pos()
                Menu.mouse_click(mouse)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: # 1 is left click
                for widget in Menu.current_page.widgets: # Stop sliding for all sliders
                    if hasattr(widget, "sliding"):
                        widget.sliding = False

            elif event.type == pygame.MOUSEMOTION:
                mouse = pygame.mouse.get_pos()
                Menu.mouse_moved(mouse)
                Menu.update() # buttons will be checked if they are hovered on or not

            elif event.type == pygame.MOUSEWHEEL:
                Menu.mouse_scroll(event.y)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # runs Menu.escape_pressed, if that returns True, then follow suit and return True
                if Menu.escape_pressed():
                    return True

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    Menu.up_pressed()

                elif event.key == pygame.K_DOWN:
                    Menu.down_pressed()

                elif event.key == pygame.K_e:
                    # if e_pressed return True, then go back to the game
                    if Menu.e_pressed():
                        return True

                Menu.key_pressed(event)

                Menu.update()

    def mouse_click(mouse):
        """Go through all Page Widgets, if the Widget is a button then check if it is clicked on"""
        if Menu.current_page.click:
            Menu.current_page.click()

        for widget in Menu.current_page.widgets:
            if hasattr(widget, "click"):
                if widget.click(mouse): # if the Button has been clicked, then stop checking the Buttons
                    break

    def mouse_moved(mouse):
        """Go through all Page Widgets, if the Widget has a mouse_moved attribute, then call it"""
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "mouse_moved"):
                widget.mouse_moved(mouse) # moves slider if need be

    def mouse_scroll(y):
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "scroll"):
                widget.scroll(y)

    def escape_pressed():
        if Menu.current_page.escape:
            if Menu.current_page.escape(): return True # return True allows for a propagation which relieves Menu's control

    def e_pressed():
        if Menu.current_page.e_press:
            if Menu.current_page.e_press():
                return True # return to playing

    def up_pressed():
        if Menu.current_page.up:
            Menu.current_page.up()

    def down_pressed():
        if Menu.current_page.down:
            Menu.current_page.down()

    def key_pressed(event):
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "key_pressed"):
                widget.key_pressed(event)

    def pause():
        Menu.change_page(pause)

    def systems():
        Menu.change_page(systems)

    def station():
        Menu.change_page(station)

    def death_screen():
        Menu.change_page(death_screen)



class Page():
    """Page contains a list of widgets
       if background_colour is None, the background remains the same i.e. the widgets are just overlayed on top of the screen
       click is a function that is called when the user clicks on the page
       escape is a function that is called when the escape key is pressed, if it returns True - the Menu system is exited, so code can continue
       up is a function that is called when the up key is pressed
       down is a function that is called when the down key is pressed
    """
    def __init__(self, *widgets, background_colour=Menu.DEFAULT_BACKGROUND_COLOUR, click=None, escape=None, e_press=None, up=None, down=None) -> None:
        self.background_colour = background_colour
        self.click = click
        self.escape = escape
        self.e_press = e_press
        self.up = up
        self.down = down

        self.widgets: tuple[Widget] = widgets

    def draw(self):
        """Draws all widgets onto the Menu, widget.draw checks if a button is hovered over"""

        if self.background_colour:
            game.WIN.fill(self.background_colour)

        # For Performance, cache the label for each button so that the buttons do not have to recalculate
        for widget in self.widgets:
            if isinstance(widget, Button):
                widget.label = widget.get_label()

        for widget in self.widgets:
            widget.draw()

        pygame.display.update()



class Widget():
    """Base class for Page elements
       x, y are floats
       x is multiplied by game.WIDTH  (e.g. if x == 0.2, then x_pos = 0.2*game.WIDTH)
       y is multiplied by game.HEIGHT (e.g. if y == 0.2, then y_pos = 0.2*game.HEIGHT)
       x, y is the centre of the Widget
    """
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def get_x(self):
        return self.x * game.WIDTH

    def get_y(self):
        return self.y * game.HEIGHT



class Image(Widget):
    """A Widget that has an image
       scale is the scale of the image, e.g. scale=1 wouldn't change image size, scale=2 would double the size
    """
    def __init__(self, x, y, image=images.DEFAULT, scale=1) -> None:
        super().__init__(x, y)
        self.image = pygame.transform.scale_by(image, scale)

    def draw(self):
        ratio = min(game.WIDTH * self.image.get_width() / 1_000_000, # Ratio of image width to game width
                    game.HEIGHT * self.image.get_width() / 625_000)
        image = pygame.transform.scale_by(self.image, ratio)
        game.WIN.blit(image, (self.get_x() - image.get_width()/2, self.get_y() - image.get_height()/2))



class AdjustableText(Widget):
    def __init__(self, top_x, top_y, bottom_x, bottom_y, text="Text", font=Menu.DEFAULT_FONT, default_font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR) -> None:
        self.top_x = top_x
        self.top_y = top_y
        self.bottom_x = bottom_x
        self.bottom_y = bottom_y

        self.text = text
        self.words = self.text.split(" ")
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
                self.default_font_size -= 1
                self.font = freetype.SysFont(self.font_type, self.default_font_size)
                self.line_spacing = self.font.get_sized_height()
                self.render_words()
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

        if len(render_list) == len(self.words):
            for element in render_list:
                self.font.render_to(game.WIN, (element[0], element[1]), text=element[2], fgcolor=self.colour)



class Text(Widget):
    """Text can be single or multi-line
       x, y is the centre of the first line of the Text
       font size is relative to screen width, if you change the screen resolution then the font size will dynamically change
       text can be a string or a function, if it's a function then that will be called, e.g. text=lambda f"SCORE: {game.SCORE}"
       if text is a function it has to return a string (can be single or multi-line)
       align is a string, can be "left", "centre" or "right", this is for the x value
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, spacing=Menu.DEFAULT_TEXT_SPACING, align="centre") -> None:
        super().__init__(x, y)

        if isinstance(text, str):
            self.text = [sentence.lstrip() for sentence in text.split("\n")]
        else: # if text is a function
            self.text = text

        self.font = font
        self.font_size = font_size
        self.colour = colour
        self.spacing = lambda: spacing * game.HEIGHT
        self.align = align

        self.labels_text = None
        self.labels_size = None

    def get_blit_x(self, label: pygame.surface.Surface):
        if self.align == "centre":
            return self.get_x() - label.get_width()/2
        elif self.align == "left":
            return self.get_x()
        elif self.align == "right":
            return self.get_x() - label.get_width()

    def update_labels_info(self):
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = self.text()
        else:
            text = self.text
        self.labels_text = text

        self.labels_size = round(game.WIDTH * self.font_size / 900)

        font = pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900))

        if isinstance(text, list):
            self.labels = [font.render(sentence, True, self.colour) for sentence in text]
        else: # if text is a function
            self.labels = [font.render(sentence.lstrip(), True, self.colour) for sentence in text.split("\n")] # split sentence up into lines, then turn each line into a label

        return self.labels

    def get_labels(self):
        """Creates a list of label for every sentence of the text"""
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = [sentence.lstrip() for sentence in self.text().split("\n")]
        else:
            text = self.text

        if text != self.labels_text or round(game.WIDTH * self.font_size / 900) != self.labels_size:
            self.update_labels_info()

        return self.labels

    def draw(self):
        labels = self.get_labels()
        cum_height = 0 # cumulative height of all the labels above a certain label
        for label in labels:
            position = self.get_blit_x(label), self.get_y() - label.get_height()/2 + cum_height # Adjust coordinates to be centre of Widget
            game.WIN.blit(label, position)
            cum_height += label.get_height() + self.spacing()



class Button(Text):
    """A Widget that can be clicked on
       When a Button is clicked, the "function" method is called
       padx, pady is the padding, i.e. how much the button extends past the text, i.e. padx=1 means 1 pixel on the left AND 1 pixel on the right
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, padx=Menu.DEFAULT_PADX, pady=Menu.DEFAULT_PADY, function=None, box_colour=Menu.DEFAULT_BOX_COLOUR, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, hover_colour=Menu.DEFAULT_HOVER_COLOUR, uniform=False) -> None:
        super().__init__(x, y, text, font, font_size, colour)
        self.padx = padx
        self.pady = pady
        self.function = function
        self.box_colour = box_colour
        self.current_box_colour = box_colour
        if not outline_colour: outline_colour = box_colour
        self.outline_colour = outline_colour
        self.hover_colour = hover_colour
        self.uniform = uniform

        self.label_text = None
        self.label_size = None
        self.update_label_info()

    def click(self, mouse):
        if self.touching_mouse(mouse):
            self.function()
            return True # Tells the Menu that this Button has been clicked on

    def touching_mouse(self, mouse):
        label = self.label
        x, y, width, height = self.get_rect(label)
        x, y = x - self.padx, y - self.pady
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def get_width(self, label: pygame.Surface):
        return label.get_width() + self.padx*2 # padding*2 as there is padding on both sides

    def get_height(self, label: pygame.Surface):
        return label.get_height() + self.pady*2 # padding*2 as there is padding on both sides

    def get_rect(self, label):
        width, height = self.get_width(label), self.get_height(label)
        x, y = self.get_x() - label.get_width()/2, self.get_y() - label.get_height()/2
        return x, y, width, height

    def get_max_width(self):
        """Get greatest width of all Buttons on the current_page"""

        max_width = 0
        for widget in Menu.current_page.widgets:
            if isinstance(widget, Button) and widget.uniform:
                if widget.get_width(widget.label) > max_width:
                    max_width = widget.get_width(widget.label)
        return max_width

    def get_rect(self, label):
        """If self.uniform == True, set the width to the greatest width of all Buttons on the current_page"""
        if self.uniform:
            width, height = self.get_max_width(), self.get_height(label)
            width_difference = width - self.get_width(label)
            x, y = self.get_x() - label.get_width()/2 - width_difference/2, self.get_y() - label.get_height()/2
            return x, y, width, height

        width, height = self.get_width(label), self.get_height(label)
        x, y = self.get_x() - label.get_width()/2, self.get_y() - label.get_height()/2
        return x, y, width, height

    def update_label_info(self):
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = self.text()
        else:
            text = self.text[0]
        self.label_text = text

        self.label_size = round(game.WIDTH * self.font_size / 900)

        self.label = pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900)).render(text, True, self.colour)

    def get_label(self):
        """For buttons which currently only use the first line of text to create the button"""
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = self.text()
        else:
            text = self.text[0]

        if text != self.label_text or round(game.WIDTH * self.font_size / 900) != self.label_size:
            self.update_label_info()

        return self.label

    def draw(self):
        if self.touching_mouse(pygame.mouse.get_pos()):
            self.current_box_colour = self.hover_colour
        else:
            self.current_box_colour = self.box_colour

        label = self.label # This is updated in Page.draw()
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(game.WIN, self.current_box_colour, (x - self.padx, y - self.pady, width, height))
        pygame.draw.rect(game.WIN, self.outline_colour    , (x - self.padx, y - self.pady, width, height), width=round(game.WIDTH/300))
        position = self.get_x() - label.get_width()/2, self.get_y() - label.get_height()/2 # Adjust coordinates to be centre of Widget
        game.WIN.blit(label, position)



class SettingButton(Button):
    """A Button for settings
       When clicked on, it will change outline colour
       value is the value that the setting button affects, NOTE: value is a string and has to be an attribute of game, e.g. game.WIDTH and value="WIDTH"
       function_action is called after the value is modified
       text is a function
       min and max are the minimum and maximum values of value
       uniform arg makes all of setting buttons on the page the same width
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, padx=Menu.DEFAULT_PADX, pady=Menu.DEFAULT_PADY, value=None, function_action=None, min=1, max=100, box_colour=Menu.DEFAULT_BOX_COLOUR, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, hover_colour=Menu.DEFAULT_HOVER_COLOUR, click_outline_colour=Menu.DEFAULT_CLICK_OUTLINE_COLOUR, uniform=True) -> None:
        super().__init__(x, y, text, font, font_size, colour, padx, pady, function_action, box_colour, outline_colour, hover_colour)
        self.original_outline_colour = self.outline_colour
        self.click_outline_colour = click_outline_colour
        self.uniform = uniform
        self.value = value
        self.function_action = function_action
        self.selected = False
        if isinstance(self.get_value(), int):
            self.min = min
            self.max = max

        def function():
            self.selected = True
            self.current_box_colour = self.hover_colour
            self.outline_colour = self.click_outline_colour

            # If self.value is a bool, then when this button is clicked, the value will be flipped
            if isinstance(self.get_value(), bool):
                setattr(game, self.value, not self.get_value())
                if self.function_action:
                    self.function_action()

            Menu.update()
        self.function = function

    def get_value(self):
        return getattr(game, self.value)

    def get_slider_width(self):
        return Menu.SLIDER_WIDTH * game.WIDTH

    def get_slider(self):
        label = self.label
        ratio = (self.get_value() - self.min) / (self.max - self.min) # percentage of max value
        x, y, width, height = self.get_rect(label)
        x += ratio*(width-self.get_slider_width()) - self.padx
        width = self.get_slider_width()
        height -= self.pady*2
        return x, y, width, height

    def mouse_moved(self, mouse):
        if hasattr(self, "sliding") and self.sliding:

            x, _, width, _ = self.get_rect(self.label) # get button rect
            ratio = (self.max - self.min) / (width - self.get_slider_width()) # value per pixel
            left_slider = mouse[0] - self.get_slider_width()*self.slider_ratio # gets x of left side of the slider, keeping same slider ratio
            value = int((left_slider - x + self.padx) * ratio) + self.min # get relative mouse position from left of button * ratio
            if value < self.min: value = self.min # clip value so that it is between min and max
            elif value > self.max: value = self.max

            setattr(game, self.value, value)
            if self.function_action:
                self.function_action()

    def click(self, mouse):
        super().click(mouse)
        x, y, width, height = self.get_slider()
        if (mouse[0] > x and mouse[0] < x + width and
            mouse[1] > y and mouse[1] < y + height):
            self.sliding = True
            self.slider_ratio = (mouse[0] - x) / width # The percentage (0 to 1) of the mouse position on the sliding segment

    def up(self):
        if type(self.get_value()) == bool:
            setattr(game, self.value, not self.get_value())
        else:
            setattr(game, self.value, self.get_value() + 1 if self.get_value() < self.max else self.max)
        if self.function_action:
            self.function_action()

    def down(self):
        if type(self.get_value()) == bool:
            setattr(game, self.value, not self.get_value())
        else:
            setattr(game, self.value, self.get_value() - 1 if self.get_value() > self.min else self.min)
        if self.function_action:
            self.function_action()

    def draw(self):
        super().draw()
        # If this is an integer setting, then automatically make it a slider
        if type(self.get_value()) == int:
            x, y, width, height = self.get_slider()
            surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            pygame.draw.rect(surf, Menu.SLIDER_COLOUR, (0, 0, width, height))
            pygame.draw.rect(surf, Menu.SLIDER_OUTLINE, (0, 0, width, height), width=round(game.WIDTH/300))
            game.WIN.blit(surf, (x, y))



class WorldSelectionButton(Button):
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, padx=Menu.DEFAULT_PADX, pady=Menu.DEFAULT_PADY, function=None, box_colour=Menu.DEFAULT_BOX_COLOUR, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, hover_colour=Menu.DEFAULT_HOVER_COLOUR, uniform=False) -> None:
        self.inactive_text_colour = (150, 150, 150)
        self.inactive_box_colour = (40, 40, 40)
        self.inactive_hover_colour = (40, 40, 40)
        super().__init__(x, y, text, font, font_size, colour, padx, pady, function, box_colour, outline_colour, hover_colour, uniform)
        self.text_colour = colour
        self.default_box_colour = box_colour
        self.default_hover_colour = hover_colour

        self.text_label_active = False

    def click(self, mouse):
        if self.touching_mouse(mouse) and world_list.world_selected:
            self.function()
            return True # Tells the Menu that this Button has been clicked on

    @property
    def colour(self):
        return self.text_colour if world_list.world_selected else self.inactive_text_colour

    @colour.setter
    def colour(self, colour):
        self.text_colour = colour

    @property
    def box_colour(self):
        return self.default_box_colour if world_list.world_selected else self.inactive_box_colour

    @box_colour.setter
    def box_colour(self, colour):
        self.default_box_colour = colour

    @property
    def hover_colour(self):
        return self.default_hover_colour if world_list.world_selected else self.inactive_hover_colour

    @hover_colour.setter
    def hover_colour(self, colour):
        self.default_hover_colour = colour

    def draw(self):
        if world_list.world_selected and not self.text_label_active:
            self.text_label_active = True
            self.update_label_info()
        elif not world_list.world_selected and self.text_label_active:
            self.text_label_active = False
            self.update_label_info()
        super().draw()



class Rectangle(Widget):
    """A rectangular object of given width, height and colour
       x, y are floats (percentage from 0 to 1 of screen size)
       width, height can be int or float, int for pixel, float for ratio of screen size"""
    def __init__(self, x, y, width, height, colour, outline_colour=None, curve=0) -> None:
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.colour = colour
        self.outline_colour = outline_colour
        self.curve = curve

        if abs(width) <= 1:
            self.get_width = lambda self: self.width * game.WIDTH

        else:
            if width < 0:
                self.get_width = lambda self: game.WIDTH + self.width
            else:
                self.get_width = lambda self: self.width

        if abs(height) <= 1:
            self.get_height = lambda self: self.height * game.HEIGHT

        else:
            if height < 0:
                self.get_height = lambda self: game.HEIGHT + self.height
            else:
                self.get_height = lambda self: self.height


    def draw(self):
        if self.outline_colour:
            outline_width = round(game.WIDTH/300)
            pygame.draw.rect(game.WIN, self.outline_colour, (self.get_x() - outline_width, self.get_y() - outline_width, self.get_width(self) + 2*outline_width, self.get_height(self) + 2*outline_width), width=outline_width, border_radius=self.curve)

        pygame.draw.rect(game.WIN, self.colour, (self.get_x(), self.get_y(), self.get_width(self), self.get_height(self)), border_radius=self.curve)



class UpgradeBar(Widget):
    """Used to upgrade aspects of player systems
       value is the variable that the bar is upgrading, it is a string and has to be a variable of game (e.g. game.WIDTH, value="WIDTH")
       bar_width and bar_height are floats, which is the percentage (0 to 1) of the screen width and height
       bars is the number of bars"""
    def __init__(self, x, y, text, value, font_size=15, button_colour=(10, 20, 138), bar_colour=(255, 130, 0), outline_colour=(255, 255, 255), select_colour=(230, 110, 0), select_outline_colour=(25, 235, 20), button_width=0.1, bar_width=0.05, height=0.05, gap=5, bars=10, min_value=20, max_value=60) -> None:
        super().__init__(x, y)
        self.text = text
        self.value = value
        self.font_size = font_size
        self.button_colour = button_colour
        self.bar_colour = bar_colour
        self.outline_colour = outline_colour
        self.select_colour = select_colour
        self.select_outline_colour = select_outline_colour
        self.button_width = button_width
        self.bar_width = bar_width
        self.height = height
        self.gap = gap
        self.bars = bars
        self.min_value = min_value
        self.max_value = max_value
        self.step = (max_value - min_value) / bars
        if self.step.is_integer(): self.step = int(self.step) # if step is an integer, then remove the decimal point
        self.level = value + "_LEVEL"
        self.padlock = images.PADLOCK

    def get_value(self):
        return getattr(game, self.value)

    def set_value(self, value):
        setattr(game, self.value, value)

    def get_level(self):
        return getattr(game, self.level)

    def upgrade_level(self):
        setattr(game, self.level, self.get_level() + 1)

    def click(self, mouse):
        mx, my = mouse[0], mouse[1]

        # check if text bar is clicked on
        x = self.get_x()
        y = self.get_y()
        width = game.WIDTH * self.button_width
        height = game.HEIGHT * self.height
        if mx > x and mx < x + width and my > y and my < y + height:
            self.set_value(self.min_value)
            Menu.update()

        # go through every bar to see if it is clicked on
        for bar in range(self.bars):

            width = game.WIDTH * self.bar_width
            height = game.HEIGHT * self.height
            button_width = game.WIDTH * self.button_width
            x = self.get_x() + bar * (width + self.gap) + button_width + self.gap
            y = self.get_y()

            # if clicked on
            if mx > x and mx < x + width and my > y and my < y + height:

                # if bar is less than level then switch to that level
                if bar < self.get_level():
                    self.set_value(self.min_value + (bar+1) * self.step)
                    Menu.update()

                # if bar is the next level, upgrade to that level
                elif bar == self.get_level() and game.SCRAP_COUNT >= bar+1:
                    game.SCRAP_COUNT -= bar+1
                    self.upgrade_level()
                    self.set_value(self.min_value + self.get_level() * self.step)
                    Menu.update()

                break

    def get_label(self):
        """Gets a text label"""
        return pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900)).render(self.text, True, Menu.DEFAULT_COLOUR)

    def draw(self):

        padlock = pygame.transform.scale_by(self.padlock, game.WIDTH/1200)
        scrap = pygame.transform.scale_by(images.SCRAP, game.WIDTH/1500)

        width = game.WIDTH * self.bar_width
        height = game.HEIGHT * self.height
        button_width = game.WIDTH * self.button_width

        # draw text bar
        if self.get_value() == self.min_value: # if level 0, text bar has a select outline
            pygame.draw.rect(game.WIN, self.select_outline_colour, (self.get_x(), self.get_y(), button_width, height), border_radius=10)
        else:
            pygame.draw.rect(game.WIN, self.outline_colour, (self.get_x(), self.get_y(), button_width, height), border_radius=10)

        pygame.draw.rect(game.WIN, self.button_colour, (self.get_x()+2, self.get_y()+2, button_width-4, height-4), border_radius=10)
        label = self.get_label()
        game.WIN.blit(label, (self.get_x() + button_width/2 - label.get_width()/2, self.get_y() + height/2 - label.get_height()/2))


        # draw bars
        for bar in range(self.bars):

            x = self.get_x() + bar * (width + self.gap) + button_width + self.gap

            # draw bar outline
            if self.get_value() == (bar+1) * self.step + self.min_value: # if selected choose a different outline colour
                pygame.draw.rect(game.WIN, self.select_outline_colour, (x, self.get_y(), width, height), border_radius=10)
            else:
                pygame.draw.rect(game.WIN, self.outline_colour, (x, self.get_y(), width, height), border_radius=10)

            # fill in bar if neseccary, bar+1 so that the first bar is level 1
            if bar+1 <= self.get_level():

                if self.get_value() == (bar+1) * self.step + self.min_value: # if selected choose a different colour
                    pygame.draw.rect(game.WIN, self.select_colour, (x+2, self.get_y()+2, width-4, height-4), border_radius=10)

                else: # fill in with regular colour
                    pygame.draw.rect(game.WIN, self.bar_colour, (x+2, self.get_y()+2, width-4, height-4), border_radius=10)

            else: # fill in with background colour
                pygame.draw.rect(game.WIN, Menu.DEFAULT_BACKGROUND_COLOUR, (x+2, self.get_y()+2, width-4, height-4), border_radius=10)

                if bar == self.get_level(): # the first locked bar shows a price instead of a padlock
                    if game.SCRAP_COUNT >= bar+1: colour = Menu.DEFAULT_COLOUR
                    else: colour = (255, 0, 0)
                    number = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/50)).render(str(bar+1), True, colour)
                    game.WIN.blit(number, (x + width*0.3 - number.get_width()/2, self.get_y() + height/2 - number.get_height()/2))
                    game.WIN.blit(scrap , (x + width*0.7 - scrap.get_width()/2 , self.get_y() + height/2 - scrap.get_height()/2))

                else: # all of the locked bars show padlocks
                    game.WIN.blit(padlock, (x + width/2 - padlock.get_width()/2, self.get_y() + height/2 - padlock.get_height()/2))



class Bar():
    """x, y, width, height are proportional to screen size"""
    def __init__(self, x, y, width, height, value, max_value, colour, outline_width=0, outline_colour=game.BLACK, curve=0) -> None:
        self.x = lambda: x * game.WIDTH
        self.y = lambda: y * game.HEIGHT
        self.width = lambda: width * game.WIDTH - outline_width*2
        self.height = lambda: height * game.HEIGHT
        self.original_width = self.width
        self.colour = colour
        self.outline_width = outline_width
        self.outline_colour = outline_colour
        self.curve = curve
        self.value = value
        self.max_value = max_value

    def update(self, new_percent):
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = lambda: (self.original_width()-self.outline_width*2) * min(1, new_percent)

    def draw(self):
        self.update(self.value() / self.max_value())
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.x()+self.outline_width, self.y() - self.height()/2 + self.outline_width, # bar position is middle left
                              self.width(), self.height()-self.outline_width*2),

                        border_radius=self.curve-self.outline_width  # - self.outline_width to be the same curve as the inside curve of the outline
                        )

        if self.outline_width:
            pygame.draw.rect(game.WIN, self.outline_colour,
                        rect=(self.x()             , self.y() - self.height()/2, # bar position is middle left
                              self.original_width(), self.height()),

                        width=self.outline_width,
                        border_radius=self.curve
                        )



class ArmourBar(Bar):
    def __init__(self, x, y, width, height, value, max_value, price, number, colour, outline_width=0, outline_colour=game.BLACK, curve=0) -> None:
        super().__init__(x, y, width, height, value, max_value, colour, outline_width, outline_colour, curve)
        self.number = number
        self.price = price
        self.upgrade_value = None
        self.price_rect = None
        self.button_rect = lambda: (self.x() + self.width() + 10, self.y()-self.height()/2, 0.1*game.WIDTH, self.height())

    def draw(self):
        self.price_rect = None
        for n in range(self.number):
            # If this bar is the current one to heal
            if not self.price_rect and self.value()/self.max_value()*self.number - n < 1:
                x = self.x()+n*(self.width()/self.number)#-self.outline_width)
                width = self.width()/self.number
                if n+1 != self.number: width += self.outline_width

                self.price_rect = (x, self.y()-self.height()/2, width, self.height())
                self.upgrade_value = (n+1)/self.number * self.max_value()

            # Draw bar
            width = self.width()/self.number
            if n+1 != self.number: width += self.outline_width
            bar = UIBar(lambda: self.x()+n*(self.width()/self.number), self.y, width, self.height(), self.colour, self.outline_width, self.outline_colour, self.curve, flatten_left=False if n==0 else True, flatten_right=False if n==self.number-1 else True)
            bar.update(max(0, min(1, self.value()/self.max_value()*self.number - n)))
            bar.draw()

        # Highlight button if hovered
        mx, my = pygame.mouse.get_pos()
        rect = self.button_rect()
        if rect[0] <= mx <= rect[0]+rect[2] and rect[1] <= my <= rect[1]+rect[3]:
            pygame.draw.rect(game.WIN, self.colour, rect, border_radius=self.curve)

        # Draw price box
        pygame.draw.rect(game.WIN, game.BLACK, rect, width=self.outline_width, border_radius=self.curve)

        # Draw price number
        if game.SCRAP_COUNT >= self.price: colour = Menu.DEFAULT_COLOUR
        else: colour = (255, 0, 0)
        number = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/30)).render(str(self.price), True, colour)
        game.WIN.blit(number, (rect[0] + 0.225*rect[2] - number.get_width()/2, self.y() - number.get_height()/2))

        # Draw price scrap image
        scrap_image = pygame.transform.scale_by(images.SCRAP, game.HEIGHT/images.SCRAP.get_height()*0.07)
        game.WIN.blit(scrap_image, (rect[0] + 0.65*rect[2] - scrap_image.get_width()/2, self.y()-scrap_image.get_height()/2))

    def click(self, mouse):
        mx, my = mouse[0], mouse[1]

        # If click on price button
        r = self.button_rect()
        if game.SCRAP_COUNT >= self.price and self.value() != self.max_value() and r[0] <= mx <= r[0]+r[2] and r[1] <= my <= r[1]+r[3]:
            game.SCRAP_COUNT -= self.price
            game.player.armour = self.upgrade_value
            Menu.update()



class WorldList():
    """
    0 <= (x, y, width, height, gap) <= 1
    """
    def __init__(self, x, y, width, height, gap) -> None:
        self.x = lambda: game.WIDTH * x
        self.y = lambda: game.HEIGHT * y
        self.width = lambda: game.WIDTH * width
        self.height = lambda: game.HEIGHT * height
        self.gap = lambda: game.HEIGHT * gap

        self.screen_dimensions = game.WIDTH, game.HEIGHT

        self.scroll_height = 0

        self.sliding = False
        self.world_selected: WorldButton | None = None

        self.init_worlds()

        self.rectangle = Rectangle(x - width/2 - gap, y - height/2 - gap, width + 2*gap, height + 2*gap +  min(2, len(self.list)-1)*(height+gap), (24, 24, 24))

    def init_worlds(self):
        world_dir = game.get_world_dir()
        self.list = [World(name, seed) for name, seed in world_dir]

        x, y = self.x()/game.WIDTH, self.y()/game.HEIGHT
        self.buttons: list[WorldButton] = []
        for idx, world in enumerate(self.list):
            self.buttons.append(WorldButton(x, y + idx*(self.height()+self.gap())/game.HEIGHT, world.name, world.seed, world=world, world_list=self))

    def start_world(self, world: "World"):
        Menu.change_page(loading_world)
        game.set_name_to_top_of_world_dir(world.name)
        self.set_world_to_top(world)
        game.load_constants(world.name)
        main.main()

    def set_world_to_top(self, world: "World"):
        idx = self.list.index(world)

        del self.list[idx]
        self.list.insert(0, world)

        extra_height = (self.height() + self.gap()) / game.HEIGHT
        for button in self.buttons[:idx]:
            button.y += extra_height

        self.buttons.insert(0, self.buttons.pop(idx))
        self.buttons[0].y = self.y()/game.HEIGHT

        self.scroll_height = 0

    def create_world(self, name, seed):
        world = World(name, seed)
        self.list.append(world)

        x, y, width, height, gap = self.x()/game.WIDTH, self.y()/game.HEIGHT, self.width()/game.WIDTH, self.height()/game.HEIGHT, self.gap()/game.HEIGHT

        self.rectangle = Rectangle(x - width/2 - gap, y - height/2 - gap, width + 2*gap, height + 2*gap + min(2, len(self.list)-1)*(height+gap), (24, 24, 24))

        self.buttons.append(WorldButton(x, y, name, seed, world=world, world_list=self))

        return world

    def delete_selected_world(self):
        name = self.world_selected.text[0]

        for world in self.list:
            if world.name == name:
                self.list.remove(world)
                break

        x, y, width, height, gap = self.x()/game.WIDTH, self.y()/game.HEIGHT, self.width()/game.WIDTH, self.height()/game.HEIGHT, self.gap()/game.HEIGHT

        self.rectangle = Rectangle(x - width/2 - gap, y - height/2 - gap, width + 2*gap, height + 2*gap + min(2, len(self.list)-1)*(height+gap), (24, 24, 24))

        idx = self.buttons.index(self.world_selected)
        del self.buttons[idx]
        for button in self.buttons[idx:]:
            button.y -= (self.height() + self.gap()) / game.HEIGHT

        self.world_selected = None
        self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height) # ensure scroll is within limits

        game.delete_world(name)
        Menu.update()

    def get_total_button_height(self):
        """Gets the total height that the buttons can scroll"""
        num = min(3, len(self.list))
        total_button_height = num*(self.height()+self.gap()) - self.gap() # Height of buttons that are shown on screen
        return total_button_height

    def get_scroll_bar_height(self):
        # Correct
        num = min(3, len(self.list))

        total_button_height = self.get_total_button_height()
        max_button_height = len(self.list)*(self.height()+self.gap()) - self.gap() + (num-1)*(self.height()+self.gap()) # length of all the buttons + 2 (i.e.num-1) buttons worth of gap at the bottom

        scroll_bar_height = (total_button_height / max_button_height) * total_button_height # Ratio of visible button height over total button height, multiplied by available scroll height
        return scroll_bar_height

    def get_max_scroll_height(self):
        """Gets the total height the scroll bar can scroll"""
        scroll_bar_height = self.get_scroll_bar_height()

        total_button_height = self.get_total_button_height() # Height of buttons that are shown on screen

        max_scroll_height = total_button_height - scroll_bar_height # Amount of pixels the scroll bar can move
        return max_scroll_height

    def get_scroll_bar(self):
        scroll_bar_height = self.get_scroll_bar_height()

        return (self.x() + self.width()/2, self.y() - self.height()/2 + self.scroll_height, self.gap()/2, scroll_bar_height)

    def get_button_scroll_ratio(self):
        """Returns the ratio of button scroll to scroll bar scroll"""
        total_button_scroll_height = (len(self.list)-1) * (self.height()+self.gap())
        total_scroll_height = self.get_max_scroll_height()

        if total_scroll_height:
            ratio = total_button_scroll_height / total_scroll_height
        else:
            ratio = 1

        return -ratio # Buttons scroll opposite direction to scroll bar

    def button_scroll_height(self):
        """Returns scroll_bar height converted to scroll height for button"""

        ratio = self.get_button_scroll_ratio()

        return self.scroll_height * ratio

    def click(self, mouse):
        # Click on buttons
        for button in self.buttons:
            rect = (self.x() - self.width()/2, self.y() - 1.5*self.gap(), self.width(), self.height() + min(2, (len(self.list))-1)*(self.height()+self.gap()))
            if button.click(mouse, rect, self.button_scroll_height()) is True:
                return True

        # Click on scroll bar
        x, y, width, height = self.get_scroll_bar()
        if mouse[0] > x and mouse[0] < x + width and mouse[1] > y and mouse[1] < y + height:
            self.sliding = True
            self.slider_height = mouse[1] - y

    def mouse_moved(self, mouse):
        if self.sliding:

            top_slider = mouse[1] - self.slider_height
            top_list = self.y() - self.height()/2
            self.scroll_height = top_slider - top_list

            self.scroll_height = max(0, self.scroll_height)
            self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height)

    def scroll(self, y):
        scroll_const = 0.021 * game.HEIGHT
        self.scroll_height += y*scroll_const/self.get_button_scroll_ratio()

        self.scroll_height = max(0, self.scroll_height) # Player can't scroll up above top button
        self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height) # Player can't scroll down below bottom button
        Menu.update()

    def resize(self):
        for button in self.buttons:
            button.update_label_info()

    def draw(self):
        # If no worlds, then don't draw list
        if len(self.list) == 0:
            return

        # Draw background rectangle
        self.rectangle.draw()

        # Draw scroll bar
        if len(self.list) > 1:
            pygame.draw.rect(game.WIN, Menu.DEFAULT_HOVER_COLOUR, self.get_scroll_bar())

        # Draw buttons
        if self.screen_dimensions != (game.WIDTH, game.HEIGHT):
            self.screen_dimensions = game.WIDTH, game.HEIGHT
            self.resize()

        rect = (self.x() - self.width()/2, self.y() - 1.5*self.gap(), self.width(), self.height() + min(2, (len(self.list))-1)*(self.height()+self.gap()))
        surf = pygame.Surface((rect[2], rect[3]), flags=pygame.SRCALPHA)
        x_offset = -(self.x() - self.width()/2)
        y_offset = -(self.y() - self.height()/2) + self.button_scroll_height()

        for button in self.buttons:

            # Make all buttons the same width
            button.padx = (self.width() - button.label.get_width())/2

            # Make all buttons the same height
            button.pady = (self.height() - button.label.get_height())/2

            # Draw button
            button.draw(surf, x_offset, y_offset, rect, self.button_scroll_height())

        game.WIN.blit(surf, (rect[0], rect[1]))



class World():
    def __init__(self, name, seed) -> None:
        self.name = name
        self.seed = seed



class WorldButton(Button):
    def __init__(self, x, y, name="Text", seed="Seed", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, padx=Menu.DEFAULT_PADX, pady=Menu.DEFAULT_PADY, world=None, world_list=None, box_colour=Menu.DEFAULT_BOX_COLOUR, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, hover_colour=Menu.DEFAULT_HOVER_COLOUR, click_outline_colour=Menu.DEFAULT_CLICK_OUTLINE_COLOUR) -> None:
        self.seed = str(seed)
        super().__init__(x, y, name, font, font_size, colour, padx, pady, lambda: world_list.start_world(world), box_colour, outline_colour, hover_colour)
        self.click_outline_colour = click_outline_colour

        self.selected = False

    def touching_mouse(self, mouse, rect: tuple, scroll_height):
        if mouse[0] < rect[0] or mouse[0] > rect[0] + rect[2] or mouse[1] < rect[1] or mouse[1] > rect[1] + rect[3]:
            return False

        label = self.label
        x, y, width, height = self.get_rect(label)
        x, y = x - self.padx, y - self.pady + scroll_height
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def click(self, mouse, rect, scroll_height):
        if self.touching_mouse(mouse, rect, scroll_height):
            if self.selected:
                self.function()
                return True # Tells the Menu that this Button has been clicked on
            else:
                self.selected = True
                world_list.world_selected = self
                Menu.update()
        elif self.selected:
            if world_list.world_selected == self:
                world_list.world_selected = None
            self.selected = False
            Menu.update()

    def update_label_info(self):
        super().update_label_info()
        self.seed_label = pygame.font.SysFont(self.font, round(game.WIDTH * 0.6 * self.font_size / 900)).render(f"seed: {self.seed}", True, self.colour) # seed is 60% of the size of world

    def draw(self, surf, x_offset, y_offset, rect, scroll_height):
        # Draw button
        if self.touching_mouse(pygame.mouse.get_pos(), rect, scroll_height):
            self.current_box_colour = self.hover_colour
        else:
            self.current_box_colour = self.box_colour

        outline_colour = self.click_outline_colour if self.selected else self.outline_colour
        label = self.label # This is updated in when screen is resized
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(surf, self.current_box_colour, (x - self.padx + x_offset, y - self.pady + y_offset, width, height))
        pygame.draw.rect(surf, outline_colour         , (x - self.padx + x_offset, y - self.pady + y_offset, width, height), width=round(game.WIDTH/300))

        # Draw name
        position = self.get_x() - self.get_width(label)*0.45 + x_offset, self.get_y() - label.get_height()/2 + y_offset # Adjust coordinates to be left of button
        surf.blit(label, position)

        # Draw seed
        seed = self.seed_label # updated when screen is resized
        position = self.get_x() + self.get_width(self.label)*0.2 + x_offset, self.get_y() - seed.get_height()/2 + y_offset
        surf.blit(seed, position)


class TextInput(Widget):
    def __init__(self, x, y, width, height, header="", limit=10, font_size=Menu.DEFAULT_FONT_SIZE, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, click_outline_colour=Menu.DEFAULT_CLICK_OUTLINE_COLOUR) -> None:
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.header = header
        self.limit = limit
        self.font_size = font_size
        self.outline_colour = outline_colour
        self.click_outline_colour = click_outline_colour
        self.selected = False
        self.text = ""

    def get_width(self):
        return self.width * game.WIDTH

    def get_height(self):
        return self.height * game.HEIGHT

    def get_rect(self):
        return self.get_x() - self.get_width()/2, self.get_y() - self.get_height()/2, self.get_width(), self.get_height()

    def touching_mouse(self, mouse):
        x, y, width, height = self.get_rect()
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def click(self, mouse):
        if self.touching_mouse(mouse):
            self.selected = True
            Menu.update()
        else:
            self.selected = False

    def key_pressed(self, event):
        if self.selected:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalpha() or event.unicode.isdigit() or event.unicode in "!\"#$%&'()*+, -.:;<=>?@[]^_`{|}~":
                if len(self.text) < self.limit:
                    self.text += event.unicode

    def draw(self):
        # Draw rectangle outline
        if self.selected:
            pygame.draw.rect(game.WIN, self.click_outline_colour, self.get_rect(), width=round(game.WIDTH/300))
        else:
            pygame.draw.rect(game.WIN, self.outline_colour, self.get_rect(), width=round(game.WIDTH/300))

        # Draw header
        label = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900)).render(self.header, True, game.WHITE)
        game.WIN.blit(label, (self.get_x() - self.get_width()/2, self.get_y() - self.get_height()/2 - label.get_height()))

        # Draw input text
        label = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900)).render(self.text, True, game.WHITE)
        game.WIN.blit(label, (self.get_x() - self.get_width()/2 + round(game.WIDTH/300), self.get_y() - label.get_height()/2))



class NameTextInput(TextInput):
    def __init__(self, x, y, width, height, header="", limit=10, font_size=Menu.DEFAULT_FONT_SIZE, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, click_outline_colour=Menu.DEFAULT_CLICK_OUTLINE_COLOUR) -> None:
        super().__init__(x, y, width, height, header, limit, font_size, outline_colour, click_outline_colour)
        self.selected = True  # NameInput starts off selected

    def key_pressed(self, event):
        super().key_pressed(event)
        label = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900)).render(self.text, True, game.WHITE)
        if label.get_width() > 0.78*self.get_width():
            self.text = self.text[:-1]



class SeedTextInput(TextInput):
    def key_pressed(self, event):
        super().key_pressed(event)
        for char in self.text:
            if not char.isdigit():
                self.text = self.text.replace(char, "")



class Mission():
    def __init__(self, slot, number, goal, mission_type, reward) -> None:
        self.slot = slot

        # Changes x position based on what slot it is in (there are three mission slots)
        self.x = 0.2 + 0.3*self.slot
        self.y = 0.7

        self.width = 0.2
        self.height = 0.4

        self.accept_button = Button(self.x, self.y, "Accept", function=lambda: self.accept())
        self.decline_button = Button(self.x, self.y+0.1, "Decline", function=lambda: self.decline())
        self.claim_reward_button = Button(self.x, self.y-0.1+(self.height/2), "Claim Reward", function=lambda: self.claim_reward())

        self.mission_manager: MissionManager = None

        # number = number of things for the mission
        # goal = Target for the mission (e.g. Mother_Ship)
        # mission_type = what type of mission it is (e.g. kill mission)
        # reward = number of scrap claimed after completion
        self.number = number
        self.current_number = 0
        self.goal = goal
        self.mission_type = mission_type
        self.reward = reward

        self.progress_text = Text(self.x, self.y-0.05, text=lambda: f"{self.current_number}/{self.number}", font_size=25)

        self.progress_bar = Bar(self.x-(self.width/2), self.y, width=self.width, height=self.height/8, value=lambda: self.current_number, max_value=lambda: self.number, colour=(0, 0, 190), outline_width=3, curve=7)

        if self.mission_type == game.KILL:
            self.title_text = Text(self.x, self.y-0.1-self.height/2, "Kill Mission")

            self.info = f"Kill {self.number} {game.ENTITY_DICT.get(self.goal)}s REWARDS: {self.reward} Scrap"

        self.info_text = AdjustableText((self.x-(self.width/2))*game.WIDTH, (self.y-(self.height/2)) * game.HEIGHT, (self.x+(self.width/2))* game.WIDTH, (self.y-0.3+self.height/2)*game.HEIGHT, text=self.info, default_font_size=70)

        # True if you have clicked accept on a mission
        self.in_progress = False

        # False if one of the three missions is in progress - when false, you will not be able to accept the mission
        self.active = True

        # Draw the info_text immediately since we dont want to wait for the menu to draw it
        self.info_text.draw()

    def accept(self):
        self.in_progress = True
        self.mission_manager.any_mission_active = True
        game.CURRENT_MISSION = [self.current_number, self.number, self.goal, self.mission_type, self.reward]
        Menu.update()

    def decline(self):
        if self.in_progress:
            self.mission_manager.any_mission_active = False
            game.CURRENT_MISSION = None
        self.mission_manager.remove_mission(self)
        Menu.update()

    def claim_reward(self):
        self.mission_manager.any_mission_active = False
        game.SCRAP_COUNT += self.reward
        game.CURRENT_MISSION = None
        self.decline() # Removes this mission after claiming reward

    def click(self, mouse):
        # Making sure button functions are run when clicked
        if not self.in_progress:
            if self.active:
                if self.accept_button.click(mouse) is True: return True
                if self.decline_button.click(mouse) is True: return True
        else:
            if self.current_number >= self.number:
                if self.claim_reward_button.click(mouse) is True: return True
            else:
                if self.decline_button.click(mouse) is True: return True

    def update(self):
        # Drawing title and info
        self.title_text.draw()
        self.info_text.draw()

        # If the mission is in progress - draw the progress bar and stop drawing the accept and decline button. Once the mission is done, it draws the claim reward button
        if self.in_progress:
            self.current_number = game.CURRENT_MISSION[0]
            if self.current_number >= self.number:
                self.claim_reward_button.draw()
            else:
                self.decline_button.draw()
            self.progress_bar.draw()
            self.progress_text.draw()

        else:
            if self.active:
                self.accept_button.draw()
                self.decline_button.draw()

class MissionManager(Widget):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)

        self.missions: list = []

        # Set this value to a slot number so that the next mission will be added to this slot
        self.slot_missing = 0

        # If true then you should not be able to accept another mission
        self.any_mission_active = False

        self.class_list = {"Enemy_Ship": 1,
                           "Missile_Ship": 2,
                           "Drone_Enemy": 1,
                           "Mother_Ship": 2}

        # Spawns in three missions
        while self.slot_missing < 3:
            self.add_mission()
            self.slot_missing += 1

    def add_mission(self):
        goal = random.choice(list(self.class_list.keys()))
        number = random.randint(5, 15)
        reward = number * (1+game.CURRENT_SHIP_LEVEL)**0.6 * self.class_list[goal]  # reward depends on number, difficulty and type of enemy
        reward *= 0.9 + random.random()*0.2  # reward +- 10% to make it look a bit random
        mission = Mission(self.slot_missing, number, goal, game.KILL, round(reward))
        mission.mission_manager = self
        self.missions.append(mission)

    def remove_mission(self, mission):
        if mission in self.missions:
            self.slot_missing = mission.slot
            self.add_mission()
            self.missions.remove(mission)

    def get_current_mission(self):
        if game.CURRENT_MISSION and self.any_mission_active == False:
            del(self.missions[0])
            self.slot_missing = 0
            mission = Mission(self.slot_missing, game.CURRENT_MISSION[1], game.CURRENT_MISSION[2], game.CURRENT_MISSION[3], game.CURRENT_MISSION[4])
            mission.current_number = game.CURRENT_MISSION[0]
            mission.in_progress = True
            self.any_mission_active = True
            mission.mission_manager = self
            self.missions.insert(0, mission)

    def click(self, mouse):
        for mission in self.missions:
            if mission.click(mouse) is True: return True

    def draw(self):
        self.get_current_mission()
        for mission in self.missions:
            if self.any_mission_active:
                mission.active = False
            else:
                mission.active = True
            mission.update()



# FRAMEWORK
########################################################################################################################################################
# PAGES




main_menu = Page(
    Image(0.5, 3/16, images.ASTRO_ATTACK_LOGO),
    Button(0.5, 3/8, "Single Player", font_size=40, function=lambda: Menu.change_page(single_player)),
    Button(0.5, 4/8, "Multiplayer"  , font_size=40, function=lambda: Menu.change_page(multiplayer)),
    Button(0.5, 5/8, "Settings"     , font_size=40, function=lambda: Menu.change_page(settings)),
    Button(0.5, 6/8, "Info"         , font_size=40, function=lambda: Menu.change_page(info)),
    Button(0.5, 7/8, "Quit"         , font_size=40, function=lambda: Menu.change_page(quit_confirm)),
    Text(0.95, 0.95, "a1.4.0", font_size=20),
    escape=lambda: Menu.change_page(quit_confirm)
)

info = Page(
    Text(0.5, 0.125,   "CREDITS"          , font_size=40),
    Text(0.5, 0.2  , """Rex Attwood
                        Gabriel Correia""", font_size=20),
    Text(0.5, 0.27 ,   "Fred"             , font_size=5),
    Text(0.5, 0.35 ,   "CONTROLS"         , font_size=40),
    Text(0.5, 0.42 , """Change Settings: Up, Down, Drag
                        Pause: Esc
                        Movement: W, A, S, D
                        Boost: Space
                        Systems & Station: E
                        Look: Mouse
                        Zoom: Scroll
                        Shoot: Left Click
                        Target: Right Click
                        Change Weapon: 1, 2, 3, 4""", font_size=20),
    Button(0.5, 7/8,   "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
    escape=lambda: Menu.change_page(main_menu)
)

settings = Page(
    SettingButton(0.25, 1/6, lambda: f"SCREEN WIDTH: {game.WIDTH}"         , font_size=40, value="WIDTH"        , function_action=lambda: make_windowed(), min=192, max=game.FULLSCREEN_SIZE[0]),
    SettingButton(0.75, 1/6, lambda: f"SCREEN HEIGHT: {game.HEIGHT}"       , font_size=40, value="HEIGHT"       , function_action=lambda: make_windowed(), min=108, max=game.FULLSCREEN_SIZE[1]),
    SettingButton(0.25, 2/6, lambda: f"FULL SCREEN: {game.FULLSCREEN}"     , font_size=40, value="FULLSCREEN"   , function_action=lambda: change_fullscreen()),
    SettingButton(0.75, 2/6, lambda: f"LOAD DISTANCE: {game.LOAD_DISTANCE}", font_size=40, value="LOAD_DISTANCE", function_action=lambda: game.save_settings(), min=4, max=26),
    Button(0.5, 7/8, "Main Menu" , font_size=40, function=lambda: Menu.change_page(main_menu)),
    click=lambda: page_click(),
    escape=lambda: Menu.change_page(main_menu),
    up=lambda: settings_up(),
    down=lambda: settings_down()
)

pause = Page(
    Image( 0.5, 0.245, images.ASTRO_ATTACK_LOGO, scale=0.6),
    Button(0.5, 0.345, "Continue", font_size=40, function=lambda: setattr(Menu, "running", False)),
    Button(0.5, 0.46, "Main Menu", font_size=40, function=lambda: exit_game()),
    background_colour=None,
    escape=lambda: True,
)

world_list = WorldList(0.5, 0.242, width=0.6, height=0.12, gap=0.04)

single_player = Page(
    Text(0.5, 0.09, "Worlds"),
    Button(0.5, 0.752, "New World", function=lambda: Menu.change_page(new_world)),
    WorldSelectionButton(0.28, 0.752, "Play", function=lambda: world_list.world_selected.function(), uniform=True),
    WorldSelectionButton(0.72, 0.752, "Delete", function=lambda: world_list.delete_selected_world(), uniform=True),
    Button(0.5, 0.875, "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
    world_list,
    escape=lambda: Menu.change_page(main_menu)
)

multiplayer = Page(
    Text(0.5, 0.45, "Coming soon in a1.7!"),
    Button(0.5, 0.875, "Main Menu" , font_size=40, function=lambda: Menu.change_page(main_menu)),
    escape=lambda: Menu.change_page(main_menu)
)

new_world = Page(
    NameTextInput(0.5, 0.3, 0.5, 0.1, "Name", limit=20),
    SeedTextInput(0.5, 0.53, 0.5, 0.1, "Seed", limit=6),
    Button(0.5, 0.752, "Create World", function=lambda: create_world()),
    Button(0.5, 0.875, "Back" , font_size=40, function=lambda: Menu.change_page(single_player)),
    click=lambda: page_click(),
    escape=lambda: Menu.change_page(single_player)
)

creating_world = Page(
    Text(0.5, 0.5, "Creating world...")
)

loading_world = Page(
    Text(0.5, 0.5, "Loading world...")
)

saving_world = Page(
    Text(0.5, 0.5, "Saving world...")
)

name_already_chosen = Page(
    Rectangle(0.08, 0.08, 0.84, 0.84, (40, 40, 40), outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, curve=10),
    Text(0.5, 0.5, "World name already chosen"),
    Button(0.5, 0.65, "OK", function=lambda: Menu.change_page(new_world)),
    background_colour=None
)

quit_confirm = Page(
    Rectangle(0.35, 0.41, 0.3, 0.31, (40, 40, 40), outline_colour=Menu.DEFAULT_OUTLINE_COLOUR),
    Text(0.5, 0.46, "Quit?"),
    Button(0.5, 0.55, "No", function=lambda: Menu.change_page(main_menu), uniform=True),
    Button(0.5, 0.65, "Yes", function=game.quit, uniform=True),
    background_colour=None,
    escape=lambda: Menu.change_page(main_menu)
)

station = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Upgrades"),
    Button(0.27, 0.23, "Upgrades", function=lambda: Menu.change_page(station), uniform=True),
    Button(0.5, 0.23, "Missions", function=lambda: Menu.change_page(missions), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), uniform=True),
    Button(0.2, 0.7, "Armour", function=lambda: Menu.change_page(armour)),
    Button(0.4, 0.7, "Weapon", function=lambda: Menu.change_page(weapon)),
    Button(0.6, 0.7, "Engine", function=lambda: Menu.change_page(engine)),
    Button(0.8, 0.7, "Radar" , function=lambda: Menu.change_page(radar)),
    Image(0.2, 0.5, images.ARMOUR_ICON, scale=6),
    Image(0.4, 0.5, images.WEAPON_ICON, scale=6),
    Image(0.6, 0.5, images.ENGINE_ICON, scale=6),
    Image(0.8, 0.5, images.RADAR_ICON, scale=6),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

missions = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Missions"),
    Button(0.27, 0.23, "Upgrades", function=lambda: Menu.change_page(station), uniform=True),
    Button(0.5, 0.23, "Missions", function=lambda: Menu.change_page(missions), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), uniform=True),
    MissionManager(0.5, 0.5),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

stats = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Stats"),
    Button(0.27, 0.23, "Upgrades", function=lambda: Menu.change_page(station), uniform=True),
    Button(0.5, 0.23, "Missions", function=lambda: Menu.change_page(missions), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), uniform=True),
    Text(0.5, 0.5, lambda: f"Skill level: {stats_skill_levels[min(10, int(game.SCORE/50))].upper()}"),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

stats_skill_levels = (
    "noob",
    "beginner",
    "novice",
    "apprentice",
    "fighter",
    "gamer",
    "pro",
    "legend",
    "hacker",
    "god",
    "developer"
)

armour = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Armour"),
    UpgradeBar(0.19, 0.3, "Health", "MAX_PLAYER_HEALTH", min_value=game.MAX_PLAYER_HEALTH, max_value=100),
    UpgradeBar(0.19, 0.4, "Shield", "MAX_PLAYER_SHIELD", min_value=game.MAX_PLAYER_SHIELD, max_value=25),
    UpgradeBar(0.19, 0.5, "Recharge", "PLAYER_SHIELD_RECHARGE", min_value=game.PLAYER_SHIELD_RECHARGE, max_value=3),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: True
)

weapon = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Weapon"),
    Button(0.3, 0.3, "Default", function=lambda: Menu.change_page(default_gun)),
    Button(0.3, 0.5, "Gatling", function=lambda: Menu.change_page(gatling_gun)),
    Button(0.3, 0.7, "Sniper" , function=lambda: Menu.change_page(sniper_gun)),
    Button(0.7, 0.3, "Laser"  , function=lambda: Menu.change_page(laser)),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: True
)

engine = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Engine"),
    UpgradeBar(0.19, 0.3, "Acceleration", "PLAYER_ACCELERATION", min_value=game.PLAYER_ACCELERATION, max_value=1500),
    UpgradeBar(0.19, 0.4, "Max Speed", "MAX_PLAYER_SPEED", min_value=game.MIN_PLAYER_SPEED, max_value=1000),
    UpgradeBar(0.19, 0.5, "Max Boost", "MAX_BOOST_AMOUNT", min_value=20, max_value=50),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: True
)

radar = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Radar"),
    UpgradeBar(0.19, 0.3, "Item Magnet", "PICKUP_DISTANCE", min_value=game.PICKUP_DISTANCE, max_value=300),
    UpgradeBar(0.19, 0.4, "Max Zoom", "CURRENT_MIN_ZOOM", min_value=game.CURRENT_MIN_ZOOM, max_value=game.MIN_ZOOM),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: True
)

default_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Default"),
    UpgradeBar(0.19, 0.3, "Fire Rate", "PLAYER_DEFAULT_FIRE_RATE", min_value=game.PLAYER_DEFAULT_FIRE_RATE, max_value=20),
    UpgradeBar(0.19, 0.4, "Damage", "PLAYER_DEFAULT_DAMAGE", min_value=game.PLAYER_DEFAULT_DAMAGE, max_value=2),
    UpgradeBar(0.19, 0.5, "Bullet Speed", "PLAYER_DEFAULT_BULLET_SPEED", min_value=game.PLAYER_DEFAULT_BULLET_SPEED, max_value=1000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(weapon),
    e_press=lambda: True
)

gatling_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Gatling"),
    UpgradeBar(0.19, 0.3, "Fire Rate", "PLAYER_GATLING_FIRE_RATE", min_value=game.PLAYER_GATLING_FIRE_RATE, max_value=40),
    UpgradeBar(0.19, 0.4, "Damage", "PLAYER_GATLING_DAMAGE", min_value=game.PLAYER_GATLING_DAMAGE, max_value=1),
    UpgradeBar(0.19, 0.5, "Bullet Speed", "PLAYER_GATLING_BULLET_SPEED", min_value=game.PLAYER_GATLING_BULLET_SPEED, max_value=1000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(weapon),
    e_press=lambda: True
)

sniper_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Sniper"),
    UpgradeBar(0.19, 0.3, "Fire Rate", "PLAYER_SNIPER_FIRE_RATE", min_value=game.PLAYER_SNIPER_FIRE_RATE, max_value=5),
    UpgradeBar(0.19, 0.4, "Damage", "PLAYER_SNIPER_DAMAGE", min_value=game.PLAYER_SNIPER_DAMAGE, max_value=5),
    UpgradeBar(0.19, 0.5, "Bullet Speed", "PLAYER_SNIPER_BULLET_SPEED", min_value=game.PLAYER_SNIPER_BULLET_SPEED, max_value=2000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(weapon),
    e_press=lambda: True
)

laser = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Laser"),
    UpgradeBar(0.19, 0.3, "Range" , "PLAYER_LASER_RANGE" , min_value=game.PLAYER_LASER_RANGE, max_value=700),
    UpgradeBar(0.19, 0.4, "Damage", "PLAYER_LASER_DAMAGE", min_value=game.PLAYER_LASER_DAMAGE, max_value=20),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(weapon),
    e_press=lambda: True
)

systems = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Systems"),

    Text(0.3, 0.3, "Health", font_size=25),
    Bar(0.39, 0.298, width=0.32, height=0.1, value=lambda: game.player.health, max_value=lambda: game.MAX_PLAYER_HEALTH, colour=(255, 0, 0), outline_width=5, curve=12),
    Text(0.405, 0.3, lambda: f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", font_size=25, align="left"),

    Text(0.3, 0.45, "Armour", font_size=25),
    ArmourBar(0.39, 0.448, width=0.32, height=0.1, value=lambda: game.player.armour, max_value=lambda: game.MAX_PLAYER_ARMOUR, price=3, number=3, colour=(185, 185, 185), outline_width=5, curve=12),
    Text(0.405, 0.45, lambda: f"{round(game.player.armour)} | {game.MAX_PLAYER_ARMOUR}", font_size=25, align="left"),

    Text(0.3, 0.6, "Shield", font_size=25),
    Bar(0.39, 0.598, width=0.32, height=0.1, value=lambda: game.player.shield, max_value=lambda: game.MAX_PLAYER_SHIELD, colour=(34, 130, 240), outline_width=5, curve=12),
    Text(0.405, 0.6, lambda: f"{round(game.player.shield)} | {game.MAX_PLAYER_SHIELD}", font_size=25, align="left"),

    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align="right"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

death_screen = Page(
    Text(  0.5, 0.25 , "YOU DIED!"                 , colour=(255, 0, 0)    , font_size=40),
    Text(  0.5, 0.4, lambda: f"SCORE: {game.SCORE}", colour=(100, 100, 255), font_size=40),
    Button(0.5, 0.6 , "Respawn"   , font_size=40, function=lambda: main.main()),
    Button(0.5, 0.75, "Main Menu" , font_size=40, function=lambda: exit_game())
)



#################
### Functions ###
#################

def get_widget(name: str, page: Page | None = None) -> Widget | None:
    if not page: page = Menu.current_page
    for widget in page.widgets:
        if widget.__name__ == name:
            return widget

def create_world():
    # Get name and seed
    for widget in Menu.current_page.widgets:
        if type(widget) == NameTextInput:

            # Check world name is not already used
            for world_name, seed in game.get_world_dir():
                if widget.text == world_name:
                    Menu.change_page(name_already_chosen)
                    return

            name = widget.text
            widget.text = ""

        elif type(widget) == SeedTextInput:
            seed = widget.text
            widget.text = ""

    Menu.change_page(creating_world)

    # Generate random seed if no seed inputted
    if seed == "":
        seed = random.randint(0, 999_999)

    game.reset_constants()
    game.NAME = name
    game.SEED = seed
    game.init_chunks()
    game.player = get_player()
    game.save_constants(name)

    game.update_world_dir(name, seed)

    world = world_list.create_world(name, seed)

    world_list.start_world(world)

def exit_game():
    Menu.change_page(saving_world)

    # Save current game
    game.save_constants(game.NAME)

    Menu.change_page(main_menu)

def page_click():
    """If there is a selected widget that shouldn't be, un-select it"""
    mouse = pygame.mouse.get_pos()
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected") and widget.selected and not widget.touching_mouse(mouse): # if widget should be un-selected
            widget.selected = False
            if isinstance(widget, SettingButton): widget.outline_colour = widget.original_outline_colour
            Menu.update()
            break

def settings_up():
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected"):
            if widget.selected:
                widget.up()

def settings_down():
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected"):
            if widget.selected:
                widget.down()

def change_fullscreen():
    if game.FULLSCREEN:
        # Mouse moves when resizing, this keeps mouse in same relative position
        mouse_ratio = [i / j for i, j in list(zip(pygame.mouse.get_pos(), pygame.display.get_window_size()))]
        pygame.display.set_mode(flags=pygame.FULLSCREEN+pygame.RESIZABLE)
        pygame.mouse.set_pos([i * j for i, j in list(zip(mouse_ratio, game.FULLSCREEN_SIZE))])

    else:
        # Mouse moves when resizing, this keeps mouse in same relative position
        mouse_ratio = [i / j for i, j in list(zip(pygame.mouse.get_pos(), pygame.display.get_window_size()))]
        pygame.mouse.set_pos([i * j for i, j in list(zip(mouse_ratio, game.WINDOW_SIZE))])
        pygame.display.set_mode(game.WINDOW_SIZE, flags=pygame.RESIZABLE)

    game.WIDTH, game.HEIGHT = pygame.display.get_window_size()
    game.save_settings()

def make_windowed():
    game.FULLSCREEN = False
    pygame.display.set_mode((game.WIDTH, game.HEIGHT), flags=pygame.RESIZABLE)
    game.save_settings()

def repair_armour():
    if game.SCRAP_COUNT < 5:
        return
    else:
        game.SCRAP_COUNT -= 5
        game.player.armour += 5

        if game.player.armour > game.MAX_PLAYER_ARMOUR:
            game.player.armour = game.MAX_PLAYER_ARMOUR
