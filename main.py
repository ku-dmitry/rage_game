import random

from kivy.config import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform

Config.set('graphics', 'width', 1280)
Config.set('graphics', 'height', 720)
Builder.load_file('menu.kv')


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2d, perspective
    from controls import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    fixed_velocity = NumericProperty(0)
    menu_widget = ObjectProperty()

    V_NB_LINES = 14
    V_LINES_SPACING = .07
    vertical_lines = []

    H_NB_LINES = 14
    H_LINES_SPACING = .07
    horizontal_lines = []

    FORWARD_VELOCITY = .001
    current_offset_y = 0
    current_y_loop = 0

    STEERING_VELOCITY = .01
    current_offset_x = 0
    current_speed_x = 0

    NB_TILES = 14
    tiles = []
    tiles_coordinates = []

    player = None
    PLAYER_WIDTH = .05
    PLAYER_HEIGHT = .035
    PLAYER_BASE_Y = .04
    player_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_over_state = False
    game_started_state = False

    menu_title = StringProperty("Rage Game")
    start_button_title = StringProperty("START")

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.reset_game()
        self.init_player()
        if self.is_desktop():
                self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
                self.keyboard.bind(on_key_down=self.on_keyboard_down)
                self.keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tiles_coordinates = []
        self.generate_start_line()
        self.generate_tiles_coordinates()

        self.game_over_state = False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def check_player_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_player_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_player_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0,3):
            px, py = self.player_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def generate_start_line(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        current_y = 0
        current_x = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            current_y = last_coordinates[1] + 1
            current_x = last_coordinates[0]

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if current_x <= start_index:
                r = 1
            if current_x >= end_index:
                r = 2
            self.tiles_coordinates.append((current_x, current_y))
            if r == 1:
                current_x += 1
                self.tiles_coordinates.append((current_x, current_y))
                current_y += 1
                self.tiles_coordinates.append((current_x, current_y))
            if r == 2:
                current_x -= 1
                self.tiles_coordinates.append((current_x, current_y))
                current_y += 1
                self.tiles_coordinates.append((current_x, current_y))
            current_y += 1

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset * spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index+self.V_NB_LINES - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)
        for i in range(0, self.V_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def init_player(self):
        with self.canvas:
            Color(0, 0, 0)
            self.player = Triangle()

    def update_player(self):
        center_x = self.width / 2
        base_y = self.PLAYER_BASE_Y * self.height
        player_half_width = self.PLAYER_WIDTH * self.width / 2
        player_height = self.PLAYER_HEIGHT * self.height
        self.player_coordinates[0] = (center_x - player_half_width, base_y)
        self.player_coordinates[1] = (center_x, base_y + player_height)
        self.player_coordinates[2] = (center_x + player_half_width, base_y)
        x1, y1 = self.transform(*self.player_coordinates[0])
        x2, y2 = self.transform(*self.player_coordinates[1])
        x3, y3 = self.transform(*self.player_coordinates[2])
        self.player.points = [x1, y1, x2, y2, x3, y3]

    def update(self, dt):
        time_factor = dt * 60
        self.perspective_point_x = self.width / 2
        self.perspective_point_y = self.height / 2
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_player()
        if not self.game_over_state and self.game_started_state:
            self.fixed_velocity = self.FORWARD_VELOCITY * self.height
            self.current_offset_y += self.fixed_velocity * time_factor
            self.current_offset_x += self.current_speed_x * time_factor
            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.generate_tiles_coordinates()
            fixed_steering = self.current_speed_x * self.width
            self.current_offset_x += fixed_steering * time_factor
        if not self.check_player_collision() and not self.game_over_state:
            self.game_over_state = True
            self.menu_title = "GAME OVER"
            self.start_button_title = "AGAIN"
            self.menu_widget.opacity = 80

    @staticmethod
    def is_desktop():
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def on_start_button_pressed(self):
        self.reset_game()
        self.game_started_state = True
        self.menu_widget.opacity = 0


class RageApp(App):
    pass


RageApp().run()
