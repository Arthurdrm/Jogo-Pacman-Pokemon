"""Entidades do jogo: Ash Ketchum (Player) e Fantasmas Pokémon com IA."""

import math
import random
import pygame
from src.constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    DIR_NONE, DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)
from src.maze import Maze


def get_tile(pixel_x: float, pixel_y: float) -> tuple[int, int]:
    """Converte coordenada em pixels para coluna e linha da grade."""
    return int(pixel_x // TILE_SIZE), int(pixel_y // TILE_SIZE)


class Ash:
    """Personagem principal controlado pelo jogador (Ash Ketchum estilo Pac-Man)."""

    def __init__(self, start_col: float, start_row: float):
        self.start_x = start_col * TILE_SIZE + TILE_SIZE // 2
        self.start_y = start_row * TILE_SIZE + TILE_SIZE // 2
        self.speed = 2.4
        self.radius = 13
        self.reset()

    def reset(self):
        """Restaura Ash para a posição inicial."""
        self.x = self.start_x
        self.y = self.start_y
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.mouth_angle = 35.0
        self.mouth_delta = 4.0
        self.is_moving = False
        self.dying_progress = 0.0

    def set_desired_direction(self, direction: tuple[int, int]):
        """Armazena o comando do teclado para virar na próxima interseção válida."""
        self.next_direction = direction
        # Permite reversão imediata de 180° sem esperar o centro da célula
        if (direction[0] == -self.direction[0] and direction[0] != 0) or \
           (direction[1] == -self.direction[1] and direction[1] != 0):
            self.direction = direction

    def update(self, maze: Maze):
        """Atualiza a física de movimento, colisões e animação da boca."""
        if self.dying_progress > 0.0:
            self.dying_progress = min(1.0, self.dying_progress + 0.02)
            return

        col, row = get_tile(self.x, self.y)
        cell_cx = col * TILE_SIZE + TILE_SIZE // 2
        cell_cy = row * TILE_SIZE + TILE_SIZE // 2

        # 1. Tentar mudar para a direção desejada se estiver alinhado ao centro
        if self.next_direction != self.direction:
            dist_to_center = math.hypot(self.x - cell_cx, self.y - cell_cy)
            if dist_to_center <= self.speed * 1.5:
                next_c = col + self.next_direction[0]
                next_r = row + self.next_direction[1]
                if not maze.is_wall(next_c, next_r):
                    # Alinha perfeitamente ao eixo e vira
                    if self.next_direction[0] != 0:
                        self.y = cell_cy
                    if self.next_direction[1] != 0:
                        self.x = cell_cx
                    self.direction = self.next_direction

        # 2. Verificar se pode continuar na direção atual
        target_c = col + self.direction[0]
        target_r = row + self.direction[1]

        # Tratamento especial do túnel horizontal
        is_tunnel = (row == 14) and (col <= 1 or col >= GRID_COLS - 2)

        can_move = True
        if not is_tunnel:
            # Se colidir com parede na frente
            if maze.is_wall(target_c, target_r):
                # Se passou do centro da célula na direção do movimento, trava no centro
                if (self.direction == DIR_RIGHT and self.x >= cell_cx) or \
                   (self.direction == DIR_LEFT and self.x <= cell_cx) or \
                   (self.direction == DIR_DOWN and self.y >= cell_cy) or \
                   (self.direction == DIR_UP and self.y <= cell_cy):
                    can_move = False
                    self.x = cell_cx if self.direction[0] != 0 else self.x
                    self.y = cell_cy if self.direction[1] != 0 else self.y

        self.is_moving = can_move
        if can_move:
            self.x += self.direction[0] * self.speed
            self.y += self.direction[1] * self.speed

            # Túnel wrap-around
            if row == 14:
                if self.x < -TILE_SIZE // 2:
                    self.x = (GRID_COLS - 0.5) * TILE_SIZE
                elif self.x > (GRID_COLS - 0.5) * TILE_SIZE:
                    self.x = -TILE_SIZE // 2

            # Animação da boca abrindo e fechando
            self.mouth_angle += self.mouth_delta
            if self.mouth_angle >= 50.0 or self.mouth_angle <= 0.0:
                self.mouth_delta = -self.mouth_delta
        else:
            self.mouth_angle = 20.0


class Ghost:
    """Fantasma Pokémon com IA única, modos de perseguição, dispersão e pânico."""

    STATE_IN_HOUSE = "IN_HOUSE"
    STATE_LEAVING = "LEAVING"
    STATE_CHASE = "CHASE"
    STATE_SCATTER = "SCATTER"
    STATE_FRIGHTENED = "FRIGHTENED"
    STATE_EATEN = "EATEN"

    def __init__(self, name: str, home_col: float, home_row: float, exit_delay: float):
        self.name = name
        self.home_x = home_col * TILE_SIZE + TILE_SIZE // 2
        self.home_y = home_row * TILE_SIZE + TILE_SIZE // 2
        self.exit_delay = exit_delay
        self.base_speed = 2.1
        self.radius = 13

        # Cantos de dispersão (Scatter Targets)
        self.scatter_targets = {
            "gengar": (GRID_COLS - 2, 0),    # Topo direito
            "gastly": (1, 0),                 # Topo esquerdo
            "haunter": (GRID_COLS - 1, GRID_ROWS - 1), # Fundo direito
            "koffing": (0, GRID_ROWS - 1),    # Fundo esquerdo
        }
        self.reset()

    def reset(self):
        """Restaura fantasma para a posição de início."""
        self.x = self.home_x
        self.y = self.home_y
        self.direction = DIR_UP
        self.state = self.STATE_IN_HOUSE if self.exit_delay > 0 else self.STATE_CHASE
        self.timer = 0
        self.frightened_timer = 0
        self.house_bounce_dir = -1

    def make_frightened(self, duration_frames: int):
        """Ativa o modo assustado (quando Ash consome a Master Ball)."""
        if self.state not in (self.STATE_IN_HOUSE, self.STATE_LEAVING, self.STATE_EATEN):
            self.state = self.STATE_FRIGHTENED
            self.frightened_timer = duration_frames
            # Inverte a direção imediatamente
            self.direction = (-self.direction[0], -self.direction[1])

    def update(self, maze: Maze, ash: Ash, blinky_ghost=None):
        """Atualiza a IA e posição do fantasma."""
        self.timer += 1

        # 1. Dentro da casa dos fantasmas (quica para cima e para baixo)
        if self.state == self.STATE_IN_HOUSE:
            self.y += self.house_bounce_dir * 0.8
            if abs(self.y - self.home_y) > 6:
                self.house_bounce_dir = -self.house_bounce_dir
            if self.timer >= self.exit_delay:
                self.state = self.STATE_LEAVING
            return

        # 2. Saindo da casa (navega até o centro da porta e sobe)
        if self.state == self.STATE_LEAVING:
            door_x = 13.5 * TILE_SIZE + TILE_SIZE // 2
            door_y = 11.0 * TILE_SIZE + TILE_SIZE // 2
            # Move horizontalmente para a porta
            if abs(self.x - door_x) > 1.0:
                self.x += 1.2 if self.x < door_x else -1.2
            else:
                self.x = door_x
                # Move verticalmente para fora do portão
                if self.y > door_y:
                    self.y -= 1.2
                    self.direction = DIR_UP
                else:
                    self.y = door_y
                    self.state = self.STATE_CHASE
                    self.direction = DIR_LEFT
            return

        # 3. Retornando derrotado (apenas olhos em alta velocidade)
        if self.state == self.STATE_EATEN:
            target_x = 13.5 * TILE_SIZE + TILE_SIZE // 2
            target_y = 11.0 * TILE_SIZE + TILE_SIZE // 2
            if math.hypot(self.x - target_x, self.y - target_y) < 4.0:
                self.state = self.STATE_LEAVING
                return
            speed = self.base_speed * 1.8
            self._move_towards_target(maze, target_x // TILE_SIZE, target_y // TILE_SIZE, speed, allow_gate=True)
            return

        # 4. Modo Assustado
        if self.state == self.STATE_FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.state = self.STATE_CHASE
            speed = self.base_speed * 0.65
            self._move_random_at_intersection(maze, speed)
            return

        # 5. Modos de Ataque e Dispersão (CHASE / SCATTER)
        # Ciclo padrão arcade: 20s perseguição / 7s dispersão
        cycle_time = self.timer % (27 * 60)
        is_scatter = cycle_time < (7 * 60)

        target_col, target_row = self._calculate_target(ash, blinky_ghost, is_scatter)
        self._move_towards_target(maze, target_col, target_row, self.base_speed)

    def _calculate_target(self, ash: Ash, blinky_ghost, is_scatter: bool) -> tuple[int, int]:
        """Calcula a célula de destino conforme a personalidade de cada Pokémon."""
        if is_scatter:
            return self.scatter_targets[self.name]

        ash_col, ash_row = get_tile(ash.x, ash.y)

        if self.name == "gengar":
            # GENGAR (Blinky): Perseguição direta à posição do Ash
            return (ash_col, ash_row)

        elif self.name == "gastly":
            # GASTLY (Pinky): Emboscada — mira 4 ladrilhos à frente de onde Ash está olhando
            dx, dy = ash.direction
            return (ash_col + dx * 4, ash_row + dy * 4)

        elif self.name == "haunter":
            # HAUNTER (Inky): Ataque em pinça combinado com o Gengar
            dx, dy = ash.direction
            pivot_col = ash_col + dx * 2
            pivot_row = ash_row + dy * 2
            if blinky_ghost:
                b_col, b_row = get_tile(blinky_ghost.x, blinky_ghost.y)
                # Vetor de Blinky até o ponto à frente do Ash, dobrado
                return (pivot_col + (pivot_col - b_col), pivot_row + (pivot_row - b_row))
            return (pivot_col, pivot_row)

        else:
            # KOFFING (Clyde): Se estiver longe de Ash (> 8 blocos), ataca; se perto, foge para o canto
            dist = math.hypot(ash_col - self.x // TILE_SIZE, ash_row - self.y // TILE_SIZE)
            if dist > 8.0:
                return (ash_col, ash_row)
            return self.scatter_targets["koffing"]

    def _move_towards_target(self, maze: Maze, target_c: int, target_r: int, speed: float, allow_gate: bool = False):
        """Move o fantasma escolhendo a melhor rota em interseções baseada na menor distância até o alvo."""
        col, row = get_tile(self.x, self.y)
        cell_cx = col * TILE_SIZE + TILE_SIZE // 2
        cell_cy = row * TILE_SIZE + TILE_SIZE // 2

        # Wrap horizontal do túnel
        if row == 14:
            if self.x < -TILE_SIZE // 2:
                self.x = (GRID_COLS - 0.5) * TILE_SIZE
            elif self.x > (GRID_COLS - 0.5) * TILE_SIZE:
                self.x = -TILE_SIZE // 2

        # Ao se aproximar do centro do ladrilho, avalia novas direções
        dist_to_center = math.hypot(self.x - cell_cx, self.y - cell_cy)
        if dist_to_center <= speed:
            self.x = cell_cx
            self.y = cell_cy

            possible_dirs = [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]
            # Não pode dar ré de 180 graus
            opposite_dir = (-self.direction[0], -self.direction[1])
            valid_dirs = []

            for d in possible_dirs:
                if d == opposite_dir:
                    continue
                nc = col + d[0]
                nr = row + d[1]
                if not maze.is_wall(nc, nr, allow_gate=allow_gate):
                    valid_dirs.append(d)

            if valid_dirs:
                # Escolhe a direção com menor distância euclidiana até a célula alvo
                best_dir = min(valid_dirs, key=lambda d: math.hypot((col + d[0]) - target_c, (row + d[1]) - target_r))
                self.direction = best_dir

        self.x += self.direction[0] * speed
        self.y += self.direction[1] * speed

    def _move_random_at_intersection(self, maze: Maze, speed: float):
        """Movimentação aleatória quando no modo Assustado (vulnerável)."""
        col, row = get_tile(self.x, self.y)
        cell_cx = col * TILE_SIZE + TILE_SIZE // 2
        cell_cy = row * TILE_SIZE + TILE_SIZE // 2

        dist_to_center = math.hypot(self.x - cell_cx, self.y - cell_cy)
        if dist_to_center <= speed:
            self.x = cell_cx
            self.y = cell_cy
            possible_dirs = [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]
            opposite_dir = (-self.direction[0], -self.direction[1])
            valid_dirs = [d for d in possible_dirs if d != opposite_dir and not maze.is_wall(col + d[0], row + d[1])]
            if valid_dirs:
                self.direction = random.choice(valid_dirs)

        self.x += self.direction[0] * speed
        self.y += self.direction[1] * speed
