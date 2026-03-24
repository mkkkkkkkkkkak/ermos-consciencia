"""
ERMOS - Sistema de Geração de Mundo
Gera mapa procedural com biomas, estruturas e eventos
"""
import random
import math
from src.constants import *


class Tile:
    def __init__(self, tipo, passavel=True, opaco=False):
        self.tipo = tipo
        self.passavel = passavel
        self.opaco = opaco
        self.visitado = False
        self.visivel = False
        self.item = None
        self.estrutura = None
        # Cor para renderização pixel
        self.cor = self._cor_por_tipo()

    def _cor_por_tipo(self):
        cores = {
            'grama':        (0.15, 0.22, 0.10),
            'terra':        (0.30, 0.22, 0.12),
            'asfalto':      (0.18, 0.17, 0.16),
            'concreto':     (0.28, 0.27, 0.25),
            'agua':         (0.10, 0.20, 0.35),
            'areia':        (0.55, 0.48, 0.32),
            'neve':         (0.85, 0.88, 0.92),
            'lama':         (0.25, 0.20, 0.12),
            'parede':       (0.22, 0.20, 0.18),
            'tijolo':       (0.38, 0.20, 0.12),
            'metal':        (0.30, 0.30, 0.28),
            'madeira_ch':   (0.35, 0.25, 0.12),
            'sangue':       (0.40, 0.05, 0.05),
            'floresta_d':   (0.08, 0.15, 0.06),
            'floresta_c':   (0.12, 0.20, 0.08),
            'pedra':        (0.32, 0.30, 0.28),
            'arvore':       (0.10, 0.18, 0.06),
        }
        return cores.get(self.tipo, (0.2, 0.2, 0.2))


class World:
    def __init__(self, seed=None):
        self.seed = seed or random.randint(0, 999999)
        random.seed(self.seed)
        self.width = MAP_W
        self.height = MAP_H
        self.tiles = []
        self.time_of_day = 6.0   # hora do dia (0-24)
        self.day_count = 1
        self.weather = 'claro'
        self.weather_timer = 0
        self.events_queue = []
        self.active_events = []
        self.npcs = []
        self.zombies = []
        self.items_world = []
        self.structures = []
        self.hordas_ativas = []
        self.virus_evolution = 0   # 0-100, muda comportamento zumbis
        self.world_history = []    # registro de eventos importantes
        self.generate()

    def generate(self):
        """Gera o mundo proceduralmente"""
        self.tiles = [[Tile('grama') for _ in range(self.width)] for _ in range(self.height)]
        self._gen_noise()
        self._gen_biomes()
        self._gen_cidade()
        self._gen_floresta()
        self._gen_zona_militar()
        self._gen_vila_inicial()
        self._gen_ocean_islands()
        self._scatter_items()

    def _gen_noise(self):
        """Perlin noise simplificado para altura do terreno"""
        self.heightmap = [[0.0]*self.width for _ in range(self.height)]
        scale = 12.0
        for y in range(self.height):
            for x in range(self.width):
                nx = x / self.width * scale
                ny = y / self.height * scale
                v = (math.sin(nx*1.5 + 0.3) * math.cos(ny*1.2 + 0.7) +
                     math.sin(nx*3.1 + 1.1) * math.cos(ny*2.8 + 0.4) * 0.5 +
                     math.sin(nx*6.0 + 0.8) * math.cos(ny*5.5 + 1.3) * 0.25)
                self.heightmap[y][x] = (v + 1.75) / 3.5

    def _gen_biomes(self):
        for y in range(self.height):
            for x in range(self.width):
                h = self.heightmap[y][x]
                if h < 0.25:
                    self.tiles[y][x] = Tile('agua', passavel=False)
                elif h < 0.35:
                    self.tiles[y][x] = Tile('areia')
                elif h < 0.55:
                    self.tiles[y][x] = Tile('grama')
                elif h < 0.70:
                    self.tiles[y][x] = Tile('terra')
                elif h < 0.85:
                    self.tiles[y][x] = Tile('pedra')
                else:
                    self.tiles[y][x] = Tile('neve')

    def _gen_cidade(self):
        """Gera região de cidade destruída no centro-norte"""
        cx, cy = self.width // 2, self.height // 4
        for _ in range(25):
            bx = cx + random.randint(-18, 18)
            by = cy + random.randint(-12, 12)
            bw = random.randint(3, 8)
            bh = random.randint(3, 8)
            self._place_building(bx, by, bw, bh, 'tijolo' if random.random() > 0.4 else 'concreto')
        # Ruas
        for x in range(cx-20, cx+20):
            if 0 < x < self.width:
                for y in range(cy-14, cy+14):
                    if 0 < y < self.height:
                        if x % 7 == 0 or y % 7 == 0:
                            if self.tiles[y][x].tipo not in ['agua']:
                                self.tiles[y][x] = Tile('asfalto')

    def _place_building(self, bx, by, bw, bh, material):
        for dy in range(bh):
            for dx in range(bw):
                x, y = bx+dx, by+dy
                if 0 < x < self.width-1 and 0 < y < self.height-1:
                    if dx == 0 or dx == bw-1 or dy == 0 or dy == bh-1:
                        self.tiles[y][x] = Tile(material, passavel=False, opaco=True)
                    else:
                        self.tiles[y][x] = Tile('concreto')
        # Porta aleatória
        lado = random.randint(0, 3)
        if lado == 0 and bh > 2:
            px = bx + random.randint(1, bw-2)
            self.tiles[by][px] = Tile('madeira_ch')
        elif lado == 1:
            px = bx + random.randint(1, bw-2)
            self.tiles[by+bh-1][px] = Tile('madeira_ch')

    def _gen_floresta(self):
        """Gera floresta densa no oeste"""
        fx, fy = self.width // 5, self.height // 2
        for y in range(fy-20, fy+20):
            for x in range(fx-15, fx+15):
                if 0 < x < self.width and 0 < y < self.height:
                    if self.tiles[y][x].tipo not in ['agua']:
                        if random.random() > 0.3:
                            t = Tile('floresta_d' if random.random() > 0.4 else 'floresta_c',
                                     passavel=random.random() > 0.2,
                                     opaco=True)
                            self.tiles[y][x] = t

    def _gen_zona_militar(self):
        """Zona militar no leste"""
        mx, my = self.width * 3 // 4, self.height // 3
        # Cerca
        for dx in range(-12, 13):
            for dy in range(-10, 11):
                x, y = mx+dx, my+dy
                if 0 < x < self.width and 0 < y < self.height:
                    if abs(dx) == 12 or abs(dy) == 10:
                        self.tiles[y][x] = Tile('metal', passavel=False, opaco=True)
                    elif self.tiles[y][x].tipo not in ['agua']:
                        self.tiles[y][x] = Tile('concreto')
        # Bunkers
        for _ in range(4):
            bx = mx + random.randint(-9, 9)
            by = my + random.randint(-7, 7)
            self._place_building(bx, by, random.randint(3,5), random.randint(3,4), 'metal')
        # Porta
        self.tiles[my-10][mx] = Tile('metal')

    def _gen_vila_inicial(self):
        """Vila inicial no sul - ponto de início do jogador"""
        vx, vy = self.width // 2, self.height * 3 // 4
        for _ in range(6):
            bx = vx + random.randint(-10, 10)
            by = vy + random.randint(-8, 8)
            self._place_building(bx, by, random.randint(3,5), random.randint(3,4), 'madeira_ch')
        # Fogueira central
        self.tiles[vy][vx].estrutura = {'tipo': 'fogueira', 'ativa': True}
        # Poço
        self.tiles[vy+2][vx+1].estrutura = {'tipo': 'poco', 'agua': 100}

    def _gen_ocean_islands(self):
        """Bordas são oceano, com ilhas espalhadas"""
        for y in range(self.height):
            for x in range(self.width):
                dist_borda = min(x, y, self.width-1-x, self.height-1-y)
                if dist_borda < 6:
                    self.tiles[y][x] = Tile('agua', passavel=False)
        # Ilhas raras
        for _ in range(3):
            ix = random.randint(8, self.width-8)
            iy = random.randint(8, self.height-8)
            if self.tiles[iy][ix].tipo == 'agua':
                for dy in range(-4, 5):
                    for dx in range(-4, 5):
                        if dx*dx + dy*dy < 16:
                            nx, ny = ix+dx, iy+dy
                            if 0 < nx < self.width and 0 < ny < self.height:
                                self.tiles[ny][nx] = Tile('areia')

    def _scatter_items(self):
        """Espalha itens pelo mundo"""
        item_list = list(ITEMS.keys())
        for _ in range(200):
            x = random.randint(1, self.width-2)
            y = random.randint(1, self.height-2)
            if self.tiles[y][x].passavel and self.tiles[y][x].item is None:
                item_key = random.choice(item_list)
                qtd = random.randint(1, 3)
                self.tiles[y][x].item = {'tipo': item_key, 'qtd': qtd}

    # === TEMPO ===
    def update(self, dt, world_speed=1.0):
        """Atualiza o estado do mundo"""
        real_dt = dt * world_speed
        self.time_of_day += real_dt / HOUR_DURATION
        if self.time_of_day >= 24.0:
            self.time_of_day -= 24.0
            self.day_count += 1
            self._on_new_day()

        # Clima
        self.weather_timer -= real_dt
        if self.weather_timer <= 0:
            self._change_weather()

        # Evolução do vírus (a cada 10 dias)
        if self.day_count % 10 == 0:
            self.virus_evolution = min(100, self.virus_evolution + 2)

    def _on_new_day(self):
        """Eventos que ocorrem a cada novo dia"""
        # Chance de eventos dinâmicos
        roll = random.random()
        if roll < 0.15:
            self.events_queue.append({'tipo': 'horda', 'tamanho': random.randint(5, 20)})
        elif roll < 0.25:
            self.events_queue.append({'tipo': 'comerciante', 'posicao': self._random_passable()})
        elif roll < 0.30:
            self.events_queue.append({'tipo': 'guerra_vilas'})
        elif roll < 0.33:
            self.events_queue.append({'tipo': 'desastre', 'subtipo': random.choice(['incendio','terremoto'])})

        self.world_history.append(f"Dia {self.day_count}: Amanheceu.")

    def _change_weather(self):
        """Muda clima com peso por probabilidade"""
        pesos = {'claro':35,'nublado':25,'chuva':20,'tempestade':8,'neve':7,'neblina':5}
        opcoes = list(pesos.keys())
        pesos_vals = list(pesos.values())
        self.weather = random.choices(opcoes, weights=pesos_vals, k=1)[0]
        self.weather_timer = random.uniform(300, 900)   # 5-15 min

    def _random_passable(self):
        for _ in range(100):
            x = random.randint(0, self.width-1)
            y = random.randint(0, self.height-1)
            if self.tiles[y][x].passavel:
                return (x, y)
        return (self.width//2, self.height//2)

    # === FOG OF WAR ===
    def compute_fov(self, ox, oy, radius):
        """Raycasting FOV"""
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[y][x].visivel = False
        self.tiles[oy][ox].visivel = True
        self.tiles[oy][ox].visitado = True
        for angle in range(360):
            rad = math.radians(angle)
            rx, ry = float(ox), float(oy)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            for _ in range(radius):
                rx += cos_a
                ry += sin_a
                ix, iy = int(rx), int(ry)
                if ix < 0 or iy < 0 or ix >= self.width or iy >= self.height:
                    break
                self.tiles[iy][ix].visivel = True
                self.tiles[iy][ix].visitado = True
                if self.tiles[iy][ix].opaco:
                    break

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    @property
    def is_night(self):
        return self.time_of_day < 6.0 or self.time_of_day >= 20.0

    @property
    def light_level(self):
        h = self.time_of_day
        if 6 <= h < 8:
            return (h - 6) / 2
        elif 8 <= h < 18:
            return 1.0
        elif 18 <= h < 20:
            return (20 - h) / 2
        else:
            return 0.15
