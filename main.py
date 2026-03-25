"""
ERMOS CONSCIENCIA - Main Entry Point
"""
import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

from kivy.config import Config
Config.set('graphics', 'width', '854')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from src.screens.menu_screen import MenuScreen
from src.screens.game_screen import GameScreen
# death_screen.py contém as 3 classes: DeathScreen, InventoryScreen, JournalScreen
from src.screens.death_screen import DeathScreen, InventoryScreen, JournalScreen
from src.data.save_manager import SaveManager

Window.clearcolor = (0.04, 0.03, 0.02, 1)


class ErmosApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = SaveManager()
        self.title = 'ERMOS CONSCIENCIA'

    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(DeathScreen(name='death'))
        sm.add_widget(InventoryScreen(name='inventory'))
        sm.add_widget(JournalScreen(name='journal'))
        return sm

    def on_pause(self):
        try:
            game = self.root.get_screen('game')
            if hasattr(game, 'world') and game.world:
                self.save_manager.auto_save(game.world)
        except Exception:
            pass
        return True

    def on_resume(self):
        pass


if __name__ == '__main__':
    ErmosApp().run()
