import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from src.screens.menu_screen import MenuScreen
from src.screens.game_screen import GameScreen
from src.screens.death_screen import DeathScreen
from src.screens.inventory_screen import InventoryScreen
from src.screens.journal_screen import JournalScreen

import sys, traceback
def handle_exception(exc_type, exc_value, exc_traceback):
    with open("error_log.txt", "w") as f:
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=f)
sys.excepthook = handle_exception

Window.clearcolor = (0.04, 0.03, 0.02, 1)

class ErmosApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.3))

        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(DeathScreen(name='death'))
        sm.add_widget(InventoryScreen(name='inventory'))
        sm.add_widget(JournalScreen(name='journal'))

        return sm

if __name__ == '__main__':
    ErmosApp().run()
