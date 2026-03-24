from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="JOGO INICIADO", font_size="24sp"))
