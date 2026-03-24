from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', spacing=20, padding=50)

        btn1 = Button(text="NOVA JORNADA", size_hint=(1, 0.2), font_size="22sp")
        btn2 = Button(text="CONTINUAR", size_hint=(1, 0.2), font_size="22sp")
        btn3 = Button(text="CONFIGURAÇÕES", size_hint=(1, 0.2), font_size="22sp")

        btn1.bind(on_press=self.new_game)
        btn2.bind(on_press=self.continue_game)
        btn3.bind(on_press=self.settings)

        layout.add_widget(btn1)
        layout.add_widget(btn2)
        layout.add_widget(btn3)

        self.add_widget(layout)

    def new_game(self, *args):
        self.manager.current = "game"

    def continue_game(self, *args):
        self.manager.current = "game"

    def settings(self, *args):
        print("Configurações ainda não implementadas")
