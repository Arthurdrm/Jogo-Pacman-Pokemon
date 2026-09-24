"""Constantes e definições globais para o PokePacman (Ash Pac-Man)."""

# Dimensões da Grade (Grid 28 colunas x 31 linhas de jogo + HUD)
TILE_SIZE = 24
GRID_COLS = 28
GRID_ROWS = 31

# Largura e Altura da Janela
WINDOW_WIDTH = GRID_COLS * TILE_SIZE      # 672 pixels
HUD_TOP_HEIGHT = 2 * TILE_SIZE            # 48 pixels
GAME_HEIGHT = GRID_ROWS * TILE_SIZE       # 744 pixels
HUD_BOTTOM_HEIGHT = 2 * TILE_SIZE         # 48 pixels
WINDOW_HEIGHT = HUD_TOP_HEIGHT + GAME_HEIGHT + HUD_BOTTOM_HEIGHT # 840 pixels

FPS = 60

# Cores (RGB)
COLOR_BG = (12, 14, 20)
COLOR_WALL_OUTER = (35, 75, 180)
COLOR_WALL_INNER = (20, 45, 110)
COLOR_WALL_HIGHLIGHT = (80, 140, 240)
COLOR_GATE = (255, 175, 200)

COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_YELLOW = (255, 225, 30)
COLOR_RED = (235, 45, 45)
COLOR_GREEN = (45, 205, 90)
COLOR_CYAN = (40, 210, 240)
COLOR_ORANGE = (255, 140, 30)
COLOR_PURPLE = (145, 55, 200)
COLOR_SKIN = (255, 208, 178)
COLOR_HAIR = (22, 22, 28)

# Direções (dx, dy)
DIR_NONE = (0, 0)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# Estados do Jogo
STATE_READY = "READY"
STATE_PLAYING = "PLAYING"
STATE_DYING = "DYING"
STATE_GAMEOVER = "GAMEOVER"
STATE_VICTORY = "VICTORY"
STATE_PAUSED = "PAUSED"

# Pontuação
POINTS_POKEBALL = 10
POINTS_MASTERBALL = 50
POINTS_GHOST = [200, 400, 800, 1600]
POINTS_BONUS = {
    1: ("ORAN BERRY", 100),
    2: ("THUNDER STONE", 300),
    3: ("RARE CANDY", 500),
    4: ("MASTER FRUIT", 700),
}

# Tipos de Fantasmas Pokémon
GHOST_GENGAR = "gengar"   # Vermelho (Blinky) - Perseguição Direta
GHOST_GASTLY = "gastly"   # Rosa (Pinky) - Emboscada (Antecipa 4 passos)
GHOST_HAUNTER = "haunter" # Ciano (Inky) - Flanqueador / Vetor combinado
GHOST_KOFFING = "koffing" # Laranja (Clyde) - Disperso / Tímido se próximo
