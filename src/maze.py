"""Gerenciamento e renderização do Labirinto (Maze) estilo Pac-Man."""

import pygame
from src.constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    COLOR_BG, COLOR_WALL_OUTER, COLOR_WALL_INNER,
    COLOR_WALL_HIGHLIGHT, COLOR_GATE,
)

MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#O####.#####.##.#####.####O#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #GGGGGG# ##.######",
    "      .   #GGGGGG#   .      ",
    "######.## #GGGGGG# ##.######",
    "     #.## ######## ##.#     ",
    "     #.##    B     ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#O..##.......P........##..O#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]


class Maze:
    """Representa a grade do labirinto, colisões e itens coletáveis."""

    def __init__(self):
        self.layout = [list(row) for row in MAZE_LAYOUT]
        self.dots = set()
        self.power_pellets = set()
        self.bonus_pos = (13, 17)
        self.ash_start = (13.5, 23.0)
        self.ghost_spawns = {
            "gengar": (13.5, 11.0),   # Fora da casa (pronto para caçar)
            "gastly": (13.5, 14.0),   # Centro da casa
            "haunter": (11.5, 14.0),  # Lado esquerdo da casa
            "koffing": (15.5, 14.0),  # Lado direito da casa
        }
        self.reset_collectibles()

    def reset_collectibles(self):
        """Restaura todas as Pokébolas e Master Balls para o início do jogo/nível."""
        self.dots.clear()
        self.power_pellets.clear()
        for r, row in enumerate(self.layout):
            for c, char in enumerate(row):
                if char == ".":
                    self.dots.add((c, r))
                elif char == "O":
                    self.power_pellets.add((c, r))

    def is_wall(self, col: int, row: int, allow_gate: bool = False) -> bool:
        """Verifica se a célula especificada é intransponível."""
        # Túnel lateral (wrap-around)
        if row == 14 and (col < 0 or col >= GRID_COLS):
            return False

        if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
            return True

        char = self.layout[row][col]
        if char == "#":
            return True
        if char == "-" and not allow_gate:
            return True
        return False

    def is_ghost_gate(self, col: int, row: int) -> bool:
        """Retorna se o ladrilho é o portão da casa dos fantasmas."""
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.layout[row][col] == "-"
        return False

    def eat(self, col: int, row: int) -> str | None:
        """Come o item na posição dada. Retorna 'dot', 'power' ou None."""
        pos = (col, row)
        if pos in self.dots:
            self.dots.remove(pos)
            return "dot"
        if pos in self.power_pellets:
            self.power_pellets.remove(pos)
            return "power"
        return None

    def remaining_dots(self) -> int:
        """Contagem de itens restantes no labirinto."""
        return len(self.dots) + len(self.power_pellets)

    def draw_walls(self, surface: pygame.Surface, top_offset: int):
        """Renderiza as paredes estilizadas com contorno contínuo neon estilo arcade."""
        neon_color = (40, 110, 240)
        glow_color = (80, 170, 255)
        wall_bg = (14, 24, 52)

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                char = self.layout[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE + top_offset

                if char == "#":
                    # Fundo sólido contínuo do bloco de parede
                    pygame.draw.rect(surface, wall_bg, (x, y, TILE_SIZE, TILE_SIZE))

                    # Verifica vizinhos para traçar bordas neon contínuas
                    top_is_wall = (r > 0 and self.layout[r - 1][c] == "#")
                    bottom_is_wall = (r < GRID_ROWS - 1 and self.layout[r + 1][c] == "#")
                    left_is_wall = (c > 0 and self.layout[r][c - 1] == "#")
                    right_is_wall = (c < GRID_COLS - 1 and self.layout[r][c + 1] == "#")

                    if not top_is_wall:
                        pygame.draw.line(surface, neon_color, (x, y), (x + TILE_SIZE, y), 2)
                        pygame.draw.line(surface, glow_color, (x, y + 1), (x + TILE_SIZE, y + 1), 1)
                    if not bottom_is_wall:
                        pygame.draw.line(surface, neon_color, (x, y + TILE_SIZE - 1), (x + TILE_SIZE, y + TILE_SIZE - 1), 2)
                    if not left_is_wall:
                        pygame.draw.line(surface, neon_color, (x, y), (x, y + TILE_SIZE), 2)
                        pygame.draw.line(surface, glow_color, (x + 1, y), (x + 1, y + TILE_SIZE), 1)
                    if not right_is_wall:
                        pygame.draw.line(surface, neon_color, (x + TILE_SIZE - 1, y), (x + TILE_SIZE - 1, y + TILE_SIZE), 2)

                elif char == "-":
                    # Portão da casa dos fantasmas (linha brilhante rosa/branca)
                    gate_rect = pygame.Rect(x, y + TILE_SIZE // 2 - 2, TILE_SIZE, 5)
                    pygame.draw.rect(surface, COLOR_GATE, gate_rect, border_radius=2)
