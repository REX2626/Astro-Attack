from __future__ import annotations
from player import get_player
from ui import Bar as UIBar
import images
import game
import main
import random
from typing import Any, Callable
from pygame import freetype
import pygame
# menu v2



Coord = tuple[int, int]
Colour = tuple[int, int, int]
Rect = tuple[float, float, float, float]

EXIT = 1
CLICKED = 2



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
    SLIDER_WIDTH = 0.02  # percentage (0 to 1) of screen width
    SLIDER_COLOUR = (*game.LIGHT_GREY, 150)
    SLIDER_OUTLINE = (30, 30, 30, 150)

    def __init__(self) -> None:
        """On start up, the default page is main_menu"""
        Menu.change_page(main_menu)

    def change_page(page: Page) -> None:
        """Draw the new page, and then wait for a mouse click"""
        pygame.mouse.set_visible(True)
        Menu.current_page = page
        page.draw()

        if not Menu.running:
            Menu.running = True
            Menu.run()

    def run() -> None:
        while Menu.running:
            if Menu.check_for_inputs() == EXIT:  # if check_for_inputs() returns EXIT, then break out of Menu control
                Menu.running = False

    def update() -> None:
        """Re-draw the current_page"""
        Menu.current_page.draw()

    def resize() -> None:
        """Re-draw the current_page but with the updated screen dimensions"""
        game.update_screen_size()
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "resize"):
                widget.resize()
        Menu.update()

    def check_for_inputs() -> int | None:
        """Go through pygame.event and do the corresponding functions"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.quit()

            elif event.type == pygame.VIDEORESIZE:
                Menu.resize()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 is left click
                mouse = pygame.mouse.get_pos()
                if Menu.mouse_click(mouse) == EXIT:
                    return EXIT

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # 1 is left click
                for widget in Menu.current_page.widgets:  # Stop sliding for all sliders
                    if hasattr(widget, "sliding"):
                        widget.sliding = False

            elif event.type == pygame.MOUSEMOTION:
                mouse = pygame.mouse.get_pos()
                Menu.mouse_moved(mouse)
                Menu.update()  # buttons will be checked if they are hovered on or not

            elif event.type == pygame.MOUSEWHEEL:
                Menu.mouse_scroll(event.y)

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # runs Menu.escape_pressed, if that returns EXIT, then follow suit and return EXIT
                if Menu.escape_pressed():
                    return EXIT

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:
                    Menu.up_pressed()

                elif event.key == pygame.K_DOWN:
                    Menu.down_pressed()

                elif event.key == pygame.K_e:
                    # if e_pressed return EXIT, then go back to the game
                    if Menu.e_pressed():
                        return EXIT

                elif event.key == pygame.K_TAB:
                    # if tab_pressed return EXIT, then go back to the game
                    if Menu.tab_pressed():
                        return EXIT

                Menu.key_pressed(event)

                Menu.update()

    def mouse_click(mouse: Coord) -> int | None:
        """Go through all Page Widgets, if the Widget is a button then check if it is clicked on"""
        if Menu.current_page.click:
            Menu.current_page.click()

        for widget in Menu.current_page.widgets:
            if hasattr(widget, "click"):
                result = widget.click(mouse)
                if result == CLICKED:  # if the Button has been clicked, then stop checking the Buttons
                    break
                elif result == EXIT:
                    return EXIT

    def mouse_moved(mouse: Coord) -> None:
        """Go through all Page Widgets, if the Widget has a mouse_moved attribute, then call it"""
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "mouse_moved"):
                widget.mouse_moved(mouse)  # moves slider if need be

    def mouse_scroll(y: int) -> None:
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "scroll"):
                widget.scroll(y)

    def escape_pressed() -> int | None:
        if Menu.current_page.escape:
            if Menu.current_page.escape():
                return EXIT  # return EXIT allows for a propagation which relieves Menu's control

    def e_pressed() -> int | None:
        if Menu.current_page.e_press:
            if Menu.current_page.e_press():
                return EXIT  # return to playing

    def tab_pressed() -> int | None:
        if Menu.current_page.tab_press:
            if Menu.current_page.tab_press():
                return EXIT  # return to playing

    def up_pressed() -> None:
        if Menu.current_page.up:
            Menu.current_page.up()

    def down_pressed() -> None:
        if Menu.current_page.down:
            Menu.current_page.down()

    def key_pressed(event: pygame.Event) -> None:
        for widget in Menu.current_page.widgets:
            if hasattr(widget, "key_pressed"):
                widget.key_pressed(event)

    def pause() -> None:
        Menu.change_page(pause)

    def systems() -> None:
        Menu.change_page(systems)

    def station() -> None:
        Menu.change_page(station)

    def death_screen() -> None:
        Menu.change_page(death_screen)



class Page():
    """Page contains a list of widgets
       if background_colour is None, the background remains the same i.e. the widgets are just overlayed on top of the screen
       click is a function that is called when the user clicks on the page
       escape is a function that is called when the escape key is pressed, if it returns True - the Menu system is exited, so code can continue
       up is a function that is called when the up key is pressed
       down is a function that is called when the down key is pressed
    """
    def __init__(self,
            *widgets: Widget,
            background_colour: Colour = Menu.DEFAULT_BACKGROUND_COLOUR,
            click: Callable | None = None,
            escape: Callable | None = None,
            e_press: Callable | None = None,
            tab_press: Callable | None = None,
            up: Callable | None = None,
            down: Callable | None = None
        ) -> None:
        self.background_colour = background_colour
        self.click = click
        self.escape = escape
        self.e_press = e_press
        self.tab_press = tab_press
        self.up = up
        self.down = down

        self.widgets = widgets

    def draw(self) -> None:
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
    """
    Base class for Page elements

    `x` (float)

    `y` (float)

    arguments (`x`, `y`) are the ratio of the screen (e.g. 0.1 or 0.78)

    Widget.x, Widget.y is the location in pixels

    Widget._x, Widget._y is the location in ratio (same as input arguments)
    """
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x * game.WIDTH

    @property
    def y(self) -> float:
        return self._y * game.HEIGHT



class RectWidget(Widget):
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        super().__init__(x, y)
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width * game.WIDTH

    @width.setter
    def width(self, new_width: float) -> None:
        self._width = new_width

    @property
    def height(self) -> float:
        return self._height * game.HEIGHT

    @height.setter
    def height(self, new_height: float) -> None:
        self._height = new_height



class Image(Widget):
    """
    A Widget that has an image

    `scale` is the scale of the image, e.g. scale=1 wouldn't change image size, scale=2 would double the size
    """
    def __init__(self, x: float, y: float, image: pygame.Surface = images.DEFAULT, scale: float = 1) -> None:
        super().__init__(x, y)
        self.image = pygame.transform.scale_by(image, scale)

    def draw(self) -> None:
        ratio = min(game.WIDTH * self.image.get_width() / 1_000_000,  # Ratio of image width to game width
                    game.HEIGHT * self.image.get_width() / 625_000)
        image = pygame.transform.scale_by(self.image, ratio)
        game.WIN.blit(image, (self.x - image.get_width()/2, self.y - image.get_height()/2))



class AdjustableText(RectWidget):
    def __init__(self,
            x: float,
            y: float,
            width: float,
            height: float,
            text: str = "",
            font: str = Menu.DEFAULT_FONT,
            default_font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR
        ) -> None:
        super().__init__(x, y, width, height)

        self.words = text.split(" ")
        self.font_type = font
        self.font_size = default_font_size
        self.default_font_size = default_font_size
        self.colour = colour

        self.font = freetype.SysFont(self.font_type, self.default_font_size)

        self.line_spacing = self.font.get_sized_height()

        self.low_letters = ["g", "j", "q", "p", "y"]

    def change_text(self, text: str) -> None:
        self.words = text.split(" ")

    def render_words(self) -> list:
        self.font = freetype.SysFont(self.font_type, self.font_size)
        self.line_spacing = self.font.get_sized_height()

        low_letter_difference = self.font.get_rect("y").height - self.font.get_rect("u").height
        low_letter = False
        x, y = self.x, self.y
        space = self.font.get_rect(' ')

        render_list = []

        for word in self.words:
            bounds = self.font.get_rect(word)

            for letter in self.low_letters:
                if letter in word:
                    low_letter = True
                    break

            if x + bounds.width >= self.x + self.width:
                x, y = self.x, y + self.line_spacing

            if x + bounds.width >= self.x + self.width or y + self.line_spacing >= self.y + self.height:
                self.font_size -= 1
                return self.render_words()

            if low_letter:
                render_list.append((x, y + (self.line_spacing - bounds.height), word))
                low_letter = False
            else:
                render_list.append((x, y + (self.line_spacing - bounds.height) - low_letter_difference, word))
            x += bounds.width + space.width

        return render_list

    def draw(self) -> None:
        self.font_size = self.default_font_size
        render_list = self.render_words()

        for element in render_list:
            self.font.render_to(game.WIN, (element[0], element[1]), text=element[2], fgcolor=self.colour)



class Text(Widget):
    """
    Text can be single or multi-line

    (`x`, `y`) is the centre of the first line of the Text

    `text` can be a string or a function, if it's a function then that will be called, e.g. text=lambda f"SCORE: {game.SCORE}"

    `font_size` is relative to screen width, if you change the screen resolution then the font size will dynamically change

    `align` can be pygame.FONT_LEFT, pygame.FONT_RIGHT, pygame.FONT_CENTER, this is for the x value

    NOTE: if text is a function it has to return a string (can be single or multi-line)
    """
    def __init__(
            self,
            x: float,
            y: float,
            text: str | Callable[[], str],
            font: str = Menu.DEFAULT_FONT,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR,
            spacing: float = Menu.DEFAULT_TEXT_SPACING,
            align: int = pygame.FONT_CENTER
        ) -> None:
        super().__init__(x, y)

        self.text = text

        self.font = font
        self.font_size = font_size
        self.colour = colour
        self.spacing = lambda: spacing * game.HEIGHT
        self.align = align

        self.height = None
        self.label_text = None
        self.label_size = None

    def get_blit_x(self, label: pygame.Surface) -> float:
        if self.align == pygame.FONT_CENTER:
            return self.x - label.get_width()/2
        elif self.align == pygame.FONT_LEFT:
            return self.x
        elif self.align == pygame.FONT_RIGHT:
            return self.x - label.get_width()

    def update_label_info(self) -> pygame.Surface:
        """
        Creates a new text label with the required info
        """
        if callable(self.text):
            text = self.text()
        else:
            text = self.text

        text = "\n".join([sentence.lstrip() for sentence in text.split("\n")])  # Remove whitespace before each line

        self.label_text = text
        self.label_size = round(game.WIDTH * self.font_size / 900)

        font = pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900))
        font.align = self.align

        self.height = font.get_height()
        self.label = font.render(text, True, self.colour)

        return self.label

    def get_label(self) -> pygame.Surface:
        """
        Returns a text label, updates label if necessary
        """
        if callable(self.text):
            text = self.text()
        else:
            text = self.text

        if text != self.label_text or round(game.WIDTH * self.font_size / 900) != self.label_size:
            self.update_label_info()

        return self.label

    def draw(self) -> None:
        """
        Draws the text label to the screen
        """
        label = self.get_label()
        position = self.get_blit_x(label), self.y - self.height/2  # Adjust coordinates to be centre of Widget
        game.WIN.blit(label, position)



class Button(Text):
    """
    A Widget that can be clicked on

    When a Button is clicked, the `function` method is called

    (`padx`, `pady`) is the padding, i.e. how much the button extends past the text, i.e. padx=1 means 1 pixel on the left AND 1 pixel on the right
    """
    def __init__(
            self,
            x: float,
            y: float,
            text: str,
            font: str = Menu.DEFAULT_FONT,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR,
            padx: int = Menu.DEFAULT_PADX,
            pady: int = Menu.DEFAULT_PADY,
            function: None | Callable = None,
            box_colour: Colour = Menu.DEFAULT_BOX_COLOUR,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            hover_colour: Colour = Menu.DEFAULT_HOVER_COLOUR,
            uniform: bool = False
        ) -> None:
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

        self.update_label_info()

    def click(self, mouse: Coord) -> bool:
        if self.touching_mouse(mouse):
            if self.function() == EXIT:
                return EXIT
            return CLICKED  # Tells the Menu that this Button has been clicked on

    def touching_mouse(self, mouse: Coord) -> bool:
        label = self.label
        x, y, width, height = self.get_rect(label)
        x, y = x - self.padx, y - self.pady
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def get_width(self, label: pygame.Surface) -> float:
        return label.get_width() + self.padx*2  # padding*2 as there is padding on both sides

    def get_height(self) -> float:
        return self.height + self.pady*2  # padding*2 as there is padding on both sides

    def get_max_width(self) -> float:
        """
        Get greatest width of all Buttons on the current_page
        """
        max_width = 0
        for widget in Menu.current_page.widgets:
            if isinstance(widget, Button) and widget.uniform:
                if widget.get_width(widget.label) > max_width:
                    max_width = widget.get_width(widget.label)
        return max_width

    def get_rect(self, label: pygame.Surface) -> Rect:
        """
        If self.uniform is True, set the width to the greatest width of all Buttons on the current_page
        """
        if self.uniform:
            width, height = self.get_max_width(), self.get_height()
            width_difference = width - self.get_width(label)
            x, y = self.x - label.get_width()/2 - width_difference/2, self.y - self.height/2
            return x, y, width, height

        width, height = self.get_width(label), self.get_height()
        x, y = self.x - label.get_width()/2, self.y - self.height/2
        return x, y, width, height

    def draw(self) -> None:
        """
        Draws the button to the screen
        """
        if self.touching_mouse(pygame.mouse.get_pos()):
            self.current_box_colour = self.hover_colour
        else:
            self.current_box_colour = self.box_colour

        label = self.label  # This is updated in Page.draw()
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(game.WIN, self.current_box_colour, (x - self.padx, y - self.pady, width, height))
        pygame.draw.rect(game.WIN, self.outline_colour, (x - self.padx, y - self.pady, width, height), width=round(game.WIDTH/300))
        position = self.x - label.get_width()/2, self.y - self.height/2  # Adjust coordinates to be centre of Widget
        game.WIN.blit(label, position)



class SettingButton(Button):
    """
    A Button for settings

    When clicked on, it will change outline colour

    `value` is the value that the setting button affects, NOTE: value is a string and has to be an attribute of game, e.g. game.WIDTH and value="WIDTH"

    `function_action` is called after the value is modified

    `text` is a function

    (`min` and `max`) are the minimum and maximum values of value

    `uniform` makes all of the setting buttons on the page the same width
    """
    def __init__(
            self,
            x: float,
            y: float,
            text: str,
            font: str = Menu.DEFAULT_FONT,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR,
            padx: int = Menu.DEFAULT_PADX,
            pady: int = Menu.DEFAULT_PADY,
            value: str = None,
            function_action: None | Callable = None,
            min: float = 1,
            max: float = 100,
            box_colour: Colour = Menu.DEFAULT_BOX_COLOUR,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            hover_colour: Colour = Menu.DEFAULT_HOVER_COLOUR,
            click_outline_colour: Colour = Menu.DEFAULT_CLICK_OUTLINE_COLOUR,
            uniform: bool = True
        ) -> None:
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

        def function() -> None:
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

    def get_value(self) -> Any:
        return getattr(game, self.value)

    def get_slider_width(self) -> float:
        return Menu.SLIDER_WIDTH * game.WIDTH

    def get_slider(self) -> Rect:
        label = self.label
        ratio = (self.get_value() - self.min) / (self.max - self.min)  # percentage of max value
        x, y, width, height = self.get_rect(label)
        x += ratio*(width-self.get_slider_width()) - self.padx
        width = self.get_slider_width()
        height -= self.pady*2
        return x, y, width, height

    def mouse_moved(self, mouse: Coord) -> None:
        if hasattr(self, "sliding") and self.sliding:

            x, _, width, _ = self.get_rect(self.label)  # get button rect
            ratio = (self.max - self.min) / (width - self.get_slider_width())  # value per pixel
            left_slider = mouse[0] - self.get_slider_width()*self.slider_ratio  # gets x of left side of the slider, keeping same slider ratio
            value = int((left_slider - x + self.padx) * ratio) + self.min  # get relative mouse position from left of button * ratio
            if value < self.min: value = self.min  # clip value so that it is between min and max
            elif value > self.max: value = self.max

            setattr(game, self.value, value)
            if self.function_action:
                self.function_action()

    def click(self, mouse: Coord) -> None:
        super().click(mouse)
        x, y, width, height = self.get_slider()
        if (mouse[0] > x and mouse[0] < x + width and
            mouse[1] > y and mouse[1] < y + height):
            self.sliding = True
            self.slider_ratio = (mouse[0] - x) / width  # The percentage (0 to 1) of the mouse position on the sliding segment

    def up(self) -> None:
        if type(self.get_value()) == bool:
            setattr(game, self.value, not self.get_value())
        else:
            setattr(game, self.value, self.get_value() + 1 if self.get_value() < self.max else self.max)
        if self.function_action:
            self.function_action()

    def down(self) -> None:
        if type(self.get_value()) == bool:
            setattr(game, self.value, not self.get_value())
        else:
            setattr(game, self.value, self.get_value() - 1 if self.get_value() > self.min else self.min)
        if self.function_action:
            self.function_action()

    def draw(self) -> None:
        super().draw()
        # If this is an integer setting, then automatically make it a slider
        if type(self.get_value()) == int:
            x, y, width, height = self.get_slider()
            surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            pygame.draw.rect(surf, Menu.SLIDER_COLOUR, (0, 0, width, height))
            pygame.draw.rect(surf, Menu.SLIDER_OUTLINE, (0, 0, width, height), width=round(game.WIDTH/300))
            game.WIN.blit(surf, (x, y))



class WorldSelectionButton(Button):
    def __init__(
            self,
            x: float,
            y: float,
            text: str,
            font: str = Menu.DEFAULT_FONT,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR,
            padx: int = Menu.DEFAULT_PADX,
            pady: int = Menu.DEFAULT_PADY,
            function: Callable = None,
            box_colour: Colour = Menu.DEFAULT_BOX_COLOUR,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            hover_colour: Colour = Menu.DEFAULT_HOVER_COLOUR,
            uniform: bool = False
        ) -> None:
        self.inactive_text_colour = (150, 150, 150)
        self.inactive_box_colour = (40, 40, 40)
        self.inactive_hover_colour = (40, 40, 40)
        super().__init__(x, y, text, font, font_size, colour, padx, pady, function, box_colour, outline_colour, hover_colour, uniform)
        self.text_colour = colour
        self.default_box_colour = box_colour
        self.default_hover_colour = hover_colour

        self.text_label_active = False

    def click(self, mouse: Coord) -> bool | None:
        if self.touching_mouse(mouse) and world_list.world_selected:
            self.function()
            return CLICKED  # Tells the Menu that this Button has been clicked on

    @property
    def colour(self) -> Colour:
        return self.text_colour if world_list.world_selected else self.inactive_text_colour

    @colour.setter
    def colour(self, colour: Colour) -> None:
        self.text_colour = colour

    @property
    def box_colour(self) -> Colour:
        return self.default_box_colour if world_list.world_selected else self.inactive_box_colour

    @box_colour.setter
    def box_colour(self, colour: Colour) -> None:
        self.default_box_colour = colour

    @property
    def hover_colour(self) -> Colour:
        return self.default_hover_colour if world_list.world_selected else self.inactive_hover_colour

    @hover_colour.setter
    def hover_colour(self, colour: Colour) -> None:
        self.default_hover_colour = colour

    def draw(self) -> None:
        if world_list.world_selected and not self.text_label_active:
            self.text_label_active = True
            self.update_label_info()
        elif not world_list.world_selected and self.text_label_active:
            self.text_label_active = False
            self.update_label_info()
        super().draw()



class Rectangle(RectWidget):
    """
    A rectangular object of given `width`, `height` and `colour`

    (`x`, `y`) are floats (percentage from 0 to 1 of screen size)

    (`width`, `height`) are floats, ratio of screen size

    `curve` is the radius of the corners
    """
    def __init__(
            self,
            x: float,
            y: float,
            width: float,
            height: float,
            colour: Colour,
            outline_colour: Colour | None = None,
            curve: int = 0
        ) -> None:
        super().__init__(x, y, width, height)
        self.colour = colour
        self.outline_colour = outline_colour
        self.curve = curve

    def draw(self) -> None:
        if self.outline_colour:
            outline_width = round(game.WIDTH/300)
            pygame.draw.rect(game.WIN, self.outline_colour, (self.x - outline_width, self.y - outline_width, self.width + 2*outline_width, self.height + 2*outline_width), width=outline_width, border_radius=self.curve)

        pygame.draw.rect(game.WIN, self.colour, (self.x, self.y, self.width, self.height), border_radius=self.curve)



class UpgradeBar(Widget):
    """
    Used to upgrade aspects of player systems

    value is the variable that the bar is upgrading, it is a string and has to be a variable of game (e.g. game.WIDTH, value="WIDTH")

    bar_width and bar_height are floats, which is the percentage (0 to 1) of the screen width and height

    bars is the number of bars
    """
    def __init__(
            self,
            y: float,
            text: str,
            value: str,
            x: float = 0.23,
            font_size: int = 15,
            button_colour: Colour = (10, 20, 138),
            bar_colour: Colour = (255, 125, 0),
            outline_colour: Colour = (255, 255, 255),
            select_colour: Colour = (255, 100, 0),
            select_outline_colour: Colour = (20, 235, 25),
            button_width: float = 0.1,
            bar_width: float = 0.08,
            height: float = 0.05,
            gap: int = 5,
            bars: int = 5,
            min_value: float = 20,
            max_value: float = 60
        ) -> None:
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
        if self.step.is_integer(): self.step = int(self.step)  # if step is an integer, then remove the decimal point
        self.level = value + "_LEVEL"
        self.padlock = images.PADLOCK

    def get_value(self) -> Any:
        return getattr(game, self.value)

    def set_value(self, value: Any) -> None:
        setattr(game, self.value, value)

    def get_level(self) -> int:
        return getattr(game, self.level)

    def upgrade_level(self) -> None:
        setattr(game, self.level, self.get_level() + 1)

    def click(self, mouse: Coord) -> None:
        mx, my = mouse[0], mouse[1]

        # check if text bar is clicked on
        x = self.x
        y = self.y
        width = game.WIDTH * self.button_width
        height = game.HEIGHT * self.height
        if mx > x and mx < x + width and my > y and my < y + height:
            self.set_value(self.min_value)
            Menu.update()
            return

        # go through every bar to see if it is clicked on
        for bar in range(self.bars):

            width = game.WIDTH * self.bar_width
            height = game.HEIGHT * self.height
            button_width = game.WIDTH * self.button_width
            x = self.x + bar * (width + self.gap) + button_width + self.gap
            y = self.y

            # if clicked on
            if mx > x and mx < x + width and my > y and my < y + height:

                # if bar is less than level then switch to that level
                if bar < self.get_level():
                    self.set_value(self.min_value + (bar+1) * self.step)
                    Menu.update()

                # if bar is the next level, upgrade to that level
                elif bar == self.get_level() and game.SCRAP_COUNT >= 2**bar:
                    game.SCRAP_COUNT -= 2**bar
                    self.upgrade_level()
                    self.set_value(self.min_value + self.get_level() * self.step)
                    Menu.update()

                return

    def get_label(self) -> pygame.Surface:
        """Gets a text label"""
        font = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900))
        self.label_height = font.get_height()
        return font.render(self.text, True, Menu.DEFAULT_COLOUR)

    def draw(self) -> None:
        padlock = pygame.transform.scale_by(self.padlock, game.WIDTH/1200)
        scrap = pygame.transform.scale_by(images.SCRAP, game.WIDTH/1500)

        width = game.WIDTH * self.bar_width
        height = game.HEIGHT * self.height
        button_width = game.WIDTH * self.button_width

        # draw text bar
        if self.get_value() == self.min_value:  # if level 0, text bar has a select outline
            pygame.draw.rect(game.WIN, self.select_outline_colour, (self.x, self.y, button_width, height), border_radius=10)
        else:
            pygame.draw.rect(game.WIN, self.outline_colour, (self.x, self.y, button_width, height), border_radius=10)

        pygame.draw.rect(game.WIN, self.button_colour, (self.x+2, self.y+2, button_width-4, height-4), border_radius=10)
        label = self.get_label()
        game.WIN.blit(label, (self.x + button_width/2 - label.get_width()/2, self.y + height/2 - self.label_height/2))


        # draw bars
        for bar in range(self.bars):

            x = self.x + bar * (width + self.gap) + button_width + self.gap

            # draw bar outline
            if self.get_value() == (bar+1) * self.step + self.min_value:  # if selected choose a different outline colour
                pygame.draw.rect(game.WIN, self.select_outline_colour, (x, self.y, width, height), border_radius=10)
            else:
                pygame.draw.rect(game.WIN, self.outline_colour, (x, self.y, width, height), border_radius=10)

            # fill in bar if neseccary, bar+1 so that the first bar is level 1
            if bar+1 <= self.get_level():

                if self.get_value() == (bar+1) * self.step + self.min_value:  # if selected choose a different colour
                    pygame.draw.rect(game.WIN, self.select_colour, (x+2, self.y+2, width-4, height-4), border_radius=10)

                else:  # fill in with regular colour
                    pygame.draw.rect(game.WIN, self.bar_colour, (x+2, self.y+2, width-4, height-4), border_radius=10)

            else:  # fill in with background colour
                pygame.draw.rect(game.WIN, Menu.DEFAULT_BACKGROUND_COLOUR, (x+2, self.y+2, width-4, height-4), border_radius=10)

                if bar == self.get_level():  # the first locked bar shows a price instead of a padlock
                    if game.SCRAP_COUNT >= 2**bar: colour = Menu.DEFAULT_COLOUR
                    else: colour = (255, 0, 0)
                    number_font = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/50))
                    number = number_font.render(str(2**bar), True, colour)
                    game.WIN.blit(number, (x + width*0.35 - number.get_width()/2, self.y + height/2 - number_font.get_height()/2))
                    game.WIN.blit(scrap , (x + width*0.65 - scrap.get_width()/2 , self.y + height/2 - scrap.get_height()/2))

                else:  # all of the locked bars show padlocks
                    game.WIN.blit(padlock, (x + width/2 - padlock.get_width()/2, self.y + height/2 - padlock.get_height()/2))



class Bar(Widget):
    """x, y, width, height are proportional to screen size"""
    def __init__(self,
            x: float,
            y: float,
            width: float,
            height: float,
            value: Callable,
            max_value: Callable,
            colour: Colour,
            outline_width: int = 0,
            outline_colour: Colour = game.BLACK,
            curve: int = 0
        ) -> None:
        super().__init__(x, y)
        self.width = lambda: width * game.WIDTH - outline_width*2
        self.height = lambda: height * game.HEIGHT
        self.original_width = self.width
        self.colour = colour
        self.outline_width = outline_width
        self.outline_colour = outline_colour
        self.curve = curve
        self.value = value
        self.max_value = max_value

    def update(self, new_percent: float) -> None:
        """Updates the percentage of the bar, NOTE: percentage is from 0 to 1"""
        self.width = lambda: (self.original_width()-self.outline_width*2) * min(1, new_percent)

    def draw(self) -> None:
        self.update(self.value() / self.max_value())
        pygame.draw.rect(game.WIN, self.colour,
                        rect=(self.x + self.outline_width, self.y - self.height()/2 + self.outline_width,  # bar position is middle left
                              self.width(), self.height() - self.outline_width*2),

                        border_radius=self.curve-self.outline_width  # - self.outline_width to be the same curve as the inside curve of the outline
                        )

        if self.outline_width:
            pygame.draw.rect(game.WIN, self.outline_colour,
                        rect=(self.x, self.y - self.height()/2,  # bar position is middle left
                              self.original_width(), self.height()),

                        width=self.outline_width,
                        border_radius=self.curve
                        )



class ArmourBar(Bar):
    def __init__(
            self,
            x: float,
            y: float,
            width: float,
            height: float,
            value: Callable,
            max_value: Callable,
            price: int,
            number: int,
            colour: Colour,
            outline_width: int = 0,
            outline_colour: Colour = game.BLACK,
            curve: int = 0
        ) -> None:
        super().__init__(x, y, width, height, value, max_value, colour, outline_width, outline_colour, curve)
        self.number = number
        self.price = price
        self.upgrade_value = None
        self.price_rect = None
        self.button_rect = lambda: (self.x + self.width() + 10, self.y - self.height()/2, 0.1*game.WIDTH, self.height())

    def click(self, mouse: Coord) -> None:
        mx, my = mouse[0], mouse[1]

        # If click on price button
        r = self.button_rect()
        if game.SCRAP_COUNT >= self.price and self.value() != self.max_value() and r[0] <= mx <= r[0]+r[2] and r[1] <= my <= r[1]+r[3]:
            game.SCRAP_COUNT -= self.price
            game.player.armour = self.upgrade_value
            Menu.update()

    def draw(self) -> None:
        self.price_rect = None
        for n in range(self.number):
            # If this bar is the current one to heal
            if not self.price_rect and self.value()/self.max_value()*self.number - n < 1:
                x = self.x + n*(self.width()/self.number)
                width = self.width()/self.number
                if n+1 != self.number: width += self.outline_width

                self.price_rect = (x, self.y - self.height()/2, width, self.height())
                self.upgrade_value = (n+1)/self.number * self.max_value()

            # Draw bar
            width = self.width()/self.number
            if n+1 != self.number: width += self.outline_width
            bar = UIBar(lambda: self.x + n*(self.width()/self.number), lambda: self.y, width, self.height(), self.colour, self.outline_width, self.outline_colour, self.curve, flatten_left=False if n==0 else True, flatten_right=False if n==self.number-1 else True)
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
        number_font = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/30))
        number = number_font.render(str(self.price), True, colour)
        game.WIN.blit(number, (rect[0] + 0.225*rect[2] - number.get_width()/2, self.y + 0.002*game.HEIGHT - number_font.get_height()/2))

        # Draw price scrap image
        scrap_image = pygame.transform.scale_by(images.SCRAP, game.HEIGHT/images.SCRAP.get_height()*0.07)
        game.WIN.blit(scrap_image, (rect[0] + 0.65*rect[2] - scrap_image.get_width()/2, self.y - scrap_image.get_height()/2))



class WorldList(RectWidget):
    """
    0 <= (x, y, width, height, gap) <= 1
    """
    def __init__(self, x: float, y: float, width: float, height: float, gap: int) -> None:
        super().__init__(x, y, width, height)
        self._gap = gap

        self.screen_dimensions = game.WIDTH, game.HEIGHT

        self.scroll_height = 0

        self.sliding = False
        self.world_selected: WorldButton | None = None

        self.init_worlds()

        self.rectangle = Rectangle(x - width/2 - gap, y - height/2 - gap, width + 2*gap, height + 2*gap +  min(2, len(self.list)-1)*(height+gap), (24, 24, 24))

    @property
    def gap(self) -> float:
        return self._gap * game.HEIGHT

    def update_rectangle(self) -> None:
        self.rectangle.height = self._height + 2*self._gap + min(2, len(self.list)-1)*(self._height + self._gap)

    def init_worlds(self) -> None:
        world_dir = game.get_world_dir()
        self.list = [World(name, seed) for name, seed in world_dir]

        self.buttons: list[WorldButton] = []
        for idx, world in enumerate(self.list):
            self.buttons.append(WorldButton(self._x, self._y + idx*(self._height + self._gap), world.name, world.seed, world=world, world_list=self))

    def start_world(self, world: World) -> None:
        Menu.change_page(loading_world)
        game.set_name_to_top_of_world_dir(world.name)
        self.set_world_to_top(world)
        game.load_constants(world.name)
        main.main()

    def set_world_to_top(self, world: World) -> None:
        idx = self.list.index(world)

        del self.list[idx]
        self.list.insert(0, world)

        extra_height = self._height + self._gap
        for button in self.buttons[:idx]:
            button._y += extra_height

        self.buttons.insert(0, self.buttons.pop(idx))
        self.buttons[0]._y = self._y

        self.scroll_height = 0

    def create_world(self, name: str, seed: int) -> World:
        world = World(name, seed)
        self.list.append(world)

        self.update_rectangle()
        self.buttons.append(WorldButton(self._x, self._y, name, seed, world=world, world_list=self))

        return world

    def delete_selected_world(self) -> None:
        name = self.world_selected.text

        for world in self.list:
            if world.name == name:
                self.list.remove(world)
                break

        self.update_rectangle()

        idx = self.buttons.index(self.world_selected)
        del self.buttons[idx]
        for button in self.buttons[idx:]:
            button._y -= self._height + self._gap

        self.world_selected = None
        self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height)  # ensure scroll is within limits

        game.delete_world(name)
        Menu.update()

    def get_total_button_height(self) -> float:
        """Gets the total height that the buttons can scroll"""
        num = min(3, len(self.list))
        total_button_height = num*(self.height + self.gap) - self.gap  # Height of buttons that are shown on screen
        return total_button_height

    def get_scroll_bar_height(self) -> float:
        # Correct
        num = min(3, len(self.list))

        total_button_height = self.get_total_button_height()
        max_button_height = len(self.list)*(self.height + self.gap) - self.gap + (num-1)*(self.height + self.gap)  # length of all the buttons + 2 (i.e.num-1) buttons worth of gap at the bottom

        scroll_bar_height = (total_button_height / max_button_height) * total_button_height  # Ratio of visible button height over total button height, multiplied by available scroll height
        return scroll_bar_height

    def get_max_scroll_height(self) -> float:
        """Gets the total height the scroll bar can scroll"""
        scroll_bar_height = self.get_scroll_bar_height()

        total_button_height = self.get_total_button_height()  # Height of buttons that are shown on screen

        max_scroll_height = total_button_height - scroll_bar_height  # Amount of pixels the scroll bar can move
        return max_scroll_height

    def get_scroll_bar(self) -> Rect:
        scroll_bar_height = self.get_scroll_bar_height()

        return (self.x + self.width/2, self.y - self.height/2 + self.scroll_height, self.gap/2, scroll_bar_height)

    def get_button_scroll_ratio(self) -> float:
        """Returns the ratio of button scroll to scroll bar scroll"""
        total_button_scroll_height = (len(self.list)-1) * (self.height + self.gap)
        total_scroll_height = self.get_max_scroll_height()

        if total_scroll_height:
            ratio = total_button_scroll_height / total_scroll_height
        else:
            ratio = 1

        return -ratio  # Buttons scroll opposite direction to scroll bar

    def button_scroll_height(self) -> float:
        """Returns scroll_bar height converted to scroll height for button"""

        ratio = self.get_button_scroll_ratio()

        return self.scroll_height * ratio

    def click(self, mouse: Coord) -> bool:
        # Click on buttons
        for button in self.buttons:
            rect = (self.x - self.width/2, self.y - 1.5*self.gap, self.width, self.height + min(2, (len(self.list))-1)*(self.height + self.gap))
            if button.click(mouse, rect, self.button_scroll_height()) is True:
                return CLICKED

        # Click on scroll bar
        x, y, width, height = self.get_scroll_bar()
        if mouse[0] > x and mouse[0] < x + width and mouse[1] > y and mouse[1] < y + height:
            self.sliding = True
            self.slider_height = mouse[1] - y

    def mouse_moved(self, mouse: Coord) -> None:
        if self.sliding:

            top_slider = mouse[1] - self.slider_height
            top_list = self.y - self.height/2
            self.scroll_height = top_slider - top_list

            self.scroll_height = max(0, self.scroll_height)
            self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height)

    def scroll(self, y: int) -> None:
        scroll_const = 0.021 * game.HEIGHT
        self.scroll_height += y*scroll_const/self.get_button_scroll_ratio()

        self.scroll_height = max(0, self.scroll_height)  # Player can't scroll up above top button
        self.scroll_height = min(self.get_max_scroll_height(), self.scroll_height)  # Player can't scroll down below bottom button
        Menu.update()

    def resize(self) -> None:
        for button in self.buttons:
            button.update_label_info()

    def draw(self) -> None:
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

        rect = (self.x - self.width/2, self.y - 1.5*self.gap, self.width, self.height + min(2, (len(self.list))-1)*(self.height + self.gap))
        surf = pygame.Surface((rect[2], rect[3]), flags=pygame.SRCALPHA)
        x_offset = -(self.x - self.width/2)
        y_offset = -(self.y - self.height/2) + self.button_scroll_height()

        for button in self.buttons:

            # Make all buttons the same width
            button.padx = (self.width - button.label.get_width())/2

            # Make all buttons the same height
            button.pady = (self.height - button.height)/2

            # Draw button
            button.draw(surf, x_offset, y_offset, rect, self.button_scroll_height())

        game.WIN.blit(surf, (rect[0], rect[1]))



class World():
    def __init__(self, name: str, seed: int) -> None:
        self.name = name
        self.seed = seed



class WorldButton(Button):
    def __init__(self,
            x: float,
            y: float,
            name: str,
            seed: int,
            world: World,
            world_list: WorldList,
            font: str = Menu.DEFAULT_FONT,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            colour: Colour = Menu.DEFAULT_COLOUR,
            padx: int = Menu.DEFAULT_PADX,
            pady: int = Menu.DEFAULT_PADY,
            box_colour: Colour = Menu.DEFAULT_BOX_COLOUR,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            hover_colour: Colour = Menu.DEFAULT_HOVER_COLOUR,
            click_outline_colour: Colour = Menu.DEFAULT_CLICK_OUTLINE_COLOUR
        ) -> None:
        self.seed = str(seed)  # must be before super().__init__ because Button label requires self.seed
        super().__init__(x, y, name, font, font_size, colour, padx, pady, lambda: world_list.start_world(world), box_colour, outline_colour, hover_colour)
        self.click_outline_colour = click_outline_colour

        self.selected = False

    def touching_mouse(self, mouse: Coord, rect: Rect, scroll_height: float) -> bool:
        if mouse[0] < rect[0] or mouse[0] > rect[0] + rect[2] or mouse[1] < rect[1] or mouse[1] > rect[1] + rect[3]:
            return False

        label = self.label
        x, y, width, height = self.get_rect(label)
        x, y = x - self.padx, y - self.pady + scroll_height
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def click(self, mouse: Coord, rect: Rect, scroll_height: float) -> bool:
        if self.touching_mouse(mouse, rect, scroll_height):
            if self.selected:
                self.function()
                return CLICKED  # Tells the Menu that this Button has been clicked on
            else:
                self.selected = True
                world_list.world_selected = self
                Menu.update()
        elif self.selected:
            if world_list.world_selected == self:
                world_list.world_selected = None
            self.selected = False
            Menu.update()

    def update_label_info(self) -> None:
        super().update_label_info()
        seed_font = pygame.font.SysFont(self.font, round(game.WIDTH * 0.6 * self.font_size / 900))  # seed is 60% of the size of world
        self.seed_label = seed_font.render(f"seed: {self.seed}", True, self.colour)
        self.seed_height = seed_font.get_height()

    def draw(self, surf: pygame.Surface, x_offset: float, y_offset: float, rect: Rect, scroll_height: float) -> None:
        # Draw button
        if self.touching_mouse(pygame.mouse.get_pos(), rect, scroll_height):
            self.current_box_colour = self.hover_colour
        else:
            self.current_box_colour = self.box_colour

        outline_colour = self.click_outline_colour if self.selected else self.outline_colour
        label = self.label  # This is updated in when screen is resized
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(surf, self.current_box_colour, (x - self.padx + x_offset, y - self.pady + y_offset, width, height))
        pygame.draw.rect(surf, outline_colour         , (x - self.padx + x_offset, y - self.pady + y_offset, width, height), width=round(game.WIDTH/300))

        # Draw name
        position = self.x - self.get_width(label)*0.45 + x_offset, self.y - self.height/2 + y_offset  # Adjust coordinates to be left of button
        surf.blit(label, position)

        # Draw seed
        seed = self.seed_label  # updated when screen is resized
        position = self.x + self.get_width(label)*0.2 + x_offset, self.y - self.seed_height/2 + y_offset
        surf.blit(seed, position)


class TextInput(RectWidget):
    def __init__(self,
            x: float,
            y: float,
            width: float,
            height: float,
            header: str = "",
            limit: int = 10,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            click_outline_colour: Colour = Menu.DEFAULT_CLICK_OUTLINE_COLOUR
        ) -> None:
        super().__init__(x, y, width, height)
        self.header = header
        self.limit = limit
        self.font_size = font_size
        self.outline_colour = outline_colour
        self.click_outline_colour = click_outline_colour
        self.selected = False
        self.text = ""

    def get_rect(self) -> Rect:
        return self.x - self.width/2, self.y - self.height/2, self.width, self.height

    def touching_mouse(self, mouse: Coord) -> bool:
        x, y, width, height = self.get_rect()
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def click(self, mouse: Coord) -> None:
        if self.touching_mouse(mouse):
            self.selected = True
            Menu.update()
        else:
            self.selected = False

    def key_pressed(self, event: pygame.Event) -> None:
        if self.selected:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isalpha() or event.unicode.isdigit() or event.unicode in "!#£$%&'()+, -.:;<=>@[]^_`{}~":
                if len(self.text) < self.limit:
                    self.text += event.unicode

    def draw(self) -> None:
        # Draw rectangle outline
        if self.selected:
            pygame.draw.rect(game.WIN, self.click_outline_colour, self.get_rect(), width=round(game.WIDTH/300))
        else:
            pygame.draw.rect(game.WIN, self.outline_colour, self.get_rect(), width=round(game.WIDTH/300))

        # Draw header
        font = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900))
        label = font.render(self.header, True, game.WHITE)
        game.WIN.blit(label, (self.x - self.width/2, self.y - self.height/2 - font.get_height()))

        # Draw input text
        font = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900))
        label = font.render(self.text, True, game.WHITE)
        game.WIN.blit(label, (self.x - self.width/2 + round(game.WIDTH/300), self.y - font.get_height()/2))



class NameTextInput(TextInput):
    def __init__(self,
            x: float,
            y: float,
            width: float,
            height: float,
            header: str = "",
            limit: int = 10,
            font_size: int = Menu.DEFAULT_FONT_SIZE,
            outline_colour: Colour = Menu.DEFAULT_OUTLINE_COLOUR,
            click_outline_colour: Colour = Menu.DEFAULT_CLICK_OUTLINE_COLOUR
        ) -> None:
        super().__init__(x, y, width, height, header, limit, font_size, outline_colour, click_outline_colour)
        self.selected = True  # NameInput starts off selected

    def key_pressed(self, event: pygame.Event) -> None:
        super().key_pressed(event)
        label = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH * self.font_size / 900)).render(self.text, True, game.WHITE)
        if label.get_width() > 0.78*self.width:
            self.text = self.text[:-1]



class SeedTextInput(TextInput):
    def key_pressed(self, event: pygame.Event) -> None:
        super().key_pressed(event)
        # Ensure text is just digits
        if self.text and not self.text[-1].isdigit():
            self.text = self.text[:-1]



class Mission():
    def __init__(self, slot: int, class_list: dict[str, int]) -> None:
        self.slot = slot
        self.class_list = class_list

        # Changes x position based on what slot it is in (there are three mission slots)
        self.x = 0.2 + 0.3*self.slot
        self.y = 0.62
        self.width = 0.2
        self.height = 0.4

        self.complete_mission_text = AdjustableText(self.x - self.width/2, self.y + 0.02 - self.height/2, self.width, self.height - 0.32, "Complete the accepted mission to get another one", default_font_size=27)

        self.accept_button = Button(self.x-0.05, self.y+0.13, "Accept", font_size=20, function=self.accept)
        self.decline_button = Button(self.x+0.05, self.y+0.13, "Decline", font_size=20, function=self.decline)
        self.claim_reward_button = Button(self.x, self.y+0.13, "Claim Reward", font_size=25, colour=(255, 182, 36), function=self.claim_reward)

        self.progress_text = Text(self.x, self.y+0.095, text=lambda: f"{game.MISSIONS[self.slot]["current_number"]}/{game.MISSIONS[self.slot]["number"]}", font_size=20)
        self.progress_bar = Bar(self.x-(self.width/2), self.y+0.15, width=self.width, height=self.height/8, value=lambda: game.MISSIONS[self.slot]["current_number"], max_value=lambda: game.MISSIONS[self.slot]["number"], colour=(0, 0, 190), outline_width=3, curve=7)

        self.title_text = Text(self.x, self.y-0.05-self.height/2, "Kill Mission")
        self.info_text = AdjustableText(self.x - self.width/2, self.y + 0.02 - self.height/2, self.width, self.height - 0.32, default_font_size=32)

    @property
    def in_progress(self) -> bool:
        # True if you have clicked accept on a mission
        return game.CURRENT_MISSION_SLOT == self.slot

    def accept(self) -> None:
        if game.CURRENT_MISSION_SLOT != None:
            game.MISSIONS[game.CURRENT_MISSION_SLOT] = None
        game.CURRENT_MISSION_SLOT = self.slot
        Menu.update()

    def decline(self) -> None:
        game.MISSIONS[self.slot] = None

        # If 1 mission left then accept it automatically
        if game.MISSIONS.count(None) == 2:
            for slot, mission in enumerate(game.MISSIONS):
                if mission is not None:
                    game.CURRENT_MISSION_SLOT = slot
                    break

        Menu.update()

    def claim_reward(self) -> None:
        game.CURRENT_MISSION_SLOT = None
        game.SCRAP_COUNT += game.MISSIONS[self.slot]["reward"]
        self.refresh(self.slot)
        for slot, mission in enumerate(game.MISSIONS):
            if mission is None:
                self.refresh(slot)
        Menu.update()

    def click(self, mouse: Coord) -> bool:
        # Making sure button functions are run when clicked
        if self.in_progress:
            data = game.MISSIONS[self.slot]
            if data["current_number"] >= data["number"]:
                if self.claim_reward_button.click(mouse) is True: return CLICKED
        else:
            if self.accept_button.click(mouse) is True: return CLICKED
            if self.decline_button.click(mouse) is True: return CLICKED

    def get_enemy(self) -> str:
        class_list = list(self.class_list)
        if game.CURRENT_SHIP_LEVEL < 10:
            class_list.remove("Missile_Ship")

        return random.choice(class_list)

    def refresh(self, slot: int) -> None:
        # number = number of things for the mission
        # goal = Target for the mission (e.g. Mother_Ship)
        # mission_type = what type of mission it is (e.g. kill mission)
        # reward = number of scrap claimed after completion

        number = random.randint(5, 15)
        goal = self.get_enemy()
        mission_type = game.KILL
        reward = number * (1+game.CURRENT_SHIP_LEVEL)**0.5 * self.class_list[goal]  # reward depends on number, difficulty and type of enemy
        reward *= 0.9 + random.random()*0.2  # reward +- 10% to make it look a bit random

        game.MISSIONS[slot] = {
            "current_number": 0,
            "number": number,
            "goal": goal,
            "mission_type": mission_type,
            "reward": round(reward)
        }

    def draw(self) -> None:
        if game.MISSIONS[self.slot] is None:
            self.complete_mission_text.draw()
            return

        # Drawing title and info
        self.title_text.draw()

        data = game.MISSIONS[self.slot]
        self.info_text.change_text(f"Kill {data["number"]} {game.ENTITY_DICT.get(data["goal"])}s REWARD: {data["reward"]} Scrap")
        self.info_text.draw()

        # Draw the image for the goal
        image = game.ENTITY_IMAGE_DICT[data["goal"]]
        game.WIN.blit(image, (self.x * game.WIDTH - image.get_width()/2 - self.width/2, self.y * game.HEIGHT - image.get_height()/2))

        # If the mission is in progress - draw the progress bar and stop drawing the accept and decline button. Once the mission is done, it draws the claim reward button
        if self.in_progress:
            data = game.MISSIONS[self.slot]
            if data["current_number"] >= data["number"]:
                self.claim_reward_button.draw()
            else:
                self.progress_bar.draw()
                self.progress_text.draw()

        else:
            self.accept_button.draw()
            self.decline_button.draw()



class MissionManager():
    def __init__(self) -> None:
        class_list = {
            "Drone_Enemy": 1,
            "Enemy_Ship": 1,
            "Mother_Ship": 2,
            "Missile_Ship": 2
        }

        self.missions = [Mission(i, class_list) for i in range(3)]

    def click(self, mouse: Coord) -> bool:
        for mission in self.missions:
            if mission.click(mouse) is True:
                return CLICKED

    def draw(self) -> None:
        if game.MISSIONS == [None, None, None]:  # First time world is created
            game.MISSIONS = [None for _ in range(3)]
            for mission in self.missions:
                mission.refresh(mission.slot)

        for mission in self.missions:
            mission.draw()



class Graveyard():
    def __init__(self, y: int) -> None:
        self.y = y
        self.text = Text(0.5, y-0.02, "Graveyard", font_size=30, colour=(120, 120, 120))

    def draw(self) -> None:
        self.text.draw()

        # Draw a small image of each of the ships killed
        for num, load_image in enumerate(game.KILLED_SHIP_IMAGES):
            image = load_image()
            game.WIN.blit(pygame.transform.rotate(image, num * 200), (game.WIDTH/2 - 320 + (num % 30) * 20, self.y * game.HEIGHT + 60 - (num % 3) * 30 - num//30 * 68))

        # Draw a container for ships
        pygame.draw.rect(game.WIN, game.BLACK, (game.WIDTH/2 - 325, self.y * game.HEIGHT - 150, 650, 280), width=10)




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
    Text(0.95, 0.95, "a1.5.2", font_size=20),
    escape=lambda: Menu.change_page(quit_confirm)
)

info = Page(
    Text(0.5, 0.1,   "CREDITS"          , font_size=40),
    Text(0.5, 0.17  , """Rex Attwood
                        Gabriel Correia""", font_size=20),
    Text(0.5, 0.24 ,   "Fred"             , font_size=5),
    Text(0.5, 0.3 ,   "CONTROLS"         , font_size=40),
    Text(0.5, 0.37 , """Change Settings: Up, Down, Drag
                        Pause: Esc
                        Movement: W, A, S, D
                        Boost: Space
                        Systems: TAB
                        Station: E
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
    SettingButton(0.25, 3/6, lambda: f"RENDER: {"AGGRESSIVE" if game.ENTITY_CULLING else "PASSIVE"}", font_size=40, value="ENTITY_CULLING", function_action=lambda: game.save_settings()),
    Button(0.5, 7/8, "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
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
    escape=lambda: EXIT,
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
    Text(0.5, 0.45, "Coming soon in version b1.0!"),
    Button(0.5, 0.875, "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
    escape=lambda: Menu.change_page(main_menu)
)

new_world = Page(
    NameTextInput(0.5, 0.3, 0.5, 0.1, "Name", limit=20),
    SeedTextInput(0.5, 0.53, 0.5, 0.1, "Seed", limit=6),
    Button(0.5, 0.752, "Create World", function=lambda: create_world()),
    Button(0.5, 0.875, "Back", font_size=40, function=lambda: Menu.change_page(single_player)),
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
    Text(0.5, 0.12, "Station"),
    Button(0.12, 0.86, "Exit", function=lambda: EXIT, font_size=30),
    Button(0.27, 0.23, "Missions", function=lambda: Menu.change_page(missions), uniform=True),
    Button(0.5, 0.23, "Upgrades", function=lambda: Menu.change_page(station), outline_colour=(255, 125, 0), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), uniform=True),
    Button(0.2, 0.7, "Armour", function=lambda: Menu.change_page(armour)),
    Button(0.4, 0.7, "Weapon", function=lambda: Menu.change_page(blaster_gun)),
    Button(0.6, 0.7, "Engine", function=lambda: Menu.change_page(engine)),
    Button(0.8, 0.7, "Radar" , function=lambda: Menu.change_page(radar)),
    Image(0.2, 0.5, images.ARMOUR_ICON, scale=6),
    Image(0.4, 0.5, images.WEAPON_ICON, scale=6),
    Image(0.6, 0.5, images.ENGINE_ICON, scale=6),
    Image(0.8, 0.5, images.RADAR_ICON, scale=6),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: EXIT,
    e_press=lambda: EXIT
)

missions = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Station"),
    Button(0.12, 0.86, "Exit", function=lambda: EXIT, font_size=30),
    Button(0.27, 0.23, "Missions", function=lambda: Menu.change_page(missions), outline_colour=(255, 125, 0), uniform=True),
    Button(0.5, 0.23, "Upgrades", function=lambda: Menu.change_page(station), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), uniform=True),
    MissionManager(),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: EXIT,
    e_press=lambda: EXIT
)

stats = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Station"),
    Button(0.12, 0.86, "Exit", function=lambda: EXIT, font_size=30),
    Button(0.27, 0.23, "Missions", function=lambda: Menu.change_page(missions), uniform=True),
    Button(0.5, 0.23, "Upgrades", function=lambda: Menu.change_page(station), uniform=True),
    Button(0.73, 0.23, "Stats", function=lambda: Menu.change_page(stats), outline_colour=(255, 125, 0), uniform=True),
    Text(0.5, 0.45, lambda: f"Skill level: {stats_skill_levels[min(10, int(game.SCORE/50))].upper()}"),
    Graveyard(0.7),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: EXIT,
    e_press=lambda: EXIT
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
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    UpgradeBar(0.3, "Health", "MAX_PLAYER_HEALTH", min_value=game.MAX_PLAYER_HEALTH, max_value=100),
    UpgradeBar(0.4, "Shield", "MAX_PLAYER_SHIELD", min_value=game.MAX_PLAYER_SHIELD, max_value=25),
    UpgradeBar(0.5, "Recharge", "PLAYER_SHIELD_RECHARGE", min_value=game.PLAYER_SHIELD_RECHARGE, max_value=3),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

engine = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Engine"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    UpgradeBar(0.3, "Acceleration", "PLAYER_ACCELERATION", min_value=game.PLAYER_ACCELERATION, max_value=1500),
    UpgradeBar(0.4, "Max Speed", "MAX_PLAYER_SPEED", min_value=game.MIN_PLAYER_SPEED, max_value=1000),
    UpgradeBar(0.5, "Max Boost", "MAX_BOOST_AMOUNT", min_value=20, max_value=50),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

radar = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Radar"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    UpgradeBar(0.3, "Item Magnet", "PICKUP_DISTANCE", min_value=game.PICKUP_DISTANCE, max_value=300),
    UpgradeBar(0.4, "Max Zoom", "CURRENT_MIN_ZOOM", min_value=game.CURRENT_MIN_ZOOM, max_value=game.MIN_ZOOM),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

blaster_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Weapon"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    Button(0.2, 0.3, "Blaster", function=lambda: Menu.change_page(blaster_gun), outline_colour=(255, 125, 0), uniform=True),
    Button(0.2, 0.42, "Gatling", function=lambda: Menu.change_page(gatling_gun), uniform=True),
    Button(0.2, 0.54, "Sniper" , function=lambda: Menu.change_page(sniper_gun), uniform=True),
    Button(0.2, 0.66, "Laser"  , function=lambda: Menu.change_page(laser), uniform=True),
    UpgradeBar(0.35, "Fire Rate", "PLAYER_BLASTER_FIRE_RATE", x=0.32, min_value=game.PLAYER_BLASTER_FIRE_RATE, max_value=20),
    UpgradeBar(0.45, "Damage", "PLAYER_BLASTER_DAMAGE", x=0.32, min_value=game.PLAYER_BLASTER_DAMAGE, max_value=2),
    UpgradeBar(0.55, "Bullet Speed", "PLAYER_BLASTER_BULLET_SPEED", x=0.32, min_value=game.PLAYER_BLASTER_BULLET_SPEED, max_value=1000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

gatling_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Weapon"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    Button(0.2, 0.3, "Blaster", function=lambda: Menu.change_page(blaster_gun), uniform=True),
    Button(0.2, 0.42, "Gatling", function=lambda: Menu.change_page(gatling_gun), outline_colour=(255, 125, 0), uniform=True),
    Button(0.2, 0.54, "Sniper" , function=lambda: Menu.change_page(sniper_gun), uniform=True),
    Button(0.2, 0.66, "Laser"  , function=lambda: Menu.change_page(laser), uniform=True),
    UpgradeBar(0.35, "Fire Rate", "PLAYER_GATLING_FIRE_RATE", x=0.32, min_value=game.PLAYER_GATLING_FIRE_RATE, max_value=40),
    UpgradeBar(0.45, "Damage", "PLAYER_GATLING_DAMAGE", x=0.32, min_value=game.PLAYER_GATLING_DAMAGE, max_value=1),
    UpgradeBar(0.55, "Bullet Speed", "PLAYER_GATLING_BULLET_SPEED", x=0.32, min_value=game.PLAYER_GATLING_BULLET_SPEED, max_value=1000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

sniper_gun = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Weapon"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    Button(0.2, 0.3, "Blaster", function=lambda: Menu.change_page(blaster_gun), uniform=True),
    Button(0.2, 0.42, "Gatling", function=lambda: Menu.change_page(gatling_gun), uniform=True),
    Button(0.2, 0.54, "Sniper" , function=lambda: Menu.change_page(sniper_gun), outline_colour=(255, 125, 0), uniform=True),
    Button(0.2, 0.66, "Laser"  , function=lambda: Menu.change_page(laser), uniform=True),
    UpgradeBar(0.35, "Fire Rate", "PLAYER_SNIPER_FIRE_RATE", x=0.32, min_value=game.PLAYER_SNIPER_FIRE_RATE, max_value=5),
    UpgradeBar(0.45, "Damage", "PLAYER_SNIPER_DAMAGE", x=0.32, min_value=game.PLAYER_SNIPER_DAMAGE, max_value=5),
    UpgradeBar(0.55, "Bullet Speed", "PLAYER_SNIPER_BULLET_SPEED", x=0.32, min_value=game.PLAYER_SNIPER_BULLET_SPEED, max_value=2000),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

laser = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Weapon"),
    Button(0.12, 0.86, "Back", function=lambda: Menu.change_page(station), font_size=30),
    Button(0.2, 0.3, "Blaster", function=lambda: Menu.change_page(blaster_gun), uniform=True),
    Button(0.2, 0.42, "Gatling", function=lambda: Menu.change_page(gatling_gun), uniform=True),
    Button(0.2, 0.54, "Sniper" , function=lambda: Menu.change_page(sniper_gun), uniform=True),
    Button(0.2, 0.66, "Laser"  , function=lambda: Menu.change_page(laser), outline_colour=(255, 125, 0), uniform=True),
    UpgradeBar(0.4, "Range" , "PLAYER_LASER_RANGE", x=0.32, min_value=game.PLAYER_LASER_RANGE, max_value=600),
    UpgradeBar(0.5, "Damage", "PLAYER_LASER_DAMAGE", x=0.32, min_value=game.PLAYER_LASER_DAMAGE, max_value=20),
    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(station),
    e_press=lambda: EXIT
)

systems = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Systems"),
    Button(0.12, 0.86, "Exit", function=lambda: EXIT, font_size=30),

    Text(0.3, 0.3, "Health", font_size=25),
    Bar(0.39, 0.298, width=0.32, height=0.1, value=lambda: game.player.health, max_value=lambda: game.MAX_PLAYER_HEALTH, colour=(255, 0, 0), outline_width=5, curve=12),
    Text(0.405, 0.3, lambda: f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", font_size=25, align=pygame.FONT_LEFT),

    Text(0.3, 0.45, "Armour", font_size=25),
    ArmourBar(0.39, 0.448, width=0.32, height=0.1, value=lambda: game.player.armour, max_value=lambda: game.MAX_PLAYER_ARMOUR, price=3, number=3, colour=(185, 185, 185), outline_width=5, curve=12),
    Text(0.405, 0.45, lambda: f"{round(game.player.armour)} | {game.MAX_PLAYER_ARMOUR}", font_size=25, align=pygame.FONT_LEFT),

    Text(0.3, 0.6, "Shield", font_size=25),
    Bar(0.39, 0.598, width=0.32, height=0.1, value=lambda: game.player.shield, max_value=lambda: game.MAX_PLAYER_SHIELD, colour=(34, 130, 240), outline_width=5, curve=12),
    Text(0.405, 0.6, lambda: f"{round(game.player.shield)} | {game.MAX_PLAYER_SHIELD}", font_size=25, align=pygame.FONT_LEFT),

    Text(0.875, 0.12, lambda: f"{game.SCRAP_COUNT}", align=pygame.FONT_RIGHT),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: EXIT,
    tab_press=lambda: EXIT
)

death_screen = Page(
    Text(0.5, 0.25, "YOU DIED!", colour=(255, 0, 0), font_size=40),
    Text(0.5, 0.4, lambda: f"SCORE: {game.SCORE}", colour=(100, 100, 255), font_size=40),
    Button(0.5, 0.6, "Respawn", font_size=40, function=lambda: main.main()),
    Button(0.5, 0.75, "Main Menu", font_size=40, function=lambda: exit_game())
)



#################
### Functions ###
#################

def get_widget(name: str, page: Page | None = None) -> Widget | None:
    if not page: page = Menu.current_page
    for widget in page.widgets:
        if widget.__name__ == name:
            return widget

def create_world() -> None:
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
    else:
        seed = int(seed)

    game.reset_constants()
    game.NAME = name
    game.SEED = seed
    game.init_chunks()
    game.player = get_player()
    game.save_constants(name)

    game.update_world_dir(name, seed)

    world = world_list.create_world(name, seed)

    world_list.start_world(world)

def exit_game() -> None:
    Menu.change_page(saving_world)

    # Save current game
    game.save_constants(game.NAME)

    Menu.change_page(main_menu)

def page_click() -> None:
    """If there is a selected widget that shouldn't be, un-select it"""
    mouse = pygame.mouse.get_pos()
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected") and widget.selected and not widget.touching_mouse(mouse):  # if widget should be un-selected
            widget.selected = False
            if isinstance(widget, SettingButton): widget.outline_colour = widget.original_outline_colour
            Menu.update()
            break

def settings_up() -> None:
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected"):
            if widget.selected:
                widget.up()

def settings_down() -> None:
    for widget in Menu.current_page.widgets:
        if hasattr(widget, "selected"):
            if widget.selected:
                widget.down()

def change_fullscreen() -> None:
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

def make_windowed() -> None:
    game.FULLSCREEN = False
    pygame.display.set_mode((game.WIDTH, game.HEIGHT), flags=pygame.RESIZABLE)
    game.save_settings()

def repair_armour() -> None:
    if game.SCRAP_COUNT < 5:
        return
    else:
        game.SCRAP_COUNT -= 5
        game.player.armour += 5

        if game.player.armour > game.MAX_PLAYER_ARMOUR:
            game.player.armour = game.MAX_PLAYER_ARMOUR
