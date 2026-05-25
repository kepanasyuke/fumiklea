import pygame
import sys
import math
import random
import traceback

# ---------- Простая и надёжная инициализация ----------
pygame.init()
try:
    pygame.mixer.init()
except:
    pass

try:
    screen = pygame.display.set_mode((800, 600))
except pygame.error as e:
    print(f"Не могу создать окно: {e}")
    print("Попробуйте запустить веб-версию: make run-web")
    sys.exit(1)

pygame.display.set_caption("HARVARD MARK II - ULTIMATE CRT MONITOR")
clock = pygame.time.Clock()
WIDTH, HEIGHT = 800, 600

# ---------- Базовые ретро-цвета ----------
BASE_BG = (5, 22, 5)
BASE_GREEN = (50, 230, 90)
BASE_WHITE = (210, 255, 210)
BASE_RED = (255, 60, 60)

# ---------- Шрифты ----------
font_large = pygame.font.SysFont("Courier", 32, bold=True)
font_med = pygame.font.SysFont("Courier", 22, bold=True)
font_small = pygame.font.SysFont("Courier", 16)

# ---------- Эффект послесвечения люминофора (сильно ослаблен) ----------
trail_surface = pygame.Surface((WIDTH, HEIGHT))
trail_surface.set_alpha(220)          # было 45 – теперь почти не видно следа
trail_surface.fill(BASE_BG)

# ---------- Выпуклая виньетка экрана ----------
vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for r in range(WIDTH, 0, -4):
    alpha = int(max(0, min(230, (r - WIDTH // 2) * 0.7)))
    pygame.draw.circle(vignette, (0, 5, 0, alpha), (WIDTH // 2, HEIGHT // 2), r, 4)
vignette_base = vignette.copy()

# ---------- Ресурсы для CRT-эффектов ----------
phosphor_spots = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for _ in range(8):
    px = random.randint(50, WIDTH - 50)
    py = random.randint(50, HEIGHT - 50)
    radius = random.randint(40, 120)
    alpha = random.randint(20, 60)
    pygame.draw.circle(phosphor_spots, (0, random.randint(15, 30), 0, alpha), (px, py), radius)

paper_texture = pygame.Surface((640, 470))
paper_texture.fill((215, 205, 160))
for _ in range(500):
    x = random.randint(0, 639)
    y = random.randint(0, 469)
    paper_texture.set_at((x, y), (random.randint(200, 235), random.randint(190, 220), random.randint(140, 180)))
for _ in range(3):
    cx = random.randint(100, 540)
    cy = random.randint(80, 390)
    pygame.draw.circle(paper_texture, (random.randint(80, 120), random.randint(60, 90), random.randint(30, 60)),
                       (cx, cy), random.randint(15, 30))

# ---------- Игровые переменные ----------
state = None
frame_counter = 0
moth_x, moth_y = 400, 290
moth_speed_x = random.uniform(-1.5, 1.5)
moth_speed_y = random.uniform(-1.5, 1.5)
moth_caught = False
game_completed = False
moth_rect = pygame.Rect(moth_x, moth_y, 40, 30)

# ---------- Безопасная работа со звуком ----------
SOUND_AVAILABLE = pygame.mixer.get_init() is not None

def create_sound(freq, duration, volume=0.08):
    if not SOUND_AVAILABLE:
        return None
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        value = 127 if math.sin(2.0 * math.pi * freq * t) > 0 else -127
        buf.append(int(value + 128))
    sound = pygame.mixer.Sound(buffer=buf)
    sound.set_volume(volume)
    return sound

sound_intro1 = create_sound(440, 0.08)
sound_intro2 = create_sound(880, 0.08)
sound_catch = create_sound(587, 0.12)
sound_relay_click = create_sound(800, 0.03)
sound_log_print = [create_sound(650 + i * 30, 0.03) for i in range(6)]

# ---------- Функции рисования и эффектов ----------
def get_jitter(amount=0):          # по умолчанию 0 – без дрожания (текст не прыгает)
    return random.choice([-amount, 0, amount])

def draw_crt_scanlines(screen, dynamic=True):
    for y in range(0, HEIGHT, 4):
        if dynamic:
            brightness = 80 + int(40 * math.sin(y / HEIGHT * math.pi))
            color = (0, brightness // 5, 0)
        else:
            color = (0, 8, 0)
        pygame.draw.line(screen, color, (0, y), (WIDTH, y), 2)

def draw_vector_text(text, font, color, x, y, center=False):
    """Текст без дрожания (jitter = 0)."""
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

# ---------- Кэширование текста и glitch-эффект ----------
text_cache = {}

def get_cached_text(text, font, color):
    key = (text, id(font), color)
    if key not in text_cache:
        text_cache[key] = font.render(text, True, color)
    return text_cache[key]

def draw_cached_text(text, font, color, x, y, center=False):
    """Текст без дрожания и с кэшированием."""
    surf = get_cached_text(text, font, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

def glitch_text(text, prob=0.03):
    chars = list(text)
    for i in range(len(chars)):
        if random.random() < prob:
            chars[i] = random.choice(['#', '@', '&', '!', ' ', '*'])
    return ''.join(chars)

def draw_glitch_text(text, font, color, x, y, center=False, prob=0.03):
    glitched = glitch_text(text, prob)
    surf = font.render(glitched, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

# ---------- Кэш мерцания ----------
FLICKER_CACHE = [random.randint(-20, 20) for _ in range(100)]

# ---------- Классы состояний ----------
class IntroState:
    def handle_event(self, event):
        global state, frame_counter
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            state = RelayViewState()
            if sound_intro1:
                sound_intro1.play()
            if sound_intro2:
                sound_intro2.play()
            frame_counter = 0

    def cursor_visible(self):
        return True

    def draw(self):
        # Полная очистка экрана – текст не накладывается
        screen.fill(BASE_BG)
        draw_cached_text("=== HARVARD UNIVERSITY ===", font_large,
                         (50, 230, 90), WIDTH//2, 150, center=True)
        draw_cached_text("MARK II VECTOR MONITOR SYSTEM", font_med,
                         (50, 230, 90), WIDTH//2, 220, center=True)
        if frame_counter % 50 < 25:
            draw_glitch_text("TAP TO INITIALIZE DEBUGGING", font_med,
                             CRT_WHITE, WIDTH//2, 380, center=True, prob=0.04)
        draw_cached_text("SYS_REC_1947_09_09", font_small,
                         (50, 230, 90), WIDTH//2, 500, center=True)
        # Лёгкие CRT-эффекты поверх
        screen.blit(phosphor_spots, (0, 0))
        draw_crt_scanlines(screen, dynamic=True)
        screen.blit(vignette_base, (0, 0))

class RelayViewState:
    def __init__(self):
        self.dim_overlay = pygame.Surface((WIDTH, HEIGHT))
        self.dim_overlay.fill((0, 0, 0))

    def handle_event(self, event):
        global moth_caught
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            if moth_rect.collidepoint(mx, my) and not moth_caught:
                moth_caught = True
                if sound_catch:
                    sound_catch.play()

    def cursor_visible(self):
        return False

    def draw(self):
        global state, game_completed, frame_counter, moth_x, moth_y
        global CRT_GREEN, CRT_WHITE

        flicker_alpha = int(15 + 10 * math.sin(frame_counter * 0.05))
        self.dim_overlay.set_alpha(flicker_alpha)

        # --- Реле (с дрожанием для линий) ---
        jx, jy = get_jitter(1), get_jitter(1)
        big_rect = pygame.Rect(200 + jx, 140 + jy, 400, 300)
        pygame.draw.rect(screen, CRT_GREEN, big_rect, 4)
        pygame.draw.line(screen, CRT_GREEN, (200 + jx, 295 + jy), (365 + jx, 295 + jy), 6)
        pygame.draw.line(screen, CRT_GREEN, (600 + jx, 295 + jy), (435 + jx, 295 + jy), 6)

        # --- Зона сброса (текст без дрожания) ---
        log_zone = pygame.Rect(240, 480, 320, 70)
        log_color = CRT_GREEN if not moth_caught else CRT_WHITE
        pygame.draw.rect(screen, log_color, log_zone, 2)
        draw_vector_text("[ COOPER LOG ENTRY AREA ]", font_small, log_color, WIDTH//2, 515, center=True)

        # --- Логика поимки ---
        if moth_caught:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            moth_rect.center = (mouse_x, mouse_y)
            moth_x, moth_y = moth_rect.topleft
            if log_zone.colliderect(moth_rect):
                state = LogViewState()
                frame_counter = 0
                game_completed = True
                if sound_relay_click:
                    sound_relay_click.play()

        # --- Моль (с дрожанием и вибрацией) ---
        if not moth_caught:
            offset_x = int(math.sin(frame_counter * 0.7) * 4)
            offset_y = int(math.cos(frame_counter * 0.5) * 4)
        else:
            offset_x = offset_y = 0
        moth_draw_x = moth_rect.x + offset_x + get_jitter(1)
        moth_draw_y = moth_rect.y + offset_y + get_jitter(1)
        moth_clr = CRT_GREEN if not moth_caught else CRT_WHITE
        pygame.draw.ellipse(screen, moth_clr, (moth_draw_x, moth_draw_y, moth_rect.width, moth_rect.height))
        if not moth_caught:
            wing_w = int(math.sin(frame_counter * 0.9) * 12)
        else:
            wing_w = 0
        pygame.draw.line(screen, moth_clr, (moth_draw_x + 20, moth_draw_y + 15),
                         (moth_draw_x + 5, moth_draw_y - 12 + wing_w), 3)
        pygame.draw.line(screen, moth_clr, (moth_draw_x + 20, moth_draw_y + 15),
                         (moth_draw_x + 5, moth_draw_y + 42 - wing_w), 3)

        # --- Пинцет (с дрожанием) ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        p_clr = CRT_WHITE if moth_caught else CRT_GREEN
        gap = 6 if moth_caught else 18
        pygame.draw.line(screen, p_clr, (mouse_x - 30, mouse_y - 35), (mouse_x, mouse_y - gap//2), 3)
        pygame.draw.line(screen, p_clr, (mouse_x - 30, mouse_y + 35), (mouse_x, mouse_y + gap//2), 3)
        pygame.draw.line(screen, p_clr, (mouse_x - 55, mouse_y), (mouse_x - 30, mouse_y - 35), 2)
        pygame.draw.line(screen, p_clr, (mouse_x - 55, mouse_y), (mouse_x - 30, mouse_y + 35), 2)

        # --- CRT-эффекты ---
        screen.blit(phosphor_spots, (0, 0))
        if random.random() < 0.3:
            scratch_x = random.randint(0, WIDTH)
            scratch_y = random.randint(0, HEIGHT)
            pygame.draw.line(screen, (255, 255, 255), (scratch_x, scratch_y),
                             (scratch_x + random.randint(-15, 15), scratch_y + random.randint(-1, 1)), 1)
        screen.blit(self.dim_overlay, (0, 0))

        # Динамическая виньетка (один раз)
        scale_factor = 1.0 + 0.005 * math.sin(frame_counter * 0.02)
        scaled_w = int(WIDTH * scale_factor)
        scaled_h = int(HEIGHT * scale_factor)
        vignette_dynamic = pygame.transform.scale(vignette_base, (scaled_w, scaled_h))
        vignette_rect = vignette_dynamic.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(vignette_dynamic, vignette_rect)
        draw_crt_scanlines(screen, dynamic=True)

class LogViewState:
    def handle_event(self, event):
        global state, moth_caught, game_completed, frame_counter
        global moth_x, moth_y, moth_speed_x, moth_speed_y
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_completed:
                state = IntroState()
                moth_caught = False
                game_completed = False
                moth_x, moth_y = 380, 280
                moth_speed_x = random.uniform(-1.5, 1.5)
                moth_speed_y = random.uniform(-1.5, 1.5)
                moth_rect.topleft = (moth_x, moth_y)
                frame_counter = 0

    def cursor_visible(self):
        return True

    def draw(self):
        # Очищаем фон (чёрный, как у ЭЛТ, но под бумагой)
        screen.fill(BASE_BG)

        # Рисуем бумагу
        jx, jy = 0, 0  # без дрожания
        screen.blit(paper_texture, (80 + jx, 50 + jy))
        pygame.draw.rect(screen, (80, 100, 60), (80 + jx, 50 + jy, 640, 470), 3)  # тёмная рамка

        # Заголовок – ярко‑зелёный
        draw_vector_text("LOGBOOK: SEPTEMBER 9, 1947", font_large, (120, 220, 100), WIDTH//2, 95, center=True)

        # Сканирующая строка (очень слабая, почти незаметная)
        scan_y = (frame_counter * 3) % 470
        pygame.draw.line(screen, (50, 80, 50, 40), (80, 50 + scan_y), (720, 50 + scan_y), 1)

        lines = [
            "1100  Started computer. Tasks loaded successfully.",
            "1545  Relay #70 Panel F stuck open.",
            "      Investigation showed an insect blocking contact.",
            "      Removed moth from relay with brass tweezers.",
            " ",
            "\"First actual case of bug being found.\""
        ]

        # Полупрозрачная подложка для текста (чуть светлее фона)
        text_bg = pygame.Surface((600, 350), pygame.SRCALPHA)
        text_bg.fill((180, 160, 120, 64))  # светло‑коричневый с прозрачностью
        screen.blit(text_bg, (100, 140))

        # Основной текст – тёмно‑зелёный, почти чёрный
        dark_green = (20, 50, 20)
        for idx, line in enumerate(lines):
            if frame_counter > idx * 25:
                typed_len = min(len(line), max(0, frame_counter - idx * 25 - 10))
                displayed = line[:typed_len]
                # Цвет: последняя строка (историческая) – белый, остальные – тёмно‑зелёный
                if idx == 5:
                    color = (240, 240, 200) if typed_len == len(line) else (120, 120, 80)
                else:
                    color = dark_green
                draw_vector_text(displayed, font_small, color, 110, 160 + idx * 35)
                if typed_len == len(line) and frame_counter == idx * 25 + len(line) + 10:
                    if idx < len(sound_log_print) and sound_log_print[idx]:
                        sound_log_print[idx].play()

        # Вклеенный трофей (моль) – яркий
        if frame_counter > 200:
            cx, cy = 400, 430
            progress = min(1.0, (frame_counter - 200) / 60)
            pygame.draw.rect(screen, (80, 80, 50), (cx - 50, cy - 20, 100, 45), 1)
            if progress > 0.5:
                pygame.draw.ellipse(screen, (50, 150, 50), (cx - 15, cy - 6, 30, 13))
                pygame.draw.line(screen, (50, 150, 50), (cx, cy), (cx - 8, cy - 12), 2)
                pygame.draw.line(screen, (50, 150, 50), (cx, cy), (cx - 8, cy + 12), 2)
                pygame.draw.line(screen, (50, 150, 50), (cx - 10, cy - 6), (cx - 20, cy - 14), 1)
                pygame.draw.line(screen, (50, 150, 50), (cx + 10, cy - 6), (cx + 20, cy - 14), 1)
            if frame_counter % 50 < 25:
                draw_vector_text("HISTORY LOGGED. PRESS ANY KEY TO RESTART.", font_med, (220, 220, 150), WIDTH//2, 555, center=True)

        # Лёгкие CRT-линии (почти прозрачные, чтобы не портить читаемость)
        for y in range(0, HEIGHT, 6):
            pygame.draw.line(screen, (0, 20, 0, 30), (0, y), (WIDTH, y), 1)

        # Чтобы вернуть шум
        screen.blit(vignette_base, (0, 0))   # закомментировано

# ---------- Стартовое состояние ----------
state = IntroState()

# ---------- Главный цикл ----------
running = True
try:
    while running:
        frame_counter += 1

        # Шлейф – теперь почти незаметен, старые кадры быстро исчезают
        screen.blit(trail_surface, (0, 0))

        # Мерцание цветов
        flicker = FLICKER_CACHE[frame_counter % len(FLICKER_CACHE)]
        CRT_GREEN = (max(20, min(255, BASE_GREEN[0] + flicker)),
                     max(50, min(255, BASE_GREEN[1] + flicker)),
                     max(30, min(255, BASE_GREEN[2] + flicker)))
        CRT_WHITE = (max(150, min(255, BASE_WHITE[0] + flicker)),
                     max(150, min(255, BASE_WHITE[1] + flicker)),
                     max(150, min(255, BASE_WHITE[2] + flicker)))
        CRT_RED = (max(150, min(255, BASE_RED[0] + flicker)),
                   max(20, min(255, BASE_RED[1] + flicker)),
                   max(20, min(255, BASE_RED[2] + flicker)))

        # Движение моли (только если не поймана)
        if isinstance(state, RelayViewState) and not moth_caught:
            moth_x += moth_speed_x
            moth_y += moth_speed_y
            left_bound = 200
            right_bound = 600 - moth_rect.width
            top_bound = 150
            bottom_bound = 400 - moth_rect.height
            if moth_x < left_bound:
                moth_x = left_bound
                moth_speed_x *= -1
            if moth_x > right_bound:
                moth_x = right_bound
                moth_speed_x *= -1
            if moth_y < top_bound:
                moth_y = top_bound
                moth_speed_y *= -1
            if moth_y > bottom_bound:
                moth_y = bottom_bound
                moth_speed_y *= -1
            if random.random() < 0.02:
                moth_speed_x += random.uniform(-0.3, 0.3)
                moth_speed_y += random.uniform(-0.3, 0.3)
                speed = math.hypot(moth_speed_x, moth_speed_y)
                if speed > 2.0:
                    moth_speed_x = moth_speed_x / speed * 2.0
                    moth_speed_y = moth_speed_y / speed * 2.0
            moth_rect.topleft = (moth_x, moth_y)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.mouse.set_visible(state.cursor_visible())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            state.handle_event(event)

        state.draw()

        # Обновляем шлейф (сохраняем текущий экран для следующего кадра)
        trail_surface.blit(screen, (0, 0))

        pygame.display.flip()
        clock.tick(60)

except Exception as e:
    print("Произошла ошибка:")
    traceback.print_exc()
finally:
    pygame.quit()
    sys.exit()