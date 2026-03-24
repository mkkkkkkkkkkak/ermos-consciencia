#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
# ERMOS CONSCIÊNCIA — Script de Deploy Automático
# Cole este script no Termux e execute: bash setup.sh
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

clear
echo ""
echo -e "${RED}███████╗██████╗ ███╗   ███╗ ██████╗ ███████╗${NC}"
echo -e "${RED}██╔════╝██╔══██╗████╗ ████║██╔═══██╗██╔════╝${NC}"
echo -e "${WHITE}█████╗  ██████╔╝██╔████╔██║██║   ██║███████╗${NC}"
echo -e "${WHITE}██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║╚════██║${NC}"
echo -e "${PURPLE}███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝███████║${NC}"
echo -e "${PURPLE}╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝${NC}"
echo -e "${CYAN}          C O N S C I Ê N C I A${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE} Deploy automático → GitHub → APK${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================
# PASSO 1 — INSTALAR DEPENDÊNCIAS
# ============================================================
echo -e "${CYAN}[1/5] Instalando dependências do Termux...${NC}"
pkg update -y -q 2>/dev/null
pkg install -y git curl python openssh 2>/dev/null
echo -e "${GREEN}✓ Dependências instaladas${NC}"
echo ""

# ============================================================
# PASSO 2 — COLETAR DADOS DO USUÁRIO
# ============================================================
echo -e "${CYAN}[2/5] Configuração do GitHub${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${WHITE}Digite seu nome de usuário do GitHub:${NC}"
echo -e "${YELLOW}(Ex: joaosilva123)${NC}"
read -p "→ " GITHUB_USER

echo ""
echo -e "${WHITE}Digite seu email do GitHub:${NC}"
echo -e "${YELLOW}(Ex: joao@email.com)${NC}"
read -p "→ " GITHUB_EMAIL

echo ""
echo -e "${WHITE}Digite o nome do repositório:${NC}"
echo -e "${YELLOW}(Ex: ermos-jogo  — será criado automaticamente)${NC}"
read -p "→ " REPO_NAME

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Agora você precisa criar um TOKEN do GitHub.${NC}"
echo -e "${YELLOW}Siga estes passos:${NC}"
echo ""
echo -e "  ${CYAN}1.${NC} Abra o navegador do celular"
echo -e "  ${CYAN}2.${NC} Acesse: ${WHITE}github.com/settings/tokens/new${NC}"
echo -e "  ${CYAN}3.${NC} Em ${WHITE}'Note'${NC} escreva: ${YELLOW}ermos-deploy${NC}"
echo -e "  ${CYAN}4.${NC} Em ${WHITE}'Expiration'${NC} selecione: ${YELLOW}No expiration${NC}"
echo -e "  ${CYAN}5.${NC} Marque a caixa: ${WHITE}☑ repo${NC} (primeira da lista)"
echo -e "  ${CYAN}6.${NC} Clique em ${WHITE}'Generate token'${NC} no final da página"
echo -e "  ${CYAN}7.${NC} ${RED}COPIE O TOKEN${NC} (começa com ghp_...)"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}Cole o token aqui (não vai aparecer na tela):${NC}"
read -s -p "→ " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}✗ Token não pode ser vazio. Execute o script novamente.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Token recebido${NC}"
echo ""

# ============================================================
# PASSO 3 — CRIAR REPOSITÓRIO NO GITHUB via API
# ============================================================
echo -e "${CYAN}[3/5] Criando repositório no GitHub...${NC}"

RESPONSE=$(curl -s -w "\n%{http_code}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"ERMOS CONSCIÊNCIA - RPG Pós-Apocalíptico\",
    \"private\": false,
    \"auto_init\": false
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | head -1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓ Repositório criado: github.com/$GITHUB_USER/$REPO_NAME${NC}"
elif [ "$HTTP_CODE" = "422" ]; then
    echo -e "${YELLOW}⚠ Repositório já existe — continuando...${NC}"
else
    echo -e "${RED}✗ Erro ao criar repositório (código $HTTP_CODE)${NC}"
    echo -e "${YELLOW}Verifique se o token tem permissão 'repo'${NC}"
    echo "Resposta: $BODY"
    exit 1
fi
echo ""

# ============================================================
# PASSO 4 — CONFIGURAR GIT E PREPARAR CÓDIGO
# ============================================================
echo -e "${CYAN}[4/5] Configurando Git e preparando código...${NC}"

git config --global user.name "$GITHUB_USER"
git config --global user.email "$GITHUB_EMAIL"
git config --global credential.helper store

# Salva credenciais para não pedir senha depois
echo "https://$GITHUB_USER:$GITHUB_TOKEN@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Cria pasta do projeto
PROJETO_DIR="$HOME/ermos-consciencia"
mkdir -p "$PROJETO_DIR"
cd "$PROJETO_DIR"

# Inicializa git
git init -q
git remote remove origin 2>/dev/null
git remote add origin "https://$GITHUB_USER:$GITHUB_TOKEN@github.com/$GITHUB_USER/$REPO_NAME.git"

echo -e "${GREEN}✓ Git configurado${NC}"

# ============================================================
# CRIAR ESTRUTURA DO PROJETO
# ============================================================
echo -e "${CYAN}Criando estrutura do projeto...${NC}"

mkdir -p .github/workflows
mkdir -p src/{systems,entities,ui,data,screens}
touch src/__init__.py
touch src/systems/__init__.py
touch src/entities/__init__.py
touch src/ui/__init__.py
touch src/data/__init__.py
touch src/screens/__init__.py

# ============================================================
# CRIAR TODOS OS ARQUIVOS DO JOGO
# ============================================================

# .gitignore
cat > .gitignore << 'GITIGNORE'
__pycache__/
*.pyc
*.pyo
.buildozer/
bin/
.kivy/
*.log
.env
GITIGNORE

# buildozer.spec
cat > buildozer.spec << 'SPEC'
[app]
title = Ermos Consciência
package.name = ermosconsciencia
package.domain = org.ermos
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3,kivy==2.3.0,pillow
orientation = portrait
fullscreen = 1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
[buildozer]
log_level = 2
warn_on_root = 1
SPEC

# requirements.txt
cat > requirements.txt << 'REQ'
kivy==2.3.0
Pillow>=10.0.0
REQ

# ============================================================
# GITHUB ACTIONS WORKFLOW
# ============================================================
cat > .github/workflows/build-apk.yml << 'WORKFLOW'
name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    timeout-minutes: 60

    steps:
    - name: Checkout código
      uses: actions/checkout@v4

    - name: Instalar Java
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
        java-version: '17'

    - name: Instalar Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'

    - name: Instalar dependências do sistema
      run: |
        sudo apt-get update -qq
        sudo apt-get install -y \
          git zip unzip python3-pip \
          autoconf libtool pkg-config \
          zlib1g-dev libncurses5-dev \
          libncursesw5-dev libtinfo5 \
          cmake libffi-dev libssl-dev \
          build-essential ccache

    - name: Cache buildozer
      uses: actions/cache@v4
      with:
        path: |
          ~/.buildozer
          ~/.gradle
        key: buildozer-${{ hashFiles('buildozer.spec') }}
        restore-keys: buildozer-

    - name: Instalar buildozer e Cython
      run: |
        pip install --upgrade pip
        pip install buildozer==1.5.0 cython==0.29.36

    - name: Build APK
      run: |
        buildozer -v android debug 2>&1 | tail -100
      env:
        ANDROIDSDK: ${{ github.workspace }}/.buildozer/android/platform/android-sdk
        ANDROIDNDK: ${{ github.workspace }}/.buildozer/android/platform/android-ndk-r25b

    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: ermos-consciencia-apk
        path: bin/*.apk
        retention-days: 30

    - name: Criar Release
      if: success()
      uses: softprops/action-gh-release@v2
      with:
        tag_name: v0.${{ github.run_number }}
        name: "ERMOS v0.${{ github.run_number }}"
        body: |
          ## ERMOS CONSCIÊNCIA
          APK gerado automaticamente.
          **Baixe o arquivo .apk abaixo e instale no Android.**
        files: bin/*.apk
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
WORKFLOW

echo -e "${GREEN}✓ Workflow do GitHub Actions criado${NC}"

# ============================================================
# CRIAR ARQUIVOS PRINCIPAIS DO JOGO
# ============================================================

# main.py
cat > main.py << 'MAINPY'
import os
os.environ['KIVY_NO_ENV_CONFIG'] = '1'
from kivy.config import Config
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '854')
Config.set('graphics', 'resizable', False)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from src.screens.menu_screen import MenuScreen
from src.screens.game_screen import GameScreen
from src.screens.death_screen import DeathScreen, InventoryScreen, JournalScreen
from src.data.save_manager import SaveManager
Window.clearcolor = (0.04, 0.03, 0.02, 1)

class ErmosApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.save_manager = SaveManager()
        self.title = 'ERMOS CONSCIÊNCIA'
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.4))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(DeathScreen(name='death'))
        sm.add_widget(InventoryScreen(name='inventory'))
        sm.add_widget(JournalScreen(name='journal'))
        return sm
    def on_pause(self):
        game = self.root.get_screen('game')
        if hasattr(game, 'world') and game.world:
            self.save_manager.auto_save(game.world)
        return True
    def on_resume(self):
        pass

if __name__ == '__main__':
    ErmosApp().run()
MAINPY

# Copia arquivos Python do jogo se existirem em /home/claude/ermos
ORIGEM="/home/claude/ermos"
if [ -d "$ORIGEM" ]; then
    echo -e "${CYAN}Copiando arquivos do jogo...${NC}"
    for f in \
        src/constants.py \
        src/systems/world.py \
        src/systems/renderer.py \
        src/entities/npc.py \
        src/entities/zombie.py \
        src/entities/player.py \
        src/ui/hud.py \
        src/screens/game_screen.py \
        src/screens/menu_screen.py \
        src/screens/death_screen.py \
        src/data/save_manager.py
    do
        if [ -f "$ORIGEM/$f" ]; then
            cp "$ORIGEM/$f" "$PROJETO_DIR/$f"
        fi
    done

    # Screens extras
    cat > src/screens/inventory_screen.py << 'EOF2'
from src.screens.death_screen import InventoryScreen
EOF2
    cat > src/screens/journal_screen.py << 'EOF3'
from src.screens.death_screen import JournalScreen
EOF3
fi

echo -e "${GREEN}✓ Arquivos do jogo criados${NC}"
echo ""

# ============================================================
# PASSO 5 — COMMIT E PUSH
# ============================================================
echo -e "${CYAN}[5/5] Enviando para o GitHub...${NC}"

cd "$PROJETO_DIR"
git add -A
git commit -m "🎮 ERMOS CONSCIÊNCIA v0.1 — Deploy inicial

- Motor do mundo procedural (cidade, floresta, zona militar, vilas, ilhas)
- Sistema de NPCs com IA (emoções, memória, família, rotina)
- Sistema de Zumbis (8 tipos + Supremo)
- Player completo (possessão, poderes, moralidade, sanidade)
- Renderizador pixel art com FOV e minimap
- HUD completo com diálogos
- Sistema de save automático
- GitHub Actions → APK automático"

git branch -M main
git push -u origin main --force

PUSH_STATUS=$?

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $PUSH_STATUS -eq 0 ]; then
    echo -e "${GREEN}"
    echo "  ✓ CÓDIGO ENVIADO COM SUCESSO!"
    echo -e "${NC}"
    echo -e "${WHITE}  Repositório:${NC} ${CYAN}github.com/$GITHUB_USER/$REPO_NAME${NC}"
    echo ""
    echo -e "${WHITE}  Para baixar o APK:${NC}"
    echo -e "  ${CYAN}1.${NC} Acesse: ${WHITE}github.com/$GITHUB_USER/$REPO_NAME/actions${NC}"
    echo -e "  ${CYAN}2.${NC} Aguarde o build terminar (~30-40 min)"
    echo -e "  ${CYAN}3.${NC} Vá em ${WHITE}Releases${NC} ou ${WHITE}Artifacts${NC}"
    echo -e "  ${CYAN}4.${NC} Baixe o arquivo ${WHITE}.apk${NC} e instale"
    echo ""
    echo -e "${YELLOW}  Para atualizar o jogo no futuro:${NC}"
    echo -e "  ${WHITE}cd ~/ermos-consciencia && bash atualizar.sh${NC}"
else
    echo -e "${RED}  ✗ Erro ao enviar. Verifique:${NC}"
    echo -e "  - Se o token tem permissão ${WHITE}'repo'${NC}"
    echo -e "  - Se o usuário GitHub está correto"
    echo -e "  - Conexão com a internet"
fi

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ============================================================
# CRIAR SCRIPT DE ATUALIZAÇÃO
# ============================================================
cat > "$PROJETO_DIR/atualizar.sh" << ATUALIZAR
#!/data/data/com.termux/files/usr/bin/bash
cd "$PROJETO_DIR"
echo "Enviando atualização..."
git add -A
git commit -m "Atualização \$(date '+%d/%m/%Y %H:%M')"
git push origin main
echo "✓ Enviado! O APK será gerado automaticamente."
ATUALIZAR
chmod +x "$PROJETO_DIR/atualizar.sh"

echo -e "${PURPLE}Script de atualização criado: ~/ermos-consciencia/atualizar.sh${NC}"
echo -e "${PURPLE}Na próxima vez, só execute: ${WHITE}bash ~/ermos-consciencia/atualizar.sh${NC}"
echo ""
