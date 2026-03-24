"""
ERMOS - Sistema de NPCs
IA comportamental com necessidades, emoções, memória e objetivos próprios
"""
import random
import math
from src.constants import *


class Memory:
    """Memória individual de um NPC"""
    def __init__(self, assunto, descricao, emocao, intensidade, dia):
        self.assunto = assunto       # 'jogador', 'evento', 'lugar', 'npc'
        self.descricao = descricao
        self.emocao = emocao         # 'medo','raiva','gratidao','tristeza','neutro'
        self.intensidade = intensidade  # 0-100
        self.dia = dia
        self.vezes_lembrado = 0

    def desvanecer(self):
        """Memórias desaparecem gradualmente (exceto traumas)"""
        if self.intensidade < 80:
            self.intensidade = max(0, self.intensidade - 0.1)


class NPC:
    def __init__(self, x, y, world, npc_id=None):
        self.id = npc_id or random.randint(10000, 99999)
        self.x = float(x)
        self.y = float(y)
        self.world = world

        # === IDENTIDADE ===
        self.genero = random.choice(['M', 'F'])
        names = NPC_NAMES_M if self.genero == 'M' else NPC_NAMES_F
        self.nome = random.choice(names)
        self.sobrenome = random.choice(['Silva','Santos','Oliveira','Costa','Rocha','Lima','Souza','Ferreira'])
        self.nome_completo = f"{self.nome} {self.sobrenome}"
        self.idade = random.randint(18, 65)
        self.ocupacao = random.choice(NPC_OCCUPATIONS)

        # === PERSONALIDADE (0-100 cada traço) ===
        self.personalidade = {
            'bondade':      random.randint(10, 90),
            'coragem':      random.randint(10, 90),
            'ganancia':     random.randint(5, 80),
            'lealdade':     random.randint(20, 95),
            'desconfianca': random.randint(10, 80),
            'inteligencia': random.randint(20, 95),
        }
        self.objetivo_vida = random.choice(NPC_GOALS)

        # === NECESSIDADES BIOLÓGICAS ===
        self.hp = 100.0
        self.hp_max = 100.0
        self.fome = random.uniform(40, 90)
        self.sede = random.uniform(40, 90)
        self.cansaco = random.uniform(0, 50)
        self.temperatura = 37.0

        # === EMOÇÕES ATUAIS ===
        self.emocoes = {
            'medo':     0.0,
            'raiva':    0.0,
            'tristeza': 0.0,
            'alegria':  random.uniform(20, 60),
            'confianca_player': 50.0,   # relação com o jogador
        }

        # === ESTADO ===
        self.estado = 'patrulhando'  # patrulhando, trabalhando, dormindo, fugindo, combate, conversando
        self.dormindo = False
        self.morto = False
        self.infectado = False
        self.vivo = True

        # === FAMÍLIA E RELAÇÕES ===
        self.familia = []     # lista de IDs de NPCs
        self.amigos = []
        self.inimigos = []
        self.conjuge = None
        self.filhos = []
        self.gravidez = None  # None ou {dias_restantes, pai_id}

        # === MEMÓRIA ===
        self.memorias = []
        self.conhece_player = False
        self.trauma_possessao = False  # se viu possessão

        # === INVENTÁRIO ===
        self.inventario = self._inventario_inicial()
        self.arma_equipada = None

        # === MOVIMENTO ===
        self.vel = random.uniform(0.6, 1.0)
        self.destino = None
        self.path = []
        self.timer_decisao = random.uniform(0, 5)
        self.rotina = self._gerar_rotina()

        # === VILA ===
        self.vila_id = None
        self.casa_pos = None

        # === RUMORES ===
        self.rumores = []   # boatos que o NPC sabe e pode espalhar

    def _inventario_inicial(self):
        inv = {}
        if random.random() > 0.5:
            inv['lata_feijao'] = random.randint(1, 3)
        if random.random() > 0.4:
            inv['agua_garrafa'] = random.randint(1, 2)
        if random.random() > 0.7:
            armas = ['faca', 'bat_prego', 'arco']
            inv[random.choice(armas)] = 1
        return inv

    def _gerar_rotina(self):
        """Rotina diária baseada na ocupação"""
        rotinas = {
            'coletor':    [('dormir',0,6),('trabalhar',7,17),('descansar',17,21),('dormir',21,24)],
            'construtor': [('dormir',0,6),('construir',7,18),('descansar',18,22),('dormir',22,24)],
            'medico':     [('dormir',0,7),('trabalhar',8,20),('descansar',20,23),('dormir',23,24)],
            'soldado':    [('patrulhar',0,8),('descansar',8,16),('patrulhar',16,24)],
            'fazendeiro': [('dormir',0,5),('trabalhar',6,18),('descansar',18,21),('dormir',21,24)],
            'comerciante':[('dormir',0,7),('comerciar',8,20),('descansar',20,23),('dormir',23,24)],
        }
        return rotinas.get(self.ocupacao, [('dormir',0,6),('vagar',6,22),('dormir',22,24)])

    def _atividade_hora(self, hora):
        for (ativ, inicio, fim) in self.rotina:
            if inicio <= hora < fim:
                return ativ
        return 'vagar'

    def update(self, dt, world, player, npcs_proximos, zombies_proximos):
        if self.morto or not self.vivo:
            return

        hora = world.time_of_day

        # === NECESSIDADES ===
        self.fome = max(0, self.fome - HUNGER_RATE * dt / 3600)
        self.sede = max(0, self.sede - THIRST_RATE * dt / 3600)
        self.cansaco += dt / 3600 * 5

        # Dano por necessidades críticas
        if self.fome <= 0 or self.sede <= 0:
            self.hp -= 1.0 * dt / 60
        if self.cansaco >= 100:
            self.hp -= 0.5 * dt / 60

        # Consumir inventário se necessário
        if self.fome < 30 and 'lata_feijao' in self.inventario:
            self.fome = min(100, self.fome + 30)
            self.inventario['lata_feijao'] -= 1
            if self.inventario['lata_feijao'] <= 0:
                del self.inventario['lata_feijao']
        if self.sede < 20 and 'agua_garrafa' in self.inventario:
            self.sede = min(100, self.sede + 40)
            self.inventario['agua_garrafa'] -= 1
            if self.inventario['agua_garrafa'] <= 0:
                del self.inventario['agua_garrafa']

        # === EMOÇÕES - decaem com o tempo ===
        for emocao in ['medo', 'raiva', 'tristeza']:
            self.emocoes[emocao] = max(0, self.emocoes[emocao] - 2 * dt / 60)

        # === PERCEPÇÃO DE ZUMBIS ===
        if zombies_proximos:
            z_mais_proximo = min(zombies_proximos, key=lambda z: self._dist(z.x, z.y))
            d = self._dist(z_mais_proximo.x, z_mais_proximo.y)
            if d < 8:
                coragem = self.personalidade['coragem']
                if coragem < 40 or self.hp < 30:
                    self.emocoes['medo'] = min(100, self.emocoes['medo'] + 30)
                    self.estado = 'fugindo'
                    self._fugir_de(z_mais_proximo.x, z_mais_proximo.y)
                else:
                    self.estado = 'combate'
                    self.destino = (int(z_mais_proximo.x), int(z_mais_proximo.y))

        # === DORMIR ===
        ativ = self._atividade_hora(hora)
        if ativ == 'dormir' and self.emocoes['medo'] < 20:
            if not self.dormindo:
                self.dormindo = True
                self.estado = 'dormindo'
            self.cansaco = max(0, self.cansaco - 10 * dt / 60)
            self.hp = min(self.hp_max, self.hp + 0.5 * dt / 60)
            return

        self.dormindo = False

        # === DECISÕES ===
        self.timer_decisao -= dt
        if self.timer_decisao <= 0:
            self.timer_decisao = random.uniform(2, 6)
            if self.estado not in ['fugindo', 'combate', 'conversando']:
                self._decidir_acao(ativ, player, npcs_proximos)

        # === MOVIMENTO ===
        if self.destino and self.estado != 'dormindo':
            self._mover_para_destino(dt, world)

        # === MEMORIAS DESVANECEM ===
        for m in self.memorias:
            m.desvanecer()
        self.memorias = [m for m in self.memorias if m.intensidade > 0]

        # === MORTE ===
        if self.hp <= 0:
            self._morrer(world)

    def _decidir_acao(self, atividade, player, npcs_proximos):
        """Lógica de decisão baseada em personalidade e estado"""
        if atividade in ('trabalhar', 'construir'):
            # Vai para área de trabalho
            tx = self.x + random.randint(-5, 5)
            ty = self.y + random.randint(-5, 5)
            self.destino = (int(tx), int(ty))
            self.estado = 'trabalhando'

        elif atividade == 'patrulhar':
            self.estado = 'patrulhando'
            self.destino = (
                int(self.x + random.randint(-8, 8)),
                int(self.y + random.randint(-8, 8))
            )

        elif atividade == 'vagar':
            self.estado = 'vagando'
            self.destino = (
                int(self.x + random.randint(-6, 6)),
                int(self.y + random.randint(-6, 6))
            )

        # NPCs ganancosos tentam pegar recursos próximos
        if self.personalidade['ganancia'] > 60:
            # lógica de coleta
            pass

    def _mover_para_destino(self, dt, world):
        if not self.destino:
            return
        dx = self.destino[0] - self.x
        dy = self.destino[1] - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < 0.5:
            self.destino = None
            return
        nx = dx / dist
        ny = dy / dist
        nx_pos = self.x + nx * self.vel * dt * 3
        ny_pos = self.y + ny * self.vel * dt * 3
        tile = world.get_tile(int(nx_pos), int(ny_pos))
        if tile and tile.passavel:
            self.x = nx_pos
            self.y = ny_pos

    def _fugir_de(self, fx, fy):
        dx = self.x - fx
        dy = self.y - fy
        dist = math.sqrt(dx*dx + dy*dy) or 1
        self.destino = (
            int(self.x + (dx/dist) * 10),
            int(self.y + (dy/dist) * 10)
        )

    def _dist(self, ox, oy):
        return math.sqrt((self.x-ox)**2 + (self.y-oy)**2)

    def receber_dano(self, dano, fonte=None):
        self.hp -= dano
        self.emocoes['medo'] = min(100, self.emocoes['medo'] + 20)
        self.emocoes['raiva'] = min(100, self.emocoes['raiva'] + 15)
        if self.hp <= 0:
            self._morrer(self.world)

    def _morrer(self, world):
        self.vivo = False
        self.morto = True
        self.estado = 'morto'
        # Pode ser possuído
        self.pode_ser_possuido = True
        world.world_history.append(f"Dia {world.day_count}: {self.nome_completo} morreu.")

    def adicionar_memoria(self, assunto, descricao, emocao, intensidade):
        mem = Memory(assunto, descricao, emocao, intensidade, self.world.day_count)
        self.memorias.append(mem)
        # Traumas são permanentes
        if intensidade >= 80:
            mem.intensidade = 100  # nunca desaparece

    def interagir_com_player(self, player):
        """Retorna diálogo baseado no estado emocional e memórias"""
        conf = self.emocoes['confianca_player']
        medo = self.emocoes['medo']
        trauma = self.trauma_possessao

        if trauma:
            return {
                'fala': f"*recua* V-você... eu vi o que você fez com aquele corpo. Fique longe de mim!",
                'opcoes': ['Tentar explicar', 'Ameaçar', 'Ir embora']
            }
        if medo > 60:
            return {
                'fala': f"*tremendo* Por favor, não me machuque!",
                'opcoes': ['Acalmar', 'Ajudar', 'Ignorar']
            }
        if conf < 20:
            return {
                'fala': f"*desconfiante* O que você quer? Não te conheço.",
                'opcoes': ['Apresentar-se', 'Oferecer item', 'Ir embora']
            }
        if conf > 70:
            return {
                'fala': f"Olá, {self.nome} fala. Que bom te ver. Precisa de algo?",
                'opcoes': ['Trocar itens', 'Pedir para se juntar', 'Contar rumores', 'Tchau']
            }
        return {
            'fala': f"Sobrevivendo aqui. Você também?",
            'opcoes': ['Trocar itens', 'Perguntar sobre área', 'Ir embora']
        }

    def reagir_possessao_saindo(self):
        """Reação ao ver alguém sair de um corpo"""
        self.trauma_possessao = True
        self.emocoes['medo'] = 100
        self.emocoes['confianca_player'] = max(0, self.emocoes['confianca_player'] - 60)
        self.adicionar_memoria(
            'possessao',
            'Vi uma entidade sair de um corpo morto!',
            'medo',
            95
        )
        self.estado = 'fugindo'
        # Espalha rumor
        self.rumores.append({
            'texto': 'Tem uma entidade sobrenatural por aqui. Vi com meus próprios olhos!',
            'credibilidade': 80
        })

    def espalhar_rumor(self, npc_alvo):
        """Passa rumores para NPCs próximos"""
        if self.rumores and random.random() > 0.7:
            rumor = random.choice(self.rumores)
            if rumor not in npc_alvo.rumores:
                npc_alvo.rumores.append(rumor)
                rumor['credibilidade'] = max(20, rumor['credibilidade'] - 10)

    @property
    def nome_display(self):
        return self.nome_completo

    @property
    def esta_vivo(self):
        return self.vivo and not self.morto


class NPCManager:
    def __init__(self, world):
        self.world = world
        self.npcs = []
        self.npc_id_counter = 1
        self._spawn_inicial()

    def _spawn_inicial(self):
        """Spawna NPCs iniciais nas vilas"""
        # Vila inicial
        vx, vy = MAP_W // 2, MAP_H * 3 // 4
        for _ in range(8):
            x = vx + random.randint(-6, 6)
            y = vy + random.randint(-6, 6)
            npc = NPC(x, y, self.world, self.npc_id_counter)
            self.npc_id_counter += 1
            self.npcs.append(npc)

        # Cidade
        cx, cy = MAP_W // 2, MAP_H // 4
        for _ in range(15):
            x = cx + random.randint(-15, 15)
            y = cy + random.randint(-10, 10)
            npc = NPC(x, y, self.world, self.npc_id_counter)
            self.npc_id_counter += 1
            self.npcs.append(npc)

        # Floresta
        fx, fy = MAP_W // 5, MAP_H // 2
        for _ in range(5):
            x = fx + random.randint(-8, 8)
            y = fy + random.randint(-8, 8)
            npc = NPC(x, y, self.world, self.npc_id_counter)
            self.npc_id_counter += 1
            npc.ocupacao = random.choice(['explorador', 'coletor'])
            self.npcs.append(npc)

        # Criação de famílias aleatórias
        self._gerar_familias()

    def _gerar_familias(self):
        adultos = [n for n in self.npcs if n.idade >= 18]
        random.shuffle(adultos)
        for i in range(0, len(adultos)-1, 2):
            if random.random() > 0.5:
                a, b = adultos[i], adultos[i+1]
                a.conjuge = b.id
                b.conjuge = a.id
                # Filhos
                n_filhos = random.randint(0, 3)
                for _ in range(n_filhos):
                    crianca = NPC(a.x + random.randint(-2,2), a.y + random.randint(-2,2),
                                  self.world, self.npc_id_counter)
                    self.npc_id_counter += 1
                    crianca.idade = random.randint(3, 16)
                    crianca.sobrenome = a.sobrenome
                    a.filhos.append(crianca.id)
                    b.filhos.append(crianca.id)
                    crianca.familia = [a.id, b.id]
                    self.npcs.append(crianca)

    def update(self, dt, player):
        """Atualiza todos os NPCs — apenas os próximos do jogador (otimização)"""
        px, py = player.x, player.y
        for npc in self.npcs:
            d = abs(npc.x - px) + abs(npc.y - py)
            if d > 40:  # só atualiza NPCs próximos
                continue
            proximos_npcs = [n for n in self.npcs if n != npc and abs(n.x-npc.x)+abs(n.y-npc.y) < 10]
            proximos_z = [z for z in self.world.zombies if abs(z.x-npc.x)+abs(z.y-npc.y) < 12]
            npc.update(dt, self.world, player, proximos_npcs, proximos_z)

        # Espalhar rumores entre NPCs próximos
        if random.random() < 0.01:
            for npc in self.npcs:
                proximos = [n for n in self.npcs if n != npc and abs(n.x-npc.x)+abs(n.y-npc.y) < 5]
                for p in proximos:
                    npc.espalhar_rumor(p)

    def get_npcs_vivos(self):
        return [n for n in self.npcs if n.esta_vivo]

    def get_npcs_mortos_possuiveis(self):
        return [n for n in self.npcs if n.morto and hasattr(n, 'pode_ser_possuido')]

    def spawn_npc(self, x=None, y=None):
        if x is None:
            pos = self.world._random_passable()
            x, y = pos
        npc = NPC(x, y, self.world, self.npc_id_counter)
        self.npc_id_counter += 1
        self.npcs.append(npc)
        return npc
