import pygame
import game
import main
# menu v2



class Menu():
    """Menu controls the current page and checks for mouse clicks"""
    
    background_colour = game.DARK_GREY
    box_colour = game.MEDIUM_GREY

    DEFAULT_FONT = "bahnschrift"
    DEFAULT_FONT_SIZE = 40
    DEFAULT_COLOUR = game.WHITE
    
    def __init__(self) -> None:
        """On start up, the default page is main_menu"""
        Menu.change_page(main_menu)

    def change_page(page: "Page"):
        """Draw the new page, and then wait for a mouse click"""
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

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                Menu.mouse_click(mouse)

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
    def __init__(self, *widgets, background_colour=Menu.background_colour, click=None, escape=None, up=None, down=None) -> None:
        self.background_colour = background_colour
        self.click = click
        self.escape = escape
        self.up = up
        self.down = down

        self.widgets: tuple[Widget] = widgets

    def draw(self):
        
        if self.background_colour:
            game.WIN.fill(self.background_colour)

        for widget in self.widgets:
            widget.draw()

        pygame.display.update()



class Widget():
    """Base class for Page elements
       x, y can be float or int
       if (x, y) is a float (e.g. 0.5 = 50%), the element's location is that percentage of the screen
       if (x, y) is an int (e.g. 100 or -200), the element is placed that many pixels from the edge, negative pixels are placed from the right
       x, y is the centre of the Widget
       font size is relative to screen width, if you change the screen resolution then the font size will dynamically change
       text can be a string or a function, if it's a function then that will be called, e.g. text=lambda f"SCORE: {game.SCORE}"
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=40, colour=Menu.DEFAULT_COLOUR) -> None:
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

        self.text = text
        self.font = font
        self.font_size = font_size
        self.colour = colour

    def get_label(self):
        if callable(self.text): # if text is a function, e.g. lambda: f"SCORE: {game.SCORE}", then it will be called
            text = self.text()
        else:
            text = self.text
        return pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900)).render(text, True, self.colour)

    def draw(self):
        label = self.get_label()
        position = self.get_position_x(self, label), self.get_position_y(self, label) # Adjust coordinates to be centre of Widget
        game.WIN.blit(label, position)



class Text(Widget):
    """Multi-line text Widget
       x, y is the centre of the first line of the Text
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=40, colour=Menu.DEFAULT_COLOUR) -> None:
        super().__init__(x, y, text, font, font_size, colour)
        self.text = [sentence.lstrip() for sentence in text.split("\n")]

    def get_labels(self):
        font = pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900))
        labels = [font.render(sentence, True, self.colour) for sentence in self.text]
        return labels

    def draw(self):
        labels = self.get_labels()
        for idx, label in enumerate(labels):
            position = self.get_position_x(self, label), self.get_position_y(self, label) + idx * label.get_height() - label.get_height()/2
            game.WIN.blit(label, position)



class Button(Widget):
    """A Widget that can be clicked on
       When a Button is clicked, the "function" method is called
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=40, colour=Menu.DEFAULT_COLOUR, function=None, box_colour=Menu.box_colour, outline_colour=None) -> None:
        super().__init__(x, y, text, font, font_size, colour)
        self.box_colour = box_colour
        if not outline_colour: outline_colour = box_colour
        self.outline_colour = outline_colour
        self.function = function

    def click(self, mouse):
        if self.clicked_on(mouse):
            self.function()
            return True # Tells the Menu that this Button has been clicked on

    def clicked_on(self, mouse):
        label = self.get_label()
        width, height = label.get_width(), label.get_height()
        x, y = self.get_position_x(self, label), self.get_position_y(self, label)
        return (mouse[0] > x and mouse[0] < x + width and
                mouse[1] > y and mouse[1] < y + height)

    def get_width_and_height(self):
        label = self.get_label()
        return label.get_width(), label.get_height()

    def get_rect(self, label):
        width, height = self.get_width_and_height()
        x, y = self.get_position_x(self, label), self.get_position_y(self, label)
        return x, y, width, height

    def draw(self):
        label = self.get_label()
        x, y, width, height = self.get_rect(label)
        pygame.draw.rect(game.WIN, self.box_colour, (round(x), round(y), width, height))
        pygame.draw.rect(game.WIN, self.outline_colour, (round(x), round(y), width, height), width=round(game.WIDTH/300))
        super().draw()



class SettingButton(Button):
    """A Button for settings
       When clicked on, it will change outline colour
       value is the value that the setting button affects, NOTE: value is a string and has to be an attribute of game, e.g. game.WIDTH and value="WIDTH"
       function_action is called after the value is modified
       text is a function
       uniform arg makes all of setting buttons on the page the same width
    """
    def __init__(self, x, y, text="Text", font=Menu.DEFAULT_FONT, font_size=40, colour=Menu.DEFAULT_COLOUR, value=None, function_action=None, box_colour=Menu.box_colour, outline_colour=None, click_outline_colour=game.LIGHT_GREY, uniform=True) -> None:
        super().__init__(x, y, text, font, font_size, colour, function_action, box_colour, outline_colour)
        self.original_outline_colour = self.outline_colour
        self.click_outline_colour = click_outline_colour
        self.uniform = uniform
        self.value = value
        self.function_action = function_action
        self.selected = False

        def function():
            self.selected = True
            self.outline_colour = self.click_outline_colour

            # If self.value is a bool, then when this button is clicked, the value will be flipped
            if isinstance(self.get_value(), bool):
                setattr(game, self.value, not self.get_value())
                if self.function_action:
                    self.function_action()

            Menu.update()
            self.outline_colour = self.original_outline_colour
        self.function = function

    def get_value(self):
        return getattr(game, self.value)
        
    def up(self):
        setattr(game, self.value, self.get_value() + 1)
        if self.function_action:
            self.function_action()

    def down(self):
        setattr(game, self.value, self.get_value() - 1)
        if self.function_action:
            self.function_action()

    def get_label(self):
        return pygame.font.SysFont(self.font, round(game.WIDTH * self.font_size / 900)).render(self.text(), True, self.colour)

    def get_max_width(self):
        """Get greatest width of all SettingButtons on the current_page"""

        max_width = 0
        for widget in Menu.current_page.widgets:
            if isinstance(widget, SettingButton):
                if widget.get_label().get_width() > max_width:
                    max_width = widget.get_label().get_width()
        return max_width

    def get_rect(self, label):
        """If self.uniform == True, set the width to the greatest width of all SettingButtons on the current_page"""
        if self.uniform:
            width, height = self.get_max_width(), self.get_label().get_height()
            width_difference = width - self.get_label().get_width()
            x, y = self.get_position_x(self, label) - width_difference/2, self.get_position_y(self, label)
            return x, y, width, height

        width, height = self.get_width_and_height()
        x, y = self.get_position_x(self, label), self.get_position_y(self, label)
        return x, y, width, height

# FRAMEWORK
########################################################################################################################################################
# PAGES




main_menu = Page(
    Widget(0.5, 1/7, "Astro Attack" , font_size=40),
    Button(0.5, 2/7, "Single Player", font_size=40, function=lambda: main.main()),
    Button(0.5, 3/7, "Multiplayer"  , font_size=40, function=lambda: main.main()),
    Button(0.5, 4/7, "Settings"     , font_size=40, function=lambda: Menu.change_page(settings)),
    Button(0.5, 5/7, "Info"         , font_size=40, function=lambda: Menu.change_page(info)),
    Button(0.5, 6/7, "Quit"         , font_size=40, function=game.quit)
)

info = Page(
    Widget(0.5, 1/8,   "CREDITS"          , font_size=40),
    Text(0.5, 2/8,   """Rex Attwood
                        Gabriel Correia""", font_size=20),
    Widget(0.5, 2.5/8, "Fred"             , font_size=5),
    Widget(0.5, 3.4/8, "CONTROLS"         , font_size=40),
    Text(0.5, 4.7/8, """CHANGE SETTINGS: UP AND DOWN ARROWS
                        PAUSE: ESC"""     , font_size=20),
    Button(0.5, 5/6,   "MAIN MENU"        , font_size=40, function=lambda: Menu.change_page(main_menu))
)

settings = Page(
    SettingButton(0.25, 1/6, lambda: f"SCREEN WIDTH: {game.WIDTH}"       , font_size=40, value="WIDTH"     , function_action=lambda: make_windowed()),
    SettingButton(0.75, 1/6, lambda: f"SCREEN HEIGHT: {game.HEIGHT}"     , font_size=40, value="HEIGHT"    , function_action=lambda: make_windowed()),
    SettingButton(0.25, 2/6, lambda: f"FULL SCREEN: {game.FULLSCREEN}"   , font_size=40, value="FULLSCREEN", function_action=lambda: change_fullscreen()),
    SettingButton(0.75, 2/6, lambda: f"SIZE LINK: {game.SIZE_LINK}"      , font_size=40, value="SIZE_LINK" , function_action=None),
    Button(0.5, 5/6, "MAIN MENU" , font_size=40, function=lambda: Menu.change_page(main_menu)),
    click=lambda: settings_click(),
    up=lambda: settings_up(),
    down=lambda: settings_down()
)

pause = Page(
    Widget(0.5, 1/7, "Astro Attack" , font_size=40),
    Button(0.5, 0.5, "MAIN MENU"    , font_size=40, function=lambda: Menu.change_page(main_menu)),
    background_colour=None,
    escape=lambda: True
)

death_screen = Page(
    Widget(0.5, 1/6, "YOU DIED!"                           , colour=(255, 0, 0)    , font_size=40),
    Widget(0.5, 2/6, lambda: f"SCORE: {game.SCORE}"        , colour=(100, 100, 255), font_size=40),
    Widget(0.5, 3/6, lambda: f"HIGHSCORE: {game.HIGHSCORE}", colour=(255, 255, 100), font_size=40),
    Button(0.5, 4/6, "PLAY AGAIN", font_size=40, function=lambda: main.main()),
    Button(0.5, 5/6, "MAIN MENU" , font_size=40, function=lambda: Menu.change_page(main_menu))
)



#################
### Functions ###
#################

def settings_click():
    """Un-select all settings buttons"""
    for widget in Menu.current_page.widgets:
        if isinstance(widget, SettingButton):
            widget.selected = False

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