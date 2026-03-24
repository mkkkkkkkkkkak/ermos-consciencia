"""
ERMOS - Sistema de Zumbis
Tipos, comportamento, evolução e o Supremo
"""
import random
import math
from src.constants import *


class Zombie:
    def __init__(self, x, y, tipo='errante', world=None):
        self.x = float(x)
        self.y = float(y)
        self.tipo = tipo
        self.world = world
        self.id = random.randint(100000, 999999)

        stats = ZOMBIE_TYPES.get(tipo, ZOMBIE_TYPES['errante'])
        self.hp = stats['hp']
        self.hp_max = stats['hp']
        self.dano = stats['dano']
        self.vel_base = stats['vel']
        self.visao = stats['visao']
        self.xp_val = stats['xp']
        self.cor = stats['cor']

        # Evolução pelo vírus (cresce com world.virus_evolution)
        self.nivel_evolucao = 0
        self.vivo = True
        self.morto = False

        # Estado IA
        self.estado = 'vagando'  # vagando, caçando, dormindo, em_horda
        self.alvo = None
        self.alvo_ultimo_pos = None
        self.timer_barulho = 0
        self.horda_id = None

        # Comportamento especial por tipo
        self.pode_escalar = tipo in ('escalador', 'supremo')
        self.pode_usar_ferramentas = tipo in ('inteligente', 'supremo')
        self.aprendizado = {}   # para o supremo

        # Timer de ataque
        self.timer_ataque = 0
        self.vel_ataque = 1.0

        # Pathfinding simplificado
        self.destino = None
        self.wander_timer = random.uniform(1, 4)

    @property
    def vel(self):
        v = self.vel_base
        world = self.world
        if world:
            if world.is_night:
                v *= 1.3
            clima = world.weather
            if clima == 'chuva':
                v *= 0.85
            elif clima == 'neve':
                v *= 0.7
            elif clima == 'tempestade':
                v *= 0.6
            # Evolução do vírus torna mais rápido
            v *= (1 + world.virus_evolution / 500)
        return v

    def update(self, dt, world, player, outros_zombies):
        if not self.vivo:
            return

        # Atualiza evolução
        if world:
            evolucao_nova = world.virus_evolution // 20
            if evolucao_nova > self.nivel_evolucao:
                self.nivel_evolucao = evolucao_nova
                self.hp_max += 10
                self.hp = min(self.hp + 10, self.hp_max)
                self.dano += 2

        # Timer de ataque
        self.timer_ataque = max(0, self.timer_ataque - dt)

        px, py = player.x, player.y
        dist_player = math.sqrt((self.x-px)**2 + (self.y-py)**2)

        # === DETECÇÃO ===
        detectou = False
        if dist_player <= self.visao:
            # Melhor detecção à noite (zumbis enxergam no escuro)
            detectou = True
        elif self.alvo_ultimo_pos:
            # Lembram da última posição do alvo
            detectou = True

        # Barulho de arma de fogo atrai
        if hasattr(player, 'barulho_ativo') and player.barulho_ativo > 0:
            raio_barulho = player.barulho_ativo * 3
            if dist_player <= raio_barulho:
                detectou = True
                self.alvo_ultimo_pos = (px, py)

        # === COMPORTAMENTO POR ESTADO ===
        if detectou and dist_player < self.visao * 1.5:
            self.estado = 'caçando'
            self.alvo_ultimo_pos = (px, py)

        if self.estado == 'caçando':
            self._caçar(dt, world, player, dist_player)
        elif self.estado == 'vagando':
            self._vagar(dt, world)

        # Em horda: coordenam posições
        if self.horda_id and self.estado == 'caçando':
            for z in outros_zombies:
                if z.horda_id == self.horda_id and z != self:
                    if z.estado != 'caçando':
                        z.estado = 'caçando'
                        z.alvo_ultimo_pos = self.alvo_ultimo_pos

    def _caçar(self, dt, world, player, dist_player):
        # Se alcançou — atacar
        if dist_player < 1.2 and self.timer_ataque <= 0:
            player.receber_dano(self.dano, fonte=self)
            self.timer_ataque = self.vel_ataque
            # Chance de infecção
            if random.random() < 0.05:
                player.adicionar_doenca('virus_z')
            return

        # Mover em direção ao player
        px, py = player.x, player.y
        if self.alvo_ultimo_pos:
            tx, ty = self.alvo_ultimo_pos
            # Se chegou onde estava o player e não o encontrou, para de caçar
            if math.sqrt((self.x-tx)**2+(self.y-ty)**2) < 1.0:
                if dist_player > self.visao:
                    self.estado = 'vagando'
                    self.alvo_ultimo_pos = None
                    return
            else:
                px, py = tx, ty

        dx = px - self.x
        dy = py - self.y
        d = math.sqrt(dx*dx+dy*dy) or 1
        nx, ny = dx/d, dy/d

        nova_x = self.x + nx * self.vel * dt * 3
        nova_y = self.y + ny * self.vel * dt * 3

        tile = world.get_tile(int(nova_x), int(nova_y))
        if tile and (tile.passavel or (self.pode_escalar and tile.tipo != 'agua')):
            self.x = nova_x
            self.y = nova_y
        else:
            # Tenta desviar
            self.x += random.uniform(-0.5, 0.5) * self.vel * dt
            self.y += random.uniform(-0.5, 0.5) * self.vel * dt

    def _vagar(self, dt, world):
        self.wander_timer -= dt
        if self.wander_timer <= 0 or not self.destino:
            self.wander_timer = random.uniform(2, 5)
            self.destino = (
                self.x + random.uniform(-6, 6),
                self.y + random.uniform(-6, 6)
            )

        if self.destino:
            dx = self.destino[0] - self.x
            dy = self.destino[1] - self.y
            d = math.sqrt(dx*dx+dy*dy)
            if d < 0.5:
                self.destino = None
                return
            nx, ny = dx/d, dy/d
            nova_x = self.x + nx * self.vel * 0.5 * dt * 3
            nova_y = self.y + ny * self.vel * 0.5 * dt * 3
            tile = world.get_tile(int(nova_x), int(nova_y))
            if tile and tile.passavel:
                self.x = nova_x
                self.y = nova_y

    def receber_dano(self, dano, parte_do_corpo=None):
        """Supremo só morre com acerto no cérebro/coração"""
        if self.tipo == 'supremo':
            if parte_do_corpo in ('cerebro', 'coracao'):
                dano *= 10
            else:
                dano = int(dano * 0.1)  # quase invulnerável no corpo
            # Aprende o estilo de ataque do player
            if parte_do_corpo:
                self.aprendizado[parte_do_corpo] = self.aprendizado.get(parte_do_corpo, 0) + 1

        self.hp -= dano
        if self.hp <= 0:
            self._morrer()

    def _morrer(self):
        self.vivo = False
        self.morto = True
        # Corpo permanece no chão (pode ser possuído)
        self.pode_ser_possuido = True


class ZombieSupremo(Zombie):
    """O Zumbi Supremo — único por mundo, aprende e evolui"""
    def __init__(self, x, y, world):
        super().__init__(x, y, 'supremo', world)
        self.aprendizados_player = []
        self.vezes_regenerou = 0
        self.regenerando = False
        self.timer_regeneracao = 0
        self.comportamentos_imitados = []

    def update(self, dt, world, player, outros_zombies):
        # Regeneração
        if self.hp < self.hp_max * 0.3 and not self.regenerando:
            self.regenerando = True
            self.timer_regeneracao = 30  # 30s para regenerar

        if self.regenerando:
            self.timer_regeneracao -= dt
            self.hp = min(self.hp_max, self.hp + self.hp_max * 0.01 * dt)
            if self.hp >= self.hp_max * 0.8:
                self.regenerando = False
                self.vezes_regenerou += 1

        # Aprende com movimento do player
        self._aprender_com_player(player)
        super().update(dt, world, player, outros_zombies)

    def _aprender_com_player(self, player):
        """Imita comportamentos do player"""
        if hasattr(player, 'ultimo_movimento') and player.ultimo_movimento:
            self.comportamentos_imitados.append(player.ultimo_movimento)
            # Antecipa movimentos
            if len(self.comportamentos_imitados) > 20:
                self.comportamentos_imitados.pop(0)

    def receber_dano(self, dano, parte_do_corpo=None):
        # Já aprendeu onde foi atacado — esquiva
        if parte_do_corpo and self.aprendizados_player.count(parte_do_corpo) > 3:
            dano = int(dano * 0.2)  # esquiva eficiente
        self.aprendizados_player.append(parte_do_corpo)
        super().receber_dano(dano, parte_do_corpo)


class ZombieManager:
    def __init__(self, world):
        self.world = world
        self.zombies = []
        self.hordas = []
        self.supremo = None
        self.supremo_spawned = False
        self._spawn_inicial()

    def _spawn_inicial(self):
        tipos_comuns = ['errante', 'errante', 'errante', 'corredor', 'escalador']
        # Cidade tem mais zumbis
        cx, cy = MAP_W//2, MAP_H//4
        for _ in range(40):
            x = cx + random.randint(-18, 18)
            y = cy + random.randint(-12, 12)
            tipo = random.choice(tipos_comuns)
            if random.random() < 0.05:
                tipo = 'tank'
            elif random.random() < 0.03:
                tipo = 'inteligente'
            self.zombies.append(Zombie(x, y, tipo, self.world))

        # Espalhados pelo mapa
        for _ in range(60):
            x = random.randint(5, MAP_W-5)
            y = random.randint(5, MAP_H-5)
            tile = self.world.get_tile(x, y)
            if tile and tile.passavel:
                tipo = random.choices(
                    ['errante','corredor','escalador','tank','inteligente','militar'],
                    weights=[50, 20, 10, 8, 7, 5]
                )[0]
                self.zombies.append(Zombie(x, y, tipo, self.world))

    def update(self, dt, player):
        px, py = player.x, player.y
        vivos = [z for z in self.zombies if z.vivo]

        for z in vivos:
            d = abs(z.x-px)+abs(z.y-py)
            if d < 45:  # só atualiza zumbis próximos
                prox = [o for o in vivos if o != z and abs(o.x-z.x)+abs(o.y-z.y) < 8]
                z.update(dt, self.world, player, prox)

        # Supremo
        if self.supremo and self.supremo.vivo:
            self.supremo.update(dt, self.world, player, vivos)

        # Spawn de horda noturna
        if self.world.is_night and random.random() < 0.001 * dt:
            self._spawnar_horda(px, py)

        # Spawn do Supremo (extremamente raro)
        if not self.supremo_spawned and random.random() < SUPREMO_SPAWN_CHANCE * dt:
            self._spawnar_supremo()

        # Processar eventos de horda do mundo
        for evento in self.world.events_queue[:]:
            if evento['tipo'] == 'horda':
                self._spawnar_horda(px, py, evento['tamanho'])
                self.world.events_queue.remove(evento)

        # Remove zumbis mortos após um tempo
        self.zombies = [z for z in self.zombies if z.vivo or z.morto]

    def _spawnar_horda(self, px, py, tamanho=None):
        n = tamanho or random.randint(8, 25)
        angulo = random.uniform(0, math.pi*2)
        dist = random.uniform(15, 25)
        hx = px + math.cos(angulo) * dist
        hy = py + math.sin(angulo) * dist
        horda_id = random.randint(1000, 9999)
        for i in range(n):
            x = hx + random.randint(-3, 3)
            y = hy + random.randint(-3, 3)
            tipo = random.choices(['errante','corredor'], weights=[70,30])[0]
            z = Zombie(x, y, tipo, self.world)
            z.horda_id = horda_id
            z.estado = 'caçando'
            z.alvo_ultimo_pos = (px, py)
            self.zombies.append(z)
        self.world.world_history.append(f"Dia {self.world.day_count}: Horda de {n} zumbis surgiu!")

    def _spawnar_supremo(self):
        px, py = MAP_W//2, MAP_H//4
        self.supremo = ZombieSupremo(px+5, py+5, self.world)
        self.zombies.append(self.supremo)
        self.supremo_spawned = True
        self.world.world_history.append(
            f"Dia {self.world.day_count}: ⚠️ O SUPREMO foi avistado. Que Deus nos ajude."
        )

    def get_zombies_vivos(self):
        return [z for z in self.zombies if z.vivo]

    def get_zombies_mortos_possuiveis(self):
        return [z for z in self.zombies if z.morto and hasattr(z, 'pode_ser_possuido')]
