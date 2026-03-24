"""
ERMOS CONSCIÊNCIA - Constantes e Configurações
"""

# === TELA ===
SCREEN_W = 480
SCREEN_H = 854
TILE_SIZE = 32
MAP_W = 80   # tiles
MAP_H = 80   # tiles

# === TEMPO ===
DAY_DURATION = 600       # segundos por dia completo (10 min)
HOUR_DURATION = DAY_DURATION / 24
TICK_RATE = 1/60         # 60 fps

# === MUNDO ===
WORLD_SEED = 42
REGIONS = ['cidade', 'floresta', 'militar', 'vila', 'oceano', 'ilha']

# === CLIMA ===
WEATHER_TYPES = {
    'claro':     {'temp_mod': 0,   'visib': 1.0, 'zumbi_mod': 1.0},
    'nublado':   {'temp_mod': -2,  'visib': 0.8, 'zumbi_mod': 1.1},
    'chuva':     {'temp_mod': -5,  'visib': 0.6, 'zumbi_mod': 0.9},
    'tempestade':{'temp_mod': -10, 'visib': 0.3, 'zumbi_mod': 0.7},
    'neve':      {'temp_mod': -20, 'visib': 0.5, 'zumbi_mod': 0.8},
    'neblina':   {'temp_mod': -3,  'visib': 0.4, 'zumbi_mod': 1.3},
}

# === JOGADOR ===
PLAYER_STATS = {
    'hp': 100,
    'stamina': 100,
    'fome': 100,
    'sede': 100,
    'sanidade': 100,
    'temperatura': 37.0,
    'humanidade': 100,   # reduz ao usar possessão
    'xp': 0,
    'nivel': 1,
}

# === SOBREVIVÊNCIA (por hora de jogo) ===
HUNGER_RATE    = 2.5
THIRST_RATE    = 3.5
STAMINA_REGEN  = 15
STAMINA_DRAIN  = 20   # ao correr

# === TEMPERATURA CORPORAL ===
TEMP_DANGER_LOW  = 35.0
TEMP_DANGER_HIGH = 39.5
TEMP_DEATH_LOW   = 32.0
TEMP_DEATH_HIGH  = 42.0

# === POSSESSÃO ===
POSSESSION_HUMANIDADE_COST = 5     # por uso
POSSESSION_DURATION_MAX    = 120   # segundos
POSSESSION_RANGE           = 8     # tiles
POSSESSION_SANIDADE_DRAIN  = 0.5   # por segundo possuído

# === PODERES ===
POWERS = {
    'possessao_basica':    {'custo_humanidade': 5,  'nivel_req': 1,  'descricao': 'Possuir corpo morto próximo'},
    'possessao_avancada':  {'custo_humanidade': 10, 'nivel_req': 5,  'descricao': 'Possessão à distância'},
    'controle_mental':     {'custo_humanidade': 15, 'nivel_req': 10, 'descricao': 'Influenciar NPC vivo'},
    'manipular_zumbi':     {'custo_humanidade': 20, 'nivel_req': 15, 'descricao': 'Controlar zumbi temporariamente'},
    'visao_espiritual':    {'custo_humanidade': 3,  'nivel_req': 3,  'descricao': 'Ver auras e emoções dos NPCs'},
    'terror_sobrenatural': {'custo_humanidade': 25, 'nivel_req': 20, 'descricao': 'Causar pânico em área'},
}

# === NPCS ===
NPC_NAMES_M = ['Carlos','Miguel','João','Pedro','Rafael','Bruno','Diego','Mateus','Lucas','André',
               'Tiago','Vitor','Henrique','Gabriel','Rodrigo','Felipe','Caio','Thiago','Igor','Alan']
NPC_NAMES_F = ['Ana','Maria','Julia','Luisa','Camila','Beatriz','Sofia','Fernanda','Leticia','Amanda',
               'Priscila','Vanessa','Bianca','Natalia','Larissa','Isabela','Renata','Claudia','Patricia','Sara']

NPC_TRAITS = ['bondoso','ganancioso','desconfiado','corajoso','covarde','leal','traidor',
              'inteligente','impulsivo','calculista','misericordioso','cruel','curioso','paranóico']

NPC_GOALS = ['encontrar familia','construir casa','liderar vila','vingar morte',
             'encontrar cura','acumular recursos','proteger criancas','descobrir origem do virus']

NPC_OCCUPATIONS = ['coletor','construtor','medico','soldado','comerciante','fazendeiro',
                   'explorador','mecanico','cozinheiro','lider','espiao','ladrao']

# === ZUMBIS ===
ZOMBIE_TYPES = {
    'errante':   {'hp':30,  'dano':8,   'vel':0.6, 'visao':5,  'xp':10,  'cor':(0.3,0.5,0.2,1)},
    'corredor':  {'hp':40,  'dano':12,  'vel':1.4, 'visao':7,  'xp':20,  'cor':(0.4,0.3,0.1,1)},
    'escalador': {'hp':35,  'dano':10,  'vel':1.0, 'visao':6,  'xp':25,  'cor':(0.3,0.4,0.2,1)},
    'tank':      {'hp':200, 'dano':30,  'vel':0.4, 'visao':4,  'xp':50,  'cor':(0.2,0.2,0.2,1)},
    'inteligente':{'hp':60, 'dano':15,  'vel':0.9, 'visao':10, 'xp':75,  'cor':(0.4,0.5,0.3,1)},
    'militar':   {'hp':80,  'dano':20,  'vel':1.1, 'visao':8,  'xp':100, 'cor':(0.3,0.4,0.3,1)},
    'cientifico':{'hp':120, 'dano':25,  'vel':0.8, 'visao':12, 'xp':200, 'cor':(0.5,0.6,0.2,1)},
    'supremo':   {'hp':500, 'dano':50,  'vel':1.2, 'visao':15, 'xp':1000,'cor':(0.7,0.1,0.1,1)},
}

# Supremo só aparece 1 vez por mundo
SUPREMO_SPAWN_CHANCE = 0.0001

# === ITENS ===
ITEMS = {
    # Comida
    'lata_feijao':    {'tipo':'comida', 'fome':30, 'sede':-5,  'peso':0.5, 'icone':'🥫'},
    'agua_garrafa':   {'tipo':'agua',   'fome':0,  'sede':40,  'peso':0.5, 'icone':'💧'},
    'carne_crua':     {'tipo':'comida', 'fome':20, 'sede':-10, 'peso':0.8, 'doenca_risco':0.3, 'icone':'🥩'},
    'fruta':          {'tipo':'comida', 'fome':15, 'sede':10,  'peso':0.2, 'icone':'🍎'},
    'ração_militar':  {'tipo':'comida', 'fome':60, 'sede':-10, 'peso':0.4, 'icone':'🎖️'},
    # Médico
    'bandagem':       {'tipo':'medico', 'cura':20, 'peso':0.1, 'icone':'🩹'},
    'antibiotico':    {'tipo':'medico', 'cura_doenca':True, 'peso':0.1, 'icone':'💊'},
    'morphina':       {'tipo':'medico', 'cura':50, 'dor':True, 'peso':0.2, 'icone':'💉'},
    # Armas
    'faca':           {'tipo':'arma', 'dano':15, 'durabilidade':100, 'vel_ataque':1.5, 'peso':0.5, 'icone':'🔪'},
    'bat_prego':      {'tipo':'arma', 'dano':25, 'durabilidade':80,  'vel_ataque':0.8, 'peso':1.5, 'icone':'🔨'},
    'pistola':        {'tipo':'arma_fogo', 'dano':45, 'municao':12, 'durabilidade':200, 'peso':0.9, 'barulho':8, 'icone':'🔫'},
    'espingarda':     {'tipo':'arma_fogo', 'dano':80, 'municao':6,  'durabilidade':150, 'peso':3.0, 'barulho':12,'icone':'🔫'},
    'arco':           {'tipo':'arma_distancia', 'dano':30, 'municao':20, 'durabilidade':120, 'peso':1.5, 'barulho':1,'icone':'🏹'},
    'machado':        {'tipo':'arma', 'dano':35, 'durabilidade':150, 'vel_ataque':0.6, 'peso':2.0, 'icone':'🪓'},
    # Ferramentas
    'isqueiro':       {'tipo':'ferramenta', 'uso':'fogo', 'peso':0.1, 'icone':'🔥'},
    'corda':          {'tipo':'ferramenta', 'uso':'escalar', 'peso':0.5, 'icone':'🪢'},
    'radio':          {'tipo':'ferramenta', 'uso':'comunicar', 'peso':0.8, 'icone':'📻'},
    'mapa':           {'tipo':'ferramenta', 'uso':'navegar', 'peso':0.1, 'icone':'🗺️'},
    # Recursos
    'madeira':        {'tipo':'recurso', 'peso':2.0, 'icone':'🪵'},
    'metal_sucata':   {'tipo':'recurso', 'peso':1.5, 'icone':'⚙️'},
    'tecido':         {'tipo':'recurso', 'peso':0.3, 'icone':'🧵'},
    'combustivel':    {'tipo':'recurso', 'peso':1.0, 'icone':'⛽'},
}

# === CONSTRUÇÕES ===
BUILDINGS = {
    'fogueira':   {'custo':{'madeira':3}, 'hp':50,  'funcao':'calor/cozinhar'},
    'abrigo':     {'custo':{'madeira':10,'tecido':5}, 'hp':100, 'funcao':'dormir/proteger'},
    'casa':       {'custo':{'madeira':25,'metal_sucata':10}, 'hp':300, 'funcao':'moradia'},
    'torre_vigia':{'custo':{'madeira':20,'metal_sucata':5},  'hp':150, 'funcao':'visao'},
    'barricada':  {'custo':{'madeira':8,'metal_sucata':5},   'hp':200, 'funcao':'defesa'},
    'fazenda':    {'custo':{'madeira':15,'tecido':5},        'hp':100, 'funcao':'comida'},
    'hospital':   {'custo':{'madeira':30,'metal_sucata':20,'tecido':10}, 'hp':400, 'funcao':'cura'},
    'forja':      {'custo':{'pedra':20,'metal_sucata':15},   'hp':250, 'funcao':'crafting'},
}

# === REPUTAÇÃO ===
REP_LEVELS = {
    -100: 'Monstro',
    -60:  'Temido',
    -30:  'Suspeito',
    0:    'Desconhecido',
    30:   'Conhecido',
    60:   'Respeitado',
    100:  'Lendário',
}

# === DOENÇAS ===
DISEASES = {
    'resfriado':   {'hp_drain':0.5, 'stamina_drain':1.0, 'duracao':48, 'cura':'descanso'},
    'pneumonia':   {'hp_drain':2.0, 'stamina_drain':3.0, 'duracao':96, 'cura':'antibiotico'},
    'infeccao':    {'hp_drain':1.5, 'stamina_drain':2.0, 'duracao':72, 'cura':'antibiotico'},
    'intoxicacao': {'hp_drain':3.0, 'stamina_drain':4.0, 'duracao':24, 'cura':'descanso'},
    'virus_z':     {'hp_drain':5.0, 'stamina_drain':5.0, 'duracao':999, 'cura':None, 'fatal':True},
}

# === CORES UI ===
COLOR_BG       = (0.04, 0.03, 0.02, 1)
COLOR_PANEL    = (0.08, 0.07, 0.05, 0.95)
COLOR_BLOOD    = (0.55, 0.0,  0.0,  1)
COLOR_BONE     = (0.91, 0.86, 0.78, 1)
COLOR_EMBER    = (0.83, 0.34, 0.04, 1)
COLOR_PALE     = (0.72, 0.66, 0.60, 1)
COLOR_GREEN    = (0.23, 0.29, 0.18, 1)
COLOR_TOXIC    = (0.42, 0.48, 0.24, 1)

# === FONTES ===
FONT_TITLE  = 'Roboto'
FONT_BODY   = 'Roboto'
