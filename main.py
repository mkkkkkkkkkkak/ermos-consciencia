import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

from src.screens.menu_screen import MenuScreen
from src.screens.game_screen import GameScreen
from src.screens.death_screen import DeathScreen

Window.clearcolor = (0.04, 0.03, 0.02, 1)

class ErmosApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(DeathScreen(name='death'))
        return sm

if __name__ == '__main__':
    ErmosApp().run()
