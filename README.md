# 🧢 PokePacman — Ash Ketchum Pac-Man Edition

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Engine](https://img.shields.io/badge/Engine-Pygame--CE%202.5%2B-yellow.svg)](https://pyga.me/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-success.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Um clássico jogo arcade estilo **Pac-Man** com **Ash Ketchum** como protagonista, coletando **Pokébolas** e **Master Balls** em um labirinto retrô enquanto foge (e captura!) os 4 Fantasmas Pokémon: **Gengar**, **Gastly**, **Haunter** e **Koffing**!

Desenvolvido **100% em Python puro** com renderização vetorial e síntese procedural de áudio 8-bit (sem dependência de arquivos externos de som ou imagem que possam quebrar).

---

## 📸 Screenshots do Jogo

<div align="center">
  <img src="docs/screenshots/gameplay.png" width="48%" alt="Tela Inicial do PokePacman" />
  <img src="docs/screenshots/gameplay_action.png" width="48%" alt="Ação de Jogo e Captura de Fantasmas" />
</div>

---

## 🎮 Funcionalidades Principais

* **🧢 Ash Ketchum como Pac-Man:**
  - Sprite procedural detalhado com o boné clássico da Liga Pokémon (Expo 1996, vermelho e branco com o símbolo verde).
  - Cabelo preto espetado, olhos estilo anime, marcas de raio em "Z" nas bochechas e animação clássica de boca abrindo/fechando (*chomp-chomp*).
  - Animação cômica de desmaio com olhos em espiral ao ser pego por um fantasma.

* **👻 Os 4 Fantasmas Pokémon com IAs Únicas:**
  - **🔴 Gengar (Blinky):** Perseguição implacável direta à posição atual do Ash.
  - **🌸 Gastly (Pinky):** Mestre de emboscadas, cerca e antecipa 4 passos à frente de onde Ash está olhando.
  - **🔷 Haunter (Inky):** Ataque em pinça combinado com o Gengar, com mãos fantasmagóricas flutuantes animadas.
  - **🟠 Koffing (Clyde):** Padrão errático; persegue de longe (> 8 blocos) e foge para o canto inferior se Ash se aproximar.

* **🟣 Master Balls & Captura ("GOTCHA!"):**
  - Consumir uma **Master Ball** (Power Pellet nos 4 cantos) transforma os fantasmas em modo vulnerável (*Ditto azul tonto com olhos em espiral*).
  - Ash ganha a habilidade temporária de capturar os fantasmas com pontuação progressiva em combo (**200, 400, 800, 1600 pts**).

* **💎 Frutas e Itens de Evolução Bônus:**
  - **Nível 1:** Fruta Oran (+100 pts)
  - **Nível 2:** Pedra do Trovão / Thunder Stone (+300 pts)
  - **Nível 3:** Doce Raro / Rare Candy (+500 pts)

* **🔊 Efeitos Sonoros Retrô Gerados por Síntese (100% Python):**
  - Efeito sonoro *waka-waka* sintetizado em tempo real.
  - Fanfarras clássicas de abertura, vitória de fase e captura de Pokémon.

* **🏆 Recorde Persistente (High Score):**
  - Salva automaticamente o maior recorde atingido em arquivo local (`highscore.json`).

---

## ⌨️ Controles

| Tecla | Ação |
| :--- | :--- |
| **Setas do Teclado** ou **W, A, S, D** | Movimentar Ash Ketchum (com buffer de virada suave) |
| **P** | Pausar / Continuar jogo |
| **F** | Alternar modo Tela Cheia (*Fullscreen*) |
| **ESPAÇO** ou **ENTER** ou **R** | Reiniciar partida após Fim de Jogo |
| **ESC** | Sair do jogo |

---

## 🚀 Como Executar

### Pré-requisitos
* Python 3.10 ou superior.

### 🐧 No Linux:
```bash
# 1. Clonar ou entrar na pasta
cd pacman-ash-pokemon

# 2. Criar ambiente virtual e instalar dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Iniciar o jogo
./run_game.sh
# ou: python3 main.py
```

### 🪟 No Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

*(Opcional) Para gerar um executável `.exe` independente no Windows, basta rodar o script `build_exe.bat`.*

---

## 🧪 Executando os Testes Automatizados

O projeto conta com suíte completa de testes unitários para o labirinto, colisões, IA dos fantasmas e mecânicas de pontuação:

```bash
pytest tests/ -v
```

---

## 📁 Estrutura do Projeto

```text
pacman-ash-pokemon/
├── src/
│   ├── constants.py    # Dimensões de tela, cores, estados e pontuações
│   ├── maze.py         # Grade 28x31 do labirinto, túneis e colisões
│   ├── sprites.py      # Renderizadores vetoriais de Ash, Pokébolas e Fantasmas
│   ├── sound.py        # Sintetizador procedural de áudio 8-bit
│   ├── entity.py       # Entidades Ash (Player) e Ghosts com IA
│   └── game.py         # GameManager, HUD, loop principal e transições
├── tests/
│   └── test_game.py    # Testes unitários com pytest
├── docs/
│   └── screenshots/    # Imagens do jogo para o repositório
├── main.py             # Ponto de entrada
├── run_game.sh         # Inicializador rápido para Linux
├── build_exe.bat       # Script de empacotamento PyInstaller para Windows
├── requirements.txt    # Dependências mínimas (pygame-ce)
└── README.md           # Apresentação do projeto
```

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja `LICENSE` para mais detalhes.
Pokémon e personagens são marcas registradas da Nintendo / Game Freak / The Pokémon Company.
Pac-Man é marca registrada da Bandai Namco Entertainment. Este projeto é uma homenagem e demonstração educacional sem fins lucrativos.
