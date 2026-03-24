"""
ERMOS - Entidade do Jogador
Sobrevivência, possessão, poderes, combate, psicológico
"""
import random
import math
from src.constants import *


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        # === STATS BASE ===
        self.hp = 100.0
        self.hp_max = 100.0
        self.stamina = 100.0
        self.stamina_max = 100.0
        self.fome = 100.0
        self.sede = 100.0
        self.sanidade = 100.0
        self.temperatura = 37.0
        self.humanidade = 100.0   # perde ao usar possessão
        self.xp = 0
        self.nivel = 1

        # === MOVIMENTO ===
        self.vel = 2.5
        self.correndo = False
        self.barulho_ativo = 0    # aumenta quando usa armas de fogo
        self.ultimo_movimento = None
        self.direcao = (0, 1)

        # === POSSESSÃO ===
        self.possuindo = False
        self.corpo_possuido = None    # referência ao NPC/Zombie possuído
        self.timer_possessao = 0
        self.poderes_desbloqueados = ['possessao_basica']
        self.poder_ativo = None

        # === IDENTIDADE ===
        # Memórias dos corpos possuídos acumulam
        self.memorias_alheias = []
        self.confusao_identidade = 0   # 0-100, sobe com possessão
        self.alucinacoes_ativas = []

        # === INVENTÁRIO ===
        self.inventario = {
            'agua_garrafa': 2,
            'lata_feijao': 1,
            'faca': 1,
            'bandagem': 2,
        }
        self.capacidade_max = 20
        self.arma_equipada = 'faca'
        self.municao = {}

        # === DOENÇAS ===
        self.doencas = []

        # === REPUTAÇÃO ===
        self.reputacao_global = 0    # -100 a 100
        self.reputacao_regioes = {}
        self.mortes_causadas = 0
        self.npcs_ajudados = 0
        self.crimes_cometidos = 0
        self.procurado = False
        self.recompensa = 0

        # === MORALIDADE ===
        self.caminho = 'neutro'   # humano, sombrio, neutro
        self.acoes_boas = 0
        self.acoes_ruins = 0
        self.aparencia_changed = False   # muda ao ir para sombrio

        # === VILA ===
        self.vila_liderada = None

        # === COMBATE ===
        self.timer_ataque = 0
        self.vel_ataque = 0.5
        self.em_combate = False
        self.ultimo_dano_recebido = 0
        self.invulneravel_timer = 0

        # === PSICOLÓGICO ===
        self.timer_alucinacao = 0
        self.sons_estranhos = []
        self.realidade_instavel = False

        # === MORTE / REVIVE ===
        self.mortes = 0
        self.morto = False
        self.pode_reviver = True

        # === LOG PESSOAL ===
        self.diario = []
        self.missoes = []
        self.missoes_completas = []

    def update(self, dt, world, teclas, joystick=None):
        if self.morto:
            return

        # Timers
        self.timer_ataque = max(0, self.timer_ataque - dt)
        self.invulneravel_timer = max(0, self.invulneravel_timer - dt)
        self.barulho_ativo = max(0, self.barulho_ativo - dt)

        # === NECESSIDADES (por hora de jogo) ===
        mult = 1.0
        if self.correndo:
            mult = 2.0
        if world.weather in ('neve', 'tempestade'):
            mult *= 1.5

        self.fome = max(0, self.fome - HUNGER_RATE * dt / 3600 * mult)
        self.sede = max(0, self.sede - THIRST_RATE * dt / 3600 * mult)

        # Stamina
        if self.correndo:
            self.stamina = max(0, self.stamina - STAMINA_DRAIN * dt)
            if self.stamina <= 0:
                self.correndo = False
        else:
            self.stamina = min(self.stamina_max, self.stamina + STAMINA_REGEN * dt)

        # Temperatura corporal
        self._atualizar_temperatura(dt, world)

        # Dano por necessidades
        if self.fome <= 0:
            self.hp -= 1.0 * dt / 60
            self._log("Estou com muita fome...")
        if self.sede <= 0:
            self.hp -= 2.0 * dt / 60
            self._log("Estou desidratando...")
        if self.temperatura < TEMP_DANGER_LOW:
            self.hp -= 1.5 * dt / 60
        if self.temperatura > TEMP_DANGER_HIGH:
            self.hp -= 2.0 * dt / 60

        # Doenças
        self._atualizar_doencas(dt)

        # Possessão ativa
        if self.possuindo:
            self._atualizar_possessao(dt, world)

        # Psicológico
        self._atualizar_psicologico(dt, world)

        # Moralidade — determina caminho
        self._atualizar_caminho()

        # Morte
        if self.hp <= 0:
            self._morrer()

    def _atualizar_temperatura(self, dt, world):
        clima = world.weather
        temp_mod = WEATHER_TYPES.get(clima, {}).get('temp_mod', 0)
        hora = world.time_of_day
        if world.is_night:
            temp_mod -= 3

        alvo = 37.0 + temp_mod * 0.1
        if self.temperatura > alvo:
            self.temperatura -= 0.1 * dt
        elif self.temperatura < alvo:
            self.temperatura += 0.05 * dt

        # Fogueira próxima aquece
        # (verificado pela GameScreen)

    def _atualizar_doencas(self, dt):
        novas = []
        for d in self.doencas:
            d['duracao_restante'] -= dt / 3600
            self.hp -= DISEASES[d['tipo']]['hp_drain'] * dt / 3600
            self.stamina_max = max(20, self.stamina_max - DISEASES[d['tipo']]['stamina_drain'] * dt / 3600)
            if d['duracao_restante'] > 0:
                novas.append(d)
            elif DISEASES[d['tipo']].get('fatal') and d['duracao_restante'] <= 0:
                self._morrer()  # vírus z sempre fatal
        self.doencas = novas

    def _atualizar_possessao(self, dt, world):
        self.timer_possessao -= dt
        self.sanidade -= POSSESSION_SANIDADE_DRAIN * dt
        self.humanidade -= 0.1 * dt   # lenta perda de humanidade

        # Acumula memórias alheias
        if self.corpo_possuido and random.random() < 0.01:
            self.confusao_identidade = min(100, self.confusao_identidade + 0.5)
            if hasattr(self.corpo_possuido, 'memorias') and self.corpo_possuido.memorias:
                mem = random.choice(self.corpo_possuido.memorias)
                self.memorias_alheias.append({
                    'texto': mem.descricao,
                    'de': self.corpo_possuido.nome_completo if hasattr(self.corpo_possuido, 'nome_completo') else 'Desconhecido'
                })

        if self.timer_possessao <= 0:
            self.sair_possessao(world)

    def _atualizar_psicologico(self, dt, world):
        # Sanidade cai à noite, com fome/sede baixos
        if world.is_night:
            self.sanidade = max(0, self.sanidade - 0.05 * dt)
        if self.fome < 20 or self.sede < 20:
            self.sanidade = max(0, self.sanidade - 0.1 * dt)

        # Alucinações quando sanidade < 30
        if self.sanidade < 30:
            self.timer_alucinacao -= dt
            if self.timer_alucinacao <= 0:
                self.timer_alucinacao = random.uniform(10, 30)
                self.alucinacoes_ativas.append(self._gerar_alucinacao())
                self.realidade_instavel = True

        # Recupera sanidade dormindo / em segurança
        # (implementado quando player descansa)

    def _gerar_alucinacao(self):
        tipos = [
            "Você ouve passos atrás de você...",
            "Uma sombra passa pelo canto da visão.",
            "Alguém sussurra seu nome.",
            "O corpo que você possuiu... está de pé.",
            "Você esquece momentaneamente quem é.",
            "As paredes parecem se mover.",
            "Você sente a presença de algo não-vivo.",
        ]
        return random.choice(tipos)

    def _atualizar_caminho(self):
        total = self.acoes_boas + self.acoes_ruins
        if total == 0:
            return
        ratio = self.acoes_boas / total
        if ratio > 0.65:
            self.caminho = 'humano'
        elif ratio < 0.35:
            self.caminho = 'sombrio'
            self.aparencia_changed = True
        else:
            self.caminho = 'neutro'

    def mover(self, dx, dy, dt, world):
        if self.possuindo and self.corpo_possuido:
            # Move o corpo possuído
            self.corpo_possuido.x += dx * self.vel * dt * 3
            self.corpo_possuido.y += dy * self.vel * dt * 3
            self.x = self.corpo_possuido.x
            self.y = self.corpo_possuido.y
            return

        vel = self.vel * (1.8 if self.correndo else 1.0)
        nx = self.x + dx * vel * dt * 3
        ny = self.y + dy * vel * dt * 3

        tile_x = world.get_tile(int(nx), int(self.y))
        tile_y = world.get_tile(int(self.x), int(ny))

        if tile_x and tile_x.passavel:
            self.x = nx
        if tile_y and tile_y.passavel:
            self.y = ny

        if dx != 0 or dy != 0:
            self.direcao = (dx, dy)
            self.ultimo_movimento = (dx, dy)

    def atacar(self, alvo):
        if self.timer_ataque > 0:
            return False
        arma = ITEMS.get(self.arma_equipada, {})
        dano = arma.get('dano', 5)
        tipo = arma.get('tipo', 'arma')

        if tipo == 'arma_fogo':
            chave_mun = self.arma_equipada
            if self.municao.get(chave_mun, 0) <= 0:
                self._log("Sem munição!")
                return False
            self.municao[chave_mun] -= 1
            barulho = arma.get('barulho', 8)
            self.barulho_ativo = barulho

        # Stamina
        if self.stamina < 10:
            dano = int(dano * 0.4)
            self._log("Estou exausto...")
        self.stamina = max(0, self.stamina - 10)

        # Desgaste da arma
        if self.arma_equipada in self.inventario:
            arma_item = ITEMS.get(self.arma_equipada, {})
            if 'durabilidade' in arma_item:
                # reduz durabilidade (controlado pelo inventário)
                pass

        alvo.receber_dano(dano)
        self.timer_ataque = 1.0 / (arma.get('vel_ataque', 1.0))
        self.em_combate = True
        return True

    def usar_item(self, item_key):
        if item_key not in self.inventario or self.inventario[item_key] <= 0:
            return False
        item = ITEMS.get(item_key, {})
        tipo = item.get('tipo', '')

        if tipo == 'comida':
            self.fome = min(100, self.fome + item.get('fome', 0))
            self.sede = max(0, self.sede + item.get('sede', 0))
        elif tipo == 'agua':
            self.sede = min(100, self.sede + item.get('sede', 0))
        elif tipo == 'medico':
            self.hp = min(self.hp_max, self.hp + item.get('cura', 0))
            if item.get('cura_doenca'):
                self.doencas = [d for d in self.doencas if not DISEASES.get(d['tipo'], {}).get('fatal')]

        self.inventario[item_key] -= 1
        if self.inventario[item_key] <= 0:
            del self.inventario[item_key]
        return True

    def adicionar_item(self, item_key, qtd=1):
        total = sum(self.inventario.values())
        if total >= self.capacidade_max:
            self._log("Inventário cheio!")
            return False
        self.inventario[item_key] = self.inventario.get(item_key, 0) + qtd
        return True

    def possuir(self, alvo, world):
        """Inicia possessão de um corpo"""
        if 'possessao_basica' not in self.poderes_desbloqueados:
            return False
        if self.humanidade <= 0:
            self._log("Perdi minha humanidade completamente.")
            return False
        dist = math.sqrt((self.x-alvo.x)**2+(self.y-alvo.y)**2)
        if dist > POSSESSION_RANGE and 'possessao_avancada' not in self.poderes_desbloqueados:
            self._log("Muito longe para possuir.")
            return False

        self.possuindo = True
        self.corpo_possuido = alvo
        self.timer_possessao = POSSESSION_DURATION_MAX
        self.humanidade -= POSSESSION_HUMANIDADE_COST
        self._log(f"Possuo o corpo... sinto suas memórias.")
        return True

    def sair_possessao(self, world):
        """Sai do corpo possuído"""
        if not self.possuindo:
            return
        alvo_pos = (self.corpo_possuido.x, self.corpo_possuido.y) if self.corpo_possuido else (self.x, self.y)

        # Reação dos NPCs próximos
        self._log("Saio do corpo. O mundo me vê.")
        self.possuindo = False
        old_corpo = self.corpo_possuido
        self.corpo_possuido = None
        self.sanidade -= 10
        self.confusao_identidade = min(100, self.confusao_identidade + 10)

        # Retorna ao posição do corpo
        if old_corpo:
            self.x = old_corpo.x + random.uniform(-1, 1)
            self.y = old_corpo.y + random.uniform(-1, 1)

        return alvo_pos   # para a GameScreen disparar reação dos NPCs

    def receber_dano(self, dano, fonte=None):
        if self.invulneravel_timer > 0:
            return
        self.hp -= dano
        self.invulneravel_timer = 0.3
        self.ultimo_dano_recebido = dano
        if self.hp <= 0:
            self._morrer()

    def adicionar_doenca(self, tipo):
        for d in self.doencas:
            if d['tipo'] == tipo:
                return  # já tem
        self.doencas.append({
            'tipo': tipo,
            'duracao_restante': DISEASES[tipo]['duracao'],
        })
        self._log(f"⚠️ Fui infectado com {tipo}!")

    def descansar(self, horas=8):
        self.sanidade = min(100, self.sanidade + 20 * horas)
        self.hp = min(self.hp_max, self.hp + 10 * horas)
        self.cansaco = 0

    def ganhar_xp(self, quantidade):
        self.xp += quantidade
        xp_necessario = self.nivel * 100
        if self.xp >= xp_necessario:
            self.xp -= xp_necessario
            self.nivel += 1
            self._ao_subir_nivel()
            return True
        return False

    def _ao_subir_nivel(self):
        self.hp_max += 5
        self.hp = min(self.hp_max, self.hp + 20)
        self.stamina_max += 5
        self._log(f"🎯 Nível {self.nivel}! Ficou mais forte.")

        # Desbloquear poderes por nível
        for poder, dados in POWERS.items():
            if dados['nivel_req'] == self.nivel and poder not in self.poderes_desbloqueados:
                self.poderes_desbloqueados.append(poder)
                self._log(f"✨ Poder desbloqueado: {dados['descricao']}")

    def acao_boa(self, valor=1):
        self.acoes_boas += valor
        self.reputacao_global = min(100, self.reputacao_global + valor * 2)
        self.npcs_ajudados += 1

    def acao_ruim(self, valor=1):
        self.acoes_ruins += valor
        self.reputacao_global = max(-100, self.reputacao_global - valor * 3)
        self.mortes_causadas += 1

    def _morrer(self):
        if self.morto:
            return
        self.morto = True
        self.mortes += 1
        self._log("Morri. Mas a consciência persiste...")

    def reviver(self, x, y):
        """Reviver via mecânica de possessão — perde progresso físico"""
        self.morto = False
        self.x = float(x)
        self.y = float(y)
        self.hp = 50.0
        self.fome = 40.0
        self.sede = 40.0
        self.stamina = 60.0
        self.humanidade = max(0, self.humanidade - 20)
        # Mantém XP e nível
        self._log("Volto. Diferente. Mais leve.")

    def _log(self, texto):
        if len(self.diario) > 200:
            self.diario.pop(0)
        self.diario.append(texto)

    @property
    def reputacao_label(self):
        r = self.reputacao_global
        for threshold in sorted(REP_LEVELS.keys(), reverse=True):
            if r >= threshold:
                return REP_LEVELS[threshold]
        return REP_LEVELS[-100]

    @property
    def peso_inventario(self):
        total = 0
        for item_key, qtd in self.inventario.items():
            peso = ITEMS.get(item_key, {}).get('peso', 0.5)
            total += peso * qtd
        return total
