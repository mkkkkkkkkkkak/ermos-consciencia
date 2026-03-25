"""
ERMOS - GameScreen
Tela principal do jogo com controles touch e joystick virtual
"""
import math
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, Line, RoundedRectangle
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel

from src.systems.world import World
from src.systems.renderer import GameRenderer
from src.entities.player import Player
from src.entities.npc import NPCManager
from src.entities.zombie import ZombieManager
from src.ui.hud import HUD
from src.constants import *


class VirtualJoystick(Widget):
    """Joystick virtual para mobile"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active = False
        self.origin = (0, 0)
        self.touch_pos = (0, 0)
        self.dx = 0.0
        self.dy = 0.0
        self.radius = 55
        self.size = (self.radius*2+20, self.radius*2+20)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active = True
            self.origin = (self.center_x, self.center_y)
            self._update_direction(touch)
            return True

    def on_touch_move(self, touch):
        if self.active:
            self._update_direction(touch)
            return True

    def on_touch_up(self, touch):
        if self.active:
            self.active = False
            self.dx = 0
            self.dy = 0
            self.canvas.clear()
            self._draw()
            return True

    def _update_direction(self, touch):
        ox, oy = self.center_x, self.center_y
        dx = touch.x - ox
        dy = touch.y - oy
        dist = math.sqrt(dx*dx+dy*dy)
        if dist > self.radius:
            dx = dx/dist * self.radius
            dy = dy/dist * self.radius
        self.touch_pos = (ox+dx, oy+dy)
        max_d = self.radius
        self.dx = dx / max_d
        self.dy = dy / max_d
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            # Base
            Color(0.1, 0.1, 0.1, 0.45)
            Ellipse(pos=(self.center_x-self.radius, self.center_y-self.radius),
                    size=(self.radius*2, self.radius*2))
            Color(0.3, 0.28, 0.22, 0.5)
            Line(circle=(self.center_x, self.center_y, self.radius), width=1.5)

            if self.active:
                # Knob
                Color(0.65, 0.55, 0.35, 0.8)
                kr = 22
                Ellipse(pos=(self.touch_pos[0]-kr, self.touch_pos[1]-kr),
                        size=(kr*2, kr*2))
                Color(0.8, 0.72, 0.5, 0.6)
                Ellipse(pos=(self.touch_pos[0]-kr+4, self.touch_pos[1]-kr+4),
                        size=(kr*2-8, kr*2-8))
            else:
                # Centro estático
                Color(0.4, 0.37, 0.28, 0.6)
                Ellipse(pos=(self.center_x-20, self.center_y-20), size=(40, 40))


class ActionButton(Widget):
    """Botão de ação circular"""
    def __init__(self, label, cor, callback, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.cor = cor
        self.callback = callback
        self.pressed = False
        self.size = (56, 56)
        self._draw()

    def _draw(self):
        self.canvas.clear()
        with self.canvas:
            r, g, b = self.cor
            alpha = 0.9 if self.pressed else 0.75
            scale = 0.9 if self.pressed else 1.0
            rs = 28 * scale
            Color(0, 0, 0, 0.4)
            Ellipse(pos=(self.center_x-rs+2, self.center_y-rs-2), size=(rs*2, rs*2))
            Color(r, g, b, alpha)
            Ellipse(pos=(self.center_x-rs, self.center_y-rs), size=(rs*2, rs*2))
            Color(r*1.2, g*1.2, b*1.2, 0.5)
            Ellipse(pos=(self.center_x-rs+3, self.center_y+rs*0.3), size=(rs*1.0, rs*0.5))
            # Texto
            lbl = CoreLabel(text=self.label, font_size=11)
            lbl.refresh()
            tx = lbl.texture
            Color(1, 1, 1, 0.95)
            Rectangle(texture=tx, pos=(self.center_x-tx.width//2, self.center_y-tx.height//2),
                      size=tx.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = True
            self._draw()
            if self.callback:
                self.callback()
            return True

    def on_touch_up(self, touch):
        if self.pressed:
            self.pressed = False
            self._draw()


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.world = None
        self.player = None
        self.npc_manager = None
        self.zombie_manager = None
        self.renderer = None
        self.hud = None
        self.game_loop = None
        self.paused = False
        self.npc_dialogo = None
        self.world_speed = 1.0
        # new_game=True → nova jornada; False → continuar jogo existente
        self.new_game = True

    def on_enter(self):
        # Cancela loop anterior se existir (evita duplicatas)
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None
        # Só reinicia o jogo se for nova jornada ou ainda não tiver mundo
        if self.new_game or self.world is None:
            self.setup_game()
            self.new_game = False  # reset para próxima vez
        else:
            # Retornando do inventário/diário — apenas retoma o loop
            pass
        self.game_loop = Clock.schedule_interval(self.update, TICK_RATE)

    def on_leave(self):
        if self.game_loop:
            self.game_loop.cancel()
            self.game_loop = None

    def setup_game(self, save_data=None):
        self.clear_widgets()
        layout = FloatLayout()

        # Mundo
        self.world = World()

        # Player — começa na vila sul
        px, py = MAP_W//2, MAP_H*3//4
        self.player = Player(px, py)

        # Managers
        self.npc_manager = NPCManager(self.world)
        self.zombie_manager = ZombieManager(self.world)
        self.world.zombies = self.zombie_manager.zombies

        # Renderer
        self.renderer = GameRenderer(size=Window.size, pos=(0, 0))
        self.renderer.setup(self.world, self.player, self.npc_manager, self.zombie_manager)
        layout.add_widget(self.renderer)

        # HUD
        self.hud = HUD(size=Window.size, pos=(0, 0))
        self.hud.setup(self.player, self.world)
        layout.add_widget(self.hud)

        # Joystick
        self.joystick = VirtualJoystick(
            pos=(20, 20),
            size=(130, 130)
        )
        layout.add_widget(self.joystick)

        # Botões de ação
        bw = Window.width
        # Atacar
        self.btn_attack = ActionButton('Atacar', (0.7, 0.15, 0.15),
                                        self._on_attack,
                                        pos=(bw-70, 120), size=(56, 56))
        layout.add_widget(self.btn_attack)

        # Interagir
        self.btn_interact = ActionButton('Falar', (0.2, 0.55, 0.35),
                                          self._on_interact,
                                          pos=(bw-135, 80), size=(56, 56))
        layout.add_widget(self.btn_interact)

        # Possuir
        self.btn_possess = ActionButton('Poss.', (0.45, 0.1, 0.65),
                                         self._on_possess,
                                         pos=(bw-70, 185), size=(56, 56))
        layout.add_widget(self.btn_possess)

        # Inventário
        self.btn_inv = ActionButton('Inv.', (0.35, 0.28, 0.18),
                                     self._on_inventory,
                                     pos=(bw-135, 160), size=(56, 56))
        layout.add_widget(self.btn_inv)

        # Correr (toggle)
        self.btn_run = ActionButton('Correr', (0.2, 0.4, 0.6),
                                     self._on_run,
                                     pos=(200, 20), size=(56, 56))
        layout.add_widget(self.btn_run)

        # Usar item rápido
        self.btn_use = ActionButton('Usar', (0.5, 0.6, 0.2),
                                     self._on_use_quick,
                                     pos=(265, 20), size=(56, 56))
        layout.add_widget(self.btn_use)

        # Diário / Mapa
        self.btn_map = ActionButton('Mapa', (0.3, 0.3, 0.4),
                                     self._on_journal,
                                     pos=(bw//2-28, Window.height-60), size=(56, 36))
        layout.add_widget(self.btn_map)

        self.add_widget(layout)

        # Mensagem inicial
        Clock.schedule_once(lambda dt: self.hud.adicionar_mensagem(
            "Você acorda em um mundo quebrado...", (0.8, 0.75, 0.6), 5.0), 1.0)
        Clock.schedule_once(lambda dt: self.hud.adicionar_mensagem(
            "Use o joystick para mover.", (0.7, 0.7, 0.6), 5.0), 2.5)

    def update(self, dt):
        if self.paused or not self.player:
            return

        dt = min(dt, 0.1)  # cap delta time

        # Movimento pelo joystick
        jx = self.joystick.dx
        jy = self.joystick.dy
        if abs(jx) > 0.1 or abs(jy) > 0.1:
            self.player.mover(jx, jy, dt, self.world)

        # Update world
        self.world.update(dt, self.world_speed)

        # Update player
        self.player.update(dt, self.world, None)

        # Verificar coleta de items
        self._check_item_pickup()

        # FOV
        fov_radius = 12 if not self.world.is_night else 7
        self.world.compute_fov(int(self.player.x), int(self.player.y), fov_radius)

        # Update NPCs
        self.npc_manager.update(dt, self.player)

        # Update Zombies
        self.zombie_manager.update(dt, self.player)

        # Verificar eventos do mundo
        self._process_world_events()

        # Verificar morte
        if self.player.morto:
            self._on_player_death()

        # Renderer
        self.renderer.update(dt)

        # HUD
        self.hud.update(dt)

        # Barulho de armas atrai zumbis
        if hasattr(self.player, 'barulho_ativo'):
            self.player.barulho_ativo = max(0, self.player.barulho_ativo - dt)

    def _check_item_pickup(self):
        """Coleta automática de items próximos"""
        ix, iy = int(self.player.x), int(self.player.y)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                tile = self.world.get_tile(ix+dx, iy+dy)
                if tile and tile.item:
                    item = tile.item
                    if self.player.adicionar_item(item['tipo'], item.get('qtd', 1)):
                        icone = ITEMS.get(item['tipo'], {}).get('icone', '📦')
                        self.hud.adicionar_mensagem(
                            f"{icone} Pegou {item['tipo']} x{item['qtd']}",
                            (0.85, 0.80, 0.45))
                        tile.item = None

    def _process_world_events(self):
        """Processa eventos dinâmicos do mundo"""
        for evento in self.world.events_queue[:]:
            tipo = evento.get('tipo')
            if tipo == 'comerciante':
                npc = self.npc_manager.spawn_npc()
                npc.ocupacao = 'comerciante'
                self.hud.adicionar_mensagem("Um comerciante apareceu!", (0.8, 0.8, 0.4))
                self.world.events_queue.remove(evento)
            elif tipo == 'guerra_vilas':
                self.hud.adicionar_mensagem("⚔️ Guerra entre vilas começou ao norte!", (0.9, 0.4, 0.2))
                self.world.events_queue.remove(evento)
            elif tipo == 'desastre':
                sub = evento.get('subtipo', 'incendio')
                self.hud.adicionar_mensagem(f"⚠️ Desastre: {sub}!", (1.0, 0.5, 0.2))
                self.world.events_queue.remove(evento)

    def _on_attack(self):
        """Atacar entidade mais próxima"""
        px, py = self.player.x, self.player.y
        alvo = None
        dist_min = 3.0

        # Procura zumbi mais próximo
        for z in self.zombie_manager.get_zombies_vivos():
            d = math.sqrt((z.x-px)**2+(z.y-py)**2)
            if d < dist_min:
                dist_min = d
                alvo = z

        # Procura NPC hostil próximo
        for npc in self.npc_manager.get_npcs_vivos():
            if npc.emocoes.get('raiva', 0) > 70:
                d = math.sqrt((npc.x-px)**2+(npc.y-py)**2)
                if d < dist_min:
                    dist_min = d
                    alvo = npc

        if alvo:
            acertou = self.player.atacar(alvo)
            if acertou:
                arma = ITEMS.get(self.player.arma_equipada, {})
                dano_txt = f"-{arma.get('dano', 5)}"
                self.renderer.add_floating_text(alvo.x, alvo.y, dano_txt, (0.9, 0.2, 0.2))
                self.renderer.add_particle_burst(alvo.x, alvo.y, (0.8, 0.1, 0.1), 6)

                if not alvo.vivo:
                    xp = getattr(alvo, 'xp_val', 10)
                    subiu = self.player.ganhar_xp(xp)
                    self.renderer.add_floating_text(alvo.x, alvo.y+1, f"+{xp}xp", (0.8, 0.8, 0.2))
                    if subiu:
                        self.hud.adicionar_mensagem(f"🎯 Nível {self.player.nivel}!", (0.9, 0.85, 0.3))
        else:
            self.hud.adicionar_mensagem("Nada por perto para atacar.", (0.6, 0.6, 0.55))

    def _on_interact(self):
        """Interagir com NPC próximo"""
        px, py = self.player.x, self.player.y
        npc_proximo = None
        dist_min = 3.0

        for npc in self.npc_manager.get_npcs_vivos():
            d = math.sqrt((npc.x-px)**2+(npc.y-py)**2)
            if d < dist_min:
                dist_min = d
                npc_proximo = npc

        if npc_proximo:
            resp = npc_proximo.interagir_com_player(self.player)
            self.hud.mostrar_dialogo(npc_proximo.nome_display, resp['fala'], resp['opcoes'])
            self.npc_dialogo = npc_proximo
            npc_proximo.estado = 'conversando'
            npc_proximo.emocoes['confianca_player'] = min(
                100, npc_proximo.emocoes.get('confianca_player', 50) + 2)
            # Fechar diálogo após 8 segundos
            Clock.schedule_once(lambda dt: self._fechar_dialogo(), 8.0)
        else:
            # Verificar estruturas
            tile = self.world.get_tile(int(px), int(py))
            if tile and tile.estrutura:
                est = tile.estrutura
                if est['tipo'] == 'poco':
                    self.player.sede = min(100, self.player.sede + 50)
                    self.hud.adicionar_mensagem("🌊 Bebeu água do poço.", (0.4, 0.7, 1.0))
                elif est['tipo'] == 'fogueira':
                    self.player.temperatura = min(37.5, self.player.temperatura + 2)
                    self.hud.adicionar_mensagem("🔥 Se aqueceu na fogueira.", (0.9, 0.5, 0.2))
            else:
                self.hud.adicionar_mensagem("Ninguém por perto.", (0.6, 0.6, 0.55))

    def _fechar_dialogo(self):
        self.hud.fechar_dialogo()
        if self.npc_dialogo:
            self.npc_dialogo.estado = 'patrulhando'
            self.npc_dialogo = None

    def _on_possess(self):
        """Ativar possessão no corpo mais próximo"""
        px, py = self.player.x, self.player.y

        if self.player.possuindo:
            pos = self.player.sair_possessao(self.world)
            self.hud.adicionar_mensagem("Saiu do corpo.", (0.6, 0.4, 0.8))
            # Reação dos NPCs próximos
            for npc in self.npc_manager.get_npcs_vivos():
                d = math.sqrt((npc.x-px)**2+(npc.y-py)**2)
                if d < 5:
                    npc.reagir_possessao_saindo()
                    self.hud.adicionar_mensagem(
                        f"{npc.nome} está apavorado!", (0.8, 0.6, 0.3))
            return

        # Procura corpo possuível
        alvo = None
        dist_min = POSSESSION_RANGE

        corpos_npc = self.npc_manager.get_npcs_mortos_possuiveis()
        corpos_z = self.zombie_manager.get_zombies_mortos_possuiveis()

        for c in corpos_npc + corpos_z:
            d = math.sqrt((c.x-px)**2+(c.y-py)**2)
            if d < dist_min:
                dist_min = d
                alvo = c

        if alvo:
            if self.player.possuir(alvo, self.world):
                nome = getattr(alvo, 'nome_completo', 'Corpo desconhecido')
                self.hud.adicionar_mensagem(f"👁️ Possuindo: {nome}", (0.6, 0.3, 0.9))
                self.renderer.add_particle_burst(alvo.x, alvo.y, (0.5, 0.1, 0.8), 12)
        else:
            self.hud.adicionar_mensagem(
                "Nenhum corpo disponível por perto.", (0.55, 0.45, 0.65))

    def _on_run(self):
        self.player.correndo = not self.player.correndo
        estado = "CORRENDO" if self.player.correndo else "Andando"
        self.hud.adicionar_mensagem(f"👟 {estado}", (0.6, 0.7, 0.8))

    def _on_use_quick(self):
        """Usa o melhor item médico disponível"""
        prioridade = ['morphina', 'bandagem', 'antibiotico', 'lata_feijao', 'agua_garrafa', 'fruta']
        for item in prioridade:
            if item in self.player.inventario and self.player.inventario[item] > 0:
                if self.player.usar_item(item):
                    icone = ITEMS.get(item, {}).get('icone', '💊')
                    self.hud.adicionar_mensagem(f"{icone} Usou {item}", (0.5, 0.85, 0.5))
                    return
        self.hud.adicionar_mensagem("Nada útil no inventário.", (0.6, 0.6, 0.55))

    def _on_inventory(self):
        self.new_game = False   # preserva o jogo atual
        self.manager.current = 'inventory'

    def _on_journal(self):
        self.new_game = False   # preserva o jogo atual
        self.manager.current = 'journal'

    def _on_player_death(self):
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'death'), 1.5)
        self.hud.adicionar_mensagem("Você morreu...", (0.8, 0.2, 0.2), 3.0)
