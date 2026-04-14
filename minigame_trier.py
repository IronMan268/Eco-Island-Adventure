import pygame
import random
import math
import sys

pygame.init()

# =========================
# CONFIG
# =========================
LARGEUR, HAUTEUR = 1080, 720
FPS = 60
screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Mini-jeu : Tri des déchets")
clock = pygame.time.Clock()

# =========================
# COULEURS
# =========================
BLANC = (255, 255, 255)
NOIR = (20, 20, 30)
VERT = (70, 190, 90)
ROUGE = (225, 70, 70)
BLEU = (85, 160, 255)
JAUNE = (240, 210, 70)
GRIS = (95, 95, 105)
BORDURE = (70, 120, 170)

# =========================
# POLICES
# =========================
font       = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 20)
big_font   = pygame.font.SysFont("arial", 50)
mid_font   = pygame.font.SysFont("arial", 34)

# =========================
# FOND
# =========================
background = pygame.image.load("asets/la.png").convert()
background = pygame.transform.scale(background, (LARGEUR, HAUTEUR))

# =========================
# CHARGEMENT IMAGES
# =========================
def load_img(path, size=74):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, (size, size))

# IMPORTANT :
# adapte les chemins si besoin, mais garde bien les types ci-dessous
img_bouteille = load_img("asets/456.png", 74)   # bouteille
img_canette   = load_img("asets/789.png", 74)   # canette
img_sac       = load_img("asets/1.png", 74)   # sac
img_baril     = load_img("asets/123.png",   80)   # baril toxique

# =========================
# TYPES DE DECHETS
# =========================
# ICI la logique est claire et fixe
dechets_data = [
    {"type": "recyclage", "image": img_bouteille, "nom": "bouteille"},
    {"type": "recyclage", "image": img_canette,   "nom": "canette"},
    {"type": "normal",    "image": img_sac,       "nom": "sac"},
    {"type": "toxique",   "image": img_baril,     "nom": "baril"},
]

# =========================
# POUBELLES
# =========================
bin_width  = 150
bin_height = 125
bin_y      = HAUTEUR - 165

bins = {
    "recyclage": pygame.Rect(150, bin_y, bin_width, bin_height),
    "normal":    pygame.Rect(LARGEUR // 2 - bin_width // 2, bin_y, bin_width, bin_height),
    "toxique":   pygame.Rect(LARGEUR - 150 - bin_width, bin_y, bin_width, bin_height),
}

BIN_COLORS = {
    "recyclage": BLEU,
    "normal": GRIS,
    "toxique": ROUGE,
}

bin_anim = {k: {"open": 0.0, "shake": 0.0, "shake_dir": 1} for k in bins}

# =========================
# PARTICULES
# =========================
class Particle:
    def __init__(self, x, y, color):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 9)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - random.uniform(2, 5)
        self.color = color
        self.radius = random.randint(4, 9)
        self.life = random.randint(35, 60)
        self.max_life = self.life
        self.gravity = 0.3
        self.shape = random.randint(0, 2)
        self.angle = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-0.2, 0.2)

    def update(self):
        self.vx *= 0.97
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.angle += self.rot_speed

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.radius * (self.life / self.max_life)))
        c = (*self.color, alpha)
        tmp = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)

        if self.shape == 0:
            pygame.draw.circle(tmp, c, (r * 2, r * 2), r)
        elif self.shape == 1:
            pygame.draw.rect(tmp, c, (r, r, r * 2, r * 2), border_radius=2)
        else:
            pts = []
            for i in range(5):
                a_out = self.angle + i * (2 * math.pi / 5) - math.pi / 2
                a_in = a_out + math.pi / 5
                pts.append((r * 2 + math.cos(a_out) * r * 2, r * 2 + math.sin(a_out) * r * 2))
                pts.append((r * 2 + math.cos(a_in) * r, r * 2 + math.sin(a_in) * r))
            pygame.draw.polygon(tmp, c, pts)

        surface.blit(tmp, (int(self.x) - r * 2, int(self.y) - r * 2))

particles = []

def spawn_particles(x, y, color, count=40):
    colors = [
        color,
        (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255)),
        BLANC,
        JAUNE
    ]
    for _ in range(count):
        particles.append(Particle(x, y, random.choice(colors)))

# =========================
# DECHET ACTUEL
# =========================
dechet_actuel = None
dechet_x = float(LARGEUR // 2)
dechet_y = 40.0
dechet_vx = 0.0
dechet_vy = 3.8
float_phase = 0.0

arc_start_x = 0.0
arc_start_y = 0.0
arc_t = 0.0
arc_duration = 60

# =========================
# SHAKE ÉCRAN
# =========================
screen_shake_frames = 0
screen_shake_intensity = 0

# =========================
# SCORE / TEMPS
# =========================
score = 0
bonnes_reponses = 0
erreurs = 0
objectif = 12
temps_max = 35
temps_restant = float(temps_max)
game_over = False
victoire = False

feedback_timer = 0
feedback_text = ""
feedback_color = BLANC
flash_timer = 0

# =========================
# FONCTIONS
# =========================
def nouveau_dechet():
    global dechet_actuel, dechet_x, dechet_y, dechet_vx, dechet_vy
    global arc_t, arc_start_x, arc_start_y, float_phase

    dechet_actuel = random.choice(dechets_data)
    float_phase = random.uniform(0, math.pi * 2)

    arc_start_x = -40.0 if random.random() < 0.5 else float(LARGEUR + 40)
    arc_start_y = random.uniform(60, 160)
    arc_t = 0.0

    dechet_x = arc_start_x
    dechet_y = arc_start_y
    dechet_vx = 0.0
    dechet_vy = 0.0

def reset_game():
    global score, bonnes_reponses, erreurs, temps_restant
    global game_over, victoire, feedback_timer, feedback_text
    global feedback_color, flash_timer, screen_shake_frames, particles

    score = 0
    bonnes_reponses = 0
    erreurs = 0
    temps_restant = float(temps_max)
    game_over = False
    victoire = False
    feedback_timer = 0
    feedback_text = ""
    feedback_color = BLANC
    flash_timer = 0
    screen_shake_frames = 0
    particles = []

    for k in bin_anim:
        bin_anim[k] = {"open": 0.0, "shake": 0.0, "shake_dir": 1}

    nouveau_dechet()

def get_item_color(item_type):
    return BIN_COLORS[item_type]

def draw_bin(key, rect, color, label, emoji):
    anim = bin_anim[key]
    shake = anim["shake"]
    ox = int(shake * anim["shake_dir"])

    x = rect.x + ox
    y = rect.y
    w = rect.w
    h = rect.h

    dark = (
        max(color[0] - 45, 0),
        max(color[1] - 45, 0),
        max(color[2] - 45, 0)
    )

    # ombre
    shadow = pygame.Surface((w + 30, h + 35), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 55), (10, h + 8, w, 18))
    screen.blit(shadow, (x - 10, y - 5))

    # corps
    body_top_w = int(w * 0.82)
    body_x_top = x + (w - body_top_w) // 2
    body_y_top = y + 24
    body_y_bottom = y + h - 18

    body_points = [
        (body_x_top, body_y_top),
        (body_x_top + body_top_w, body_y_top),
        (x + w, body_y_bottom),
        (x, body_y_bottom)
    ]

    pygame.draw.polygon(screen, color, body_points)
    pygame.draw.polygon(screen, dark, body_points, 3)

    # couvercle
    open_offset = int(anim["open"] * 18)
    lid_w = int(w * 0.92)
    lid_h = 18
    lid_x = x + (w - lid_w) // 2
    lid_y = y + 6 - open_offset

    pygame.draw.rect(screen, dark, (lid_x, lid_y, lid_w, lid_h), border_radius=8)
    pygame.draw.rect(screen, (35, 40, 50), (lid_x, lid_y, lid_w, lid_h), 2, border_radius=8)
    pygame.draw.rect(screen, (220, 220, 225), (x + w // 2 - 12, lid_y + 4, 24, 5), border_radius=3)

    # roues
    wheel_y = y + h - 10
    pygame.draw.circle(screen, (40, 40, 45), (x + 28, wheel_y), 10)
    pygame.draw.circle(screen, (40, 40, 45), (x + w - 28, wheel_y), 10)

    txt_emoji = mid_font.render(emoji, True, BLANC)
    txt_label = small_font.render(label, True, BLANC)
    screen.blit(txt_emoji, (x + w // 2 - txt_emoji.get_width() // 2, y + 52))
    screen.blit(txt_label, (x + w // 2 - txt_label.get_width() // 2, y + 82))

def draw_ui_panel():
    pygame.draw.rect(screen, (120, 130, 150), (24, 24, 270, 180), border_radius=16)
    ui_panel = pygame.Surface((270, 180), pygame.SRCALPHA)
    ui_panel.fill((255, 255, 255, 225))
    screen.blit(ui_panel, (20, 20))
    pygame.draw.rect(screen, BORDURE, (20, 20, 270, 180), 3, border_radius=16)
    pygame.draw.line(screen, BLANC, (35, 35), (275, 35), 2)

    screen.blit(font.render(f"Score : {score}/{objectif}", True, NOIR), (38, 35))
    screen.blit(font.render(f"Bons tris : {bonnes_reponses}", True, NOIR), (38, 72))
    screen.blit(font.render(f"Erreurs : {erreurs}", True, NOIR), (38, 109))
    screen.blit(font.render(f"Temps : {int(temps_restant)}", True, NOIR), (38, 146))

def draw_sorting_zone():
    pygame.draw.rect(screen, (150, 160, 180), (116, 536, 860, 150), border_radius=26)
    pygame.draw.rect(screen, (235, 240, 248), (110, 530, 860, 150), border_radius=26)
    pygame.draw.rect(screen, (180, 190, 210), (110, 530, 860, 150), 3, border_radius=26)
    pygame.draw.rect(screen, (248, 250, 255), (130, 545, 820, 12), border_radius=12)

def draw_current_item():
    global float_phase
    float_offset = math.sin(float_phase) * 4
    float_phase += 0.08

    # couleur du rond selon la poubelle
    item_color = get_item_color(dechet_actuel["type"])

    # ombre
    ombre = pygame.Surface((64, 20), pygame.SRCALPHA)
    pygame.draw.ellipse(ombre, (0, 0, 0, 95), (0, 0, 64, 20))
    screen.blit(ombre, (int(dechet_x) + 6, int(dechet_y) + 66))

    # rond coloré derrière l’objet
    bg_circle = pygame.Surface((92, 92), pygame.SRCALPHA)
    pygame.draw.circle(bg_circle, (*item_color, 200), (46, 46), 40)
    pygame.draw.circle(bg_circle, (255, 255, 255, 170), (46, 46), 40, 2)
    screen.blit(bg_circle, (int(dechet_x) - 9, int(dechet_y) - 8 + int(float_offset)))

    # halo léger
    halo = pygame.Surface((104, 104), pygame.SRCALPHA)
    pygame.draw.circle(halo, (255, 255, 255, 28), (52, 52), 44)
    screen.blit(halo, (int(dechet_x) - 15, int(dechet_y) - 14 + int(float_offset)))

    # image
    img = dechet_actuel["image"]
    img_rect = img.get_rect(center=(int(dechet_x) + 37, int(dechet_y) + 37 + int(float_offset)))
    screen.blit(img, img_rect)

def draw_feedback():
    if feedback_timer > 0:
        txt = big_font.render(feedback_text, True, feedback_color)
        x = LARGEUR // 2 - txt.get_width() // 2
        y = 120

        outline = big_font.render(feedback_text, True, BLANC)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            screen.blit(outline, (x + dx, y + dy))
        screen.blit(txt, (x, y))

def draw_end_panel():
    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(260, 185, 560, 250)
    pygame.draw.rect(screen, (245, 248, 250), panel, border_radius=20)
    pygame.draw.rect(screen, BORDURE, panel, 4, border_radius=20)

    titre = "MISSION REUSSIE !" if victoire else "MISSION ECHOUEE !"
    couleur_titre = VERT if victoire else ROUGE

    screen.blit(big_font.render(titre, True, couleur_titre),
                (panel.centerx - big_font.size(titre)[0] // 2, panel.y + 32))

    for i, line in enumerate([
        f"Score final : {score}",
        f"Bons tris : {bonnes_reponses}",
        f"Erreurs : {erreurs}",
    ]):
        t = font.render(line, True, NOIR)
        screen.blit(t, (panel.centerx - t.get_width() // 2, panel.y + 102 + i * 36))

    hint = small_font.render("Appuie sur R pour recommencer", True, NOIR)
    screen.blit(hint, (panel.centerx - hint.get_width() // 2, panel.y + 214))

def get_bin_hit(item_rect):
    """Retourne la poubelle touchée par le centre bas du déchet."""
    test_point = (item_rect.centerx, item_rect.bottom - 4)
    for nom_bin, rect_bin in bins.items():
        if rect_bin.collidepoint(test_point):
            return nom_bin
    return None

# =========================
# INIT
# =========================
nouveau_dechet()

# =========================
# BOUCLE PRINCIPALE
# =========================
running = True
while running:
    dt_ms = clock.tick(FPS)
    dt = dt_ms / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (game_over or victoire) and event.key == pygame.K_r:
                reset_game()

    keys = pygame.key.get_pressed()

    # UPDATE
    if not game_over and not victoire:
        temps_restant -= dt
        if temps_restant <= 0:
            temps_restant = 0
            game_over = True

        # arrivée en arc
        if arc_t < 1.0:
            arc_t += 1.0 / arc_duration
            arc_t = min(arc_t, 1.0)

            t = arc_t
            p0x, p0y = arc_start_x, arc_start_y
            p1x, p1y = LARGEUR / 2, -60.0
            p2x, p2y = LARGEUR / 2 - 37, 60.0

            dechet_x = (1 - t) ** 2 * p0x + 2 * (1 - t) * t * p1x + t ** 2 * p2x
            dechet_y = (1 - t) ** 2 * p0y + 2 * (1 - t) * t * p1y + t ** 2 * p2y
            dechet_vy = 0.0

        else:
            if keys[pygame.K_LEFT]:
                dechet_x -= 7
            if keys[pygame.K_RIGHT]:
                dechet_x += 7

            dechet_x = max(0, min(dechet_x, LARGEUR - 74))

            dechet_vy += 0.18
            dechet_y += dechet_vy

            rect_dechet = pygame.Rect(int(dechet_x), int(dechet_y), 74, 74)

            if rect_dechet.bottom >= bin_y + 10:
                poubelle_trouvee = get_bin_hit(rect_dechet)

                if poubelle_trouvee == dechet_actuel["type"]:
                    score += 1
                    bonnes_reponses += 1
                    feedback_text = "Bien trié !"
                    feedback_color = VERT
                    flash_timer = 8

                    cx = bins[poubelle_trouvee].centerx
                    cy = bins[poubelle_trouvee].y
                    spawn_particles(cx, cy, BIN_COLORS[poubelle_trouvee], count=55)
                    bin_anim[poubelle_trouvee]["open"] = 1.0

                    feedback_timer = 45
                    nouveau_dechet()

                elif poubelle_trouvee is not None:
                    erreurs += 1
                    feedback_text = "Mauvais tri !"
                    feedback_color = ROUGE
                    flash_timer = 8

                    bin_anim[poubelle_trouvee]["shake"] = 12.0
                    bin_anim[poubelle_trouvee]["shake_dir"] = 1

                    screen_shake_frames = 18
                    screen_shake_intensity = 7

                    feedback_timer = 45
                    nouveau_dechet()

                elif rect_dechet.bottom >= HAUTEUR - 20:
                    # tombé au sol sans poubelle
                    erreurs += 1
                    feedback_text = "Raté !"
                    feedback_color = ROUGE
                    flash_timer = 8
                    feedback_timer = 35
                    nouveau_dechet()

        if score >= objectif:
            victoire = True

    # animation poubelles
    for k in bin_anim:
        a = bin_anim[k]
        if a["open"] > 0:
            a["open"] = max(0.0, a["open"] - 0.05)
        if a["shake"] > 0:
            a["shake"] = max(0.0, a["shake"] - 0.8)
            a["shake_dir"] = -a["shake_dir"]

    # particules
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)

    if feedback_timer > 0:
        feedback_timer -= 1

    shake_ox, shake_oy = 0, 0
    if screen_shake_frames > 0:
        screen_shake_frames -= 1
        shake_ox = random.randint(-screen_shake_intensity, screen_shake_intensity)
        shake_oy = random.randint(-screen_shake_intensity, screen_shake_intensity)

    # AFFICHAGE
    canvas = pygame.Surface((LARGEUR, HAUTEUR))
    canvas.blit(background, (0, 0))

    old_screen = screen
    screen = canvas

    draw_sorting_zone()
    draw_ui_panel()
    draw_bin("recyclage", bins["recyclage"], BLEU, "RECYCLAGE", "♻")
    draw_bin("normal", bins["normal"], GRIS, "NORMAL", "🗑")
    draw_bin("toxique", bins["toxique"], ROUGE, "TOXIQUE", "☣")

    if dechet_actuel is not None and not game_over and not victoire:
        draw_current_item()

    for p in particles:
        p.draw(canvas)

    draw_feedback()

    if victoire or game_over:
        draw_end_panel()

    if flash_timer > 0:
        flash = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
        if feedback_color == VERT:
            flash.fill((120, 255, 120, 55))
        else:
            flash.fill((255, 120, 120, 55))
        canvas.blit(flash, (0, 0))
        flash_timer -= 1

    screen = old_screen
    old_screen.fill(NOIR)
    old_screen.blit(canvas, (shake_ox, shake_oy))

    pygame.display.flip()

pygame.quit()
sys.exit()