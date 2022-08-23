from kivy.config import Config
from transforms import transform #config parameter have to be before every other import
Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')
from kivy.core.window import Window 

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.graphics.context_instructions import Color
from kivy.properties import ObjectProperty, StringProperty, Clock, NumericProperty
from kivy import platform
from kivy.uix.image import Image
from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader
from random import randint

Builder.load_file("menu.kv")
class MainWidget(RelativeLayout):

    from transforms import transform, transform_2D, transform_perspective
    from user_action import on_keyboard_down, on_keyboard_up, on_touch_down, on_touch_up, keyboard_closed

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    menu_title = StringProperty("Informule1")
    menu_button_title = StringProperty("Start")
    score_txt = StringProperty()

    V_NB_LINES = 8
    V_LINES_SPACING = .4   #percentage from screen
    vertical_lines = []
    
    H_NB_LINES = 12
    H_LINES_SPACING = .2    #percentage from screen
    horizontal_lines = []

    current_offset_y = 0
    SPEED = 12

    current_offset_x = 0
    SPEED_x = 20
    current_speed_x = 0

    NB_TILES=16
    tiles = []
    tiles_coordinates = []

    current_y_loop = 0

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.1
    SHIP_BASE_Y = 0.04
    ship = None
    kart = Image(source="images\kart.png")
    ship_coordinates = [(),(),(),()]

    state_gameover = False
    state_game_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music_1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_song()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        #self.init_ship()
        self.add_widget(self.kart)
        self.sound_galaxy.play()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1/60) #called each n second

    def init_song(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music_1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music_1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_impact.volume = .6
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25


    def reset_game(self):
        self.current_y_loop = 0
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_speed_x = 0
        
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.score_txt = "Score : 0"

        self.state_gameover = False
    
    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y*self.height
        ship_half_width = self.SHIP_WIDTH*self.width/2
        ship_height = self.SHIP_HEIGHT*self.height

        
        self.ship_coordinates[0] = (center_x-ship_half_width/2.2, base_y)
        self.ship_coordinates[1] = (center_x, base_y+ship_height)
        self.ship_coordinates[2] = (center_x+ship_half_width/2.2, base_y)
        """
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = [x1, y1, x2, y2, x3, y3]"""
        


        
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y*self.height
        ship_half_width = self.SHIP_WIDTH*self.width/2*1.3
        ship_height = self.SHIP_HEIGHT*self.height*1.5
        
        """self.ship_coordinates[0] = (center_x-self.kart.width/2, base_y)
        self.ship_coordinates[1] = (center_x+self.kart.width/2, base_y)
        self.ship_coordinates[2] = (center_x-self.kart.width/2, base_y+ship_height)
        self.ship_coordinates[3] = (center_x+self.kart.width/2, base_y+ship_height)"""
        #Image part
        self.kart.allow_stretch = True
        self.kart.keep_ratio = False
        self.kart.size_hint_x = None
        self.kart.size_hint_y = None
        self.kart.height = ship_height
        self.kart.width = ship_half_width
        self.kart.opacity = 1
        self.kart.pos = (center_x-self.kart.width/2, base_y)


    
    def check_ship_collision(self):
        for i in range (0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop+1:
                return False
            if self.check_ship_collision_tile(ti_x, ti_y):
                return True
        return False



    def check_ship_collision_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordonates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordonates(ti_x+1, ti_y+1)
        for i in range (0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False


    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())
    
    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range (0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range (0, 5):
            self.tiles_coordinates.append((0,i))
    
    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0
        #Clean coordonate out of the screen
        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1]+1
            last_x = last_coordinates[0]

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = randint(0, 2)
            self.tiles_coordinates.append((last_x, last_y))
            start_index = -int(self.V_NB_LINES/2)+1
            end_index = start_index+self.V_NB_LINES-1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index-1:
                r = 2
            match r:
                case 1: #Right
                    last_x+=1
                    self.tiles_coordinates.append((last_x, last_y))
                    last_y+=1
                    self.tiles_coordinates.append((last_x, last_y))
                case 2: #Left
                    last_x-=1
                    self.tiles_coordinates.append((last_x, last_y))
                    last_y+=1
                    self.tiles_coordinates.append((last_x, last_y))
            
            last_y+=1

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)

            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2)+1
        end_index = start_index+self.V_NB_LINES-1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update_tile(self):
        for i in range (0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordonates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordonates(tile_coordinates[0]+1, tile_coordinates[1]+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    #dt = time difference between the previous call of the function
    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tile()
        self.update_ship()

        if not self.state_gameover and self.state_game_started:
            #To get a consistant game on every machine with different game power
            self.current_offset_y+= self.SPEED*time_factor*self.height*0.001
            self.current_offset_x+= self.current_speed_x*time_factor*self.width*0.001
            spacing_y = self.H_LINES_SPACING*self.height

            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop +=1
                self.score_txt = "Score : "+str(self.current_y_loop)
                self.generate_tiles_coordinates()

        if not self.state_gameover and not self.check_ship_collision():
            self.menu_title = "F I N I T O"
            self.menu_button_title = "RESTART"
            self.state_gameover = True
            self.menu_widget.opacity = 1
            self.sound_music_1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_gameover_voice, 3)    #Play the song 3 second later
            
    
    def play_gameover_voice(self, dt):
        if self.state_gameover:
            self.sound_gameover_voice.play()

    def get_tile_coordonates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING*self.width
        offset = index-0.5
        line_x = central_line_x + offset*spacing+self.current_offset_x

        return line_x
    
    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index*spacing_y-self.current_offset_y
        return line_y
    
    def on_menu_button_pressed(self):
        self.reset_game()
        if self.state_game_started:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music_1.play()
        self.state_game_started = True
        self.menu_widget.opacity = 0

class GalaxyApp(App):
    pass

GalaxyApp().run()