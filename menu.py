import pygame
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
    DEFAULT_CLICK_OUTLINE_COLOUR = (180, 180, 180)
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

            elif event.type == pygame.KEYDOWN and event.__dict__["key"] == pygame.K_ESCAPE:
                # runs Menu.escape_pressed, if that returns True, then follow suit and return True
                if Menu.escape_pressed():
                    return True

            elif event.type == pygame.KEYDOWN:

                if event.__dict__["key"] == pygame.K_UP:
                    Menu.up_pressed()

                elif event.__dict__["key"] == pygame.K_DOWN:
                    Menu.down_pressed()

                elif event.__dict__["key"] == pygame.K_e:
                    # if e_pressed return True, then go back to the game
                    if Menu.e_pressed():
                        return True

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
        """Go through all Page Widgets, if the Widget is a SettingButton then check if slider should be moved"""
        for widget in Menu.current_page.widgets:
            if isinstance(widget, SettingButton):
                widget.mouse_moved(mouse) # moves slider if need be

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
       x, y can be float or int
       if (x, y) is a float (e.g. 0.5 = 50%), the element's location is that percentage of the screen
       if (x, y) is an int (e.g. 100 or -200), the element is placed that many pixels from the edge, negative pixels are placed from the right
       x, y is the centre of the Widget
    """
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

        # pos is - width/2 to centre the object, objects are drawn from the top left coord
        # NOTE: get_position_x and get_position_y return the top left part of the Widget
        if type(self.x) == float:
            self.get_position_x = lambda self: self.x * game.WIDTH

        elif type(self.x) == int:
            if self.x < 0:
                self.get_position_x = lambda self: game.WIDTH + self.x
            else:
                self.get_position_x = lambda self: self.x
        
        if type(self.y) == float:
            self.get_position_y = lambda self: self.y * game.HEIGHT

        elif type(self.y) == int:
            if self.y < 0:
                self.get_position_y = lambda self: game.HEIGHT + self.y
            else:
                self.get_position_y = lambda self: self.y



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
        game.WIN.blit(image, (self.get_position_x(self) - image.get_width()/2, self.get_position_y(self) - image.get_height()/2))



class Text(Widget):
    """Text can be single of multi-line
       x, y is the centre of the first line of the Text
       font size is relative to screen width, if you change the screen resolution then the font size will dynamically change
       text can be a string or a function, if it's a function then that will be called, e.g. text=lambda f"SCORE: {game.SCORE}"
       if text is a function it has to return a string (can be single or multi-line)
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR) -> None:
        super().__init__(x, y)

        if type(self.x) == float:
            self.get_position_x = lambda self, label: self.x * game.WIDTH - label.get_width()/2

        elif type(self.x) == int:
            if self.x < 0:
                self.get_position_x = lambda self, label: game.WIDTH + self.x - label.get_width()/2
            else:
                self.get_position_x = lambda self, label: self.x - label.get_width()/2
        
        if type(self.y) == float:
            self.get_position_y = lambda self, label: self.y * game.HEIGHT - label.get_height()/2

        elif type(self.y) == int:
            if self.y < 0:
                self.get_position_y = lambda self, label: game.HEIGHT + self.y - label.get_height()/2
            else:
                self.get_position_y = lambda self, label: self.y - label.get_height()/2

        if isinstance(text, str):
            self.text = [sentence.lstrip() for sentence in text.split("\n")]
        else: # if text is a function
            self.text = text

        self.font = font
        self.font_size = font_size
        self.colour = colour

    def get_labels(self):
        """Creates a list of label for every sentence of the text"""
        font = pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900))

        if isinstance(self.text, list):
            labels = [font.render(sentence, True, self.colour) for sentence in self.text]
        else: # if text is a function
            if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
                text = self.text()
                labels = [font.render(sentence.lstrip(), True, self.colour) for sentence in text.split("\n")] # split sentence up into lines, then turn each line into a label

        return labels

    def draw(self):
        labels = self.get_labels()
        cum_height = 0 # cumulative height of all the labels above a certain label
        for label in labels:
            position = self.get_position_x(self, label), self.get_position_y(self, label) + cum_height # Adjust coordinates to be centre of Widget
            cum_height += label.get_height()
            game.WIN.blit(label, position)



class Button(Text):
    """A Widget that can be clicked on
       When a Button is clicked, the "function" method is called
       padx, pady is the padding, i.e. how much the button extends past the text, i.e. padx=1 means 1 pixel on the left AND 1 pixel on the right
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR, padx=Menu.DEFAULT_PADX, pady=Menu.DEFAULT_PADY, function=None, box_colour=Menu.DEFAULT_BOX_COLOUR, outline_colour=Menu.DEFAULT_OUTLINE_COLOUR, hover_colour=Menu.DEFAULT_HOVER_COLOUR) -> None:
        super().__init__(x, y, text, font, font_size, colour)
        self.padx = padx
        self.pady = pady
        self.function = function
        self.box_colour = box_colour
        self.current_box_colour = box_colour
        if not outline_colour: outline_colour = box_colour
        self.outline_colour = outline_colour
        self.hover_colour = hover_colour
        self.label = self.get_label() # Called at the start of Page.draw, use self.label instead of self.get_label for performance

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
        x, y = self.get_position_x(self, label), self.get_position_y(self, label)
        return x, y, width, height#

    def get_label(self):
        """For buttons which currently only use the first line of text to create the button"""
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = self.text()
        else:
            text = self.text[0]

        return pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900)).render(text, True, self.colour)

    def draw(self):
        if self.touching_mouse(pygame.mouse.get_pos()):
            self.current_box_colour = self.hover_colour
        else:
            self.current_box_colour = self.box_colour

        label = self.label # This is updated in Page.draw()
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(game.WIN, self.current_box_colour, (x - self.padx, y - self.pady, width, height))
        pygame.draw.rect(game.WIN, self.outline_colour    , (x - self.padx, y - self.pady, width, height), width=round(game.WIDTH/300))
        position = self.get_position_x(self, label), self.get_position_y(self, label) # Adjust coordinates to be centre of Widget
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

    def get_label(self):
        return pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900)).render(self.text(), True, self.colour)

    def get_max_width(self):
        """Get greatest width of all SettingButtons on the current_page"""

        max_width = 0
        for widget in Menu.current_page.widgets:
            if isinstance(widget, SettingButton):
                if widget.get_width(widget.label) > max_width:
                    max_width = widget.get_width(widget.label)
        return max_width

    def get_rect(self, label):
        """If self.uniform == True, set the width to the greatest width of all SettingButtons on the current_page"""
        if self.uniform:
            width, height = self.get_max_width(), self.get_height(label)
            width_difference = width - self.get_width(label)
            x, y = self.get_position_x(self, label) - width_difference/2, self.get_position_y(self, label)
            return x, y, width, height

        width, height = self.get_width(label), self.get_height(label)
        x, y = self.get_position_x(self, label), self.get_position_y(self, label)
        return x, y, width, height

    def draw(self):
        super().draw()
        # If this is an integer setting, then automatically make it a slider
        if type(self.get_value()) == int:
            x, y, width, height = self.get_slider()
            surf = pygame.Surface((width, height), flags=pygame.SRCALPHA)
            pygame.draw.rect(surf, Menu.SLIDER_COLOUR, (0, 0, width, height))
            pygame.draw.rect(surf, Menu.SLIDER_OUTLINE, (0, 0, width, height), width=round(game.WIDTH/300))
            game.WIN.blit(surf, (x, y))



class Rectangle(Widget):
    """A rectangular object of given width, height and colour
       x, y can be ints (percentage) or floats (pixel)
       width, height can be int or float, int for pixel, float for ratio of screen size"""
    def __init__(self, x, y, width, height, colour, curve=0) -> None:
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.colour = colour
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
        pygame.draw.rect(game.WIN, self.colour, (self.get_position_x(self), self.get_position_y(self), self.get_width(self), self.get_height(self)), border_radius=self.curve)



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
        self.level = 0
        self.padlock = images.PADLOCK

    def get_value(self):
        return getattr(game, self.value)

    def set_value(self, value):
        setattr(game, self.value, value)

    def click(self, mouse):
        mx, my = mouse[0], mouse[1]

        # check if text bar is clicked on
        x = self.get_position_x(self)
        y = self.get_position_y(self)
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
            x = self.get_position_x(self) + bar * (width + self.gap) + button_width + self.gap
            y = self.get_position_y(self)

            # if clicked on
            if mx > x and mx < x + width and my > y and my < y + height:
                
                # if bar is less than level then switch to that level
                if bar < self.level:
                    self.set_value(self.min_value + (bar+1) * self.step)
                    Menu.update()

                # if bar is the next level, upgrade to that level
                elif bar == self.level and game.SCRAP_COUNT >= bar+1:
                    game.SCRAP_COUNT -= bar+1
                    self.level += 1
                    self.set_value(self.min_value + self.level * self.step)
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
            Rectangle(int(self.get_position_x(self)), int(self.get_position_y(self)), button_width, height, self.select_outline_colour, curve=10).draw()
        else:
            Rectangle(int(self.get_position_x(self)), int(self.get_position_y(self)), button_width, height, self.outline_colour, curve=10).draw()

        Rectangle(int(self.get_position_x(self)+2), int(self.get_position_y(self)+2), button_width-4, height-4, self.button_colour, curve=10).draw()
        label = self.get_label()
        game.WIN.blit(label, (self.get_position_x(self) + button_width/2 - label.get_width()/2, self.get_position_y(self) + height/2 - label.get_height()/2))


        # draw bars
        for bar in range(self.bars):

            x = self.get_position_x(self) + bar * (width + self.gap) + button_width + self.gap

            # draw bar outline
            if self.get_value() == (bar+1) * self.step + self.min_value: # if selected choose a different outline colour
                Rectangle(int(x), int(self.get_position_y(self)), width, height, self.select_outline_colour, curve=10).draw()
            else:
                Rectangle(int(x), int(self.get_position_y(self)), width, height, self.outline_colour, curve=10).draw()

            # fill in bar if neseccary, bar+1 so that the first bar is level 1
            if bar+1 <= self.level:

                if self.get_value() == (bar+1) * self.step + self.min_value: # if selected choose a different colour
                    Rectangle(int(x+2), int(self.get_position_y(self)+2), width-4, height-4, self.select_colour, curve=10).draw()

                else: # fill in with regular colour
                    Rectangle(int(x+2), int(self.get_position_y(self)+2), width-4, height-4, self.bar_colour, curve=10).draw()

            else: # fill in with background colour
                Rectangle(int(x+2), int(self.get_position_y(self)+2), width-4, height-4, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10).draw()

                if bar == self.level: # the first locked bar shows a price instead of a padlock
                    if game.SCRAP_COUNT >= bar+1: colour = Menu.DEFAULT_COLOUR
                    else: colour = (255, 0, 0)
                    number = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/50)).render(str(bar+1), True, colour)
                    game.WIN.blit(number, (x + width*0.3 - number.get_width()/2, self.get_position_y(self) + height/2 - number.get_height()/2))
                    game.WIN.blit(scrap , (x + width*0.7 - scrap.get_width()/2 , self.get_position_y(self) + height/2 - scrap.get_height()/2))

                else: # all of the locked bars show padlocks
                    game.WIN.blit(padlock, (x + width/2 - padlock.get_width()/2, self.get_position_y(self) + height/2 - padlock.get_height()/2))



class Bar(UIBar):
    def __init__(self, x, y, width, height, value, max_value, colour, outline_width=0, outline_colour=game.BLACK, curve=0, flatten_left=False, flatten_right=False) -> None:
        super().__init__(x, y, width, height, colour, outline_width, outline_colour, curve, flatten_left, flatten_right)
        self.x = lambda: x * game.WIDTH
        self.y = lambda: y * game.HEIGHT
        self.value = value
        self.max_value = max_value

    def draw(self):
        super().update(self.value() / self.max_value())
        super().draw()



class ArmourBar(Bar):
    def __init__(self, x, y, width, height, value, max_value, price, number, colour, outline_width=0, outline_colour=game.BLACK, curve=0, flatten_left=False, flatten_right=False) -> None:
        super().__init__(x, y, width, height, value, max_value, colour, outline_width, outline_colour, curve, flatten_left, flatten_right)
        self.number = number
        self.price = price
        self.upgrade_value = None
        self.price_rect = None
        self.button_rect = (self.x() + self.width + 5, self.y()-self.height/2, 120, self.height)

    def draw(self):
        self.price_rect = None
        for n in range(self.number):
            # If this bar is the current one to heal
            if not self.price_rect and self.value()/self.max_value()*self.number - n < 1:
                x = self.x()+n*(self.width/self.number-self.outline_width)
                width = self.width/self.number

                self.price_rect = (x, self.y()-self.height/2, width, self.height)
                self.upgrade_value = (n+1)/self.number * self.max_value()

            # Draw bar
            bar = UIBar(lambda: self.x()+n*(self.width/self.number-self.outline_width), self.y, self.width/self.number, self.height, self.colour, self.outline_width, self.outline_colour, self.left_curve, flatten_left=False if n==0 else True, flatten_right=False if n==self.number-1 else True)
            bar.update(max(0, min(1, self.value()/self.max_value()*self.number - n)))
            bar.draw()

        # Draw price button
        x = self.x() + self.width + 33

        # Highlight button if hovered
        mx, my = pygame.mouse.get_pos()
        r = self.button_rect
        if r[0] <= mx <= r[0]+r[2] and r[1] <= my <= r[1]+r[3]:
            pygame.draw.rect(game.WIN, self.colour, self.button_rect, border_radius=self.left_curve)

        pygame.draw.rect(game.WIN, game.BLACK, self.button_rect, width=self.outline_width, border_radius=self.left_curve)

        if game.SCRAP_COUNT >= self.price: colour = Menu.DEFAULT_COLOUR
        else: colour = (255, 0, 0)
        number = pygame.font.SysFont(Menu.DEFAULT_FONT, round(game.WIDTH/30)).render(str(self.price), True, colour)
        game.WIN.blit(number, (x - number.get_width()/2, self.y() - number.get_height()/2))

        scrap_image = pygame.transform.scale_by(images.SCRAP, 1.8)
        game.WIN.blit(scrap_image, (x + 52 - scrap_image.get_width()/2, self.y()-scrap_image.get_height()/2))

    def click(self, mouse):
        mx, my = mouse[0], mouse[1]

        # If click on price button
        r = self.button_rect
        if game.SCRAP_COUNT >= self.price and r[0] <= mx <= r[0]+r[2] and r[1] <= my <= r[1]+r[3]:
            game.SCRAP_COUNT -= self.price
            game.player.armour = self.upgrade_value
            Menu.update()




# FRAMEWORK
########################################################################################################################################################
# PAGES




main_menu = Page(
    Image(0.5, 3/16, images.ASTRO_ATTACK_LOGO),
    Button(0.5, 3/8, "Single Player", font_size=40, function=lambda: main.main()),
    Button(0.5, 4/8, "Multiplayer"  , font_size=40, function=lambda: main.main()),
    Button(0.5, 5/8, "Settings"     , font_size=40, function=lambda: Menu.change_page(settings)),
    Button(0.5, 6/8, "Info"         , font_size=40, function=lambda: Menu.change_page(info)),
    Button(0.5, 7/8, "Quit"         , font_size=40, function=game.quit)
)

info = Page(
    Text(0.5, 0.125,   "CREDITS"          , font_size=40),
    Text(0.5, 0.2  , """Rex Attwood
                        Gabriel Correia""", font_size=20),
    Text(0.5, 0.27 ,   "Fred"             , font_size=5),
    Text(0.5, 0.35 ,   "CONTROLS"         , font_size=40),
    Text(0.5, 0.43 , """Change Settings: Up, Down, Drag
                        Pause: Esc
                        Movement: W, A, S, D
                        Boost: Space
                        Systems: E
                        Look: Mouse
                        Zoom: Scroll
                        Shoot: Left Click
                        Target: Right Click
                        Change Weapon: 1, 2, 3, 4""", font_size=20),
    Button(0.5, 5/6,   "MAIN MENU"        , font_size=40, function=lambda: Menu.change_page(main_menu)),
    escape=lambda: Menu.change_page(main_menu)
)

settings = Page(
    SettingButton(0.25, 1/6, lambda: f"SCREEN WIDTH: {game.WIDTH}"         , font_size=40, value="WIDTH"        , function_action=lambda: make_windowed(), min=192, max=game.FULLSCREEN_SIZE[0]),
    SettingButton(0.75, 1/6, lambda: f"SCREEN HEIGHT: {game.HEIGHT}"       , font_size=40, value="HEIGHT"       , function_action=lambda: make_windowed(), min=108, max=game.FULLSCREEN_SIZE[1]),
    SettingButton(0.25, 2/6, lambda: f"FULL SCREEN: {game.FULLSCREEN}"     , font_size=40, value="FULLSCREEN"   , function_action=lambda: change_fullscreen()),
    SettingButton(0.75, 2/6, lambda: f"SIZE LINK: {game.SIZE_LINK}"        , font_size=40, value="SIZE_LINK"    , function_action=None),
    SettingButton(0.25, 3/6, lambda: f"BULLET SPEED: {game.BULLET_SPEED}"  , font_size=40, value="BULLET_SPEED" , function_action=None, min=10, max=1000),
    SettingButton(0.75, 3/6, lambda: f"LOAD DISTANCE: {game.LOAD_DISTANCE}", font_size=40, value="LOAD_DISTANCE", function_action=None, min=4, max=26),
    Button(0.5, 5/6, "MAIN MENU" , font_size=40, function=lambda: Menu.change_page(main_menu)),
    click=lambda: settings_click(),
    escape=lambda: Menu.change_page(main_menu),
    up=lambda: settings_up(),
    down=lambda: settings_down()
)

pause = Page(
    Image( 0.5, 0.245, images.ASTRO_ATTACK_LOGO, scale=0.6),
    Button(0.5, 0.345, "Continue", font_size=40, function=lambda: setattr(Menu, "running", False)),
    Button(0.5, 0.46, "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
    background_colour=None,
    escape=lambda: True,
)

station = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Station"),
    Button(0.3, 0.43, "Armour", function=lambda: Menu.change_page(armour)),
    Button(0.7, 0.43, "Weapon", function=lambda: Menu.change_page(weapon)),
    Button(0.3, 0.8, "Engine", function=lambda: Menu.change_page(engine)),
    Button(0.7, 0.8, "Radar" , function=lambda: Menu.change_page(radar)),
    Image(0.3, 0.26, images.ARMOUR_ICON, scale=6),
    Image(0.7, 0.28, images.WEAPON_ICON, scale=6),
    Image(0.3, 0.635, images.ENGINE_ICON, scale=6),
    Image(0.7, 0.62, images.RADAR_ICON, scale=6),
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

armour = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Armour"),
    UpgradeBar(0.19, 0.3, "Health", "MAX_PLAYER_HEALTH", min_value=game.MAX_PLAYER_HEALTH, max_value=100),
    UpgradeBar(0.19, 0.4, "Shield", "MAX_PLAYER_SHIELD", min_value=game.MAX_PLAYER_SHIELD, max_value=20),
    UpgradeBar(0.19, 0.5, "Recharge", "PLAYER_SHIELD_RECHARGE", min_value=game.PLAYER_SHIELD_RECHARGE, max_value=3),
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
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
    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: Menu.change_page(weapon),
    e_press=lambda: True
)

systems = Page(
    Rectangle(0.05, 0.05, 0.9, 0.9, Menu.DEFAULT_BACKGROUND_COLOUR, curve=10),
    Text(0.5, 0.12, "Systems"),

    Text(0.3, 0.3, "Health", font_size=25),
    Bar(0.39, 0.298, width=410, height=85, value=lambda: game.player.health, max_value=lambda: game.MAX_PLAYER_HEALTH, colour=(255, 0, 0), outline_width=5, curve=12),
    Text(0.445, 0.3, lambda: f"{round(game.player.health)} | {game.MAX_PLAYER_HEALTH}", font_size=25),

    Text(0.3, 0.45, "Armour", font_size=25),
    ArmourBar(0.39, 0.448, width=430, height=85, value=lambda: game.player.armour, max_value=lambda: game.MAX_PLAYER_ARMOUR, price=3, number=3, colour=(185, 185, 185), outline_width=5, curve=12),
    Text(0.445, 0.45, lambda: f"{round(game.player.armour)} | {game.MAX_PLAYER_ARMOUR}", font_size=25),

    Text(0.3, 0.6, "Shield", font_size=25),
    Bar(0.39, 0.598, width=410, height=85, value=lambda: game.player.shield, max_value=lambda: game.MAX_PLAYER_SHIELD, colour=(34, 130, 240), outline_width=5, curve=12),
    Text(0.43, 0.6, lambda: f"{round(game.player.shield)} | {game.MAX_PLAYER_SHIELD}", font_size=25),

    Text(0.86, 0.12, lambda: f"{game.SCRAP_COUNT}"),
    Image(0.9, 0.12, images.SCRAP, scale=6),
    background_colour=None,
    escape=lambda: True,
    e_press=lambda: True
)

death_screen = Page(
    Text(  0.5, 1/6, "YOU DIED!"                           , colour=(255, 0, 0)    , font_size=40),
    Text(  0.5, 2/6, lambda: f"SCORE: {game.SCORE}"        , colour=(100, 100, 255), font_size=40),
    Text(  0.5, 3/6, lambda: f"HIGHSCORE: {game.HIGHSCORE}", colour=(255, 255, 100), font_size=40),
    Button(0.5, 4/6, "PLAY AGAIN", font_size=40, function=lambda: main.main()),
    Button(0.5, 5/6, "MAIN MENU" , font_size=40, function=lambda: Menu.change_page(main_menu))
)



#################
### Functions ###
#################

def settings_click():
    """If there is a selected widget that shouldn't be, un-select it"""
    mouse = pygame.mouse.get_pos()
    for widget in Menu.current_page.widgets:
        if isinstance(widget, SettingButton) and widget.selected and not widget.touching_mouse(mouse): # if widget should be un-selected
            widget.selected = False
            widget.outline_colour = widget.original_outline_colour
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

def make_windowed():
    game.FULLSCREEN = False
    pygame.display.set_mode((game.WIDTH, game.HEIGHT), flags=pygame.RESIZABLE)

def repair_armour():
    if game.SCRAP_COUNT < 5:
        return
    else:
        game.SCRAP_COUNT -= 5
        game.player.armour += 5

        if game.player.armour > game.MAX_PLAYER_ARMOUR:
            game.player.armour = game.MAX_PLAYER_ARMOUR