import pygame
import game
import images
import main
# menu v2



class Menu():
    """Menu controls the current page and checks for mouse clicks"""
    
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

        while True:
            if Menu.check_for_inputs(): # if check_for_inputs() returns True, then break out of Menu control
                break

    def update():
        """Re-draw the current_page"""
        Menu.current_page.draw()

    def resize():
        """Re-draw the current_page but with the updated screen dimensions"""
        game.WIDTH, game.HEIGHT = pygame.display.get_window_size()
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

                Menu.update()

    def mouse_click(mouse):
        """Go through all Page Widgets, if the Widget is a button then check if it is clicked on"""
        if Menu.current_page.click:
            Menu.current_page.click()

        for widget in Menu.current_page.widgets:
            if isinstance(widget, Button):
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

    def up_pressed():
        if Menu.current_page.up:
            Menu.current_page.up()

    def down_pressed():
        if Menu.current_page.down:
            Menu.current_page.down()

    def pause():
        Menu.change_page(pause)

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
    def __init__(self, *widgets, background_colour=Menu.DEFAULT_BACKGROUND_COLOUR, click=None, escape=None, up=None, down=None) -> None:
        self.background_colour = background_colour
        self.click = click
        self.escape = escape
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
            self.get_position_x = lambda self, label: self.x * game.WIDTH - label.get_width()/2

        elif type(self.x) == int:
            if self.x < 0:
                self.get_position_x = lambda self, label: game.WIDTH + self.x - label.get_width()/2
            else:
                self.get_position_x = lambda self, label: self.x - label.get_width()/2
        
        if type(self.y) == float:
            self.get_position_y = lambda self, label: self.y * game.HEIGHT - label.get_height()/2

        if type(self.y) == int:
            if self.y < 0:
                self.get_position_y = lambda self, label: game.HEIGHT + self.y - label.get_height()/2
            else:
                self.get_position_y = lambda self, label: self.y - label.get_height()/2



class Image(Widget):
    """A Widget that has an image
       scale is the scale of the image, e.g. scale=1 wouldn't change image size, scale=2 would double the size
    """
    def __init__(self, x, y, image=images.DEFAULT, scale=1) -> None:
        super().__init__(x, y)
        self.image = pygame.transform.scale(image, (image.get_width()*scale, image.get_height()*scale))

    def draw(self):
        ratio = game.WIDTH * self.image.get_width() / 1_000_000 # Ratio of image width to game width
        image = pygame.transform.scale(self.image, (self.image.get_width()*ratio, self.image.get_height()*ratio))
        game.WIN.blit(image, (self.x * game.WIDTH - image.get_width()/2, self.y * game.HEIGHT - image.get_height()/2))



class Text(Widget):
    """Text can be single of multi-line
       x, y is the centre of the first line of the Text
       font size is relative to screen width, if you change the screen resolution then the font size will dynamically change
       text can be a string or a function, if it's a function then that will be called, e.g. text=lambda f"SCORE: {game.SCORE}"
       if text is a function it has to return a string (can be single or multi-line)
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=Menu.DEFAULT_FONT_SIZE, colour=Menu.DEFAULT_COLOUR) -> None:
        super().__init__(x, y)

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
        for idx, label in enumerate(labels):
            position = self.get_position_x(self, label), self.get_position_y(self, label) + idx * label.get_height() # Adjust coordinates to be centre of Widget
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


# FRAMEWORK                                                                                           
########################################################################################################################################################
# PAGES




main_menu = Page(
    Image(0.5, 3/16, images.ASTRO_ATTACK_LOGO1),
    Button(0.5, 3/8, "Single Player", font_size=40, function=lambda: main.main()),
    Button(0.5, 4/8, "Multiplayer"  , font_size=40, function=lambda: main.main()),
    Button(0.5, 5/8, "Settings"     , font_size=40, function=lambda: Menu.change_page(settings)),
    Button(0.5, 6/8, "Info"         , font_size=40, function=lambda: Menu.change_page(info)),
    Button(0.5, 7/8, "Quit"         , font_size=40, function=game.quit)
)

info = Page(
    Text(0.5, 1/8  ,   "CREDITS"          , font_size=40),
    Text(0.5, 2/8  , """Rex Attwood
                        Gabriel Correia""", font_size=20),
    Text(0.5, 2.5/8,   "Fred"             , font_size=5),
    Text(0.5, 3.4/8,   "CONTROLS"         , font_size=40),
    Text(0.5, 4.7/8, """CHANGE SETTINGS: UP AND DOWN ARROWS
                        PAUSE: ESC"""     , font_size=20),
    Button(0.5, 5/6,   "MAIN MENU"        , font_size=40, function=lambda: Menu.change_page(main_menu)),
    escape=lambda: Menu.change_page(main_menu)
)

settings = Page(
    SettingButton(0.25, 1/6, lambda: f"SCREEN WIDTH: {game.WIDTH}"         , font_size=40, value="WIDTH"            , function_action=lambda: make_windowed(), min=192, max=game.FULLSCREEN_SIZE[0]),
    SettingButton(0.75, 1/6, lambda: f"SCREEN HEIGHT: {game.HEIGHT}"       , font_size=40, value="HEIGHT"           , function_action=lambda: make_windowed(), min=108, max=game.FULLSCREEN_SIZE[1]),
    SettingButton(0.25, 2/6, lambda: f"FULL SCREEN: {game.FULLSCREEN}"     , font_size=40, value="FULLSCREEN"       , function_action=lambda: change_fullscreen()),
    SettingButton(0.75, 2/6, lambda: f"SIZE LINK: {game.SIZE_LINK}"        , font_size=40, value="SIZE_LINK"        , function_action=None),
    SettingButton(0.25, 3/6, lambda: f"HEALTH: {game.MAX_PLAYER_HEALTH}"   , font_size=40, value="MAX_PLAYER_HEALTH", function_action=None                            , max=100),
    SettingButton(0.75, 3/6, lambda: f"LOAD DISTANCE: {game.LOAD_DISTANCE}", font_size=40, value="LOAD_DISTANCE"    , function_action=None                            , max=26),
    SettingButton(0.25, 4/6, lambda: f"BOOST: {game.MAX_BOOST_AMOUNT}"     , font_size=40, value="MAX_BOOST_AMOUNT" , function_action=None                            , max=100),
    SettingButton(0.75, 4/6, lambda: f"BULLET SPEED: {game.BULLET_SPEED}"  , font_size=40, value="BULLET_SPEED"     , function_action=None                            , max=1000),
    Button(0.5, 5/6, "MAIN MENU" , font_size=40, function=lambda: Menu.change_page(main_menu)),
    click=lambda: settings_click(),
    escape=lambda: Menu.change_page(main_menu),
    up=lambda: settings_up(),
    down=lambda: settings_down()
)

pause = Page(
    Image( 0.5, 0.245, images.ASTRO_ATTACK_LOGO1, scale=0.6),
    Button(0.5, 0.345, "Main Menu", font_size=40, function=lambda: Menu.change_page(main_menu)),
    background_colour=None,
    escape=lambda: True
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