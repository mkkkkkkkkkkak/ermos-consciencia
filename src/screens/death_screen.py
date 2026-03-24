from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

class DeathScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="VOCÊ MORREU", font_size="24sp"))
