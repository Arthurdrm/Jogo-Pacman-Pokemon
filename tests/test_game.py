"""Testes unitários e de integração para o PokePacman (Ash Ketchum Edition)."""

import os
import sys
import pytest
import pygame

# Inicialização headless do pygame para os testes
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    STATE_READY, STATE_PLAYING, STATE_DYING, STATE_GAMEOVER, STATE_VICTORY,
    POINTS_POKEBALL, POINTS_MASTERBALL, POINTS_GHOST
)
from src.maze import Maze
from src.entity import Ash, Ghost, get_tile
from src.game import GameManager


class TestPokePacman:
    """Suíte de testes de jogabilidade, física e IA."""

    def test_maze_structure_and_collectibles(self):
        """Valida dimensões do labirinto, túneis e total de Pokébolas e Master Balls."""
        maze = Maze()
        assert len(maze.dots) > 200, "O labirinto deve conter mais de 200 Pokébolas normais."
        assert len(maze.power_pellets) == 4, "Devem existir exatamente 4 Master Balls nos 4 cantos."
        # Túnel lateral (linha 14)
        assert not maze.is_wall(-1, 14), "Túnel esquerdo deve permitir travessia."
        assert not maze.is_wall(GRID_COLS, 14), "Túnel direito deve permitir travessia."
        # Parede externa
        assert maze.is_wall(0, 0), "Canto (0,0) deve ser parede intransponível."

    def test_ash_movement_and_collision(self):
        """Verifica movimentação contínua do Ash e colisão correta com paredes."""
        maze = Maze()
        ash = Ash(*maze.ash_start)
        initial_x = ash.x

        ash.set_desired_direction(DIR_LEFT)
        for _ in range(10):
            ash.update(maze)

        assert ash.x < initial_x, "Ash deve mover-se para a esquerda quando desobstruído."

    def test_ash_tunnel_wrap_around(self):
        """Verifica se Ash se teletransporta corretamente ao atravessar o túnel lateral."""
        maze = Maze()
        ash = Ash(0.0, 14.0)
        ash.direction = DIR_LEFT
        ash.next_direction = DIR_LEFT
        ash.x = -TILE_SIZE // 2 - 2

        ash.update(maze)
        assert ash.x > (GRID_COLS - 2) * TILE_SIZE, "Ash deve reaparecer na borda direita ao sair pela esquerda."

    def test_eating_pokeball_and_masterball(self):
        """Testa o consumo de itens e incremento de pontuação."""
        screen = pygame.display.set_mode((200, 200))
        game = GameManager(screen)
        game.state = STATE_PLAYING

        # Força Ash sobre uma Pokébola conhecida
        c, r = list(game.maze.dots)[0]
        game.ash.x = c * TILE_SIZE + TILE_SIZE // 2
        game.ash.y = r * TILE_SIZE + TILE_SIZE // 2

        score_before = game.score
        game._update_playing()

        assert game.score == score_before + POINTS_POKEBALL, "Consumo de Pokébola deve somar 10 pontos."
        assert (c, r) not in game.maze.dots, "Pokébola consumida deve ser removida do mapa."

    def test_master_ball_frightens_ghosts(self):
        """Valida que a Master Ball coloca os 4 fantasmas no modo vulnerável (Frightened)."""
        screen = pygame.display.set_mode((200, 200))
        game = GameManager(screen)
        game.state = STATE_PLAYING

        # Consome Master Ball
        c, r = list(game.maze.power_pellets)[0]
        game.ash.x = c * TILE_SIZE + TILE_SIZE // 2
        game.ash.y = r * TILE_SIZE + TILE_SIZE // 2

        game._update_playing()

        assert game.score >= POINTS_MASTERBALL
        # Pelo menos os fantasmas fora da casa devem estar amedrontados
        frightened_count = sum(1 for g in game.ghosts if g.state == Ghost.STATE_FRIGHTENED)
        assert frightened_count >= 1, "Fantasmas ativos devem entrar em modo Frightened."

    def test_ghost_capture_and_scoring_combo(self):
        """Testa a captura de fantasmas pelo Ash e o combo de pontuação (200, 400...)."""
        screen = pygame.display.set_mode((200, 200))
        game = GameManager(screen)
        game.state = STATE_PLAYING

        target_ghost = game.ghosts[0]
        target_ghost.state = Ghost.STATE_FRIGHTENED
        target_ghost.frightened_timer = 300

        # Posiciona Ash exatamente sobre o fantasma
        game.ash.x = target_ghost.x
        game.ash.y = target_ghost.y

        game._update_playing()

        assert target_ghost.state == Ghost.STATE_EATEN, "Fantasma capturado deve virar apenas olhos (EATEN)."
        assert game.score >= POINTS_GHOST[0], "Captura do 1º fantasma deve somar 200 pontos."

    def test_death_and_game_over(self):
        """Valida perda de vidas e transição para GAMEOVER quando as vidas chegam a zero."""
        screen = pygame.display.set_mode((200, 200))
        game = GameManager(screen)
        game.state = STATE_PLAYING
        game.lives = 1

        # Fantasma ataca Ash
        enemy = game.ghosts[0]
        enemy.state = Ghost.STATE_CHASE
        game.ash.x = enemy.x
        game.ash.y = enemy.y

        game._update_playing()

        assert game.state == STATE_DYING, "Colisão com fantasma perseguidor deve iniciar estado DYING."
        # Simula término do timer de morte
        game.state_timer = 0
        game.update()
        assert game.state == STATE_GAMEOVER, "Com 0 vidas restantes, deve transicionar para GAMEOVER."
