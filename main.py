#!/usr/bin/env python3
"""PokePacman — Ash Ketchum Pac-Man Edition.

Um jogo arcade clássico do Pac-Man com Ash Ketchum como herói,
Pokébolas e Master Balls para coletar, e os 4 Fantasmas Pokémon (Gengar, Gastly, Haunter, Koffing)!
"""

import sys
import os
import pygame

# Garante inclusão do diretório raiz no sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from src.game import GameManager
from src.sprites import draw_ash, DIR_RIGHT


def create_game_icon() -> pygame.Surface:
    """Cria o ícone da janela com o rosto/boné do Ash."""
    icon_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    draw_ash(icon_surf, 16, 16, DIR_RIGHT, mouth_angle=30.0, radius=13)
    return icon_surf


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("PokePacman — Ash Ketchum Edition")

    try:
        icon = create_game_icon()
        pygame.display.set_icon(icon)
    except Exception:
        pass

    clock = pygame.time.Clock()
    game = GameManager(screen)

    fullscreen = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    game.screen = screen
                else:
                    game.handle_input(event)

        game.update()
        game.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
