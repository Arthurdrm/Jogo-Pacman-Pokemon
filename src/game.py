"""Controlador central da lógica, pontuação, HUD e estados do PokePacman."""

import os
import json
import math
import pygame
from src.constants import (
    TILE_SIZE, GRID_COLS, GRID_ROWS,
    WINDOW_WIDTH, WINDOW_HEIGHT, HUD_TOP_HEIGHT, HUD_BOTTOM_HEIGHT,
    COLOR_BG, COLOR_WHITE, COLOR_YELLOW, COLOR_RED, COLOR_CYAN,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT,
    STATE_READY, STATE_PLAYING, STATE_DYING, STATE_GAMEOVER, STATE_VICTORY, STATE_PAUSED,
    POINTS_POKEBALL, POINTS_MASTERBALL, POINTS_GHOST, POINTS_BONUS
)
from src.maze import Maze, MAZE_LAYOUT
from src.entity import Ash, Ghost, get_tile
from src.sprites import draw_ash, draw_pokeball, draw_masterball, draw_ghost, draw_bonus_item
from src.sound import SoundManager


class FloatingText:
    """Texto flutuante temporário para pontuações de captura ('GOTCHA!', '+200')."""

    def __init__(self, text: str, x: float, y: float, color=COLOR_YELLOW, duration=60):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = duration

    def update(self):
        self.y -= 0.6
        self.lifetime -= 1

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        if self.lifetime > 0:
            surf = font.render(self.text, True, self.color)
            surface.blit(surf, (int(self.x - surf.get_width() // 2), int(self.y)))


class GameManager:
    """Gerenciador mestre do jogo."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sound = SoundManager()
        self.maze = Maze()
        self.ash = Ash(*self.maze.ash_start)

        # 4 Fantasmas com tempos de saída da casa escalonados
        self.ghosts = [
            Ghost("gengar", *self.maze.ghost_spawns["gengar"], exit_delay=0),
            Ghost("gastly", *self.maze.ghost_spawns["gastly"], exit_delay=120),
            Ghost("haunter", *self.maze.ghost_spawns["haunter"], exit_delay=280),
            Ghost("koffing", *self.maze.ghost_spawns["koffing"], exit_delay=460),
        ]

        self.score = 0
        self.high_score = self._load_high_score()
        self.lives = 3
        self.level = 1
        self.extra_life_awarded = False

        self.state = STATE_READY
        self.state_timer = 0
        self.ghost_combo = 0
        self.floating_texts: list[FloatingText] = []

        # Fruta / Bônus
        self.bonus_active = False
        self.bonus_timer = 0
        self.dots_eaten_this_level = 0

        # Fontes de texto
        pygame.font.init()
        self.font_hud = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_banner = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_score = pygame.font.SysFont("Arial", 13, bold=True)

        self._start_level()

    def _load_high_score(self) -> int:
        path = os.path.join(os.path.dirname(__file__), "..", "highscore.json")
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
        except Exception:
            pass
        return 0

    def _save_high_score(self):
        path = os.path.join(os.path.dirname(__file__), "..", "highscore.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def _start_level(self):
        """Prepara o nível atual ou reinicia."""
        self.maze.reset_collectibles()
        self.dots_eaten_this_level = 0
        self.bonus_active = False
        self._reset_positions()
        self.state = STATE_READY
        self.state_timer = 150  # 2.5 segundos
        self.sound.play_intro()

    def _reset_positions(self):
        """Reposiciona Ash e os Fantasmas mantendo itens consumidos."""
        self.ash.reset()
        for g in self.ghosts:
            g.reset()
        # Ajusta velocidade levemente com o nível
        speed_boost = min(0.6, (self.level - 1) * 0.12)
        self.ash.speed = 2.4 + speed_boost
        for g in self.ghosts:
            g.base_speed = 2.1 + speed_boost

    def handle_input(self, event: pygame.event.Event):
        """Processa eventos de teclado."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.ash.set_desired_direction(DIR_UP)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.ash.set_desired_direction(DIR_DOWN)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.ash.set_desired_direction(DIR_LEFT)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.ash.set_desired_direction(DIR_RIGHT)
            elif event.key == pygame.K_p:
                if self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
            elif event.key in (pygame.K_SPACE, pygame.K_r, pygame.K_RETURN):
                if self.state == STATE_GAMEOVER:
                    # Reinicia jogo do zero
                    self.score = 0
                    self.lives = 3
                    self.level = 1
                    self.extra_life_awarded = False
                    self._start_level()

    def update(self):
        """Loop principal de lógica por frame."""
        # Atualiza textos flutuantes
        for ft in self.floating_texts[:]:
            ft.update()
            if ft.lifetime <= 0:
                self.floating_texts.remove(ft)

        # 1. ESTADO PREPARAR (READY!)
        if self.state == STATE_READY:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = STATE_PLAYING
            return

        # 2. ESTADO PAUSADO
        if self.state == STATE_PAUSED:
            return

        # 3. ESTADO DERROTA / ANIMAÇÃO DE DESMAIO
        if self.state == STATE_DYING:
            self.ash.update(self.maze)
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self._reset_positions()
                    self.state = STATE_READY
                    self.state_timer = 90
                else:
                    self.state = STATE_GAMEOVER
            return

        # 4. ESTADO VITÓRIA (FASE CONCLUÍDA)
        if self.state == STATE_VICTORY:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.level += 1
                self._start_level()
            return

        # 5. ESTADO JOGO ATIVO (PLAYING)
        if self.state == STATE_PLAYING:
            self._update_playing()

    def _update_playing(self):
        # 1. Atualizar Ash
        self.ash.update(self.maze)

        # 2. Comer itens no ladrilho atual
        ash_c, ash_r = get_tile(self.ash.x, self.ash.y)
        item = self.maze.eat(ash_c, ash_r)
        if item == "dot":
            self.score += POINTS_POKEBALL
            self.dots_eaten_this_level += 1
            self.sound.play_chomp()
        elif item == "power":
            self.score += POINTS_MASTERBALL
            self.sound.play_power()
            self.ghost_combo = 0
            # Duração do poder diminui ligeiramente em níveis mais altos
            fright_duration = max(240, 520 - (self.level * 40))
            for g in self.ghosts:
                g.make_frightened(fright_duration)

        # Checar bônus especial (aparece após 70 e 170 bolinhas)
        if self.dots_eaten_this_level in (70, 170) and not self.bonus_active:
            self.bonus_active = True
            self.bonus_timer = 600  # 10 segundos

        if self.bonus_active:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus_active = False
            # Checar colisão com bônus
            if (ash_c, ash_r) == self.maze.bonus_pos:
                bonus_name, bonus_pts = POINTS_BONUS.get(min(self.level, 4), ("MASTER CANDY", 500))
                self.score += bonus_pts
                self.sound.play_eat_bonus()
                self.floating_texts.append(FloatingText(f"+{bonus_pts}", self.ash.x, self.ash.y + HUD_TOP_HEIGHT))
                self.bonus_active = False

        # Vida extra ao alcançar 10.000 pontos
        if self.score >= 10000 and not self.extra_life_awarded:
            self.lives += 1
            self.extra_life_awarded = True
            self.sound.play_eat_bonus()
            self.floating_texts.append(FloatingText("1UP EXTRA!", self.ash.x, self.ash.y + HUD_TOP_HEIGHT, COLOR_CYAN))

        # Atualizar Recorde
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

        # Checar vitória (limpou todas as bolinhas e master balls)
        if self.maze.remaining_dots() == 0:
            self.state = STATE_VICTORY
            self.state_timer = 120
            self.sound.play_victory()
            return

        # 3. Atualizar Fantasmas e Checar Colisões
        blinky = self.ghosts[0]
        for g in self.ghosts:
            g.update(self.maze, self.ash, blinky_ghost=blinky)

            # Colisão Ash <-> Fantasma
            dist = math.hypot(self.ash.x - g.x, self.ash.y - g.y)
            if dist < (self.ash.radius + g.radius - 4):
                if g.state == Ghost.STATE_FRIGHTENED:
                    # Ash captura o Pokémon fantasma!
                    g.state = Ghost.STATE_EATEN
                    pts = POINTS_GHOST[min(self.ghost_combo, 3)]
                    self.ghost_combo += 1
                    self.score += pts
                    self.sound.play_eat_ghost()
                    self.floating_texts.append(FloatingText(f"GOTCHA! +{pts}", g.x, g.y + HUD_TOP_HEIGHT, COLOR_CYAN))
                elif g.state in (Ghost.STATE_CHASE, Ghost.STATE_SCATTER):
                    # Fantasma pega o Ash!
                    self.state = STATE_DYING
                    self.state_timer = 80
                    self.sound.play_death()
                    break

    def draw(self):
        """Renderiza todo o jogo na tela."""
        self.screen.fill(COLOR_BG)

        # 1. RENDERIZAR HUD SUPERIOR (SCORE / RECORD / LEVEL)
        score_txt = self.font_hud.render(f"1UP  {self.score:06d}", True, COLOR_WHITE)
        self.screen.blit(score_txt, (20, 14))

        hi_txt = self.font_hud.render(f"RECORD  {self.high_score:06d}", True, COLOR_YELLOW)
        self.screen.blit(hi_txt, (WINDOW_WIDTH // 2 - hi_txt.get_width() // 2, 14))

        lvl_txt = self.font_hud.render(f"NÍVEL {self.level}", True, COLOR_CYAN)
        self.screen.blit(lvl_txt, (WINDOW_WIDTH - lvl_txt.get_width() - 20, 14))

        # 2. RENDERIZAR LABIRINTO E PAREDES
        self.maze.draw_walls(self.screen, HUD_TOP_HEIGHT)

        # 3. RENDERIZAR POKÉBOLAS (DOTS)
        for c, r in self.maze.dots:
            px = c * TILE_SIZE + TILE_SIZE // 2
            py = r * TILE_SIZE + TILE_SIZE // 2 + HUD_TOP_HEIGHT
            draw_pokeball(self.screen, px, py, radius=4)

        # 4. RENDERIZAR MASTER BALLS (POWER PELLETS)
        for c, r in self.maze.power_pellets:
            px = c * TILE_SIZE + TILE_SIZE // 2
            py = r * TILE_SIZE + TILE_SIZE // 2 + HUD_TOP_HEIGHT
            draw_masterball(self.screen, px, py, pygame.time.get_ticks() // 16)

        # 5. RENDERIZAR ITEM BÔNUS (SE ATIVO)
        if self.bonus_active:
            bx = self.maze.bonus_pos[0] * TILE_SIZE + TILE_SIZE // 2
            by = self.maze.bonus_pos[1] * TILE_SIZE + TILE_SIZE // 2 + HUD_TOP_HEIGHT
            draw_bonus_item(self.screen, bx, by, self.level)

        # 6. RENDERIZAR FANTASMAS POKÉMON
        ticks = pygame.time.get_ticks()
        for g in self.ghosts:
            gy = g.y + HUD_TOP_HEIGHT
            is_fright = g.state == Ghost.STATE_FRIGHTENED
            is_flashing = is_fright and (g.frightened_timer < 120)
            is_eaten = g.state == Ghost.STATE_EATEN
            draw_ghost(self.screen, g.x, gy, g.name, g.direction,
                       is_fright, is_flashing, is_eaten, ticks // 16)

        # 7. RENDERIZAR ASH KETCHUM (PAC-MAN)
        ash_draw_y = self.ash.y + HUD_TOP_HEIGHT
        draw_ash(self.screen, self.ash.x, ash_draw_y, self.ash.direction,
                 self.ash.mouth_angle, self.ash.dying_progress)

        # 8. TEXTOS FLUTUANTES (PONTOS / GOTCHA)
        for ft in self.floating_texts:
            ft.draw(self.screen, self.font_score)

        # 9. RENDERIZAR HUD INFERIOR (VIDAS E ITENS COLETADOS)
        hud_bottom_y = HUD_TOP_HEIGHT + (GRID_ROWS * TILE_SIZE) + 14
        # Desenha bonés do Ash para vidas restantes
        for i in range(self.lives - 1):
            lx = 30 + i * 32
            draw_ash(self.screen, lx, hud_bottom_y + 10, DIR_RIGHT, mouth_angle=0.0, radius=11)

        # Desenha ícone do item bônus da fase à direita
        draw_bonus_item(self.screen, WINDOW_WIDTH - 40, hud_bottom_y + 10, self.level)

        # 10. BANNERS DE ESTADO (READY, GAMEOVER, PAUSE, VICTORY)
        center_x = WINDOW_WIDTH // 2
        center_y = HUD_TOP_HEIGHT + (17 * TILE_SIZE) + TILE_SIZE // 2

        if self.state == STATE_READY:
            ready_surf = self.font_banner.render("PREPARE-SE!", True, COLOR_YELLOW)
            self.screen.blit(ready_surf, (center_x - ready_surf.get_width() // 2, center_y))

        elif self.state == STATE_PAUSED:
            pause_surf = self.font_banner.render("PAUSADO [P]", True, COLOR_CYAN)
            self.screen.blit(pause_surf, (center_x - pause_surf.get_width() // 2, center_y))

        elif self.state == STATE_VICTORY:
            vic_surf = self.font_banner.render("FASE CONCLUÍDA!", True, COLOR_CYAN)
            self.screen.blit(vic_surf, (center_x - vic_surf.get_width() // 2, center_y))

        elif self.state == STATE_GAMEOVER:
            gov_surf = self.font_banner.render("FIM DE JOGO!", True, COLOR_RED)
            self.screen.blit(gov_surf, (center_x - gov_surf.get_width() // 2, center_y - 20))
            sub_surf = self.font_hud.render("Pressione ESPAÇO ou ENTER para Reiniciar", True, COLOR_WHITE)
            self.screen.blit(sub_surf, (center_x - sub_surf.get_width() // 2, center_y + 20))
