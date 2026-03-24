"""
ERMOS - Renderizador do Mapa
Pixel art estilo História dos Ermos com Kivy
"""
import math
from kivy.uix.widget import Widget
from kivy.graphics import (Color, Rectangle, Ellipse, Line,
                           RoundedRectangle, Triangle, Mesh)
from kivy.graphics.texture import Texture
from kivy.core.text import Label as CoreLabel
from src.constants import *


class GameRenderer(Widget):
    """Renderizador principal do jogo"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.world = None
        self.player = None
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.5    # escala dos tiles
        self.tile_px = int(TILE_SIZE * self.zoom)
        self.show_minimap = True
        self.anim_timer = 0
        self.particles = []   # efeitos visuais
        self.damage_flashes = []
        self.floating_texts = []

    def setup(self, world, player, npc_manager, zombie_manager):
        self.world = world
        self.player = player
        self.npc_manager = npc_manager
        self.zombie_manager = zombie_manager

    def update_camera(self):
        if not self.player:
            return
        tw = self.tile_px
        self.camera_x = self.player.x * tw - self.width / 2
        self.camera_y = self.player.y * tw - self.height / 2

    def world_to_screen(self, wx, wy):
        tx = wx * self.tile_px - self.camera_x
        ty = wy * self.tile_px - self.camera_y
        return tx, ty

    def update(self, dt):
        self.anim_timer += dt
        # Atualizar partículas
        self.particles = [p for p in self.particles if p['vida'] > 0]
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vida'] -= dt
        # Textos flutuantes
        self.floating_texts = [t for t in self.floating_texts if t['vida'] > 0]
        for t in self.floating_texts:
            t['y'] += 20 * dt
            t['vida'] -= dt

        self.update_camera()
        self.render()

    def render(self):
        if not self.world or not self.player:
            return
        self.canvas.clear()
        with self.canvas:
            # Fundo
            Color(0.04, 0.03, 0.02, 1)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

            self._render_tiles()
            self._render_estruturas()
            self._render_items_chao()
            self._render_zombies()
            self._render_npcs()
            self._render_player()
            self._render_particles()
            self._render_floating_texts()
            self._render_fog()
            self._render_weather_overlay()
            if self.show_minimap:
                self._render_minimap()

    def _render_tiles(self):
        if not self.world:
            return
        tw = self.tile_px
        # Calcula range visível
        cols = int(self.width / tw) + 3
        rows = int(self.height / tw) + 3
        start_x = max(0, int(self.camera_x / tw) - 1)
        start_y = max(0, int(self.camera_y / tw) - 1)
        end_x = min(self.world.width, start_x + cols)
        end_y = min(self.world.height, start_y + rows)

        light = self.world.light_level
        pulsating = 0.5 + 0.5 * math.sin(self.anim_timer * 2)

        for ty in range(start_y, end_y):
            for tx in range(start_x, end_x):
                tile = self.world.tiles[ty][tx]
                sx, sy = self.world_to_screen(tx, ty)

                if not tile.visitado:
                    Color(0, 0, 0, 1)
                    Rectangle(pos=(sx, sy), size=(tw, tw))
                    continue

                r, g, b = tile.cor
                if not tile.visivel:
                    r, g, b = r * 0.35, g * 0.35, b * 0.35
                else:
                    r = r * light
                    g = g * light
                    b = b * light

                # Animação de água
                if tile.tipo == 'agua':
                    wave = 0.8 + 0.1 * math.sin(self.anim_timer * 2 + tx * 0.5)
                    r, g, b = r * wave, g * wave, b * wave + 0.05

                Color(r, g, b, 1)
                Rectangle(pos=(sx, sy), size=(tw-1, tw-1))

                # Borda do tile para definição pixel art
                if tile.visivel:
                    Color(r*0.7, g*0.7, b*0.7, 0.3)
                    Line(rectangle=(sx, sy, tw-1, tw-1), width=0.5)

    def _render_estruturas(self):
        if not self.world:
            return
        tw = self.tile_px
        for ty in range(self.world.height):
            for tx in range(self.world.width):
                tile = self.world.tiles[ty][tx]
                if not tile.estrutura or not tile.visivel:
                    continue
                sx, sy = self.world_to_screen(tx, ty)
                est = tile.estrutura
                if est['tipo'] == 'fogueira':
                    # Chama animada
                    Color(0.9, 0.4, 0.1, 0.9)
                    flicker = 0.8 + 0.2 * math.sin(self.anim_timer * 8)
                    Ellipse(pos=(sx+tw*0.2, sy+tw*0.1), size=(tw*0.6*flicker, tw*0.7*flicker))
                    Color(1.0, 0.8, 0.1, 0.7)
                    Ellipse(pos=(sx+tw*0.3, sy+tw*0.2), size=(tw*0.4*flicker, tw*0.5*flicker))
                    # Luz ao redor
                    Color(0.9, 0.5, 0.1, 0.05 * flicker)
                    Ellipse(pos=(sx-tw, sy-tw), size=(tw*4, tw*4))
                elif est['tipo'] == 'poco':
                    Color(0.3, 0.3, 0.4, 1)
                    Rectangle(pos=(sx+tw*0.1, sy+tw*0.1), size=(tw*0.8, tw*0.8))
                    Color(0.1, 0.2, 0.5, 1)
                    Ellipse(pos=(sx+tw*0.2, sy+tw*0.2), size=(tw*0.6, tw*0.6))

    def _render_items_chao(self):
        if not self.world:
            return
        tw = self.tile_px
        bounce = math.sin(self.anim_timer * 3) * 2
        for ty in range(max(0, int(self.camera_y/tw)-1),
                        min(self.world.height, int((self.camera_y+self.height)/tw)+2)):
            for tx in range(max(0, int(self.camera_x/tw)-1),
                            min(self.world.width, int((self.camera_x+self.width)/tw)+2)):
                tile = self.world.tiles[ty][tx]
                if not tile.item or not tile.visivel:
                    continue
                sx, sy = self.world_to_screen(tx, ty)
                # Brilho do item
                Color(0.9, 0.85, 0.3, 0.6 + 0.2 * math.sin(self.anim_timer * 4))
                Ellipse(pos=(sx+tw*0.25, sy+tw*0.25+bounce*0.5), size=(tw*0.5, tw*0.5))
                Color(1, 1, 0.5, 0.9)
                Ellipse(pos=(sx+tw*0.3, sy+tw*0.3+bounce*0.5), size=(tw*0.4, tw*0.4))

    def _render_zombies(self):
        if not hasattr(self, 'zombie_manager'):
            return
        tw = self.tile_px
        for z in self.zombie_manager.zombies:
            sx, sy = self.world_to_screen(z.x, z.y)
            tile = self.world.get_tile(int(z.x), int(z.y))
            if not tile or not tile.visivel:
                continue

            r, g, b, a = z.cor
            # Corpo
            Color(r, g, b, a)
            bx = sx - tw*0.3
            by = sy - tw*0.1
            bw = tw * 0.6
            bh = tw * 0.7
            Rectangle(pos=(bx, by), size=(bw, bh))

            # Cabeça
            Color(r*1.1, g*1.1, b*0.8, 1)
            Ellipse(pos=(sx-tw*0.2, sy+tw*0.45), size=(tw*0.4, tw*0.4))

            # Olhos vermelhos
            Color(0.9, 0.1, 0.1, 1)
            Ellipse(pos=(sx-tw*0.15, sy+tw*0.55), size=(tw*0.1, tw*0.1))
            Ellipse(pos=(sx+tw*0.05, sy+tw*0.55), size=(tw*0.1, tw*0.1))

            # HP bar
            hp_ratio = z.hp / z.hp_max
            Color(0.2, 0.0, 0.0, 0.8)
            Rectangle(pos=(bx, by+bh+2), size=(bw, 4))
            Color(0.8, 0.1, 0.1, 0.9)
            Rectangle(pos=(bx, by+bh+2), size=(bw*hp_ratio, 4))

            # Supremo tem efeito especial
            if z.tipo == 'supremo':
                pulse = abs(math.sin(self.anim_timer * 3))
                Color(0.8, 0.0, 0.0, 0.2 * pulse)
                Ellipse(pos=(sx-tw, sy-tw), size=(tw*3, tw*3))

    def _render_npcs(self):
        if not hasattr(self, 'npc_manager'):
            return
        tw = self.tile_px
        for npc in self.npc_manager.npcs:
            sx, sy = self.world_to_screen(npc.x, npc.y)
            tile = self.world.get_tile(int(npc.x), int(npc.y))
            if not tile or not tile.visivel:
                continue

            if npc.morto:
                # Corpo no chão
                Color(0.4, 0.3, 0.25, 0.7)
                Rectangle(pos=(sx-tw*0.35, sy-tw*0.1), size=(tw*0.7, tw*0.25))
                if hasattr(npc, 'pode_ser_possuido'):
                    # Brilho de possessão disponível
                    Color(0.5, 0.2, 0.8, 0.3 + 0.2*math.sin(self.anim_timer*3))
                    Ellipse(pos=(sx-tw*0.4, sy-tw*0.15), size=(tw*0.8, tw*0.35))
                continue

            # Skin base (cores por gênero/ocupação)
            skin_map = {
                'medico':     (0.85, 0.85, 0.92),
                'soldado':    (0.25, 0.35, 0.22),
                'coletor':    (0.55, 0.42, 0.28),
                'construtor': (0.50, 0.38, 0.22),
                'comerciante':(0.65, 0.55, 0.30),
            }
            r, g, b = skin_map.get(npc.ocupacao, (0.60, 0.48, 0.32))

            # Pernas
            Color(r*0.7, g*0.7, b*0.6, 1)
            walk = math.sin(self.anim_timer * 6) * 2 if npc.estado == 'trabalhando' else 0
            Rectangle(pos=(sx-tw*0.2, sy-tw*0.1), size=(tw*0.18, tw*0.35))
            Rectangle(pos=(sx+tw*0.02, sy-tw*0.1+walk), size=(tw*0.18, tw*0.35))

            # Corpo
            Color(r, g, b, 1)
            Rectangle(pos=(sx-tw*0.22, sy+tw*0.2), size=(tw*0.44, tw*0.35))

            # Cabeça
            skin_face = (0.82, 0.65, 0.48) if npc.genero == 'M' else (0.87, 0.70, 0.55)
            Color(*skin_face, 1)
            Ellipse(pos=(sx-tw*0.18, sy+tw*0.5), size=(tw*0.36, tw*0.36))

            # Olhos
            Color(0.1, 0.08, 0.05, 1)
            Ellipse(pos=(sx-tw*0.1, sy+tw*0.60), size=(tw*0.07, tw*0.07))
            Ellipse(pos=(sx+tw*0.03, sy+tw*0.60), size=(tw*0.07, tw*0.07))

            # Emoção visível (medo = tremor, raiva = vermelho)
            if npc.emocoes.get('medo', 0) > 50:
                shake = math.sin(self.anim_timer * 15) * 1.5
                Color(0.9, 0.9, 1.0, 0.3)
                Ellipse(pos=(sx-tw*0.3+shake, sy-tw*0.2), size=(tw*0.6, tw*0.9))
            elif npc.emocoes.get('raiva', 0) > 50:
                Color(0.8, 0.1, 0.1, 0.2)
                Ellipse(pos=(sx-tw*0.3, sy-tw*0.2), size=(tw*0.6, tw*0.9))

            # Dormindo
            if npc.dormindo:
                Color(0.8, 0.9, 1.0, 0.6)
                # "zzz" effect
                z_size = tw * 0.12
                Color(0.9, 0.95, 1.0, 0.8)
                Ellipse(pos=(sx+tw*0.15, sy+tw*0.75), size=(z_size, z_size))

    def _render_player(self):
        if not self.player:
            return
        tw = self.tile_px
        p = self.player
        sx, sy = self.world_to_screen(p.x, p.y)

        if p.morto:
            Color(0.4, 0.3, 0.25, 0.5)
            Rectangle(pos=(sx-tw*0.4, sy), size=(tw*0.8, tw*0.2))
            return

        t = self.anim_timer

        # === CAMINHO SOMBRIO: aparência muda ===
        if p.caminho == 'sombrio':
            aura_alpha = 0.15 + 0.1 * math.sin(t * 2)
            Color(0.5, 0.0, 0.5, aura_alpha)
            Ellipse(pos=(sx-tw*0.8, sy-tw*0.4), size=(tw*2.0, tw*2.0))

        # Possessão: mostra no corpo hospedeiro
        if p.possuindo and p.corpo_possuido:
            host = p.corpo_possuido
            hsx, hsy = self.world_to_screen(host.x, host.y)
            Color(0.5, 0.2, 0.9, 0.4 + 0.2*math.sin(t*5))
            Ellipse(pos=(hsx-tw*0.5, hsy-tw*0.3), size=(tw*1.0, tw*1.3))
            return

        # === RENDER NORMAL DO PLAYER ===
        # Sombra
        Color(0, 0, 0, 0.3)
        Ellipse(pos=(sx-tw*0.25, sy-tw*0.05), size=(tw*0.5, tw*0.15))

        # Pernas animadas
        walk_anim = math.sin(t * 7) * 3 if (p.correndo or p.ultimo_movimento) else 0
        leg_color = (0.22, 0.22, 0.32) if p.caminho != 'sombrio' else (0.12, 0.02, 0.12)
        Color(*leg_color, 1)
        Rectangle(pos=(sx-tw*0.22, sy-tw*0.12+walk_anim), size=(tw*0.18, tw*0.38))
        Rectangle(pos=(sx+tw*0.04, sy-tw*0.12-walk_anim), size=(tw*0.18, tw*0.38))

        # Corpo
        body_color = (0.25, 0.35, 0.45) if p.caminho != 'sombrio' else (0.15, 0.02, 0.18)
        Color(*body_color, 1)
        Rectangle(pos=(sx-tw*0.25, sy+tw*0.18), size=(tw*0.50, tw*0.40))

        # Braços
        Color(*body_color, 0.9)
        Rectangle(pos=(sx-tw*0.38, sy+tw*0.22), size=(tw*0.14, tw*0.28))
        Rectangle(pos=(sx+tw*0.24, sy+tw*0.22), size=(tw*0.14, tw*0.28))

        # Cabeça
        face_color = (0.80, 0.65, 0.50)
        if p.caminho == 'sombrio':
            face_color = (0.55, 0.40, 0.50)
        Color(*face_color, 1)
        Ellipse(pos=(sx-tw*0.20, sy+tw*0.53), size=(tw*0.40, tw*0.40))

        # Olhos — mudam com humanidade
        if p.humanidade > 50:
            Color(0.2, 0.4, 0.7, 1)
        else:
            Color(0.6, 0.1, 0.6, 1)
        Ellipse(pos=(sx-tw*0.12, sy+tw*0.62), size=(tw*0.08, tw*0.08))
        Ellipse(pos=(sx+tw*0.04, sy+tw*0.62), size=(tw*0.08, tw*0.08))

        # Arma equipada (visualização simples)
        if p.arma_equipada:
            Color(0.5, 0.4, 0.3, 0.9)
            Line(points=[sx+tw*0.25, sy+tw*0.28, sx+tw*0.55, sy+tw*0.38], width=2)

        # Invulnerabilidade flash
        if p.invulneravel_timer > 0:
            Color(1, 1, 1, 0.4)
            Ellipse(pos=(sx-tw*0.35, sy-tw*0.15), size=(tw*0.8, tw*1.1))

        # Alucinações
        if p.sanidade < 30 and math.sin(t * 10) > 0.8:
            Color(0.5, 0.0, 0.5, 0.15)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

    def _render_particles(self):
        for p in self.particles:
            a = p['vida'] / p['vida_max']
            Color(*p['cor'], a)
            Ellipse(pos=(p['x']-p['r'], p['y']-p['r']), size=(p['r']*2, p['r']*2))

    def _render_floating_texts(self):
        for ft in self.floating_texts:
            a = min(1.0, ft['vida'])
            Color(*ft['cor'], a)
            lbl = CoreLabel(text=ft['text'], font_size=ft.get('size', 14))
            lbl.refresh()
            Rectangle(texture=lbl.texture,
                      pos=(ft['x'] - lbl.texture.width//2, ft['y']),
                      size=lbl.texture.size)

    def _render_fog(self):
        """Overlay de escuridão noturna e névoa"""
        if not self.world:
            return
        light = self.world.light_level
        if light < 1.0:
            Color(0, 0, 0, (1 - light) * 0.75)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

        # Vinheta
        for i in range(4):
            alpha = 0.15 - i * 0.03
            margin = i * 30
            Color(0, 0, 0, alpha)
            Line(rectangle=(margin, margin, self.width-2*margin, self.height-2*margin), width=30-i*6)

    def _render_weather_overlay(self):
        if not self.world:
            return
        clima = self.world.weather
        t = self.anim_timer
        if clima == 'chuva' or clima == 'tempestade':
            intensidade = 0.15 if clima == 'chuva' else 0.3
            Color(0.5, 0.6, 0.8, intensidade)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
            # Gotas
            Color(0.6, 0.7, 0.9, 0.4)
            for i in range(20):
                rx = (i * 137 + t * 150) % self.width
                ry = (i * 73 + t * 300) % self.height
                Line(points=[rx, ry, rx-2, ry-12], width=1)
        elif clima == 'neve':
            Color(0.9, 0.95, 1.0, 0.1)
            Rectangle(pos=(0, 0), size=(self.width, self.height))
            Color(1, 1, 1, 0.6)
            for i in range(15):
                sx = (i * 89 + t * 20) % self.width
                sy = (i * 61 + t * 40) % self.height
                Ellipse(pos=(sx, sy), size=(3, 3))
        elif clima == 'neblina':
            Color(0.7, 0.75, 0.8, 0.25)
            Rectangle(pos=(0, 0), size=(self.width, self.height))

    def _render_minimap(self):
        if not self.world:
            return
        mm_size = 100
        mm_x = self.width - mm_size - 10
        mm_y = self.height - mm_size - 10
        tw = mm_size / self.world.width

        # Fundo
        Color(0, 0, 0, 0.7)
        RoundedRectangle(pos=(mm_x-2, mm_y-2), size=(mm_size+4, mm_size+4), radius=[4])

        # Tiles visitados
        for ty in range(0, self.world.height, 2):
            for tx in range(0, self.world.width, 2):
                tile = self.world.tiles[ty][tx]
                if not tile.visitado:
                    continue
                r, g, b = tile.cor
                if not tile.visivel:
                    r, g, b = r*0.4, g*0.4, b*0.4
                Color(r, g, b, 1)
                Rectangle(pos=(mm_x + tx*tw, mm_y + ty*tw), size=(max(1, tw*2), max(1, tw*2)))

        # NPCs
        for npc in self.npc_manager.npcs:
            if npc.vivo:
                Color(0.3, 0.8, 0.3, 0.9)
                Ellipse(pos=(mm_x+npc.x*tw-1, mm_y+npc.y*tw-1), size=(3, 3))

        # Zumbis
        for z in self.zombie_manager.get_zombies_vivos():
            Color(0.8, 0.2, 0.2, 0.8)
            Ellipse(pos=(mm_x+z.x*tw-1, mm_y+z.y*tw-1), size=(2, 2))

        # Player
        Color(1, 0.9, 0.2, 1)
        Ellipse(pos=(mm_x+self.player.x*tw-2, mm_y+self.player.y*tw-2), size=(5, 5))

        # Borda
        Color(0.5, 0.45, 0.35, 0.8)
        Line(rectangle=(mm_x, mm_y, mm_size, mm_size), width=1)

    def add_particle_burst(self, wx, wy, cor, n=8):
        sx, sy = self.world_to_screen(wx, wy)
        import random
        for _ in range(n):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(30, 80)
            self.particles.append({
                'x': sx, 'y': sy,
                'vx': math.cos(angle)*speed,
                'vy': math.sin(angle)*speed,
                'cor': cor[:3],
                'r': random.uniform(2, 5),
                'vida': random.uniform(0.3, 0.8),
                'vida_max': 0.8,
            })

    def add_floating_text(self, wx, wy, text, cor=(1,1,1), size=14):
        sx, sy = self.world_to_screen(wx, wy)
        self.floating_texts.append({
            'x': sx, 'y': sy + 20,
            'text': text, 'cor': cor,
            'size': size, 'vida': 1.5,
        })
