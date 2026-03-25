"""
ERMOS - Telas: Morte, Inventário, Diário
"""
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from src.constants import *


# ============================================================
# TELA DE MORTE
# ============================================================
class DeathScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = 0
        self.canvas_widget = DeathCanvas(size=Window.size, pos=(0, 0))
        fl = FloatLayout()
        fl.add_widget(self.canvas_widget)
        self.add_widget(fl)
        self._clock = None

    def on_enter(self):
        self._clock = Clock.schedule_interval(self._update, 1/60)

    def on_leave(self):
        if self._clock:
            self._clock.cancel()

    def _update(self, dt):
        self.canvas_widget.anim += dt
        self.canvas_widget.render()

    def on_touch_down(self, touch):
        w, h = Window.size
        btn_h = max(48, int(h * 0.065))
        bw = max(220, int(w * 0.55))
        margin = 12

        # Botão "POSSUIR NOVO CORPO" — centro em h*0.355
        revive_cy = h * 0.355
        if (revive_cy - btn_h//2 - margin) < touch.y < (revive_cy + btn_h//2 + margin):
            try:
                game = self.manager.get_screen('game')
                if game.player and game.world:
                    px = game.world.width // 2
                    py = game.world.height * 3 // 4
                    game.player.reviver(px, py)
                    game.new_game = False
                else:
                    game.new_game = True
                self.manager.current = 'game'
            except Exception:
                self.manager.current = 'game'
            return True

        # Botão "MENU PRINCIPAL" — centro em h*0.225
        menu_cy = h * 0.225
        if (menu_cy - btn_h//2 - margin) < touch.y < (menu_cy + btn_h//2 + margin):
            self.manager.current = 'menu'
            return True

        return super().on_touch_down(touch)


class DeathCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.anim = 0

    def render(self):
        self.canvas.clear()
        w, h = self.width, self.height
        t = self.anim
        with self.canvas:
            Color(0.02, 0.01, 0.01, 1)
            Rectangle(pos=(0, 0), size=(w, h))

            # Sangue escorrendo do topo
            for i in range(8):
                rx = w * (0.1 + i * 0.11 + 0.02*math.sin(t+i))
                altura = h * (0.5 + 0.3 * ((t*0.3+i*0.4) % 1.0))
                Color(0.4, 0.0, 0.0, 0.6)
                Line(points=[rx, h, rx, h-altura], width=3)

            # Texto morte
            alpha_fade = min(1.0, t * 0.5)
            Color(0.7, 0.05, 0.05, alpha_fade)
            self._txt('VOCÊ MORREU', w//2, h*0.67, 48, center=True)

            Color(0.6, 0.5, 0.4, alpha_fade * 0.8)
            self._txt('a consciência persiste...', w//2, h*0.58, 16, center=True)

            # Botão Reviver
            bw = max(220, int(w * 0.55))
            btn_h = max(48, int(h * 0.065))
            bx = w//2 - bw//2
            revive_cy = int(h * 0.355)
            by = revive_cy - btn_h//2
            Color(0.25, 0.0, 0.35, 0.85)
            RoundedRectangle(pos=(bx, by), size=(bw, btn_h), radius=[8])
            Color(0.5, 0.1, 0.7, 0.9)
            Line(rectangle=(bx, by, bw, btn_h), width=1.5)
            Color(0.85, 0.75, 0.95, 1)
            self._txt('POSSUIR NOVO CORPO', w//2, revive_cy, max(14, int(btn_h*0.35)), center=True)

            # Botão Menu
            menu_cy = int(h * 0.225)
            by2 = menu_cy - btn_h//2
            Color(0.12, 0.10, 0.08, 0.8)
            RoundedRectangle(pos=(bx, by2), size=(bw, btn_h), radius=[8])
            Color(0.4, 0.35, 0.25, 0.7)
            Line(rectangle=(bx, by2, bw, btn_h), width=1.2)
            Color(0.65, 0.60, 0.50, 0.9)
            self._txt('MENU PRINCIPAL', w//2, menu_cy, max(14, int(btn_h*0.35)), center=True)

            # Info perda
            Color(0.45, 0.40, 0.35, 0.6)
            self._txt('Perdeu progresso físico. Manteve experiência.', w//2, h*0.48, 11, center=True)

    def _txt(self, text, x, y, size, center=False):
        lbl = CoreLabel(text=str(text), font_size=size)
        lbl.refresh()
        tx = lbl.texture
        if center:
            Rectangle(texture=tx, pos=(x - tx.width//2, y - tx.height//2), size=tx.size)
        else:
            Rectangle(texture=tx, pos=(x, y), size=tx.size)


# ============================================================
# INVENTÁRIO
# ============================================================
class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False

    def on_enter(self):
        self.clear_widgets()
        self._build_ui()

    def _build_ui(self):
        game = self.manager.get_screen('game')
        player = game.player if game else None

        fl = FloatLayout()
        bg = Widget(size=Window.size, pos=(0, 0))
        with bg.canvas:
            Color(0.05, 0.04, 0.03, 0.97)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(0.4, 0.3, 0.1, 0.6)
            Line(rectangle=(15, 15, Window.width-30, Window.height-30), width=1.2)
        fl.add_widget(bg)

        # Título
        titulo = Widget(size=(Window.width, 60),
                        pos=(0, Window.height-70))
        with titulo.canvas:
            Color(0.85, 0.75, 0.5, 1)
            lbl = CoreLabel(text='INVENTÁRIO', font_size=24)
            lbl.refresh()
            Color(0.85, 0.75, 0.5, 1)
            Rectangle(texture=lbl.texture,
                      pos=(Window.width//2 - lbl.texture.width//2, Window.height-55),
                      size=lbl.texture.size)
        fl.add_widget(titulo)

        # Grid de items
        if player:
            y_off = Window.height - 90
            x_off = 20
            col_w = (Window.width - 40) // 3
            row_h = 65
            items_list = list(player.inventario.items())

            for i, (item_key, qtd) in enumerate(items_list):
                col = i % 3
                row = i // 3
                ix = x_off + col * col_w
                iy = y_off - row * row_h
                item_data = ITEMS.get(item_key, {})
                icone = item_data.get('icone', '📦')

                slot = ItemSlot(item_key=item_key, qtd=qtd, icone=icone,
                                item_data=item_data, player=player,
                                screen=self,
                                pos=(ix, iy-row_h), size=(col_w-8, row_h-6))
                fl.add_widget(slot)

            # Peso total
            peso_w = Widget(size=(Window.width, 30), pos=(0, 40))
            with peso_w.canvas:
                Color(0.6, 0.55, 0.45, 0.8)
                lbl2 = CoreLabel(text=f'Peso: {player.peso_inventario:.1f}kg / {player.capacidade_max}kg',
                                 font_size=12)
                lbl2.refresh()
                Rectangle(texture=lbl2.texture, pos=(20, 44), size=lbl2.texture.size)
            fl.add_widget(peso_w)

        # Botão fechar
        btn = CloseButton(pos=(Window.width//2-60, 8), size=(120, 36),
                          callback=self._fechar)
        fl.add_widget(btn)
        self.add_widget(fl)

    def _fechar(self):
        self.manager.current = 'game'


class ItemSlot(Widget):
    def __init__(self, item_key, qtd, icone, item_data, player, screen, **kwargs):
        super().__init__(**kwargs)
        self.item_key = item_key
        self.qtd = qtd
        self.icone = icone
        self.item_data = item_data
        self.player = player
        self.screen = screen
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.10, 0.08, 0.06, 0.9)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
            Color(0.3, 0.25, 0.15, 0.7)
            Line(rectangle=(*self.pos, *self.size), width=1)

            # Ícone
            lbl_i = CoreLabel(text=self.icone, font_size=22)
            lbl_i.refresh()
            Color(1, 1, 1, 0.9)
            Rectangle(texture=lbl_i.texture,
                      pos=(self.x+6, self.y+self.height//2-10), size=lbl_i.texture.size)

            # Nome
            lbl_n = CoreLabel(text=self.item_key.replace('_', ' '), font_size=10)
            lbl_n.refresh()
            Color(0.8, 0.75, 0.65, 0.9)
            Rectangle(texture=lbl_n.texture,
                      pos=(self.x+34, self.y+self.height-18), size=lbl_n.texture.size)

            # Qtd
            lbl_q = CoreLabel(text=f'x{self.qtd}', font_size=12)
            lbl_q.refresh()
            Color(0.7, 0.85, 0.5, 1)
            Rectangle(texture=lbl_q.texture,
                      pos=(self.x+self.width-30, self.y+4), size=lbl_q.texture.size)

            # Info (tipo)
            tipo = self.item_data.get('tipo', '')
            cor_tipo = {
                'comida': (0.7, 0.85, 0.4),
                'agua':   (0.4, 0.7, 0.9),
                'medico': (0.9, 0.4, 0.4),
                'arma':   (0.85, 0.5, 0.3),
                'arma_fogo': (0.9, 0.3, 0.2),
                'recurso':   (0.7, 0.65, 0.5),
            }.get(tipo, (0.6, 0.6, 0.6))
            lbl_t = CoreLabel(text=tipo, font_size=9)
            lbl_t.refresh()
            Color(*cor_tipo, 0.7)
            Rectangle(texture=lbl_t.texture,
                      pos=(self.x+34, self.y+5), size=lbl_t.texture.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Usar item ao tocar
            if self.player.usar_item(self.item_key):
                self.screen._build_ui()
            return True


class CloseButton(Widget):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        with self.canvas:
            Color(0.25, 0.20, 0.12, 0.9)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[6])
            Color(0.5, 0.45, 0.30, 0.8)
            Line(rectangle=(*self.pos, *self.size), width=1)
            lbl = CoreLabel(text='← Voltar', font_size=14)
            lbl.refresh()
            Color(0.85, 0.80, 0.65, 1)
            Rectangle(texture=lbl.texture,
                      pos=(self.x + self.width//2 - lbl.texture.width//2,
                           self.y + self.height//2 - lbl.texture.height//2),
                      size=lbl.texture.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()
            return True


# ============================================================
# DIÁRIO / HISTÓRICO
# ============================================================
class JournalScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self._build()

    def _build(self):
        game = self.manager.get_screen('game')
        player = game.player if game else None
        world = game.world if game else None

        fl = FloatLayout()
        bg = Widget(size=Window.size, pos=(0, 0))
        with bg.canvas:
            Color(0.04, 0.035, 0.025, 0.98)
            Rectangle(pos=(0, 0), size=Window.size)
            Color(0.35, 0.25, 0.08, 0.5)
            Line(rectangle=(15, 15, Window.width-30, Window.height-30), width=1)
        fl.add_widget(bg)

        # Título
        header = Widget(size=(Window.width, 50), pos=(0, Window.height-60))
        with header.canvas:
            Color(0.8, 0.68, 0.4, 1)
            lbl = CoreLabel(text='📖 DIÁRIO / HISTÓRICO', font_size=20)
            lbl.refresh()
            Rectangle(texture=lbl.texture,
                      pos=(Window.width//2 - lbl.texture.width//2, Window.height-50),
                      size=lbl.texture.size)
        fl.add_widget(header)

        # Conteúdo
        entries = []
        if player:
            entries += [(txt, (0.75, 0.72, 0.62)) for txt in player.diario[-30:]]
        if world:
            entries += [(txt, (0.55, 0.65, 0.50)) for txt in world.world_history[-20:]]

        y = Window.height - 80
        content = Widget(size=(Window.width, max(Window.height, len(entries)*22 + 80)),
                         pos=(0, 0))
        with content.canvas:
            for i, (txt, cor) in enumerate(reversed(entries)):
                Color(*cor, 0.9)
                lbl = CoreLabel(text=f"  {txt[:60]}", font_size=11)
                lbl.refresh()
                ey = y - i * 22
                if ey > 50:
                    Rectangle(texture=lbl.texture, pos=(15, ey), size=lbl.texture.size)
                    if i % 2 == 0:
                        Color(1, 1, 1, 0.02)
                        Rectangle(pos=(10, ey-2), size=(Window.width-20, 20))

        sv = ScrollView(size=(Window.width, Window.height-100), pos=(0, 50))
        sv.add_widget(content)
        fl.add_widget(sv)

        # Stats rápidas
        if player:
            stats_w = Widget(size=(Window.width, 45), pos=(0, 50))
            with stats_w.canvas:
                Color(0.08, 0.06, 0.04, 0.95)
                Rectangle(pos=(0, 50), size=(Window.width, 45))
                stats = (f"Nv.{player.nivel}  |  "
                         f"Mortes:{player.mortes}  |  "
                         f"Ajudados:{player.npcs_ajudados}  |  "
                         f"Rep:{player.reputacao_label}")
                Color(0.65, 0.60, 0.45, 0.9)
                lbl2 = CoreLabel(text=stats, font_size=10)
                lbl2.refresh()
                Rectangle(texture=lbl2.texture,
                          pos=(Window.width//2 - lbl2.texture.width//2, 62),
                          size=lbl2.texture.size)
            fl.add_widget(stats_w)

        # Botão fechar
        btn = CloseButton(pos=(Window.width//2-60, 8), size=(120, 36),
                          callback=lambda: setattr(self.manager, 'current', 'game'))
        fl.add_widget(btn)
        self.add_widget(fl)
