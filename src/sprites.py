"""Renderizadores vetoriais e procedurais dos personagens: Ash Ketchum, Pokébolas e Fantasmas Pokémon."""

import math
import pygame
from src.constants import (
    COLOR_WHITE, COLOR_BLACK, COLOR_RED, COLOR_SKIN, COLOR_HAIR,
    COLOR_YELLOW, COLOR_CYAN, COLOR_ORANGE, COLOR_PURPLE,
    DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT
)


def draw_ash(surface: pygame.Surface, x: float, y: float, direction: tuple[int, int],
             mouth_angle: float, dying_progress: float = 0.0, radius: int = 14):
    """Desenha a cabeça/rosto icônico do Ash Ketchum com boné clássico Pokémon e boca animada."""
    center_x = int(x)
    center_y = int(y)

    if dying_progress > 0.0:
        # Animação de desmaio / rotação ao ser derrotado
        shrink = max(0.1, 1.0 - dying_progress)
        cur_radius = int(radius * shrink)
        if cur_radius <= 2:
            return
        # Rosto pálido com olhos em espiral (X_X)
        pygame.draw.circle(surface, (230, 210, 200), (center_x, center_y), cur_radius)
        # Olhos em X
        dx = int(cur_radius * 0.4)
        pygame.draw.line(surface, COLOR_BLACK, (center_x - dx - 3, center_y - 2), (center_x - dx + 3, center_y + 4), 2)
        pygame.draw.line(surface, COLOR_BLACK, (center_x - dx - 3, center_y + 4), (center_x - dx + 3, center_y - 2), 2)
        pygame.draw.line(surface, COLOR_BLACK, (center_x + dx - 3, center_y - 2), (center_x + dx + 3, center_y + 4), 2)
        pygame.draw.line(surface, COLOR_BLACK, (center_x + dx - 3, center_y + 4), (center_x + dx + 3, center_y - 2), 2)
        return

    # Determinar ângulo base da direção
    if direction == DIR_RIGHT:
        base_angle = 0
    elif direction == DIR_UP:
        base_angle = 90
    elif direction == DIR_LEFT:
        base_angle = 180
    elif direction == DIR_DOWN:
        base_angle = 270
    else:
        base_angle = 0

    # 1. Rosto com tom de pele e corte da boca estilo Pac-Man
    half_mouth = mouth_angle / 2.0
    start_rad = math.radians(base_angle + half_mouth)
    end_rad = math.radians(base_angle + 360 - half_mouth)

    points = [(center_x, center_y)]
    steps = 28
    for i in range(steps + 1):
        ang = start_rad + (end_rad - start_rad) * (i / steps)
        px = center_x + radius * math.cos(ang)
        py = center_y - radius * math.sin(ang)
        points.append((px, py))

    if len(points) >= 3:
        pygame.draw.polygon(surface, COLOR_SKIN, points)
        pygame.draw.polygon(surface, (180, 130, 105), points, 1)

    # 2. Cabelo preto espetado do Ash (protrusões nas costas e costeletas)
    # Lado oposto à direção
    back_rad = math.radians(base_angle + 180)
    bx = center_x + int(radius * 0.65 * math.cos(back_rad))
    by = center_y - int(radius * 0.65 * math.sin(back_rad))

    hair_pts = [
        (bx, by),
        (bx + int(8 * math.cos(back_rad + 0.5)), by - int(8 * math.sin(back_rad + 0.5))),
        (bx + int(11 * math.cos(back_rad)), by - int(11 * math.sin(back_rad))),
        (bx + int(8 * math.cos(back_rad - 0.5)), by - int(8 * math.sin(back_rad - 0.5))),
    ]
    pygame.draw.polygon(surface, COLOR_HAIR, hair_pts)

    # 3. Boné Oficial da Liga Pokémon (Vermelho e Branco)
    # Metade superior / coroa
    cap_center_y = center_y - int(radius * 0.25)
    cap_rect = pygame.Rect(center_x - radius, center_y - radius, radius * 2, radius + 2)
    # Arco do boné vermelho
    pygame.draw.circle(surface, COLOR_RED, (center_x, cap_center_y), radius)
    # Painel frontal branco
    panel_rect = pygame.Rect(center_x - int(radius * 0.6), center_y - radius, int(radius * 1.2), int(radius * 0.85))
    pygame.draw.ellipse(surface, (245, 245, 248), panel_rect)

    # Logo verde da Liga Pokémon no boné (símbolo de C estilizado)
    logo_x = center_x + (2 if direction == DIR_RIGHT else (-2 if direction == DIR_LEFT else 0))
    logo_y = center_y - int(radius * 0.65)
    pygame.draw.circle(surface, (30, 180, 75), (logo_x, logo_y), 3)
    pygame.draw.circle(surface, (245, 245, 248), (logo_x, logo_y), 1)

    # Aba vermelha do boné projetada na direção do olhar
    aba_x = center_x + int(radius * 0.75 * math.cos(math.radians(base_angle)))
    aba_y = center_y - int(radius * 0.75 * math.sin(math.radians(base_angle))) - int(radius * 0.2)
    pygame.draw.line(surface, COLOR_RED, (center_x, center_y - int(radius * 0.4)), (aba_x, aba_y), 4)

    # Botão branco no topo do boné
    pygame.draw.circle(surface, COLOR_WHITE, (center_x, center_y - radius), 2)

    # 4. Olho do Ash (grande e expressivo)
    eye_offset_x = 3 if direction == DIR_RIGHT else (-5 if direction == DIR_LEFT else 0)
    eye_offset_y = 1 if direction == DIR_DOWN else (-3 if direction == DIR_UP else 0)
    eye_x = center_x + eye_offset_x
    eye_y = center_y + eye_offset_y
    # Esclera branca e pupila preta
    pygame.draw.ellipse(surface, COLOR_WHITE, (eye_x - 3, eye_y - 4, 6, 8))
    pygame.draw.circle(surface, (20, 20, 25), (eye_x, eye_y), 2)
    # Brilho de reflexo do anime
    pygame.draw.circle(surface, COLOR_WHITE, (eye_x + 1, eye_y - 1), 1)

    # 5. Marcas características em "Z" / Raio nas bochechas do Ash
    cheek_y = center_y + int(radius * 0.35)
    cheek_x = center_x + (5 if direction == DIR_RIGHT else (-5 if direction == DIR_LEFT else 4))
    # Desenha o ziguezague sutil
    pygame.draw.line(surface, (190, 110, 80), (cheek_x - 2, cheek_y - 1), (cheek_x + 2, cheek_y), 1)
    pygame.draw.line(surface, (190, 110, 80), (cheek_x + 2, cheek_y), (cheek_x - 2, cheek_y + 2), 1)
    pygame.draw.line(surface, (190, 110, 80), (cheek_x - 2, cheek_y + 2), (cheek_x + 2, cheek_y + 3), 1)


def draw_pokeball(surface: pygame.Surface, x: float, y: float, radius: int = 4):
    """Renderiza a Pokébola clássica como item coletável no labirinto."""
    cx, cy = int(x), int(y)
    # Metade superior vermelha
    pygame.draw.circle(surface, (230, 35, 35), (cx, cy), radius)
    # Metade inferior branca
    pygame.draw.arc(surface, COLOR_WHITE, (cx - radius, cy - radius, radius * 2, radius * 2), math.pi, 2 * math.pi, radius)
    pygame.draw.rect(surface, (245, 245, 250), (cx - radius, cy, radius * 2, radius))
    # Contorno e faixa central preta
    pygame.draw.circle(surface, COLOR_BLACK, (cx, cy), radius, 1)
    pygame.draw.line(surface, COLOR_BLACK, (cx - radius, cy), (cx + radius, cy), 1)
    # Botão central com brilho
    pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), max(1, radius // 3))
    pygame.draw.circle(surface, COLOR_BLACK, (cx, cy), max(1, radius // 3), 1)


def draw_masterball(surface: pygame.Surface, x: float, y: float, pulse_frame: int):
    """Renderiza a Master Ball (Power Pellet) que permite capturar os fantasmas."""
    cx, cy = int(x), int(y)
    # Efeito pulsante de tamanho
    pulse = 1.0 + 0.2 * math.sin(pulse_frame * 0.12)
    radius = int(8 * pulse)

    # Brilho aura lilás em volta
    aura_color = (200, 120, 255)
    pygame.draw.circle(surface, aura_color, (cx, cy), radius + 2, 1)

    # Metade superior roxa da Master Ball
    pygame.draw.circle(surface, (140, 40, 190), (cx, cy), radius)

    # Metade inferior branca
    pygame.draw.rect(surface, (245, 245, 250), (cx - radius, cy, radius * 2, radius))
    pygame.draw.circle(surface, COLOR_BLACK, (cx, cy), radius, 1)
    pygame.draw.line(surface, COLOR_BLACK, (cx - radius, cy), (cx + radius, cy), 2)

    # Dois nódulos redondos cor-de-rosa característicos da Master Ball
    pygame.draw.circle(surface, (245, 60, 160), (cx - int(radius * 0.5), cy - int(radius * 0.4)), max(1, radius // 4))
    pygame.draw.circle(surface, (245, 60, 160), (cx + int(radius * 0.5), cy - int(radius * 0.4)), max(1, radius // 4))

    # Letra 'M' branca estilizada no centro do topo
    font_size = max(8, int(radius * 0.9))
    try:
        font = pygame.font.SysFont("Arial", font_size, bold=True)
        m_surf = font.render("M", True, COLOR_WHITE)
        surface.blit(m_surf, (cx - m_surf.get_width() // 2, cy - radius + 1))
    except Exception:
        # Fallback se fonte falhar
        pygame.draw.circle(surface, COLOR_WHITE, (cx, cy - int(radius * 0.4)), 2)

    # Botão central com borda preta
    btn_r = max(2, radius // 4)
    pygame.draw.circle(surface, COLOR_WHITE, (cx, cy), btn_r)
    pygame.draw.circle(surface, COLOR_BLACK, (cx, cy), btn_r, 1)


def draw_ghost(surface: pygame.Surface, x: float, y: float, ghost_name: str,
               direction: tuple[int, int], is_frightened: bool, is_flashing: bool,
               is_eaten: bool, timer: int, radius: int = 14):
    """Renderiza os 4 Fantasmas Pokémon temáticos (Gengar, Gastly, Haunter, Koffing)."""
    cx, cy = int(x), int(y)

    # 1. MODO OLHOS DERROTADOS (Retornando à casa)
    if is_eaten:
        # Desenha apenas os olhos flutuantes brancos e pupilas na direção
        eye_dx = direction[0] * 3
        eye_dy = direction[1] * 3
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 5, cy), 4)
        pygame.draw.circle(surface, COLOR_WHITE, (cx + 5, cy), 4)
        pygame.draw.circle(surface, (30, 80, 220), (cx - 5 + eye_dx, cy + eye_dy), 2)
        pygame.draw.circle(surface, (30, 80, 220), (cx + 5 + eye_dx, cy + eye_dy), 2)
        return

    # 2. MODO ASSUSTADO (Ditto / Fantasma Azul Vulnerável)
    if is_frightened:
        # Alterna entre azul e branco quando estiver piscando (quase acabando)
        body_color = COLOR_WHITE if (is_flashing and (timer // 8) % 2 == 0) else (40, 130, 240)
        face_color = COLOR_RED if body_color == COLOR_WHITE else (255, 230, 180)

        # Corpo gelatinoso oval
        pygame.draw.circle(surface, body_color, (cx, cy - 2), radius)
        # Ondulação embaixo
        wave_y = cy + radius - 4
        pygame.draw.rect(surface, body_color, (cx - radius, cy - 2, radius * 2, radius - 2))
        for i in range(3):
            wx = cx - radius + i * (radius * 2 // 3) + (radius // 3)
            pygame.draw.circle(surface, body_color, (wx, wave_y), radius // 3)

        # Olhos tontos em espiral ou pontos (@_@)
        pygame.draw.circle(surface, face_color, (cx - 5, cy - 3), 3)
        pygame.draw.circle(surface, face_color, (cx + 5, cy - 3), 3)
        # Boca ondulada
        pts = [(cx - 6, cy + 5), (cx - 2, cy + 2), (cx + 2, cy + 6), (cx + 6, cy + 3)]
        pygame.draw.lines(surface, face_color, False, pts, 2)
        return

    # 3. RENDERIZAÇÃO ESPECÍFICA DE CADA POKÉMON

    if ghost_name == "gengar":
        # GENGAR (Blinky): Roxo escuro, orelhas pontiagudas, sorriso macabro denteado e olhos vermelhos
        body_purple = (110, 40, 155)
        # Orelhas pontudas
        ear_left = [(cx - radius + 1, cy - radius + 4), (cx - radius + 3, cy - radius - 5), (cx - 3, cy - radius + 1)]
        ear_right = [(cx + radius - 1, cy - radius + 4), (cx + radius - 3, cy - radius - 5), (cx + 3, cy - radius + 1)]
        pygame.draw.polygon(surface, body_purple, ear_left)
        pygame.draw.polygon(surface, body_purple, ear_right)

        # Corpo redondo com base com pontas
        pygame.draw.circle(surface, body_purple, (cx, cy), radius)
        pygame.draw.rect(surface, body_purple, (cx - radius, cy, radius * 2, radius - 3))
        # Espinhos inferiores
        for i in range(4):
            sx = cx - radius + i * (radius * 2 // 4) + (radius // 4)
            pygame.draw.circle(surface, body_purple, (sx, cy + radius - 2), 3)

        # Olhos vermelhos triangulares
        eye_y = cy - 3
        pygame.draw.polygon(surface, (240, 30, 30), [(cx - 7, eye_y - 2), (cx - 2, eye_y), (cx - 6, eye_y + 3)])
        pygame.draw.polygon(surface, (240, 30, 30), [(cx + 7, eye_y - 2), (cx + 2, eye_y), (cx + 6, eye_y + 3)])
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 4, eye_y), 1)
        pygame.draw.circle(surface, COLOR_WHITE, (cx + 4, eye_y), 1)

        # Sorriso largo com dentes brancos (marca registrada do Gengar)
        mouth_pts = [(cx - 8, cy + 3), (cx, cy + 7), (cx + 8, cy + 3)]
        pygame.draw.lines(surface, COLOR_WHITE, False, mouth_pts, 3)
        pygame.draw.line(surface, body_purple, (cx - 3, cy + 4), (cx - 3, cy + 6), 1)
        pygame.draw.line(surface, body_purple, (cx + 3, cy + 4), (cx + 3, cy + 6), 1)

    elif ghost_name == "gastly":
        # GASTLY (Pinky): Esfera preta central envolvida por névoa/gás roxo flamejante
        # Névoa gasosa externa animada
        gas_color = (150, 60, 200)
        for i in range(6):
            ang = (timer * 0.08) + i * (math.pi / 3)
            dist = radius + 3 + 2 * math.sin(timer * 0.15 + i)
            gx = cx + int(dist * math.cos(ang))
            gy = cy + int(dist * math.sin(ang))
            pygame.draw.circle(surface, gas_color, (gx, gy), 5)

        # Núcleo preto
        pygame.draw.circle(surface, (25, 18, 30), (cx, cy), radius - 1)

        # Olhos brancos enormes inclinados com pupilas pretas
        eye_left = [(cx - 9, cy - 4), (cx - 1, cy - 7), (cx - 2, cy + 1), (cx - 8, cy + 2)]
        eye_right = [(cx + 9, cy - 4), (cx + 1, cy - 7), (cx + 2, cy + 1), (cx + 8, cy + 2)]
        pygame.draw.polygon(surface, COLOR_WHITE, eye_left)
        pygame.draw.polygon(surface, COLOR_WHITE, eye_right)
        pygame.draw.circle(surface, COLOR_BLACK, (cx - 4, cy - 2), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (cx + 4, cy - 2), 2)

        # Sorriso com presas
        pygame.draw.arc(surface, (235, 70, 120), (cx - 5, cy + 1, 10, 6), math.pi, 2 * math.pi, 2)

    elif ghost_name == "haunter":
        # HAUNTER (Inky): Índigo com mãos destacadas flutuando e bochechas pontiagudas
        body_indigo = (70, 50, 165)
        # Orelhas / pontas da cabeça
        top_pts = [(cx - radius, cy - radius + 5), (cx - radius + 2, cy - radius - 4), (cx, cy - radius + 2),
                   (cx + radius - 2, cy - radius - 4), (cx + radius, cy - radius + 5)]
        pygame.draw.polygon(surface, body_indigo, top_pts)
        pygame.draw.circle(surface, body_indigo, (cx, cy), radius)

        # Bochechas pontiagudas laterais
        pygame.draw.polygon(surface, body_indigo, [(cx - radius, cy - 2), (cx - radius - 5, cy + 2), (cx - radius + 3, cy + 6)])
        pygame.draw.polygon(surface, body_indigo, [(cx + radius, cy - 2), (cx + radius + 5, cy + 2), (cx + radius - 3, cy + 6)])

        # Mãos fantasmagóricas flutuantes animadas
        hand_wobble = int(2 * math.sin(timer * 0.1))
        # Mão esquerda
        pygame.draw.circle(surface, body_indigo, (cx - radius - 7, cy + 4 + hand_wobble), 4)
        pygame.draw.line(surface, body_indigo, (cx - radius - 7, cy + 4 + hand_wobble), (cx - radius - 11, cy + 2 + hand_wobble), 2)
        # Mão direita
        pygame.draw.circle(surface, body_indigo, (cx + radius + 7, cy + 4 - hand_wobble), 4)
        pygame.draw.line(surface, body_indigo, (cx + radius + 7, cy + 4 - hand_wobble), (cx + radius + 11, cy + 2 - hand_wobble), 2)

        # Olhos triangulares brancos com pupilas
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx - 8, cy - 3), (cx - 2, cy - 4), (cx - 4, cy + 2)])
        pygame.draw.polygon(surface, COLOR_WHITE, [(cx + 8, cy - 3), (cx + 2, cy - 4), (cx + 4, cy + 2)])
        pygame.draw.circle(surface, (230, 40, 60), (cx - 5, cy - 1), 2)
        pygame.draw.circle(surface, (230, 40, 60), (cx + 5, cy - 1), 2)

        # Língua vermelha pontuda
        pygame.draw.polygon(surface, (230, 50, 70), [(cx - 3, cy + 4), (cx + 3, cy + 4), (cx, cy + 9)])

    else:
        # KOFFING (Clyde): Azul acinzentado/púrpura com crateras de gás tóxico e símbolo de caveira
        koffing_color = (105, 80, 135)
        pygame.draw.circle(surface, koffing_color, (cx, cy), radius)

        # Crateras em relevo
        crater_pos = [(cx - 8, cy - 7), (cx + 8, cy - 7), (cx - 9, cy + 5), (cx + 9, cy + 5)]
        for cpx, cpy in crater_pos:
            pygame.draw.circle(surface, (80, 60, 105), (cpx, cpy), 3)
            pygame.draw.circle(surface, (170, 210, 60), (cpx, cpy), 1)

        # Olhos redondos
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 4, cy - 2), 3)
        pygame.draw.circle(surface, COLOR_WHITE, (cx + 4, cy - 2), 3)
        pygame.draw.circle(surface, COLOR_BLACK, (cx - 4, cy - 2), 1)
        pygame.draw.circle(surface, COLOR_BLACK, (cx + 4, cy - 2), 1)

        # Boca dentada aberta com expressão de deboche
        pygame.draw.rect(surface, (245, 245, 250), (cx - 5, cy + 3, 10, 4), border_radius=2)
        pygame.draw.line(surface, COLOR_BLACK, (cx, cy + 3), (cx, cy + 7), 1)


def draw_bonus_item(surface: pygame.Surface, x: float, y: float, level: int):
    """Desenha itens especiais colecionáveis: Oran Berry, Thunder Stone ou Rare Candy."""
    cx, cy = int(x), int(y)

    if level == 1:
        # ORAN BERRY: Fruta azul de cura com folha verde
        pygame.draw.circle(surface, (50, 110, 220), (cx, cy + 2), 8)
        pygame.draw.circle(surface, (90, 150, 255), (cx - 2, cy), 3)
        # Folhinha verde
        pygame.draw.ellipse(surface, (50, 200, 70), (cx - 2, cy - 8, 8, 4))
    elif level == 2:
        # THUNDER STONE: Pedra amarela do trovão (Pikachu)
        pygame.draw.polygon(surface, (255, 215, 30), [(cx, cy - 9), (cx + 8, cy - 2), (cx + 5, cy + 8), (cx - 5, cy + 8), (cx - 8, cy - 2)])
        # Raio preto desenhado dentro da pedra
        pygame.draw.lines(surface, (30, 30, 30), False, [(cx + 2, cy - 6), (cx - 2, cy), (cx + 2, cy), (cx - 2, cy + 6)], 2)
    else:
        # RARE CANDY: Doce azul e branco em embalagem clássica de bala
        # Corpo central da bala
        pygame.draw.circle(surface, (40, 140, 240), (cx, cy), 6)
        pygame.draw.circle(surface, COLOR_WHITE, (cx - 2, cy - 2), 2)
        # Pontas torcidas da embalagem
        pygame.draw.polygon(surface, (230, 240, 255), [(cx - 6, cy), (cx - 10, cy - 4), (cx - 10, cy + 4)])
        pygame.draw.polygon(surface, (230, 240, 255), [(cx + 6, cy), (cx + 10, cy - 4), (cx + 10, cy + 4)])
