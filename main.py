from kivy.config import Config
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform

Config.set('graphics', 'width', 1280)
Config.set('graphics', 'height', 720)


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 14
    V_LINES_SPACING = .07
    vertical_lines = []

    H_NB_LINES = 14
    H_LINES_SPACING = .07
    horizontal_lines = []

    FORWARD_VELOCITY = 4
    current_offset_y = 0

    STEERING_VELOCITY = 8
    current_offset_x = 0
    current_speed_x = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        if self.is_desktop():
                self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
                self.keyboard.bind(on_key_down=self.on_keyboard_down)
                self.keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1 / 60)

    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard.unbind(on_key_up=self.on_keyboard_up)
        self.keyboard = None

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        central_line_x = int(self.width / 2)
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES/2)+0.5
        for i in range(0, self.V_NB_LINES):
            line_x = int(central_line_x + offset*spacing) + self.current_offset_x
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]
            offset += 1

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for _ in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        central_line_x = int(self.width / 2) + self.current_offset_x
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_NB_LINES / 2) + 0.5

        x_min = central_line_x+offset*spacing
        x_max = central_line_x-offset*spacing
        spacing_y = self.H_LINES_SPACING*self.height

        for i in range(0, self.V_NB_LINES):
            line_y = 0 + i*spacing_y-self.current_offset_y
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def transform(self, x, y):
        # return self.transform_2d(x, y)
        return self.perspective(x, y)

    @staticmethod
    def transform_2d(x, y):
        return x, y

    def perspective(self, x, y):
        lin_y = self.perspective_point_y * y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y

        diff_x = x-self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        factor_y = diff_y/self.perspective_point_y
        factor_y = pow(factor_y, 3)
        tr_x = self.perspective_point_x + diff_x*factor_y
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.current_speed_x = self.STEERING_VELOCITY
        elif keycode[1] == 'right':
            self.current_speed_x = -self.STEERING_VELOCITY
        return True

    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True

    def on_touch_down(self, touch):
        if touch.x <self.width/2:
            self.current_speed_x = self.STEERING_VELOCITY
        else:
            self.current_speed_x = -self.STEERING_VELOCITY

    def on_touch_up(self, touch):
        self.current_speed_x = 0

    def update(self, dt):
        time_factor = dt*60
        self.perspective_point_x = self.width/2
        self.perspective_point_y = self.height/2
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y += self.FORWARD_VELOCITY * time_factor
        self.current_offset_x += self.current_speed_x * time_factor
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y

    @staticmethod
    def is_desktop():
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False


class RageApp(App):
    pass


RageApp().run()
