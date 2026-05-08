import pygame
import sys
import random
import math
import time

# ── init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

W, H = 900, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("AlphaBeta – Um Jogo sobre Alfabetização")
clock = pygame.time.Clock()

# ── colours ───────────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
DARK_BG    = ( 18,  18,  35)
NIGHT_BG   = ( 10,  10,  22)
DAWN_BG    = ( 40,  30,  70)
PANEL_BG   = ( 30,  28,  55)
ACCENT     = ( 90, 200, 255)
GOLD       = (255, 215,  80)
WARM       = (255, 140,  60)
SOFT_GREEN = (100, 220, 130)
SOFT_RED   = (255,  90,  90)
GREY       = (120, 120, 140)
LIGHT_GREY = (180, 180, 200)
SHADOW     = (  0,   0,   0, 120)
TILE_COLOR = ( 55,  50,  90)
TILE_HOVER = ( 75,  70, 120)
TILE_SEL   = (100, 200, 255)
SLOT_EMPTY = ( 45,  42,  80)
SLOT_FILL  = ( 70, 180, 130)

# ── fonts ─────────────────────────────────────────────────────────────────────
font_xl   = pygame.font.SysFont("DejaVu Sans", 52, bold=True)
font_lg   = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
font_md   = pygame.font.SysFont("DejaVu Sans", 26, bold=False)
font_sm   = pygame.font.SysFont("DejaVu Sans", 20)
font_xs   = pygame.font.SysFont("DejaVu Sans", 15)
font_tile = pygame.font.SysFont("DejaVu Sans", 30, bold=True)

# ── game data ─────────────────────────────────────────────────────────────────
LEVELS = [
    {
        "word": "BOLA",
        "syllables": ["BO", "LA"],
        "distractors": ["CA", "ME", "TO"],
        "npc_name": "Dona Amélia",
        "npc_need": "Ela precisa ler o nome da rua para encontrar sua casa.",
        "npc_dialogue": [
            "Eu não sei ler… nunca aprendi.",
            "Moro aqui há 20 anos, mas sempre me perco.",
            "Você consegue me ajudar a montar as palavras?"
        ],
        "success_msg": "Dona Amélia aprendeu a sílaba!\nAgora ela reconhece o nome da rua!",
        "theme": "Mobilidade Urbana",
        "darkness": 0.85,
    },
    {
        "word": "PANE",
        "syllables": ["PA", "NE"],
        "distractors": ["LI", "SO", "RO"],
        "npc_name": "Sr. Benedito",
        "npc_need": "Ele precisa ler a bula do remédio para tomar a dose certa.",
        "npc_dialogue": [
            "Tenho 60 anos e nunca fui à escola.",
            "Não sei o que está escrito nessa bula…",
            "Às vezes tomo remédio errado sem querer."
        ],
        "success_msg": "Sr. Benedito entendeu a bula!\nEle vai tomar o remédio correto!",
        "theme": "Saúde",
        "darkness": 0.70,
    },
    {
        "word": "VOTO",
        "syllables": ["VO", "TO"],
        "distractors": ["MI", "RA", "DE"],
        "npc_name": "Maria José",
        "npc_need": "Ela quer votar, mas não sabe ler o número do candidato.",
        "npc_dialogue": [
            "Sempre fui dependente dos outros para votar.",
            "Não entendo o que está escrito na urna.",
            "Quero escolher por mim mesma!"
        ],
        "success_msg": "Maria José votou sozinha!\nSua voz foi ouvida pela primeira vez!",
        "theme": "Cidadania",
        "darkness": 0.55,
    },
    {
        "word": "SONHO",
        "syllables": ["SO", "NHO"],
        "distractors": ["CA", "TE", "LU"],
        "npc_name": "João (12 anos)",
        "npc_need": "Ele quer ler histórias mas tem dificuldade com as sílabas.",
        "npc_dialogue": [
            "Na minha escola não tinha livro suficiente…",
            "Minha família não pôde me ensinar a ler.",
            "Mas eu quero tanto conhecer as histórias!"
        ],
        "success_msg": "João leu sua primeira história!\nO mundo das palavras agora é dele!",
        "theme": "Educação e Futuro",
        "darkness": 0.30,
    },
    {
        "word": "LIVRE",
        "syllables": ["LI", "VRE"],
        "distractors": ["MA", "SO", "TA"],
        "npc_name": "Comunidade",
        "npc_need": "Toda a comunidade aprende junta — a alfabetização ilumina o caminho!",
        "npc_dialogue": [
            "29 milhões de brasileiros não sabem ler.",
            "Cada palavra aprendida é uma porta aberta.",
            "Juntos, podemos iluminar esse caminho!"
        ],
        "success_msg": "A comunidade está iluminada!\nO conhecimento pertence a todos!",
        "theme": "Transformação Social",
        "darkness": 0.0,
    },
]

STATS = {
    "br_illiteracy": "29 milhões de brasileiros adultos\nnão sabem ler ou escrever.",
    "impact": "O analfabetismo limita o acesso\nà saúde, trabalho e cidadania.",
    "hope": "A alfabetização é a porta de entrada\npara todos os outros direitos.",
}

# ── helpers ───────────────────────────────────────────────────────────────────

def draw_rounded_rect(surface, color, rect, radius=12, alpha=None):
    if alpha is not None:
        tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(tmp, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surface.blit(tmp, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surface, color, rect, border_radius=radius)

def text_shadow(surface, font, text, color, sx, sy, offset=2):
    shadow_surf = font.render(text, True, (0, 0, 0))
    surface.blit(shadow_surf, (sx + offset, sy + offset))
    surf = font.render(text, True, color)
    surface.blit(surf, (sx, sy))
    return surf.get_rect(topleft=(sx, sy))

def center_text(surface, font, text, color, y, shadow=True):
    surf = font.render(text, True, color)
    x = W // 2 - surf.get_width() // 2
    if shadow:
        sh = font.render(text, True, (0, 0, 0))
        surface.blit(sh, (x + 2, y + 2))
    surface.blit(surf, (x, y))
    return surf.get_rect(topleft=(x, y))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_stars(surface, stars):
    for sx, sy, size, brightness in stars:
        col = (brightness, brightness, brightness)
        pygame.draw.circle(surface, col, (sx, sy), size)

def generate_stars(n=120):
    stars = []
    for _ in range(n):
        sx = random.randint(0, W)
        sy = random.randint(0, H // 2)
        size = random.randint(1, 2)
        brightness = random.randint(100, 220)
        stars.append((sx, sy, size, brightness))
    return stars

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines

# ── particle system ───────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color=GOLD):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.uniform(0.6, 1.2)
        self.max_life = self.life
        self.color = color
        self.size = random.uniform(2, 5)

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= dt
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = max(1, int(self.size * (self.life / self.max_life)))
        tmp = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, (*self.color, alpha), (size, size), size)
        surface.blit(tmp, (int(self.x) - size, int(self.y) - size))

# ── NPC ───────────────────────────────────────────────────────────────────────

class NPC:
    def __init__(self, x, y, name, darkness):
        self.x = x
        self.y = y
        self.name = name
        self.darkness = darkness  # 0=bright, 1=very dark
        self.anim_t = 0.0
        self.dialogue_idx = 0
        self.dialogue_lines = []
        self.talking = False
        self.talk_timer = 0.0
        self.light_radius = 0.0

    def update(self, dt):
        self.anim_t += dt
        if self.talking:
            self.talk_timer -= dt
            if self.talk_timer <= 0:
                self.dialogue_idx += 1
                if self.dialogue_idx < len(self.dialogue_lines):
                    self.talk_timer = 3.0
                else:
                    self.talking = False

    def illuminate(self, amount):
        """Reduce darkness as player solves syllables."""
        self.darkness = max(0.0, self.darkness - amount)
        self.light_radius = min(200, self.light_radius + 60)

    def draw(self, surface):
        bob = math.sin(self.anim_t * 2) * 3

        # Light glow around NPC
        if self.light_radius > 0:
            for r in range(int(self.light_radius), 0, -10):
                alpha = int(30 * (1 - self.darkness) * (r / self.light_radius))
                glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 220, 120, alpha), (r, r), r)
                surface.blit(glow, (self.x - r, self.y - r))

        # Body (silhouette-style, darkened by darkness factor)
        brightness = int(220 * (1 - self.darkness * 0.7))
        body_color = (brightness, brightness - 20, brightness - 60)
        head_color = (brightness - 20, brightness - 40, brightness - 80)

        # shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 80),
                            (self.x - 20, self.y + 55 + int(bob), 40, 8))

        # body
        pygame.draw.ellipse(surface, body_color,
                            (self.x - 18, self.y + 10 + int(bob), 36, 48))
        # head
        pygame.draw.circle(surface, head_color,
                           (self.x, self.y + int(bob)), 20)

        # eyes (light up as literacy grows)
        eye_brightness = int(200 * (1 - self.darkness))
        eye_color = (eye_brightness, eye_brightness, 50 + eye_brightness)
        pygame.draw.circle(surface, eye_color, (self.x - 7, self.y - 2 + int(bob)), 4)
        pygame.draw.circle(surface, eye_color, (self.x + 7, self.y - 2 + int(bob)), 4)

        # Name tag
        name_surf = font_xs.render(self.name, True, LIGHT_GREY)
        surface.blit(name_surf, (self.x - name_surf.get_width() // 2,
                                  self.y + 70 + int(bob)))

# ── Tile (syllable) ───────────────────────────────────────────────────────────

class Tile:
    def __init__(self, text, x, y, is_correct=False, idx=0):
        self.text = text
        self.x = x
        self.y = y
        self.w = 80
        self.h = 60
        self.is_correct = is_correct
        self.idx = idx
        self.selected = False
        self.hovered = False
        self.shake = 0.0
        self.pulse = 0.0

    def get_rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

    def update(self, dt):
        if self.shake > 0:
            self.shake -= dt * 5
        self.pulse += dt * 3

    def draw(self, surface):
        ox = int(math.sin(self.shake * 20) * self.shake * 8) if self.shake > 0 else 0

        bg = TILE_SEL if self.selected else (TILE_HOVER if self.hovered else TILE_COLOR)
        rect = (self.x - self.w // 2 + ox, self.y - self.h // 2, self.w, self.h)

        # glow if selected
        if self.selected:
            for gw in [6, 4, 2]:
                draw_rounded_rect(surface, ACCENT,
                                  (rect[0] - gw, rect[1] - gw,
                                   self.w + gw * 2, self.h + gw * 2), 14 + gw, 60)

        draw_rounded_rect(surface, bg, rect, 12)
        pygame.draw.rect(surface, ACCENT if self.selected else (80, 75, 130),
                         rect, 2, border_radius=12)

        surf = font_tile.render(self.text, True,
                                WHITE if self.selected else LIGHT_GREY)
        surface.blit(surf, (self.x - surf.get_width() // 2,
                            self.y - surf.get_height() // 2))

# ── Word Slot ─────────────────────────────────────────────────────────────────

class WordSlot:
    def __init__(self, index, x, y):
        self.index = index
        self.x = x
        self.y = y
        self.w = 90
        self.h = 65
        self.filled_text = ""
        self.correct = False
        self.flash = 0.0

    def fill(self, text, correct):
        self.filled_text = text
        self.correct = correct
        self.flash = 1.0

    def clear(self):
        self.filled_text = ""
        self.correct = False

    def update(self, dt):
        if self.flash > 0:
            self.flash -= dt * 2

    def draw(self, surface):
        rect = (self.x - self.w // 2, self.y - self.h // 2, self.w, self.h)

        if self.filled_text:
            bg = SLOT_FILL if self.correct else SOFT_RED
            glow_col = SOFT_GREEN if self.correct else SOFT_RED
            if self.flash > 0:
                for gw in [8, 5, 2]:
                    draw_rounded_rect(surface, glow_col,
                                      (rect[0] - gw, rect[1] - gw,
                                       self.w + gw * 2, self.h + gw * 2), 14 + gw,
                                      int(80 * self.flash))
        else:
            bg = SLOT_EMPTY

        draw_rounded_rect(surface, bg, rect, 12)
        border_col = SOFT_GREEN if (self.filled_text and self.correct) else \
                     (SOFT_RED if self.filled_text else GREY)
        pygame.draw.rect(surface, border_col, rect, 2, border_radius=12)

        if self.filled_text:
            surf = font_tile.render(self.filled_text, True, WHITE)
            surface.blit(surf, (self.x - surf.get_width() // 2,
                                self.y - surf.get_height() // 2))
        else:
            surf = font_sm.render("?", True, GREY)
            surface.blit(surf, (self.x - surf.get_width() // 2,
                                self.y - surf.get_height() // 2))

# ── Game State Machine ────────────────────────────────────────────────────────

class Game:
    INTRO      = "intro"
    CUTSCENE   = "cutscene"
    PLAYING    = "playing"
    SUCCESS    = "success"
    TRANSITION = "transition"
    ENDING     = "ending"

    def __init__(self):
        self.state = self.INTRO
        self.level_idx = 0
        self.stars = generate_stars(150)
        self.particles = []
        self.t = 0.0

        # intro
        self.intro_alpha = 0.0

        # cutscene
        self.cutscene_line = 0
        self.cutscene_timer = 0.0
        self.cutscene_alpha = 0.0

        # playing
        self.tiles = []
        self.slots = []
        self.selected_tile = None
        self.errors = 0
        self.max_errors = 3
        self.feedback_msg = ""
        self.feedback_timer = 0.0
        self.feedback_color = WHITE
        self.word_complete = False
        self.current_syllable_idx = 0  # which slot we're filling

        # success
        self.success_timer = 0.0
        self.success_alpha = 0.0

        # NPC
        self.npc = None

        # transition
        self.trans_alpha = 0.0
        self.trans_dir = 1  # 1=fade out, -1=fade in

        # world darkness (0=bright, 1=dark)
        self.world_darkness = 1.0

        self.load_level()

    # ── level setup ───────────────────────────────────────────────────────────

    def load_level(self):
        data = LEVELS[self.level_idx]
        self.word_data = data
        self.world_darkness = data["darkness"]
        self.word_complete = False
        self.errors = 0
        self.selected_tile = None
        self.feedback_msg = ""
        self.current_syllable_idx = 0

        # NPC
        self.npc = NPC(720, 320, data["npc_name"], data["darkness"])
        self.npc.dialogue_lines = data["npc_dialogue"]
        self.npc.light_radius = (1 - data["darkness"]) * 120

        # Build tiles (syllables + distractors), shuffle
        syllables = data["syllables"]
        distractors = data["distractors"]
        all_tiles_text = syllables + distractors
        random.shuffle(all_tiles_text)

        # Position tiles in a grid below center
        cols = min(4, len(all_tiles_text))
        spacing_x = 110
        spacing_y = 85
        rows = math.ceil(len(all_tiles_text) / cols)
        start_x = W // 2 - (cols - 1) * spacing_x // 2
        start_y = 400

        self.tiles = []
        for i, text in enumerate(all_tiles_text):
            col = i % cols
            row = i // cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            is_correct = text in syllables
            idx = syllables.index(text) if is_correct else -1
            self.tiles.append(Tile(text, x, y, is_correct, idx))

        # Slots for each syllable
        n = len(syllables)
        spacing = 110
        start = W // 2 - (n - 1) * spacing // 2
        self.slots = []
        for i in range(n):
            self.slots.append(WordSlot(i, start + i * spacing, 200))

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt, events):
        self.t += dt
        self.particles = [p for p in self.particles if p.update(dt)]

        if self.state == self.INTRO:
            self._update_intro(dt, events)
        elif self.state == self.CUTSCENE:
            self._update_cutscene(dt, events)
        elif self.state == self.PLAYING:
            self._update_playing(dt, events)
        elif self.state == self.SUCCESS:
            self._update_success(dt, events)
        elif self.state == self.TRANSITION:
            self._update_transition(dt)
        elif self.state == self.ENDING:
            self._update_ending(dt, events)

        if self.npc:
            self.npc.update(dt)
        for tile in self.tiles:
            tile.update(dt)
        for slot in self.slots:
            slot.update(dt)

    def _update_intro(self, dt, events):
        self.intro_alpha = min(1.0, self.intro_alpha + dt * 0.6)
        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.state = self.CUTSCENE
                self.cutscene_line = 0
                self.cutscene_timer = 3.5
                self.cutscene_alpha = 0.0

    def _update_cutscene(self, dt, events):
        self.cutscene_alpha = min(1.0, self.cutscene_alpha + dt * 2)
        self.cutscene_timer -= dt
        if self.cutscene_timer <= 0:
            self.cutscene_line += 1
            self.cutscene_timer = 3.5
            self.cutscene_alpha = 0.0
            if self.cutscene_line >= len(self.word_data["npc_dialogue"]):
                self.state = self.PLAYING
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                self.cutscene_line += 1
                self.cutscene_timer = 3.5
                self.cutscene_alpha = 0.0
                if self.cutscene_line >= len(self.word_data["npc_dialogue"]):
                    self.state = self.PLAYING

    def _update_playing(self, dt, events):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt

        mouse_pos = pygame.mouse.get_pos()

        # hover
        for tile in self.tiles:
            tile.hovered = tile.get_rect().collidepoint(mouse_pos)

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._handle_click(mouse_pos)
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                if self.selected_tile:
                    self.selected_tile.selected = False
                    self.selected_tile = None

        # Check if word is complete
        if all(s.filled_text for s in self.slots):
            if all(s.correct for s in self.slots):
                self._on_word_complete()

    def _handle_click(self, pos):
        # Click on a tile
        for tile in self.tiles:
            if tile.get_rect().collidepoint(pos):
                if self.selected_tile == tile:
                    tile.selected = False
                    self.selected_tile = None
                else:
                    if self.selected_tile:
                        self.selected_tile.selected = False
                    tile.selected = True
                    self.selected_tile = tile
                    # Auto-place in next empty slot
                    self._try_place_tile(tile)
                return

    def _try_place_tile(self, tile):
        # Find the next empty slot
        for slot in self.slots:
            if not slot.filled_text:
                expected = self.word_data["syllables"][slot.index]
                correct = (tile.text == expected)
                slot.fill(tile.text, correct)
                tile.selected = False
                self.selected_tile = None

                if correct:
                    self.feedback_msg = f"✓ '{tile.text}' — Correto!"
                    self.feedback_color = SOFT_GREEN
                    self.feedback_timer = 1.5
                    # illuminate NPC
                    n_syllables = len(self.word_data["syllables"])
                    self.npc.illuminate(0.6 / n_syllables)
                    # particles
                    sx, sy = slot.x, slot.y
                    for _ in range(20):
                        self.particles.append(Particle(sx, sy, GOLD))
                    self.world_darkness = max(0.0, self.world_darkness - 0.15 / n_syllables)
                else:
                    self.errors += 1
                    self.feedback_msg = f"✗ '{tile.text}' — Tente novamente! ({self.max_errors - self.errors} tentativas restantes)"
                    self.feedback_color = SOFT_RED
                    self.feedback_timer = 2.0
                    slot.clear()
                    tile.shake = 1.0
                    if self.errors >= self.max_errors:
                        self._reset_puzzle()
                return

    def _reset_puzzle(self):
        for slot in self.slots:
            slot.clear()
        self.errors = 0
        self.feedback_msg = "Sem problemas! Vamos tentar de novo."
        self.feedback_color = ACCENT
        self.feedback_timer = 2.0
        random.shuffle(self.tiles)
        # Reposition tiles
        cols = min(4, len(self.tiles))
        spacing_x = 110
        rows = math.ceil(len(self.tiles) / cols)
        start_x = W // 2 - (cols - 1) * spacing_x // 2
        start_y = 400
        for i, tile in enumerate(self.tiles):
            col = i % cols
            row = i // cols
            tile.x = start_x + col * spacing_x
            tile.y = start_y + row * spacing_y

    def _on_word_complete(self):
        self.word_complete = True
        self.state = self.SUCCESS
        self.success_timer = 0.0
        self.success_alpha = 0.0
        # big particle burst
        for _ in range(60):
            x = random.randint(200, 700)
            y = random.randint(150, 400)
            col = random.choice([GOLD, SOFT_GREEN, ACCENT, WHITE])
            self.particles.append(Particle(x, y, col))
        # NPC fully illuminated
        self.npc.darkness = 0.0
        self.npc.light_radius = 200

    def _update_success(self, dt, events):
        self.success_timer += dt
        self.success_alpha = min(1.0, self.success_timer * 1.5)
        # Keep spawning particles
        if random.random() < 0.3:
            x = random.randint(150, 650)
            y = random.randint(100, 450)
            col = random.choice([GOLD, SOFT_GREEN, ACCENT])
            self.particles.append(Particle(x, y, col))

        for e in events:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) and self.success_timer > 1.5:
                self.level_idx += 1
                if self.level_idx >= len(LEVELS):
                    self.state = self.ENDING
                else:
                    self.state = self.TRANSITION
                    self.trans_alpha = 0.0
                    self.trans_dir = 1

    def _update_transition(self, dt):
        speed = 2.0
        if self.trans_dir == 1:
            self.trans_alpha = min(1.0, self.trans_alpha + dt * speed)
            if self.trans_alpha >= 1.0:
                self.load_level()
                self.state = self.CUTSCENE
                self.cutscene_line = 0
                self.cutscene_timer = 3.5
                self.cutscene_alpha = 0.0
                self.trans_dir = -1
        else:
            self.trans_alpha = max(0.0, self.trans_alpha - dt * speed)
            if self.trans_alpha <= 0.0:
                self.state = self.PLAYING

    def _update_ending(self, dt, events):
        self.success_alpha = min(1.0, self.success_alpha + dt * 0.5)
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                self.__init__()

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface):
        # Background: interpolate between night dark and dawn bright
        bg = lerp_color(DAWN_BG, NIGHT_BG, self.world_darkness)
        surface.fill(bg)

        # Stars (faded by world brightness)
        star_alpha = self.world_darkness
        for sx, sy, size, brightness in self.stars:
            alpha_b = int(brightness * star_alpha)
            if alpha_b > 10:
                pygame.draw.circle(surface, (alpha_b, alpha_b, alpha_b), (sx, sy), size)

        # Horizon glow
        glow_intensity = int(80 * (1 - self.world_darkness))
        if glow_intensity > 0:
            for r in range(200, 0, -20):
                ga = int(glow_intensity * (1 - r / 200))
                tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(tmp, (255, 200, 100, ga), (r, r), r)
                surface.blit(tmp, (W // 2 - r, H - r // 2))

        if self.state == self.INTRO:
            self._draw_intro(surface)
        elif self.state == self.CUTSCENE:
            self._draw_cutscene(surface)
        elif self.state == self.PLAYING:
            self._draw_playing(surface)
        elif self.state == self.SUCCESS:
            self._draw_playing(surface)
            self._draw_success(surface)
        elif self.state == self.TRANSITION:
            self._draw_playing(surface)
            overlay = pygame.Surface((W, H))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(int(255 * self.trans_alpha))
            surface.blit(overlay, (0, 0))
        elif self.state == self.ENDING:
            self._draw_ending(surface)

        # particles always on top
        for p in self.particles:
            p.draw(surface)

    def _draw_intro(self, surface):
        alpha = int(255 * self.intro_alpha)

        # Title
        title = "AlphaBeta"
        surf = font_xl.render(title, True, GOLD)
        surf.set_alpha(alpha)
        surface.blit(surf, (W // 2 - surf.get_width() // 2, 120))

        # Subtitle
        sub = "Um jogo sobre alfabetização no Brasil"
        s2 = font_md.render(sub, True, LIGHT_GREY)
        s2.set_alpha(alpha)
        surface.blit(s2, (W // 2 - s2.get_width() // 2, 195))

        # Stats panel
        panel_y = 260
        draw_rounded_rect(surface, PANEL_BG, (100, panel_y, W - 200, 140), 16, 180)

        stat_lines = [
            "📊  29 milhões de brasileiros adultos não sabem ler ou escrever.",
            "🏥  O analfabetismo limita o acesso à saúde, trabalho e cidadania.",
            "🌟  Você pode ajudar — uma sílaba de cada vez.",
        ]
        for i, line in enumerate(stat_lines):
            s = font_sm.render(line, True, LIGHT_GREY)
            s.set_alpha(alpha)
            surface.blit(s, (130, panel_y + 18 + i * 38))

        # Level indicator
        s3 = font_md.render(f"5 histórias reais. 5 comunidades. Comece.", True, ACCENT)
        s3.set_alpha(alpha)
        surface.blit(s3, (W // 2 - s3.get_width() // 2, 430))

        blink = abs(math.sin(self.t * 2))
        start = font_sm.render("Pressione qualquer tecla para começar", True,
                               (int(180 * blink), int(200 * blink), 255))
        start.set_alpha(alpha)
        surface.blit(start, (W // 2 - start.get_width() // 2, 490))

    def _draw_cutscene(self, surface):
        data = self.word_data
        alpha = int(255 * self.cutscene_alpha)

        # Dark overlay
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 140))
        surface.blit(ov, (0, 0))

        # Theme badge
        badge = font_xs.render(f"Tema: {data['theme']}", True, ACCENT)
        surface.blit(badge, (30, 30))

        level_badge = font_xs.render(f"Nível {self.level_idx + 1} / {len(LEVELS)}", True, GOLD)
        surface.blit(level_badge, (W - level_badge.get_width() - 30, 30))

        # NPC drawing (large, centered)
        if self.npc:
            self.npc.x = W // 2
            self.npc.y = H // 2 - 60
            self.npc.draw(surface)

        # Dialogue bubble
        line_idx = min(self.cutscene_line, len(data["npc_dialogue"]) - 1)
        line = data["npc_dialogue"][line_idx]

        bw = 600
        bh = 80
        bx = W // 2 - bw // 2
        by = H - 160
        draw_rounded_rect(surface, (20, 20, 40), (bx, by, bw, bh), 16, 220)
        pygame.draw.rect(surface, ACCENT, (bx, by, bw, bh), 2, border_radius=16)

        # Name
        name_s = font_sm.render(data["npc_name"] + ":", True, GOLD)
        name_s.set_alpha(alpha)
        surface.blit(name_s, (bx + 20, by + 12))

        wrapped = wrap_text(line, font_sm, bw - 40)
        for i, wline in enumerate(wrapped):
            ws = font_sm.render(wline, True, WHITE)
            ws.set_alpha(alpha)
            surface.blit(ws, (bx + 20, by + 38 + i * 22))

        # Need description
        need_s = font_xs.render(data["npc_need"], True, LIGHT_GREY)
        surface.blit(need_s, (W // 2 - need_s.get_width() // 2, H - 60))

        hint = font_xs.render("ESPAÇO para avançar", True, GREY)
        surface.blit(hint, (W - hint.get_width() - 20, H - 25))

        # Progress dots
        for i, dl in enumerate(data["npc_dialogue"]):
            col = ACCENT if i == line_idx else GREY
            pygame.draw.circle(surface, col, (W // 2 - 20 + i * 20, by - 20), 5)

    def _draw_playing(self, surface):
        data = self.word_data

        # Top bar
        draw_rounded_rect(surface, PANEL_BG, (0, 0, W, 55), 0, 200)
        theme_s = font_sm.render(f"Tema: {data['theme']}", True, ACCENT)
        surface.blit(theme_s, (20, 15))

        level_s = font_sm.render(f"Nível {self.level_idx + 1}/{len(LEVELS)}", True, GOLD)
        surface.blit(level_s, (W - level_s.get_width() - 20, 15))

        # Error hearts
        for i in range(self.max_errors):
            col = SOFT_RED if i < self.errors else SOFT_GREEN
            pygame.draw.circle(surface, col, (W // 2 - 30 + i * 30, 27), 8)

        # Instruction
        inst = font_xs.render("Monte a palavra clicando nas sílabas abaixo →", True, GREY)
        surface.blit(inst, (20, 58))

        # Word label
        word_label = font_md.render(f"Palavra: {data['word']}", True, GOLD)
        surface.blit(word_label, (W // 2 - word_label.get_width() // 2, 80))

        # Help sub-label
        help_label = font_xs.render("(Encontre as sílabas corretas e coloque nos espaços)", True, GREY)
        surface.blit(help_label, (W // 2 - help_label.get_width() // 2, 112))

        # Slots
        for slot in self.slots:
            slot.draw(surface)

        # Connector dashes between slots
        for i in range(len(self.slots) - 1):
            x1 = self.slots[i].x + self.slots[i].w // 2
            x2 = self.slots[i + 1].x - self.slots[i + 1].w // 2
            y = self.slots[i].y
            pygame.draw.line(surface, GREY, (x1, y), (x2, y), 2)

        # Tiles
        # Panel behind tiles
        if self.tiles:
            min_tx = min(t.x - t.w // 2 for t in self.tiles) - 20
            max_tx = max(t.x + t.w // 2 for t in self.tiles) + 20
            min_ty = min(t.y - t.h // 2 for t in self.tiles) - 15
            max_ty = max(t.y + t.h // 2 for t in self.tiles) + 15
            draw_rounded_rect(surface, PANEL_BG,
                              (min_tx, min_ty, max_tx - min_tx, max_ty - min_ty), 16, 160)
            syl_label = font_xs.render("Sílabas disponíveis — clique para selecionar:", True, GREY)
            surface.blit(syl_label, (min_tx, min_ty - 20))

        for tile in self.tiles:
            tile.draw(surface)

        # NPC on the right
        if self.npc:
            self.npc.x = 720
            self.npc.y = 310
            self.npc.draw(surface)

        # NPC panel
        npc_panel_x = 630
        npc_panel_y = 380
        draw_rounded_rect(surface, PANEL_BG, (npc_panel_x, npc_panel_y, 240, 80), 12, 180)
        n_s = font_xs.render(data["npc_name"], True, GOLD)
        surface.blit(n_s, (npc_panel_x + 10, npc_panel_y + 10))
        need_lines = wrap_text(data["npc_need"], font_xs, 220)
        for i, nl in enumerate(need_lines[:3]):
            ns = font_xs.render(nl, True, LIGHT_GREY)
            surface.blit(ns, (npc_panel_x + 10, npc_panel_y + 28 + i * 16))

        # Feedback
        if self.feedback_timer > 0 and self.feedback_msg:
            alpha_f = min(255, int(255 * self.feedback_timer))
            fw = 500
            fh = 40
            fx = W // 2 - fw // 2
            fy = 140
            draw_rounded_rect(surface, (0, 0, 0), (fx, fy, fw, fh), 10, alpha_f)
            fb_s = font_sm.render(self.feedback_msg, True, self.feedback_color)
            fb_s.set_alpha(alpha_f)
            surface.blit(fb_s, (W // 2 - fb_s.get_width() // 2, fy + 7))

        # World darkness vignette
        if self.world_darkness > 0:
            vign = pygame.Surface((W, H), pygame.SRCALPHA)
            for edge in range(80, 0, -20):
                ea = int(self.world_darkness * 180 * (1 - edge / 80))
                pygame.draw.rect(vign, (0, 0, 0, ea), (0, 0, W, H), edge)
            surface.blit(vign, (0, 0))

    def _draw_success(self, surface):
        alpha = int(255 * self.success_alpha)

        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, int(160 * self.success_alpha)))
        surface.blit(ov, (0, 0))

        # Big success text
        suf = font_xl.render("✦ Iluminado! ✦", True, GOLD)
        suf.set_alpha(alpha)
        surface.blit(suf, (W // 2 - suf.get_width() // 2, 140))

        msg = self.word_data["success_msg"]
        lines = msg.split("\n")
        for i, line in enumerate(lines):
            ls = font_md.render(line, True, WHITE)
            ls.set_alpha(alpha)
            surface.blit(ls, (W // 2 - ls.get_width() // 2, 220 + i * 40))

        # Word assembled big
        word_s = font_xl.render(self.word_data["word"], True, ACCENT)
        word_s.set_alpha(alpha)
        surface.blit(word_s, (W // 2 - word_s.get_width() // 2, 330))

        if self.success_timer > 1.5:
            cont = font_sm.render("Clique ou pressione qualquer tecla para continuar →", True, LIGHT_GREY)
            cont.set_alpha(int(alpha * abs(math.sin(self.t * 3))))
            surface.blit(cont, (W // 2 - cont.get_width() // 2, 460))

    def _draw_ending(self, surface):
        alpha = int(255 * self.success_alpha)

        # Bright background
        bright_bg = lerp_color(DARK_BG, (30, 60, 100), self.success_alpha)
        surface.fill(bright_bg)

        # Sun
        sun_y = int(H // 2 - 80 * self.success_alpha)
        pygame.draw.circle(surface, GOLD, (W // 2, sun_y), int(60 * self.success_alpha))
        for r in [80, 100, 130]:
            tmp = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(tmp, (255, 200, 60, int(40 * self.success_alpha)), (r, r), r)
            surface.blit(tmp, (W // 2 - r, sun_y - r))

        # Title
        t1 = font_xl.render("A Comunidade está Iluminada!", True, GOLD)
        t1.set_alpha(alpha)
        surface.blit(t1, (W // 2 - t1.get_width() // 2, 80))

        # Stats panel
        draw_rounded_rect(surface, PANEL_BG, (80, 170, W - 160, 200), 16, int(200 * self.success_alpha))
        facts = [
            "🌟 Você ajudou 5 pessoas a conquistar suas primeiras palavras.",
            "📚 No Brasil, 29 milhões de adultos ainda precisam dessa ajuda.",
            "🤝 Projetos de alfabetização como EJA, MOVA e Alfasol estão mudando esse cenário.",
            "💡 Cada pessoa alfabetizada impacta toda uma família e comunidade.",
        ]
        for i, fact in enumerate(facts):
            fs = font_sm.render(fact, True, LIGHT_GREY)
            fs.set_alpha(alpha)
            surface.blit(fs, (110, 188 + i * 38))

        # Call to action
        cta_lines = [
            "Você pode fazer a diferença:",
            "Apoie projetos locais de alfabetização • Doe livros • Ensine alguém próximo",
        ]
        for i, cl in enumerate(cta_lines):
            col = ACCENT if i == 0 else LIGHT_GREY
            cs = font_md.render(cl, True, col)
            cs.set_alpha(alpha)
            surface.blit(cs, (W // 2 - cs.get_width() // 2, 395 + i * 38))

        restart = font_sm.render("Pressione R para jogar novamente", True, GREY)
        restart.set_alpha(alpha)
        surface.blit(restart, (W // 2 - restart.get_width() // 2, 490))

        credits = font_xs.render("AlphaBeta  •  Jogo sobre Alfabetização", True, GREY)
        surface.blit(credits, (W // 2 - credits.get_width() // 2, H - 25))

# ── main loop ─────────────────────────────────────────────────────────────────

def main():
    game = Game()
    prev_time = time.time()

    while True:
        now = time.time()
        dt = min(now - prev_time, 0.05)
        prev_time = now

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                if game.state not in (game.INTRO, game.ENDING):
                    pass  # could add pause

        game.update(dt, events)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(120)

if __name__ == "__main__":
    main()
