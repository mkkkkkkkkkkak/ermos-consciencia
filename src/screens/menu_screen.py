"""
ERMOS - Tela de Menu Principal
Correções:
  - Coordenadas de toque corrigidas (Kivy: Y=0 embaixo)
  - Botões maiores e proporcional à tela
  - Botão Configurações funcional
  - Botão Continuar carrega save se disponível
"""
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse, Line, RoundedRectangle
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = 0
        self.layout = FloatLayout()
        self.canvas_widget = MenuCanvas(size=Window.size, pos=(0, 0))
        self.layout.add_widget(self.canvas_widget)
        self.add_widget(self.layout)
        self._clock = None
        self._show_settings = False

    def on_enter(self):
        self._show_settings = False
        self._clock = Clock.schedule_interval(self._update, 1/60)

    def on_leave(self):
        if self._clock:
            self._clock.cancel()
            self._clock = None

    def _update(self, dt):
        self.canvas_widget.anim += dt
        self.canvas_widget.show_settings = self._show_settings
        self.canvas_widget.render()

    def on_touch_down(self, touch):
        w, h = Window.size

        if self._show_settings:
            self._show_settings = False
            return True

        btn_h = max(56, int(h * 0.072))
        btn_w = max(240, int(w * 0.65))
        bx = w // 2 - btn_w // 2
        margin = 12

        # NOVA JORNADA: centro em h*0.52
        nova_cy = h * 0.52
        if (nova_cy - btn_h//2 - margin) < touch.y < (nova_cy + btn_h//2 + margin):
            if bx - margin < touch.x < bx + btn_w + margin:
                game = self.manager.get_screen('game')
                game.new_game = True
                self.manager.current = 'game'
                return True

        # CONTINUAR: centro em h*0.40
        cont_cy = h * 0.40
        if (cont_cy - btn_h//2 - margin) < touch.y < (cont_cy + btn_h//2 + margin):
            if bx - margin < touch.x < bx + btn_w + margin:
                game = self.manager.get_screen('game')
                game.new_game = False
                self.manager.current = 'game'
                return True

        # CONFIGURAÇÕES: centro em h*0.28
        cfg_cy = h * 0.28
        if (cfg_cy - btn_h//2 - margin) < touch.y < (cfg_cy + btn_h//2 + margin):
            if bx - margin < touch.x < bx + btn_w + margin:
                self._show_settings = True
                return True

        return super().on_touch_down(touch)


class MenuCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = 0
        self.show_settings = False

    def render(self):
        self.canvas.clear()
        w, h = self.width, self.height
        t = self.anim
        with self.canvas:
            Color(0.04, 0.03, 0.02, 1)
            Rectangle(pos=(0, 0), size=(w, h))

            for i in range(5):
                alpha = 0.04 + 0.02 * math.sin(t * 0.5 + i)
                rx = w * (0.1 + i * 0.2 + 0.05 * math.sin(t * 0.3 + i))
                ry = h * (0.3 + 0.1 * math.sin(t * 0.2 + i * 1.3))
                Color(0.3, 0.05, 0.05, alpha)
                Ellipse(pos=(rx - 100, ry - 60), size=(200, 120))

            Color(0.35, 0.05, 0.05, 0.4)
            Line(points=[0, h * 0.45, w, h * 0.45], width=1)

            self._draw_city_silhouette(w, h)

            Color(0.85, 0.82, 0.70, 0.9)
            lx = w * 0.75
            ly = h * 0.72
            Ellipse(pos=(lx - 25, ly - 25), size=(50, 50))
            Color(0.04, 0.03, 0.02, 0.6)
            Ellipse(pos=(lx - 18, ly - 20), size=(50, 50))

            for i in range(30):
                sx = (i * 137.5) % w
                sy = h * 0.5 + (i * 73.1) % (h * 0.45)
                alpha = 0.3 + 0.3 * math.sin(t * 2 + i * 0.7)
                Color(0.9, 0.88, 0.75, alpha)
                Ellipse(pos=(sx, sy), size=(2, 2))

            self._draw_title(w, h, t)

            if self.show_settings:
                self._draw_settings(w, h)
            else:
                self._draw_buttons(w, h, t)

            self._draw_footer(w, h)

    def _draw_city_silhouette(self, w, h):
        Color(0.07, 0.05, 0.04, 1)
        buildings = [
            (w*0.05, h*0.35, w*0.08, h*0.12),
            (w*0.12, h*0.30, w*0.06, h*0.17),
            (w*0.17, h*0.38, w*0.05, h*0.09),
            (w*0.22, h*0.28, w*0.07, h*0.19),
            (w*0.30, h*0.35, w*0.05, h*0.12),
            (w*0.60, h*0.32, w*0.07, h*0.15),
            (w*0.68, h*0.27, w*0.06, h*0.20),
            (w*0.75, h*0.34, w*0.08, h*0.13),
            (w*0.84, h*0.30, w*0.05, h*0.17),
            (w*0.90, h*0.36, w*0.06, h*0.11),
        ]
        for bx, by, bw, bh in buildings:
            Rectangle(pos=(bx, by), size=(bw, bh))
            Color(0.12, 0.08, 0.05, 0.8)
            for wy in range(3):
                for wx in range(2):
                    Rectangle(
                        pos=(bx + bw*0.15 + wx*bw*0.4, by + bh*0.2 + wy*bh*0.25),
                        size=(bw*0.2, bh*0.15))
            Color(0.07, 0.05, 0.04, 1)

    def _draw_title(self, w, h, t):
        Color(0.5, 0.0, 0.0, 0.3)
        self._txt('ERMOS', w//2 + 3, h*0.80 - 3, 72, center=True)
        Color(0.92, 0.86, 0.76, 1)
        self._txt('ERMOS', w//2, h*0.80, 72, center=True)
        Color(0.65, 0.10, 0.10, 0.9)
        self._txt('CONSCIENCIA', w//2, h*0.73, 26, center=True)
        alpha = 0.5 + 0.3 * math.sin(t * 1.5)
        Color(0.70, 0.65, 0.56, alpha)
        self._txt('viver nao significa vencer', w//2, h*0.67, 14, center=True)

    def _draw_buttons(self, w, h, t):
        btn_h = max(56, int(h * 0.072))
        btn_w = max(240, int(w * 0.65))
        bx = w // 2 - btn_w // 2
        font_size = max(16, int(btn_h * 0.38))

        # NOVA JORNADA
        nova_cy = int(h * 0.52)
        by = nova_cy - btn_h // 2
        Color(0.40, 0.04, 0.04, 0.88)
        RoundedRectangle(pos=(bx, by), size=(btn_w, btn_h), radius=[10])
        Color(0.75, 0.12, 0.12, 0.95)
        Line(rectangle=(bx, by, btn_w, btn_h), width=1.8)
        Color(0.95, 0.88, 0.75, 1)
        self._txt('NOVA JORNADA', w//2, nova_cy, font_size, center=True)

        # CONTINUAR
        cont_cy = int(h * 0.40)
        by2 = cont_cy - btn_h // 2
        Color(0.15, 0.13, 0.10, 0.75)
        RoundedRectangle(pos=(bx, by2), size=(btn_w, btn_h), radius=[10])
        Color(0.42, 0.37, 0.26, 0.65)
        Line(rectangle=(bx, by2, btn_w, btn_h), width=1.4)
        Color(0.72, 0.67, 0.56, 0.9)
        self._txt('CONTINUAR', w//2, cont_cy, font_size, center=True)

        # CONFIGURACOES
        cfg_cy = int(h * 0.28)
        by3 = cfg_cy - btn_h // 2
        Color(0.10, 0.10, 0.10, 0.70)
        RoundedRectangle(pos=(bx, by3), size=(btn_w, btn_h), radius=[10])
        Color(0.32, 0.28, 0.18, 0.55)
        Line(rectangle=(bx, by3, btn_w, btn_h), width=1.2)
        Color(0.60, 0.56, 0.45, 0.85)
        self._txt('CONFIGURACOES', w//2, cfg_cy, font_size - 1, center=True)

    def _draw_settings(self, w, h):
        pw, ph = int(w * 0.85), int(h * 0.52)
        px = w // 2 - pw // 2
        py = h // 2 - ph // 2
        Color(0.06, 0.05, 0.04, 0.97)
        RoundedRectangle(pos=(px, py), size=(pw, ph), radius=[12])
        Color(0.55, 0.45, 0.25, 0.7)
        Line(rectangle=(px, py, pw, ph), width=1.5)

        Color(0.85, 0.78, 0.55, 1)
        self._txt('CONFIGURACOES', w//2, py + ph - 40, 20, center=True)

        configs = [
            ('Versao', 'v0.1'),
            ('Motor', 'Kivy 2.3 / Python 3'),
            ('Plataforma', 'Android / Desktop'),
            ('Salvar', 'Auto ao pausar'),
            ('Controles', 'Joystick + botoes'),
        ]
        for i, (chave, valor) in enumerate(configs):
            ey = py + ph - 78 - i * 40
            Color(0.50, 0.45, 0.32, 0.7)
            self._txt(chave + ':', px + 22, ey, 14)
            Color(0.80, 0.75, 0.60, 0.9)
            self._txt(valor, px + 150, ey, 14)

        Color(0.55, 0.50, 0.38, 0.75)
        self._txt('Toque para fechar', w//2, py + 18, 13, center=True)

    def _draw_footer(self, w, h):
        Color(0.35, 0.30, 0.22, 0.4)
        self._txt('v0.1 - ERMOS CONSCIENCIA', w//2, 12, 10, center=True)

    def _txt(self, text, x, y, size, center=False):
        lbl = CoreLabel(text=str(text), font_size=size)
        lbl.refresh()
        tx = lbl.texture
        if center:
            Rectangle(texture=tx, pos=(x - tx.width//2, y - tx.height//2), size=tx.size)
        else:
            Rectangle(texture=tx, pos=(x, y), size=tx.size)
