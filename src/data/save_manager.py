"""
ERMOS - Sistema de Save
Salva e carrega o estado do jogo em JSON
"""
import json
import os
import time
from src.constants import *


SAVE_DIR = os.path.join(os.path.expanduser('~'), '.ermos_saves')
SAVE_FILE = os.path.join(SAVE_DIR, 'save_slot1.json')
AUTO_SAVE_FILE = os.path.join(SAVE_DIR, 'autosave.json')


class SaveManager:
    def __init__(self):
        os.makedirs(SAVE_DIR, exist_ok=True)

    def save(self, world, filename=None):
        f = filename or SAVE_FILE
        data = self._serialize(world)
        try:
            with open(f, 'w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar: {e}")
            return False

    def auto_save(self, world):
        return self.save(world, AUTO_SAVE_FILE)

    def load(self, filename=None):
        f = filename or SAVE_FILE
        if not os.path.exists(f):
            f = AUTO_SAVE_FILE
        if not os.path.exists(f):
            return None
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                return json.load(fp)
        except Exception as e:
            print(f"Erro ao carregar: {e}")
            return None

    def has_save(self):
        return os.path.exists(SAVE_FILE) or os.path.exists(AUTO_SAVE_FILE)

    def _serialize(self, world):
        """Serializa apenas dados essenciais (não o mapa inteiro)"""
        player = world.player if hasattr(world, 'player') else None
        data = {
            'versao': '0.1',
            'timestamp': time.time(),
            'world': {
                'seed': world.seed,
                'dia': world.day_count,
                'hora': world.time_of_day,
                'clima': world.weather,
                'virus_evolution': world.virus_evolution,
                'historico': world.world_history[-50:],
            },
        }
        if player:
            data['player'] = {
                'x': player.x, 'y': player.y,
                'hp': player.hp, 'hp_max': player.hp_max,
                'stamina': player.stamina,
                'fome': player.fome, 'sede': player.sede,
                'sanidade': player.sanidade,
                'humanidade': player.humanidade,
                'xp': player.xp, 'nivel': player.nivel,
                'inventario': player.inventario,
                'arma_equipada': player.arma_equipada,
                'reputacao': player.reputacao_global,
                'caminho': player.caminho,
                'mortes': player.mortes,
                'npcs_ajudados': player.npcs_ajudados,
                'poderes': player.poderes_desbloqueados,
                'diario': player.diario[-100:],
                'acoes_boas': player.acoes_boas,
                'acoes_ruins': player.acoes_ruins,
            }
        return data

    def apply_save(self, data, world, player):
        """Aplica dados salvos ao mundo e player"""
        if 'world' in data:
            wd = data['world']
            world.day_count = wd.get('dia', 1)
            world.time_of_day = wd.get('hora', 8.0)
            world.weather = wd.get('clima', 'claro')
            world.virus_evolution = wd.get('virus_evolution', 0)
            world.world_history = wd.get('historico', [])

        if 'player' in data and player:
            pd = data['player']
            player.x = pd.get('x', world.width//2)
            player.y = pd.get('y', world.height*3//4)
            player.hp = pd.get('hp', 100)
            player.hp_max = pd.get('hp_max', 100)
            player.fome = pd.get('fome', 100)
            player.sede = pd.get('sede', 100)
            player.sanidade = pd.get('sanidade', 100)
            player.humanidade = pd.get('humanidade', 100)
            player.xp = pd.get('xp', 0)
            player.nivel = pd.get('nivel', 1)
            player.inventario = pd.get('inventario', {})
            player.arma_equipada = pd.get('arma_equipada', 'faca')
            player.reputacao_global = pd.get('reputacao', 0)
            player.caminho = pd.get('caminho', 'neutro')
            player.mortes = pd.get('mortes', 0)
            player.npcs_ajudados = pd.get('npcs_ajudados', 0)
            player.poderes_desbloqueados = pd.get('poderes', ['possessao_basica'])
            player.diario = pd.get('diario', [])
            player.acoes_boas = pd.get('acoes_boas', 0)
            player.acoes_ruins = pd.get('acoes_ruins', 0)
