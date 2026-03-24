"""
ERMOS - HUD (Interface do Jogador)
Barras de status, alertas, diálogos, inventário overlay
"""
import math
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.text import Label as CoreLabel
from src.constants import *


class HUD(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = None
        self.world = None
        self.mensagens = []     # mensagens temporárias no topo
        self.dialogo_ativo = None
        self.anim_timer = 0
        self.alert_pulse = 0

    def setup(self, player, world):
        self.player = player
        self.world = world

    def update(self, dt):
        self.anim_timer += dt
        self.alert_pulse = abs(math.sin(self.anim_timer * 3))
        # Remove mensagens antigas
        self.mensagens = [(txt, t-dt, cor) for txt, t, cor in self.mensagens if t > 0]
        self.render()

    def render(self):
        if not self.player or not self.world:
            return
        self.canvas.clear()
        with self.canvas:
            self._render_status_bars()
            self._render_info_top()
            self._render_mensagens()
            self._render_dialogo()
            self._render_alucinacoes()
            self._render_possessao_overlay()

    def _render_status_bars(self):
        p = self.player
        # Painel inferior esquerdo
        px_off = 12
        py_off = 12
        bar_w = 120
        bar_h = 10
        gap = 14

        # Fundo do painel
        Color(0, 0, 0, 0.6)
        RoundedRectangle(pos=(px_off-4, py_off-4), size=(bar_w+24, gap*6+12), radius=[6])

        bars = [
            ('HP',       p.hp,       p.hp_max,    (0.8, 0.15, 0.15)),
            ('Energia',  p.stamina,  p.stamina_max,(0.3, 0.7,  0.3)),
            ('Fome',     p.fome,     100,           (0.75, 0.55, 0.1)),
            ('Sede',     p.sede,     100,           (0.2, 0.5,  0.8)),
            ('Sanidade', p.sanidade, 100,           (0.6, 0.3,  0.7)),
            ('Humano',   p.humanidade,100,          (0.9, 0.75, 0.3)),
        ]

        for i, (nome, val, maximo, cor) in enumerate(bars):
            y = py_off + i * gap
            ratio = max(0, min(1, val / maximo))

            # Label
            self._draw_text(nome, px_off, y+1, size=9, cor=(0.7, 0.65, 0.55))

            # Barra fundo
            Color(0.12, 0.10, 0.08, 0.9)
            Rectangle(pos=(px_off+42, y), size=(bar_w, bar_h))

            # Barra valor
            # Pulsa quando crítico
            r, g, b = cor
            if ratio < 0.25:
                r = r * (0.7 + 0.3 * self.alert_pulse)
            Color(r, g, b, 0.9)
            Rectangle(pos=(px_off+42, y), size=(bar_w * ratio, bar_h))

            # Valor numérico
            self._draw_text(f"{int(val)}", px_off+44+bar_w, y+1, size=9, cor=(0.6, 0.55, 0.45))

    def _render_info_top(self):
        if not self.world:
            return
        w = self.width
        # Painel central topo
        Color(0, 0, 0, 0.55)
        RoundedRectangle(pos=(w//2-110, self.height-44), size=(220, 36), radius=[6])

        # Hora do dia
        h = int(self.world.time_of_day)
        m = int((self.world.time_of_day % 1) * 60)
        periodo = '🌙' if self.world.is_night else '☀️'
        hora_txt = f"{periodo} {h:02d}:{m:02d}  Dia {self.world.day_count}"
        self._draw_text(hora_txt, w//2, self.height-32, size=13,
                        cor=(0.9, 0.85, 0.7), center=True)

        # Clima
        icones_clima = {
            'claro':'☀️','nublado':'⛅','chuva':'🌧️',
            'tempestade':'⛈️','neve':'❄️','neblina':'🌫️'
        }
        clima_icon = icones_clima.get(self.world.weather, '')
        self._draw_text(clima_icon, w//2+80, self.height-32, size=13,
                        cor=(0.8, 0.8, 0.8), center=True)

        # Reputação e caminho
        rep = self.player.reputacao_label
        caminho_cor = {
            'humano':  (0.6, 0.9, 0.6),
            'sombrio': (0.8, 0.2, 0.8),
            'neutro':  (0.7, 0.7, 0.7),
        }.get(self.player.caminho, (0.7, 0.7, 0.7))

        Color(0, 0, 0, 0.5)
        RoundedRectangle(pos=(w-155, self.height-44), size=(148, 36), radius=[6])
        self._draw_text(f"[{rep}]", w-80, self.height-32, size=11,
                        cor=caminho_cor, center=True)

        # Nível e XP
        Color(0, 0, 0, 0.5)
        RoundedRectangle(pos=(8, self.height-44), size=(120, 36), radius=[6])
        self._draw_text(f"Nv.{self.player.nivel}  {self.player.xp}xp",
                        60, self.height-32, size=12,
                        cor=(0.85, 0.75, 0.35), center=True)

        # Doenças
        if self.player.doencas:
            Color(0.8, 0.1, 0.1, 0.8 * self.alert_pulse)
            RoundedRectangle(pos=(w//2-50, self.height-70), size=(100, 20), radius=[4])
            nomes = ', '.join(d['tipo'] for d in self.player.doencas[:2])
            self._draw_text(f"⚠️ {nomes}", w//2, self.height-62, size=10,
                            cor=(1, 0.9, 0.9), center=True)

        # Procurado
        if self.player.procurado:
            Color(0.8, 0.1, 0.1, 0.7 * self.alert_pulse)
            RoundedRectangle(pos=(w//2-70, self.height-95), size=(140, 22), radius=[4])
            self._draw_text(f"🔴 PROCURADO ${self.player.recompensa}",
                            w//2, self.height-86, size=11,
                            cor=(1, 0.8, 0.8), center=True)

    def _render_mensagens(self):
        """Mensagens flutuantes no canto direito"""
        x = self.width - 220
        y = self.height - 100
        for i, (txt, t, cor) in enumerate(reversed(self.mensagens[-5:])):
            alpha = min(1.0, t / 0.5)
            Color(0, 0, 0, 0.5 * alpha)
            RoundedRectangle(pos=(x-6, y-i*22-4), size=(210, 20), radius=[4])
            self._draw_text(txt, x, y-i*22+2, size=11,
                            cor=(*cor[:3], alpha))

    def _render_dialogo(self):
        if not self.dialogo_ativo:
            return
        d = self.dialogo_ativo
        # Painel de diálogo na parte inferior
        dw = self.width - 40
        dh = 160
        dx = 20
        dy = 10

        Color(0.06, 0.05, 0.04, 0.95)
        RoundedRectangle(pos=(dx, dy), size=(dw, dh), radius=[8])
        Color(0.4, 0.3, 0.1, 0.8)
        Line(rectangle=(dx, dy, dw, dh), width=1.2, cap='round')

        # Nome do NPC
        self._draw_text(d.get('nome', 'Desconhecido'),
                        dx+15, dy+dh-22, size=13, cor=(0.85, 0.7, 0.4))

        # Fala
        fala = d.get('fala', '')
        self._draw_text_wrapped(fala, dx+15, dy+dh-50, dw-30, size=11,
                                cor=(0.8, 0.78, 0.72))

        # Opções
        opcoes = d.get('opcoes', [])
        for i, op in enumerate(opcoes[:4]):
            oy = dy + 12 + i * 28
            ox = dx + 15
            Color(0.15, 0.12, 0.08, 0.9)
            RoundedRectangle(pos=(ox-4, oy-4), size=(dw//2-20, 24), radius=[4])
            self._draw_text(f"[{i+1}] {op}", ox, oy+3, size=11, cor=(0.75, 0.80, 0.75))

    def _render_alucinacoes(self):
        if not self.player:
            return
        if self.player.sanidade < 20 and self.player.alucinacoes_ativas:
            # Borda vermelha/roxa pulsando
            pulse = self.alert_pulse
            Color(0.4, 0.0, 0.4, 0.15 * pulse)
            Line(rectangle=(0, 0, self.width, self.height), width=12)
            Color(0.6, 0.0, 0.2, 0.08 * pulse)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            if self.player.alucinacoes_ativas:
                txt = self.player.alucinacoes_ativas[-1]
                self._draw_text(txt, self.width//2, self.height//2,
                                size=13, cor=(0.8, 0.3, 0.8, 0.7), center=True)

    def _render_possessao_overlay(self):
        if not self.player or not self.player.possuindo:
            return
        t_ratio = self.player.timer_possessao / POSSESSION_DURATION_MAX
        pulse = abs(math.sin(self.anim_timer * 4))

        # Borda roxa indicando possessão
        Color(0.4, 0.1, 0.7, 0.3 * pulse)
        Line(rectangle=(0, 0, self.width, self.height), width=8)

        # Timer de possessão
        bar_w = 200
        bx = self.width//2 - bar_w//2
        by = self.height - 75

        Color(0, 0, 0, 0.7)
        RoundedRectangle(pos=(bx-4, by-4), size=(bar_w+8, 20), radius=[6])
        Color(0.5, 0.1, 0.8, 0.9)
        Rectangle(pos=(bx, by), size=(bar_w * t_ratio, 12))
        self._draw_text("POSSESSÃO ATIVA",
                        self.width//2, by+2, size=10,
                        cor=(0.8, 0.5, 1.0), center=True)

        # Memórias alheias surgindo
        if self.player.confusao_identidade > 30:
            mem = self.player.memorias_alheias
            if mem:
                ultima = mem[-1]
                self._draw_text(f'"{ultima["texto"][:40]}..."',
                                self.width//2, self.height//2 - 40,
                                size=11, cor=(0.7, 0.5, 0.9, 0.6), center=True)

    def _draw_text(self, texto, x, y, size=12, cor=(1,1,1), center=False):
        lbl = CoreLabel(text=str(texto), font_size=size,
                        color=cor if len(cor) == 4 else (*cor, 1))
        lbl.refresh()
        tx = lbl.texture
        if center:
            Color(*cor[:3], cor[3] if len(cor)==4 else 1)
            Rectangle(texture=tx, pos=(x - tx.width//2, y - tx.height//2), size=tx.size)
        else:
            Color(*cor[:3], cor[3] if len(cor)==4 else 1)
            Rectangle(texture=tx, pos=(x, y), size=tx.size)

    def _draw_text_wrapped(self, texto, x, y, max_w, size=11, cor=(1,1,1)):
        """Texto com quebra de linha simples"""
        palavras = texto.split(' ')
        linha = ''
        linha_y = y
        for palavra in palavras:
            teste = linha + palavra + ' '
            lbl = CoreLabel(text=teste, font_size=size)
            lbl.refresh()
            if lbl.texture.width > max_w and linha:
                self._draw_text(linha.strip(), x, linha_y, size=size, cor=cor)
                linha_y -= size + 3
                linha = palavra + ' '
            else:
                linha = teste
        if linha.strip():
            self._draw_text(linha.strip(), x, linha_y, size=size, cor=cor)

    def adicionar_mensagem(self, texto, cor=(0.9, 0.85, 0.7), duracao=3.0):
        self.mensagens.append((texto, duracao, cor))

    def mostrar_dialogo(self, npc_nome, fala, opcoes):
        self.dialogo_ativo = {
            'nome': npc_nome,
            'fala': fala,
            'opcoes': opcoes,
        }

    def fechar_dialogo(self):
        self.dialogo_ativo = None
