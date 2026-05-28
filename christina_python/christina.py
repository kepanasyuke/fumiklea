import numpy as np
import json
import http.server
import socketserver
import threading
import webbrowser
import time

# --- ГЛОБАЛЬНЫЕ КОНСТАНТЫ МАТРИЦЫ ---
WIDTH, HEIGHT = 32, 32
TOTAL_FRAMES = 50
TOTAL_SCENES = 19

# ------------------------- ЦВЕТА -------------------------
# --- ПАЛИТРА ЦВЕТОВ КРИСТИНЫ (СИНТАКСИС ИСПРАВЛЕН) ---
# ------------------------- ЦВЕТА -------------------------
# --- ПАЛИТРА ЦВЕТОВ КРИСТИНЫ (СИНТАКСИС ИСПРАВЛЕН) ---
C = {
    'BLK': [0, 0, 0],         # Глухая ночная тьма
    'WHT': [255, 255, 255],   # Фары / Ядро взрыва / Блики
    'RED': [220, 10, 20],     # Кузов Кристины (Плимут Fury)
    'B_RED': [150, 0, 10],    # Кроваво-красная выштамповка / Текст
    'CHRM': [130, 140, 150],  # Хром / Асфальт
    'BLU': [0, 85, 255],      # Лобовое стекло / Неоновые ноты
    'YLW': [255, 215, 0],     # Золотые ноты / Стрелка радиолы
    'ORG': [255, 100, 0],     # Искры / Огонь
    'GRN': [0, 220, 80],      # Зелёная подсветка шкал
    'BRN': [50, 25, 10],      # Глубокое лакированное дерево (Махагони)
    'L_BRN': [100, 60, 30],   # Блик светлого ореха (Волокна дерева)
    'B_YLW': [220, 180, 100], # Выцветшая лампа бакелитовой шкалы
    'PNK': [230, 0, 120],      # Розовый индикатор (ИСПРАВЛЕНО — ЗАПЯТАЯ ВЫШЕ НА МЕСТЕ)
    'C_VINTAGE_RED': = [140, 5, 20],  # Глубокий вишневый кузов Кристины
    'C_DARK_SALON': = [60, 5, 10]    # Мрачный бордовый интерьер салона

}

# --- СОСТОЯНИЕ ИГРОКА (СТАТУС-БАРЫ В СТРОКАХ 24-32) ---
player_stats = {
    "rem": 100,  # Ремонт кузова Кристины (%)
    "ras": 0,    # Рассудок водителя (Арни) (%)
    "top": 80    # Топливо в баке (%)
}

def render_status_bars(frame):
    """
    Строго отрисовывает нижнюю часть матрицы (строки 24-32),
    чтобы параметры были видны прямо на светодиодном табло, 
    не мешая основной анимации сцен сверху.
    """
    # Очищаем нижнюю зону (строки 24-31) в чёрный цвет
    frame[24:32, :] = C['BLK']
    
    # Отрисовка полосы РЕМОНТА (Строка 25, x: 2..12)
    rem_pixels = int((player_stats["rem"] / 100) * 10)
    frame[25, 2:2+rem_pixels] = C['RED']
    
    # Отрисовка полосы РАССУДКА (Строка 27, x: 2..12)
    ras_pixels = int((player_stats["ras"] / 100) * 10)
    frame[27, 2:2+ras_pixels] = C['GRN']
    
    # Отрисовка полосы ТОПЛИВА (Строка 29, x: 2..12)
    top_pixels = int((player_stats["top"] / 100) * 10)
    frame[29, 2:2+top_pixels] = C['YLW']


def generate_scenes():
    all_scenes = []
    for scene_idx in range(TOTAL_SCENES):
        scene_frames = []
        for f_idx in range(TOTAL_FRAMES):
            # Создаем пустой черный кадр
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            t = f_idx / TOTAL_FRAMES


# ------------------------- ГЕНЕРАЦИЯ СЦЕН (С ИСПРАВЛЕНИЕМ ГРАНИЦ) -------------------------
def generate_scenes():
    all_scenes = []
    for scene_idx in range(TOTAL_SCENES):
        scene_frames = []
        for f_idx in range(TOTAL_FRAMES):
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            t = f_idx / TOTAL_FRAMES

            # --- СЦЕНА 0: Базовая (Кристина в огне — ПОМЯТАЯ ФОРМА №1) ---
            if scene_idx == 0:
                # 1. Зажигаем зловещие фары фар (плавное разгорание, затем мерцание)
                bright = 255 if f_idx >= 15 else int((f_idx / 15) * 255)
                # Фары из первой модели (строка 14, колонки 5:8 и 24:27)
                frame[14:16, 5:8] = frame[14:16, 24:27] = [bright, int(bright * 0.8), 0]
                
                # 2. Отрисовка кузова из вашей любимой первой версии
                frame[12:14, 4:28] = C['RED']       # Темно-красный капот
                frame[13, 11:21] = C['B_RED']       # Выштамповка на капорте
                frame[14:16, 8:24] = C['BLK']       # Ниша под решетку (между фарами)
                frame[15, 8:24] = C['CHRM']         # Хромированная решетка

                # 3. Синхронизированный СМЯТЫЙ бампер (вмятина всегда зафиксирована)
                # Базовый бампер шел по строке 16-17. Сминаем центр (от 11 до 21 пикселя) вверх на 2 строки.
                for x in range(4, 28):
                    if 11 <= x <= 21:
                        pixel_y = 14  # Вмятина ушла вверх, перекрывая решетку
                    else:
                        pixel_y = 16  # Целая часть бампера по бокам
                    
                    frame[pixel_y, x] = C['CHRM']
                    if pixel_y + 1 < HEIGHT:
                        frame[pixel_y + 1, x] = C['CHRM']

                # 4. Анимация яростного пиксельного пламени снизу
                if f_idx > 10:
                    for x in range(WIDTH):
                        h = int((np.sin(x + f_idx) + 1.2) * 5 * ((f_idx - 10) / 40))
                        for y in range(h):
                            if HEIGHT - 1 - y >= 0:
                                frame[HEIGHT - 1 - y, x] = C['YLW'] if y < h - 3 else C['ORG']

            # --- СЦЕНА 1: Регенерация бампера (Восстановление к ФОРМЕ №1 — "Show Me") ---
            elif scene_idx == 1:
                # 1. Постоянная основа кузова из первой версии
                frame[12:14, 4:28] = C['RED']
                frame[13, 11:21] = C['B_RED']
                frame[14:16, 8:24] = C['BLK']
                frame[15, 8:24] = C['CHRM']
                
                # Стабильно горящие фары
                frame[14:16, 5:8] = [200, 160, 0]
                frame[14:16, 24:27] = [200, 160, 0]

                # 2. Динамическое выпрямление бампера
                # t меняется от 0.0 до 1.0. Сдвигаем центральную вмятину из y=14 обратно вниз на y=16.
                # К 35-му кадру бампер должен стать полностью ровным.
                for x in range(4, 28):
                    if t < 0.70 and 11 <= x <= 21:
                        # Плавный сдвиг центральной части вниз с течением времени
                        current_offset = int((1.0 - (t / 0.70)) * 2)
                        pixel_y = 16 - current_offset
                    else:
                        pixel_y = 16  # Идеальное положение из первой модели

                    frame[pixel_y, x] = C['CHRM']
                    if pixel_y + 1 < HEIGHT:
                        frame[pixel_y + 1, x] = C['CHRM']

                # 3. Эффект финального глянцевого блика новизны (с 38 по 50 кадр)
                if f_idx >= 38:
                    glint_progress = (f_idx - 38) / 12
                    glint_x = int(4 + glint_progress * 22)
                    for k in range(2):
                        if 4 <= glint_x + k <= 27:
                            frame[16:18, glint_x + k] = C['WHT']

            # --- СЦЕНА 2: Спидометр (Взгляд из салона: Стрелка ложится за 120) ---
            elif scene_idx == 2:
                # 1. Окружающая темнота салона и зеленая неоновая подсветка торпеды
                frame[12:24, 3:29] = [20, 20, 25]  # Корпус приборной панели
                
                # 2. Отрисовка винтажной круглой шкалы спидометра (Белый/Серебряный полукруг)
                for a in range(5, 27):
                    # Рисуем дугу спидометра (параболическая арка приборной панели)
                    y = 22 - int(np.sin((a - 5) / 21 * np.pi) * 11)
                    if 0 <= y < HEIGHT:
                        frame[y, a] = C['WHT']
                        # Зеленое неоновое свечение под шкалой (как в Plymouth Fury 58-го)
                        if y + 1 < HEIGHT:
                            frame[y + 1, a] = C['GRN']

                # Добавляем пиксели делений скорости (ограничители на шкале)
                frame[22, 5] = frame[11, 16] = frame[22, 26] = C['YLW']

                # 3. Расчет бешеного движения стрелки (ложится слева направо до упора)
                # t идет от 0.0 до 1.0. Угол поворота стрелки: от 180 до 0 градусов
                angle = np.pi - (t * np.pi)
                sx = int(16 + np.cos(angle) * 9)
                sy = int(22 - np.sin(angle) * 9)
                
                # Отрисовка центральной ступицы стрелки
                frame[22, 16] = C['B_RED']
                frame[21, 16] = C['RED']
                
                # Прорисовка самой стрелки (линия из центра к краю шкалы)
                for i in range(10):
                    y = int(22 + (sy - 22) * i / 9)
                    x = int(16 + (sx - 16) * i / 9)
                    if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                        frame[y, x] = C['B_RED']  # Ярко-красная стрелка

            # --- СЦЕНА 3: Выхлоп и бампер Кристины (С кузовом и лесом по бокам) ---
            elif scene_idx == 3:
                # 1. ОТРИСОВКА НОЧНОГО ЛЕСА ПО БОКАМ (Статический фон)
                # Левый лесок (несколько вертикальных стволов и ветки)
                frame[8:24, 0] = [20, 35, 20]      # Темно-зеленый силуэт дерева
                frame[6:14, 1] = [15, 30, 15]
                frame[10:18, 2] = [10, 25, 10]

                # Правый лесок (асимметричный, для естественности)
                frame[7:24, 31] = [20, 35, 20]     # Дальние сосны
                frame[5:12, 30] = [15, 30, 15]
                frame[9:16, 29] = [10, 25, 10]

                # 2. АНИМАЦИЯ ВИБРАЦИИ МОТОРА (Кузов и бампер дрожат вместе)
                bounce = 1 if (f_idx % 4 < 2) else 0
                y_base = 15 + bounce  # Базовая высота для задней части машины

                # 3. КРАСНАЯ ПОЛОСА КУЗОВА (Нижняя кромка багажника над бампером)
                # Рисуем сочную красную полосу шириной от x=4 до x=27
                frame[y_base, 4:28] = C['RED']
                frame[y_base+1, 4:28] = C['RED']

                # 4. МАССИВНЫЙ ХРОМИРОВАННЫЙ БАМПЕР (Строго под красным кузовом)
                frame[y_base+2 : y_base+4, 4:28] = C['CHRM']

                # Грозные отблески стоп-сигналов по краям бампера (пульсируют)
                pulse = int(160 + np.sin(f_idx * 0.5) * 95)
                frame[y_base+2, 4:7] = [pulse, 0, 0]
                frame[y_base+2, 25:28] = [pulse, 0, 0]

                # 5. ЦИКЛ АНИМАЦИИ ДЫМА (Полностью рабочий и закрытый)
                smoke_stage = f_idx % 8
                # Левая труба на x=8, правая на x=23
                for x_pipe in [8, 23]:
                    # Стадия 1: Плотная серая струя прямо из-под хрома
                    if smoke_stage > 0:
                        if y_base + 4 < HEIGHT:
                            frame[y_base + 4, x_pipe] = [140, 140, 145]
                    
                    # Стадия 2: Облако расширяется и опускается ниже к земле
                    if smoke_stage > 2:
                        if y_base + 5 < HEIGHT:
                            frame[y_base + 5, (x_pipe - 1) : (x_pipe + 2)] = [100, 100, 105]
                    
                    # Стадия 3: Дым рассеивается у самого низа матрицы, становясь темнее
                    if smoke_stage > 5:
                        if y_base + 6 < HEIGHT:
                            frame[y_base + 6, (x_pipe - 2) : (x_pipe + 3)] = [60, 60, 65]

            # --- СЦЕНА 4: Преследование Бадди (Фары Кристины и неоновое имя) ---
            elif scene_idx == 4:
                # Вся матрица по умолчанию залита глубокой ночной темнотой
                
                # 1. РАСЧЕТ ПРИБЛИЖЕНИЯ КРИСТИНЫ (Идеально круглые фары разрастаются)
                headlight_radius = int(2 + t * 10)
                
                # Четко фиксируем центры фар, чтобы левая фара была идеально ровной
                left_center_x, left_center_y = 7, 16
                right_center_x, right_center_y = 24, 16

                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        dist_left = np.hypot(x - left_center_x, y - left_center_y)
                        dist_right = np.hypot(x - right_center_x, y - right_center_y)
                        
                        if dist_left < headlight_radius or dist_right < headlight_radius:
                            min_dist = min(dist_left, dist_right)
                            # Ослепительно белое ядро внутри фары
                            if min_dist < headlight_radius * 0.4:
                                frame[y, x] = C['WHT']
                            else:
                                # Внешнее жёлтое гало фары зловеще мерцает
                                flash = int(215 + np.sin(f_idx * 0.8) * 40)
                                frame[y, x] = [flash, int(flash * 0.85), 10]

                # 2. ФАЗА ИМЕНИ: В КОНЦЕ ПОЯВЛЯЕТСЯ ГЛИТЧУЮЩЕЕ ИМЯ ЖЕРТВЫ (кадры 35-49)
                # До 35 кадра на экране ТОЛЬКО чистые расширяющиеся фары машины.
                if f_idx >= 35:
                    # Эффект зловещей текстовой метки Кристины. 
                    # Буквы прорисованы вручную по пиксельной сетке, чтобы быть читаемыми!
                    # Добавим мелкую дрожь (глитч) тексту за счет изменения координат от кадра к кадру
                    glitch_x = 1 if (f_idx % 2 == 0) else 0
                    glitch_y = 1 if (f_idx % 3 == 0) else 0
                    
                    # Задаем базовое смещение для центрирования надписи "BUDDY"
                    tx = 2 + glitch_x
                    ty = 13 + glitch_y
                    
                    # Цвет текста: Ярко-красный/пурпурный глитч поверх фар Кристины
                    text_color = C['B_RED'] if (f_idx % 4 > 0) else C['WHT']
                    
                    # Матрица букв "B U D D Y" (высота 6 пикселей)
                    # Буква B
                    frame[ty:ty+6, tx] = frame[ty, tx:tx+3] = frame[ty+2, tx:tx+3] = frame[ty+5, tx:tx+3] = text_color
                    frame[ty+1, tx+3] = frame[ty+3, tx+3] = frame[ty+4, tx+3] = text_color
                    
                    # Буква U (сдвиг +5 пикселей)
                    tx_u = tx + 5
                    frame[ty:ty+5, tx_u] = frame[ty:ty+5, tx_u+3] = frame[ty+5, tx_u+1:tx_u+3] = text_color
                    
                    # Буква D (сдвиг +10 пикселей)
                    tx_d1 = tx + 10
                    frame[ty:ty+6, tx_d1] = frame[ty, tx_d1:tx_d1+3] = frame[ty+5, tx_d1:tx_d1+3] = text_color
                    frame[ty+1:ty+5, tx_d1+3] = text_color
                    
                    # Вторая буква D (сдвиг +15 пикселей)
                    tx_d2 = tx + 15
                    frame[ty:ty+6, tx_d2] = frame[ty, tx_d2:tx_d2+3] = frame[ty+5, tx_d2:tx_d2+3] = text_color
                    frame[ty+1:ty+5, tx_d2+3] = text_color
                    
                    # Буква Y (сдвиг +20 пикселей)
                    tx_y = tx + 20
                    frame[ty:ty+3, tx_y] = frame[ty:ty+3, tx_y+4] = text_color
                    frame[ty+3, tx_y+1:tx_y+4] = frame[ty+4:ty+6, tx_y+2] = text_color

            # --- СЦЕНА 5: Мастерская Дарнелла (АКТИВНАЯ ГРАФИКА: Неон, дождь и лужа) ---
            elif scene_idx == 5:
                if (12 <= f_idx <= 14) or (28 <= f_idx <= 29) or (42 <= f_idx <= 45):
                    neon_color = C['BLK']
                    neon_on = False
                else:
                    neon_flicker = int(220 + np.sin(f_idx * 1.5) * 35)
                    neon_color = [neon_flicker, 20, int(neon_flicker * 0.6)]
                    neon_on = True
                ny = 3
                frame[ny:ny+5, 3] = frame[ny, 3:6] = frame[ny+4, 3:6] = neon_color
                frame[ny+1:ny+4, 6] = neon_color
                frame[ny:ny+5, 8] = frame[ny:ny+5, 11] = frame[ny, 9:11] = frame[ny+2, 9:11] = neon_color
                frame[ny:ny+5, 13] = frame[ny, 13:16] = frame[ny+2, 13:16] = neon_color
                frame[ny+1, 16] = frame[ny+3, 15] = frame[ny+4, 16] = neon_color
                frame[ny:ny+5, 18] = frame[ny:ny+5, 22] = neon_color
                frame[ny+1, 19] = frame[ny+2, 20] = frame[ny+3, 21] = neon_color
                frame[ny:ny+5, 24] = frame[ny, 24:28] = frame[ny+2, 24:27] = frame[ny+4, 24:28] = neon_color
                ny_s = 9
                nx_s = 13
                frame[ny_s, nx_s] = frame[ny_s+1, nx_s] = neon_color
                nx_s2 = 15
                frame[ny_s, nx_s2:nx_s2+3] = frame[ny_s+2, nx_s2:nx_s2+3] = frame[ny_s+4, nx_s2:nx_s2+3] = neon_color
                frame[ny_s+1, nx_s2] = frame[ny_s+3, nx_s2+2] = neon_color
                for drop_id in range(3):
                    drop_x = (drop_id * 9 + 7) % WIDTH
                    drop_y = int(12 + (f_idx + drop_id * 15) % 10)
                    if 12 <= drop_y <= 21:
                        frame[drop_y, drop_x] = C['BLU']
                p_y1, p_y2 = 22, 23
                frame[p_y1, 8:24] = C['BLK']
                frame[p_y2, 6:26] = C['BLK']
                if neon_on:
                    wave_shift = 1 if (f_idx % 4 < 2) else 0
                    reflect_brightness = int(70 + np.sin(f_idx * 0.8) * 30)
                    REFLECT_COLOR = [reflect_brightness, 10, int(reflect_brightness * 0.6)]
                    frame[p_y1, (12 + wave_shift) : (19 + wave_shift)] = REFLECT_COLOR
                    frame[p_y2, (10 - wave_shift) : (17 - wave_shift)] = REFLECT_COLOR
                if f_idx % 12 == 0:
                    frame[p_y1, 15:18] = C['CHRM']

            # --- СЦЕНА 6: Взрыв, лужа, пар и уезд машины Кристины (Часть 1) ---
            elif scene_idx == 6:
                # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!
                frame[22, 6:26] = C['BLU']
                center_x, center_y = 6, 4
                
                # --- АКТ 1: ДВА ПООЧЕРЕДНЫХ "HR" ЛЕСЕНКОЙ В ТЕМНОТЕ ---
                if f_idx < 15:
                    text_color = C['B_RED'] if f_idx % 2 == 0 else C['WHT']
                    if f_idx < 8:
                        if 2 <= f_idx <= 5:
                            tx2, ty2 = 11, 9
                            frame[ty2:ty2+4, tx2] = frame[ty2:ty2+4, tx2+2] = frame[ty2+2, tx2+1] = text_color
                            frame[ty2:ty2+4, tx2+4] = frame[ty2, tx2+4:tx2+7] = frame[ty2+2, tx2+4:tx2+6] = text_color
                            frame[ty2+1, tx2+6] = frame[ty2+3, tx2+5] = frame[ty2+4, tx2+6] = text_color
                    else:
                        if 10 <= f_idx <= 13:
                            tx1, ty1 = 6, 4
                            frame[ty1:ty1+4, tx1] = frame[ty1:ty1+4, tx1+2] = frame[ty1+2, tx1+1] = text_color
                            frame[ty1:ty1+4, tx1+4] = frame[ty1, tx1+4:tx1+7] = frame[ty1+2, tx1+4:tx1+6] = text_color
                            frame[ty1+1, tx1+6] = frame[ty1+3, tx1+5] = frame[ty1+4, tx1+6] = text_color
                
                # --- АКТ 2: ОТРИСОВКА ВЗРЫВА И ПОЖАРА ---
                if f_idx >= 15:
                    fire_radius = int(1 + ((f_idx - 15) / 34) * 15) if f_idx < 42 else max(0, 15 - (f_idx - 42) * 2)
                    for y in range(0, 15):
                        for x in range(WIDTH):
                            dist = np.hypot(x - center_x, y - center_y)
                            if dist < fire_radius:
                                if dist < fire_radius * 0.25:
                                    frame[y, x] = C['WHT']
                                elif dist < fire_radius * 0.65:
                                    ylw_flicker = int(220 + np.sin(f_idx * 1.5 + x) * 35)
                                    frame[y, x] = [ylw_flicker, int(ylw_flicker * 0.85), 0]
                                else:
                                    org_flicker = int(190 + np.cos(f_idx * 1.1 - y) * 45)
                                    frame[y, x] = [org_flicker, int(org_flicker * 0.4), 10]
                
                # --- ДВИЖЕНИЕ МАШИНЫ, ПЛАВЛЕНИЕ И ПАР ---
                if f_idx >= 28:
                    if f_idx < 42:
                        car_progress = (f_idx - 28) / 14
                        cy = int(8 + car_progress * 9)
                    else:
                        exit_progress = (f_idx - 42) / 7
                        cy = int(17 + exit_progress * 12)
                        
                    if 0 <= cy < 24:
                        frame[cy:min(24, cy+2), 4:28] = C['RED']
                        frame[cy, 11:21] = C['B_RED']
                        if cy+2 < 24: frame[cy+2, 8:24] = C['BLK']
                        if cy+3 < 24: frame[cy+3, 8:24] = C['CHRM']
                        if cy+2 < 24:
                            frame[cy+1:min(24, cy+3), 5:8] = C['WHT']
                            frame[cy+1:min(24, cy+3), 24:27] = C['WHT']
                        if cy+4 < 24: frame[cy+4, 4:28] = C['CHRM']
                        
                        if 34 <= f_idx < 42:
                            melt_intensity = (f_idx - 34)
                            for x in range(4, 28):
                                if (x + f_idx) % 3 == 0:
                                    drop_length = np.random.randint(1, max(2, melt_intensity // 2))
                                    for d in range(1, drop_length + 1):
                                        target_y = cy + 2 + d
                                        if target_y < 24:
                                            frame[target_y, x] = C['BLK'] if d % 2 == 0 else C['ORG']
                        if 36 <= f_idx < 42 and cy + 4 >= 20:
                            steam_stage = (f_idx - 36) % 6
                            for px_pipe in [8, 23]:
                                if steam_stage > 0 and cy - 1 >= 0:
                                    frame[cy - 1, px_pipe] = C['WHT']
                                if steam_stage > 2 and cy - 2 >= 0:
                                    frame[cy - 2, (px_pipe - 1) : (px_pipe + 2)] = C['WHT']
                                if steam_stage > 4 and cy - 3 >= 0:
                                    if (px_pipe + f_idx) % 2 == 0:
                                        frame[cy - 3, (px_pipe - 2) : (px_pipe + 3)] = C['WHT']

            # --- СЦЕНА 7: Отдельный затухающий титр имени CHRISTINE (Выверенный центр) ---
            elif scene_idx == 7:
                # 1. РАСЧЕТ ЯРКОСТИ ТЕКСТА КРИСТИНИ (Имя гаснет к 42 кадру)
                if f_idx < 15:
                    glow = int((f_idx / 15) * 255)
                elif 15 <= f_idx < 35:
                    glow = int(220 + np.sin(f_idx * 1.5) * 35)
                else:
                    glow = max(0, 255 - int(((f_idx - 35) / 7) * 255)) if f_idx < 42 else 0
                    
                text_glow = [glow, glow, glow]
                
                # Рисуем буквы, пока они видны на экране (до 42 кадра)
                if glow > 0 and f_idx < 42:
                    ty = 11  # Базовая высота текстовой строки
                    melt1 = int(2 + np.sin(f_idx * 0.4) * 2)  
                    melt2 = int(2 + np.cos(f_idx * 0.5) * 1.5)
                    
                    # --- Буква C ---
                    if ty + 5 + melt1 < HEIGHT:
                        frame[ty : ty + 5 + melt1, 1] = text_glow
                    frame[ty, 1:4] = text_glow
                    frame[ty + 4, 1:4] = text_glow
                    
                    # --- Буква H ---
                    frame[ty : ty + 5, 5] = text_glow
                    frame[ty : ty + 5, 7] = text_glow
                    frame[ty + 2, 6] = text_glow
                    
                    # --- Буква R ---
                    if ty + 7 + melt2 < HEIGHT:
                        frame[ty : ty + 7 + melt2, 9] = text_glow
                    frame[ty, 9:12] = text_glow
                    frame[ty + 2, 9:12] = text_glow
                    frame[ty + 1, 11] = text_glow
                    frame[ty + 3, 10] = text_glow
                    frame[ty + 4, 11] = text_glow
                    
                    # --- Буква I ---
                    frame[ty : ty + 5, 13] = text_glow
                    
                    # --- Буква S ---
                    frame[ty, 15:17] = text_glow
                    frame[ty + 2, 15:17] = text_glow
                    if ty + 5 + melt1 < HEIGHT:
                        frame[ty + 4 : ty + 5 + melt1, 15] = text_glow  
                    frame[ty + 4, 15:17] = text_glow
                    frame[ty + 1, 15] = text_glow
                    frame[ty + 3, 16] = text_glow
                    
                    # --- Буква T ---
                    frame[ty, 18:21] = text_glow
                    frame[ty : ty + 5, 19] = text_glow
                    
                    # --- Буква I ---
                    frame[ty : ty + 5, 22] = text_glow
                    
                    # --- Буква N (x: 24..26) — ИСПРАВЛЕНА ПОД ШИРОКИЙ ШРИФТ БЕЗ НАЛОЖЕНИЙ! ---
                    if ty + 5 + melt2 < HEIGHT:
                        frame[ty : ty + 5 + melt2, 24] = text_glow  # Левая стойка течет
                    frame[ty : ty + 5, 26] = text_glow              # Правая стойка ровная
                    frame[ty + 1, 24] = text_glow
                    frame[ty + 2, 25] = text_glow                    # Тонкая диагональ
                    frame[ty + 3, 26] = text_glow
                    
                    # --- Буква E ---
                    frame[ty : ty + 5, 27] = C['BLK']  # Выжигаем артефакт перед рисованием перекладин
                    frame[ty : ty + 5, 28] = text_glow  
                    frame[ty, 28:31] = text_glow   
                    frame[ty + 2, 28:30] = text_glow 
                    frame[ty + 4, 28:31] = text_glow 

                # 4. ДЕЛИКАТНЫЙ ГОЛУБОЙ ХВОСТИК НАД НАДПИСЬЮ (Кадры 15-37)
                if 15 <= f_idx < 38:
                    angle = (f_idx - 15) * 0.18
                    radius_x = 10 - (f_idx - 15) * 0.2
                    radius_y = 5 - (f_idx - 15) * 0.1
                    
                    spark_x = int(16 + np.cos(angle) * radius_x)
                    spark_y = int(13 + np.sin(angle) * radius_y)
                    trail_x = int(16 + np.cos(angle - 0.2) * radius_x)
                    trail_y = int(13 + np.sin(angle - 0.2) * radius_y)
                    
                    if 0 <= trail_y < 24 and 0 <= trail_x < WIDTH and f_idx < 38:
                        frame[trail_y, trail_x] = C['BLU']  
                    if 0 <= spark_y < 24 and 0 <= spark_x < WIDTH and f_idx < 38:
                        frame[spark_y, spark_x] = C['WHT']  

                # 5. МАЛЕНЬКАЯ ЗВЕЗДОЧКА В ЦЕНТРЕ (Кадры 38-41)
                elif 38 <= f_idx < 42:
                    sx, sy = 16, 13
                    frame[sy, sx] = C['WHT']
                    if sy - 1 >= 0: frame[sy - 1, sx] = C['BLU']
                    if sy + 1 < 24: frame[sy + 1, sx] = C['BLU']
                    if sx - 1 >= 0: frame[sy, sx - 1] = C['BLU']
                    if sx + 1 < WIDTH: frame[sy, sx + 1] = C['BLU']

                # --- 6. КРИСТИНА НАДВИГАЕТСЯ ИЗ ТЕМНОТЫ ПО ФОРМЕ №1 (Кадры 42-49) ---
                if f_idx >= 42:
                    # Полная очистка рабочей зоны перед появлением машины
                    frame[0:24, :] = C['BLK']
                    
                    # Плавный наезд машины на камеру (cy смещается с 8 до 12 строки)
                    t_rush = (f_idx - 42) / 7
                    cy = int(8 + t_rush * 4)
                    
                    if 0 <= cy < 24:
                        # Отрисовка вашей любимой аккуратной геометрии кузова
                        frame[cy:min(24, cy+2), 4:28] = C['RED']       
                        frame[cy, 11:21] = C['B_RED']         
                        
                        # Ниша радиатора и решетка
                        if cy+2 < 24: frame[cy+2, 8:24] = C['BLK']
                        if cy+3 < 24: frame[cy+3, 8:24] = C['CHRM']
                        
                        # Яростные белые фары плавно увеличиваются в размерах
                        if cy+2 < 24:
                            frame[cy+1:min(24, cy+3), 5:8] = C['WHT']
                            frame[cy+1:min(24, cy+3), 24:27] = C['WHT']
                            
                        # Хромированный передний бампер по низу кузова
                        if cy+4 < 24: frame[cy+4, 4:28] = C['CHRM']

            # # --- СЦЕНА 8: Салон Кристины (Вариант 1: Мрачный Неонуар) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. ПОЛУНОЧНОЕ СТЕКЛО И ДОЖДЬ (y от 0 до 15)
            #     frame[0:16, :] = [10, 15, 35] # Глубокий полуночно-синий цвет стекла
                
            #     # Тонкие капли дождя, летящие наискось
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             frame[dy, dx] = C['BLU'] if f_idx % 2 == 0 else [140, 160, 200]

            #     # 2. РАБОТА ДВОРНИКОВ (Монотонный размеренный цикл)
            #     wiper_cycle = f_idx % 16
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. ТОРПЕДО И ПРИБОРЫ (Классическая бирюзовая подсветка)
            #     frame[15:24, :] = [45, 5, 10]  # Глубокий темно-бордовый пластик торпедо
            #     frame[15, :] = C['CHRM']        # Верхний хромированный кант

            #     # Мягкое, дышащее бирюзовое свечение шкал спидометра
            #     dash_glow = int(100 + np.sin(f_idx * 0.7) * 40)
            #     frame[18:21, 6:10] = [5, dash_glow, int(dash_glow * 0.8)]   # Левая шкала
            #     frame[18:21, 22:26] = [5, dash_glow, int(dash_glow * 0.8)]  # Правая шкала

            #     # Силуэт аккуратного двухспицевого руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            #             # --- СЦЕНА 8: Салон Кристины (Вариант 2: Кровавая ярость) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. ТРЕВОЖНОЕ СТЕКЛО И КРОВАВЫЙ ДОЖДЬ (y от 0 до 15)
            #     frame[0:16, :] = [30, 0, 40]   # Мрачное темно-пурпурное стекло
                
            #     # Капли дождя вспыхивают зловещим красным цветом от отблесков приборов
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             frame[dy, dx] = C['RED'] if f_idx % 2 == 0 else C['B_RED']

            #     # 2. РАБОТА ДВОРНИКОВ (Ускоренный, агрессивный темп)
            #     wiper_cycle = (f_idx * 2) % 16  # Скорость движения увеличена вдвое!
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. ТОРПЕДО И ПРИБОРЫ (Яростная красная пульсация)
            #     frame[15:24, :] = [45, 5, 10]  # Обугленный, темный пластик панели
            #     frame[15, :] = C['CHRM']

            #     # Приборы яростно пульсируют ярко-красным, имитируя перегрев мотора и ярость Кристины
            #     dash_glow = int(140 + np.sin(f_idx * 1.5) * 110) # Высокая частота и амплитуда пульсации
            #     frame[18:21, 6:10] = [dash_glow, 0, 10]   # Левая шкала
            #     frame[18:21, 22:26] = [dash_glow, 0, 10]  # Правая шкала

            #     # Силуэт руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            # # --- СЦЕНА 8: Салон Кристины (Вариант 3: Грозовой перевал) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # Расчет вспышки молнии (Кадры 12-14 и 34-36)
            #     is_lightning = (12 <= f_idx <= 14) or (34 <= f_idx <= 36)

            #     # 1. СТЕКЛО И КАПЛИ (Меняют цвет во время вспышки)
            #     if is_lightning:
            #         frame[0:16, :] = C['WHT']      # Небо ослепительно белое от молнии
            #         drop_color = [10, 15, 35]      # Капли на стекле становятся темными силуэтами
            #     else:
            #         frame[0:16, :] = [15, 20, 45]  # Обычная грозовая ночь
            #         drop_color = C['WHT'] if f_idx % 2 == 0 else C['BLU']
                
            #     # Рендеринг капель дождя
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             frame[dy, dx] = drop_color

            #     # 2. РАБОТА ДВОРНИКОВ (Размеренный ход)
            #     wiper_cycle = f_idx % 16
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. ТОРПЕДО И ПРИБОРЫ (Освещаются вспышками)
            #     if is_lightning:
            #         frame[15:24, :] = [80, 85, 100]  # Молния холодно освещает пластик салона
            #         frame[15, :] = C['WHT']           # Хром ярко блестит от вспышки
            #     else:
            #         frame[15:24, :] = [45, 5, 15]     # Обычный салон
            #         frame[15, :] = C['CHRM']

            #     # Приборы светятся ядовито-зеленым фоном
            #     dash_glow = int(120 + np.sin(f_idx * 0.8) * 50)
            #     frame[18:21, 6:10] = [0, dash_glow, 20]
            #     frame[18:21, 22:26] = [0, dash_glow, 20]

            #     # Силуэт руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            #             # --- СЦЕНА 8: Салон Кристины (Вариант 4: Радио Рок-н-ролл) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. СТЕНА ДОЖДЯ ЗА ОКНОМ (y от 0 до 15)
            #     frame[0:16, :] = [10, 20, 45]
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             frame[dy, dx] = C['WHT'] if f_idx % 2 == 0 else C['BLU']

            #     # 2. РАБОТА ДВОРНИКОВ (Монотонный ход)
            #     wiper_cycle = f_idx % 16
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. ТОРПЕДО И ОДЕРЖИМОЕ РАДИО (x от 14 до 18, y от 18 до 20)
            #     frame[15:24, :] = [45, 10, 15]
            #     frame[15, :] = C['CHRM']

            #     # Основные приборы (Зелёная подсветка)
            #     dash_glow = int(120 + np.sin(f_idx * 0.8) * 50)
            #     frame[18:21, 6:10] = [0, dash_glow, 20]
            #     frame[18:21, 22:26] = [0, dash_glow, 20]

            #     # --- ЛАМПОВОЕ РАДИО КРИСТИНЫ ПО ЦЕНТРУ ПАНЕЛИ ---
            #     # Корпус радиолы
            #     frame[17:21, 13:19] = C['BLK']
            #     frame[17, 13:19] = C['CHRM']
                
            #     # Шкала настройки бешено глитчует и скачет (анимация стрелки радио)
            #     radio_wave = int(14 + (f_idx * 3) % 4)
            #     frame[18, 14:18] = [70, 40, 10]  # Тусклый фон шкалы
            #     if 14 <= radio_wave <= 17:
            #         # Вспышки стрелки приёмника в такт рок-н-роллу
            #         radio_blink = C['YLW'] if f_idx % 2 == 0 else C['RED']
            #         frame[18:20, radio_wave] = radio_blink

            #     # Силуэт руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            #             # --- СЦЕНА 8: Салон Кристины (Вариант 5: Одержимый глитч) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. СТЕНА ДОЖДЯ ЗА ОКНОМ (y от 0 до 15)
            #     frame[0:16, :] = [10, 15, 30]
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             frame[dy, dx] = C['WHT'] if f_idx % 2 == 0 else C['BLU']

            #     # 2. РАБОТА ДВОРНИКОВ (Монотонный ход)
            #     wiper_cycle = f_idx % 16
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. ТОРПЕДО И СБОЯЩИЕ ПРИБОРЫ (Эффект искрящейся проводки)
            #     frame[15:24, :] = [45, 5, 10]
            #     frame[15, :] = C['CHRM']

            #     # --- ЛОГИКА ОДЕРЖИМОГО МЕРЦАНИЯ ЭЛЕКТРИКИ ---
            #     # Имитируем хаотичные просадки напряжения и глитчи через остаток от деления кадра
            #     if (f_idx % 7 == 0) or (22 <= f_idx <= 25) or (40 <= f_idx <= 42):
            #         # Электроника полностью выключается — приборы гаснут в темноту
            #         dash_glow_l = [10, 10, 10]
            #         dash_glow_r = [10, 10, 10]
            #     elif f_idx % 5 == 0:
            #         # Аварийный глитч: левая шкала горит ядовито-зеленым, правая — вспыхивает красным!
            #         dash_glow_l = [0, 240, 20]
            #         dash_glow_r = [255, 10, 10]
            #     else:
            #         # Стандартный мерцающий режим
            #         glow_val = int(120 + np.sin(f_idx * 1.1) * 40)
            #         dash_glow_l = [0, glow_val, 20]
            #         dash_glow_r = [0, glow_val, 20]

            #     # Отрисовка левой и правой шкал приборов с глитч-эффектом
            #     frame[18:21, 6:10] = dash_glow_l
            #     frame[18:21, 22:26] = dash_glow_r

            #     # Силуэт руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            #             # --- СЦЕНА 8: Салон Кристины (Вариант 6: Дьявольский силуэт капота) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. СТЕКЛО И СЛЕПЯЩИЕ ЛУЧИ ФАР (y от 0 до 14)
            #     frame[0:15, :] = C['BLK']  # Ночная мгла на дороге
                
            #     # Два мощных расходящихся луча дальнего света фар Кристины изнутри салона
            #     # Лучи бьют из нижней левой и правой точек стекла вверх-вперед
            #     for y in range(0, 15):
            #         # Левый луч расширяется кверху
            #         frame[y, max(0, 2 - (14 - y)) : min(WIDTH, 9 + (14 - y))] = [110, 110, 130]
            #         # Правый луч расширяется кверху
            #         frame[y, max(0, 23 - (14 - y)) : min(WIDTH, 30 + (14 - y))] = [110, 110, 130]

            #     # Летящие наискось капли ночного дождя, ярко подсвеченные фарами
            #     for drop_id in range(4):
            #         dx = (drop_id * 8 + f_idx * 2) % WIDTH
            #         dy = (drop_id * 4 + f_idx) % 15
            #         if 0 <= dy < 15 and 0 <= dx < WIDTH:
            #             # Внутри лучей фар капли светятся ослепительно белым, снаружи — синим
            #             if frame[dy, dx][0] > 0:
            #                 frame[dy, dx] = C['WHT']
            #             else:
            #                 frame[dy, dx] = C['BLU']

            #     # 2. РАБОТА ДВОРНИКОВ (Монотонный ход)
            #     wiper_cycle = f_idx % 16
            #     if wiper_cycle < 8:
            #         wiper_x = 2 + wiper_cycle * 3
            #     else:
            #         wiper_x = 23 - (wiper_cycle - 8) * 3

            #     for wy in range(4, 15):
            #         tilt = (14 - wy) // 2
            #         wx1 = wiper_x - tilt
            #         wx2 = wiper_x + 12 - tilt
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # --- 3. КРАЙ ЯРКО-КРАСНОГО КАПОТА КРИСТИНЫ (Строка 15) ---
            #     # Машина видит дорогу своими глазами-фарами, капот уходит вдаль
            #     frame[15, :] = C['RED']
            #     frame[15, 11:21] = C['B_RED']  # Фирменная выштамповка

            #     # 4. ТОРПЕДО И ПРИБОРЫ (y от 16 до 23)
            #     frame[16:24, :] = [45, 5, 10]  # Торпедо
            #     frame[16, :] = C['CHRM']        # Молдинг

            #     # Приборы светятся ядовито-зеленым фоном
            #     dash_glow = int(120 + np.sin(f_idx * 0.8) * 50)
            #     frame[18:21, 6:10] = [0, dash_glow, 20]
            #     frame[18:21, 22:26] = [0, dash_glow, 20]

            #     # Силуэт руля Плимута (x=8, y=19)
            #     frame[18:22, 4] = C['BLK']
            #     frame[18:22, 12] = C['BLK']
            #     frame[16:18, 5:12] = C['BLK']
            #     frame[22, 5:12] = C['BLK']
            #     frame[19, 5:12] = C['BLK']

            # # --- СЦЕНА 8: Салон Кристины (Наклонные дворники, блики и силуэты салона) ---
            # elif scene_idx == 8:
            #     # Строки 24-32 строго черные, бережём индикаторы (РЕМ, РАС, ТОП) в самом низу!

            #     # 1. ЛОБОВОЕ СТЕКЛО И РЕДКИЙ ПОНЯТНЫЙ ДОЖДЬ (Строки 0-14)
            #     # Базовый глубокий синий цвет лобового стекла
            #     frame[0:15, :] = [10, 20, 60]
                
            #     # МЯГКИЕ ДИАГОНАЛЬНЫЕ БЛИКИ НА СТЕКЛЕ (Эффект света ночных фонарей)
            #     # Две тонкие полосы бликов плавно бегут слева направо по кадрам
            #     glint_shift = (f_idx // 2) % 16
            #     for gy in range(0, 15):
            #         gx1 = gy + glint_shift
            #         gx2 = gy + glint_shift + 12
            #         if 0 <= gx1 < WIDTH: frame[gy, gx1] = [20, 45, 110]  # Светло-синий блик
            #         if 0 <= gx2 < WIDTH: frame[gy, gx2] = [20, 45, 110]

            #     # Крупные вертикальные капли дождя (3 штуки, без визуального мусора)
            #     drop1_y = (f_idx) % 15
            #     drop2_y = (f_idx + 5) % 15
            #     drop3_y = (f_idx + 10) % 15
            #     frame[drop1_y, 4] = C['WHT']
            #     frame[drop2_y, 16] = C['WHT']
            #     frame[drop3_y, 28] = C['WHT']

            #     # 2. АНИМАЦИЯ НАКЛОННЫХ ДВОРНИКОВ (Движение наискосок веером)
            #     # w_phase меняется от 0 до 8 (угол наклона щеток)
            #     w_cycle = f_idx % 16
            #     w_phase = w_cycle if w_cycle < 8 else (15 - w_cycle)
                
            #     for wy in range(3, 15):
            #         # Чем выше по стеклу (меньше wy), тем сильнее сдвиг по иксу вбок
            #         tilt = int((14 - wy) * (w_phase * 0.25))
                    
            #         # Левый дворник (водительский)
            #         wx1 = 6 + tilt
            #         # Правый дворник (пассажирский) — смещен вправо
            #         wx2 = 20 + tilt
                    
            #         if 0 <= wx1 < WIDTH: frame[wy, wx1] = C['BLK']
            #         if 0 <= wx2 < WIDTH: frame[wy, wx2] = C['BLK']

            #     # 3. МОНОЛИТНАЯ ПАНЕЛЬ САЛОНА И СИДЕНЬЯ (Строки 15-23)
            #     # Торпедо покрашено в глубокий темно-красный цвет
            #     frame[15:24, :] = C['B_RED']
                
            #     # Тонкая хромированная линия-молдинг разделяет стекло и торпедо
            #     frame[15, :] = C['CHRM']

            #     # СИЛУЭТЫ СПИНОК СИДЕНИЙ ПЛИМУТА (Черные пиксели выступают по бокам панели)
            #     # Левое сиденье (Водительское, y=16..23, x=0..3)
            #     frame[16:24, 0:3] = C['BLK']
            #     # Правое сиденье (Пассажирское, y=16..23, x=29..31)
            #     frame[16:24, 29:32] = C['BLK']

            #     # Зеленые круглые шкалы приборов (Слева и Справа)
            #     frame[18:21, 6:8] = C['GRN']
            #     frame[18:21, 24:26] = C['GRN']
                
            #     # Белая точка-стрелка внутри каждого спидометра
            #     frame[19, 7] = C['WHT']
            #     frame[19, 25] = C['WHT']

            #     # 4. АККУРАТНЫЙ СИЛУЭТ РУЛЯ (Строго перед водителем, перекрывает левый прибор)
            #     # Центр руля на x=7, y=19. Тонкое черное кольцо
            #     frame[18:21, 4] = C['BLK']   # Левая дуга руля
            #     frame[18:21, 10] = C['BLK']  # Правая дуга руля
            #     frame[17, 5:10] = C['BLK']   # Верхний обод
            #     frame[21, 5:10] = C['BLK']   # Нижний обод
            #     frame[19, 5:10] = C['BLK']   # Горизонтальная спица руля
            #     frame[19, 7] = C['CHRM']     # Хромированная сердцевина

            # --- СЦЕНА 9: Ночное шоссе (Чистая ночь, свет фар, Пеннивайз и анатомические глаза без полос) ---
            elif scene_idx == 9:
                # ВНИМАНИЕ: Зона 24-32 теперь полностью отдана под глаза на чистом черном фоне!
                
                # Расчет фаз моргания и финального закрытия глаз к 45 кадру
                if f_idx >= 45:
                    is_eye_open = False
                    is_eye_half = False
                elif 42 <= f_idx < 45:
                    is_eye_open = False
                    is_eye_half = True
                else:
                    blink_stage = f_idx % 20
                    is_eye_open = (blink_stage < 14)
                    is_eye_half = (14 <= blink_stage < 17)

                # === АКТ 1: ГЛУБОКАЯ НОЧЬ, СВЕТ ФАР И ПЕННИВАЙЗ НА ОБОЧИНЕ (Кадры 0-37) ===
                if f_idx < 38:
                    frame[0:24, :] = C['BLK']  
                    
                    # ИДЕАЛЬНОЕ СУЖАЮЩЕЕСЯ ШОССЕ (3D-клин от горизонта y=6 до низа y=23)
                    for y in range(6, 24):
                        spread = int((y - 6) * 0.8)
                        left_bound = max(0, 16 - spread)
                        right_bound = min(WIDTH, 16 + spread + 1)
                        frame[y, left_bound:right_bound] = C['CHRM']

                    # ТОНКАЯ РАЗДЕЛИТЕЛЬНАЯ ПОЛОСА В ПЕРСПЕКТИВЕ
                    road_step = (f_idx * 2) % 12
                    for y in range(6, 24):
                        projected_y = y + road_step
                        if (projected_y // 4) % 2 == 0:
                            line_w = 1 if y < 16 else 2
                            frame[y, (16 - line_w // 2) : (16 + (line_w + 1) // 2)] = C['WHT']

                    # --- ВАША ТОЧНАЯ ФОРМУЛА СВЕТА ФАР (Плавная подсветка асфальта к низу кадра) ---
                    for y in range(10, 24):
                        road_w = 3 + int((y - 8) * 0.8)
                        intensity = int((y - 9) / 14.0 * 125) 
                        x_start = max(0, 16 - road_w)
                        x_end = min(WIDTH, 16 + road_w)
                        for x in range(x_start, x_end):
                            frame[y, x, 0] = min(255, int(frame[y, x, 0] + intensity))
                            frame[y, x, 1] = min(255, int(frame[y, x, 1] + int(intensity * 0.95)))
                            frame[y, x, 2] = min(255, int(frame[y, x, 2] + int(intensity * 0.4)))

                    # Прорисовка Пеннивайза на правой обочине шоссе
                    man_y = 11 + int(t * 7)  
                    current_road_w = 3 + int((man_y - 8) * 0.8)
                    man_x = min(WIDTH - 5, 16 + current_road_w + 2) 

                    if 0 <= man_y < 24 and 3 <= man_x < WIDTH - 3:
                        if 0 <= man_y + 4 < 24:
                            for sx in range(man_x - 2, man_x + 3):
                                current_pixel = frame[man_y + 4, sx]
                                frame[man_y + 4, sx] = [max(0, int(current_pixel[c]) - 55) for c in range(3)]

                        if 0 <= man_y - 4 < 24: frame[man_y - 4, man_x] = C['YLW']
                        if 0 <= man_y - 3 < 24: frame[man_y - 3, man_x - 1 : man_x + 2] = C['YLW']
                        if 0 <= man_y - 2 < 24:
                            frame[man_y - 2, man_x - 1] = C['YLW']
                            frame[man_y - 2, man_x] = C['WHT']  
                            frame[man_y - 2, man_x + 1] = C['YLW']
                        if 0 <= man_y - 1 < 24: frame[man_y - 1, man_x - 1 : man_x + 2] = C['YLW']
                        if 0 <= man_y < 24: frame[man_y, man_x - 1 : man_x + 2] = C['YLW']
                        if 0 <= man_y + 1 < 24: frame[man_y + 1, man_x - 2 : man_x + 3] = C['YLW']
                        if 0 <= man_y + 2 < 24: frame[man_y + 2, man_x - 2 : man_x + 3] = C['YLW']
                        if 0 <= man_y + 3 < 24:
                            frame[man_y + 3, man_x - 1] = C['BLK']
                            frame[man_y + 3, man_x + 1] = C['BLK']

                        # Анимация и улет его шаров по диагонали вверх-влево
                        if f_idx < 26:
                            bx, by = man_x - 3, man_y - 6
                            if 0 <= bx < WIDTH and 0 <= by < 24:
                                if f_idx < 14: frame[by, bx] = C['RED']
                                else:
                                    if by + 2 < 24 and bx + 2 < WIDTH:
                                        frame[by:by+3, bx:bx+3] = C['RED']
                                        frame[by, bx] = C['WHT']
                                        frame[by+3, bx+1] = C['BLK']
                        else:
                            fly_t = (f_idx - 26) / 23
                            bx = int((man_x - 3) - fly_t * 24)
                            by = int((man_y - 6) - fly_t * 18)
                            if 0 <= bx < WIDTH and 0 <= by < 24:
                                frame[by, bx] = C['RED']

                # === АКТ 2: ГИГАНТСКИЙ ЗНАК STOP НА ВЕСЬ ЭКРАН (Кадры 38-49) ===
                else:
                    frame[0:24, :] = C['BLK']
                    
                    # ИСПРАВЛЕНО: Знак STOP сдвинут вправо на 1 пиксель назад для идеального баланса (16 - shield_w)
                    for y in range(1, 20):
                        if y == 1 or y == 19:    shield_w = 7
                        elif y == 2 or y == 18:  shield_w = 11
                        elif y == 3 or y == 17:  shield_w = 13
                        else:                    shield_w = 15  
                        frame[y, 16 - shield_w : 16 + shield_w] = C['WHT']
                    for y in range(2, 19):
                        if y == 2 or y == 18:    shield_w = 6
                        elif y == 3 or y == 17:  shield_w = 10
                        elif y == 4 or y == 16:  shield_w = 12
                        else:                    shield_w = 14  
                        frame[y, 16 - shield_w : 16 + shield_w] = C['RED']

                    # Буквы S T O P (Попиксельно отцентрированы и выровнены)
                    # Буква 'S' (x: 4-7)
                    frame[8, 4:8] = C['WHT']
                    frame[9, 4] = C['WHT']
                    frame[10, 4:8] = C['WHT']
                    frame[11, 7] = C['WHT']
                    frame[12, 4:8] = C['WHT']
                    
                    # Буква 'T' (x: 11-14) — ИСПРАВЛЕНО: Ножка сделана толще (2 пикселя) и стоит ровно по центру
                    frame[8, 11:15] = C['WHT']
                    frame[9:13, 12] = C['WHT']
                    frame[9:13, 13] = C['WHT']
                    
                    # Буква 'O' (x: 18-21)
                    frame[8, 18:22] = C['WHT']
                    frame[9:12, 18] = C['WHT']
                    frame[9:12, 21] = C['WHT']
                    frame[12, 18:22] = C['WHT']
                    
                    # Буква 'P' (x: 25-28)
                    frame[8, 25:29] = C['WHT']
                    frame[9, 25] = C['WHT']
                    frame[9, 28] = C['WHT']
                    frame[10, 25:29] = C['WHT']
                    frame[11:13, 25] = C['WHT']

                # ====================================================================
                #  СИСТЕМНЫЙ БЛОК: ЧИСТЫЙ NUMPY-СИНТАКСИС АНАТОМИЧЕСКИХ ГЛАЗ (24-32)
                # ====================================================================
                # Всё пространство между глаз остается чистой ночной бездной
                frame[24:32, :] = C['BLK']

                # Отрисовываем ультра-детализированные глаза по бокам в стабильном NumPy формате
                if is_eye_open:
                    # --- ЛЕВЫЙ АНАТОМИЧЕСКИЙ ЧЕЛОВЕЧЕСКИЙ ГЛАЗ (x: 0..10, y: 25..29) ---
                    frame[27, 0:11] = C['WHT']      # Центральный белок
                    frame[26, 2:9] = C['WHT']       # Изгиб верхнего века
                    frame[28, 2:9] = C['WHT']       # Изгиб нижнего века
                    frame[25, 4:7] = C['WHT']       
                    frame[29, 4:7] = C['WHT']
                    
                    # Объемное затемнение яблока (Тени в уголках)
                    frame[27, 0:2] = C['CHRM']
                    frame[27, 9:11] = C['CHRM']
                    
                    # Глубокая круглая радужка и зрачок с ДВОЙНЫМ БЛИКОМ
                    frame[26:29, 4:7] = C['BLU']    # Голубая оболочка
                    frame[26:29, 5] = C['BLK']      # Вертикальное ядро зрачка
                    frame[27, 5] = C['BLK']         # Центр зрачка
                    frame[26, 4] = C['WHT']         # Первый ослепительный блик роговицы
                    frame[27, 4] = C['WHT']         # Второй поддерживающий блик влажности
                    
                    # Кровавые хоррор-капилляры в уголках белков
                    frame[27, 2] = C['B_RED']
                    frame[26, 3] = C['B_RED']

                    # --- ПРАВЫЙ АНАТОМИЧЕСКИЙ ЧЕЛОВЕЧЕСКИЙ ГЛАЗ (x: 21..31, y: 25..29) ---
                    frame[27, 21:32] = C['WHT']
                    frame[26, 23:30] = C['WHT']
                    frame[28, 23:30] = C['WHT']
                    frame[25, 25:28] = C['WHT']
                    frame[29, 25:28] = C['WHT']
                    
                    # Тени
                    frame[27, 21:23] = C['CHRM']
                    frame[27, 30:32] = C['CHRM']
                    
                    # Радужка и зрачок с двойным бликом
                    frame[26:29, 25:28] = C['BLU']
                    frame[26:29, 26] = C['BLK']
                    frame[27, 26] = C['BLK']
                    frame[26, 25] = C['WHT']
                    frame[27, 25] = C['WHT']
                    
                    # Капилляры
                    frame[27, 29] = C['B_RED']
                    frame[26, 28] = C['B_RED']

                elif is_eye_half:
                    # Плавное анатомическое смыкание человеческих век
                    frame[27, 1:10] = C['WHT']
                    frame[27, 0:2] = C['CHRM']
                    frame[27, 8:10] = C['CHRM']
                    frame[27, 4:7] = C['BLU']
                    frame[27, 5] = C['BLK']
                    
                    frame[27, 22:31] = C['WHT']
                    frame[27, 21:23] = C['CHRM']
                    frame[27, 29:31] = C['CHRM']
                    frame[27, 25:28] = C['BLU']
                    frame[27, 26] = C['BLK']
                else:
                    # Полный покой век во тьме холста (Глаза полностью закрылись к концу сцены)
                    frame[25:30, 0:11] = C['BLK']
                    frame[25:30, 21:32] = C['BLK']




            # --- СЦЕНА 10: Ретро-магнитола из дорогого дерева и бакелита (Часть 1) ---
            elif scene_idx == 10:
                # Вся матрица 32х32 — это текстурное торпедо Кристины
                frame[0:32, :] = C['BLK']

                # 1. СТАРЫЙ ДЕРЕВЯННЫЙ КОРПУС СДВИНУТ НИЖЕ НА 2 ПИКСЕЛЯ (y: 6..23)
                # Заливаем основу благородным темно-коричневым деревом
                frame[6:24, 1:31] = C['BRN']          
                
                # Текстурные волокна и прожилки дерева из светлого ореха (строки 7 и 22)
                for x_wood in range(2, 30, 3):
                    frame[7, x_wood:x_wood+2] = C['L_BRN']
                    frame[22, x_wood-1:x_wood+1] = C['L_BRN']

                # Хромированный молдинг-окантовка вокруг деревянной панели
                frame[6, 1:31] = C['CHRM']            # Верх
                frame[23, 1:31] = C['CHRM']           # Низ
                frame[6:24, 1] = C['CHRM']             # Лево
                frame[6:24, 30] = C['CHRM']            # Право
                
                # Объемные круглые ручки-регуляторы из слоновой кости и хрома (опущены ниже)
                # Левая ручка громкости (x=3..5, y=13..15)
                frame[13:16, 3:6] = C['WHT']           # Светлый бакелит ручки
                frame[14, 4] = C['CHRM']               # Хромированный центр
                frame[16, 3:6] = C['BLK']              # Тень под ней
                
                # Правая ручка тюнера (x=26..28, y=13..15)
                frame[13:16, 26:29] = C['WHT']
                frame[14, 27] = C['CHRM']
                frame[16, 26:29] = C['BLK']

                # 2. ТЕКСТУРНАЯ РЕШЕТКА РАДИОДИНАМИКА ПОД ШКАЛОЙ (y: 18..21)
                # Старинное плетение: чередуем дерево и благородное золото бакелита
                for x_grille in range(7, 25):
                    if x_grille % 2 == 0:
                        frame[18:22, x_grille] = C['B_YLW']
                    else:
                        frame[18:22, x_grille] = C['BRN']

                # 3. ЛАМПОВАЯ ШКАЛА НАСТРОЙКИ ИЗ ВЫЦВЕТШЕГО БАКЕЛИТА (x: 7..25, y: 9..14)
                # Свечение ламп теплое, желтовато-кремовое, зловеще пульсирует
                radio_glow = int(140 + np.sin(f_idx * 0.4) * 45)
                for my in range(9, 15):
                    # Плавный аналоговый градиент ламповой подсветки шкал внутри
                    frame[my, 7:25] = [radio_glow, int(radio_glow * 0.8), int(radio_glow * 0.3)]

                # Деления частот и засечки диапазона AM/FM
                for mx in range(8, 25, 2):
                    frame[9, mx] = C['BRN']            # Верхние риски шкалы
                    frame[14, mx] = C['BRN']           # Нижние риски шкалы
                frame[11, 10] = frame[11, 16] = frame[11, 22] = C['WHT'] # Контрольные белые точки шкал

                # 4. ПОДВИЖНАЯ КРОВAВАЯ СТРЕЛКА ТЮНЕРА (y: 9..14 — Опущена ниже)
                # Стрелка плавно и размашисто бегает влево-вправо по бакелитовой шкале
                freq_x = int(11 + (np.sin(t * np.pi * 3.5) + 1.0) * 5)
                if 7 <= freq_x <= 24:
                    # Кроваво-красная стрелка приёмника зловеще выделяется на теплом фоне ламп
                    frame[9:15, freq_x] = C['B_RED']
                    # Белый ослепительный блик-указатель на самом кончике стрелки для чёткости
                    frame[9, freq_x] = C['WHT']

                # --- 5. УЛЬТРА-ДЕТАЛИЗИРОВАННЫЙ ЭФФЕКТ ЗВУКА: ВЫЛЕТАЮЩИЕ ВИНТАЖНЫЕ НОТЫ ---
                # Точки старта нот опущены ниже, в район новой решётки динамика (y=17)
                note_cycle = f_idx % 16
                
                # Левая нота (Теплый выцветший бакелит, зарождается на x=12, y=17)
                if note_cycle > 0:
                    n1_progress = note_cycle / 15
                    n1_x = int(12 - n1_progress * 11)
                    n1_y = int(17 - n1_progress * 15) # Летит выше и свободнее в небо
                    
                    if 0 <= n1_x < WIDTH and 0 <= n1_y < 32:
                        # Динамический размер: издалека 1 пиксель, вблизи — крупный знак
                        if n1_progress < 0.4:
                            frame[n1_y, n1_x] = C['B_YLW']
                        else:
                            # Крупный пиксельный музыкальный знак с хвостиком и штилем
                            frame[n1_y, n1_x] = C['B_YLW']  # Основание ноты
                            if n1_x + 1 < WIDTH: frame[n1_y, n1_x + 1] = C['B_YLW']
                            if n1_y - 1 >= 0 and n1_x + 1 < WIDTH:
                                frame[n1_y - 1 : n1_y + 1, n1_x + 1] = [C['B_YLW']] * 2  # Штиль
                            if n1_y - 2 >= 0 and n1_x + 2 < WIDTH:
                                frame[n1_y - 2, n1_x + 1 : n1_x + 3] = [C['B_YLW']] * 2  # Хвостик

                # Правая нота (Ярко-желтое старое золото, зарождается на x=20, y=17)
                if f_idx >= 6:
                    note2_cycle = (f_idx - 6) % 16
                    if note2_cycle > 0:
                        n2_progress = note2_cycle / 15
                        n2_x = int(20 + n2_progress * 11)
                        n2_y = int(17 - n2_progress * 15)
                        
                        if 0 <= n2_x < WIDTH and 0 <= n2_y < 32:
                            if n2_progress < 0.4:
                                frame[n2_y, n2_x] = C['YLW']
                            else:
                                # Крупная двойная ретро-нота (двойной пиксельный аккорд)
                                if n2_x + 2 < WIDTH:
                                    frame[n2_y, n2_x] = C['YLW']
                                    frame[n2_y, n2_x + 2] = C['YLW']
                                if n2_y - 1 >= 0 and n2_x + 2 < WIDTH:
                                    frame[n2_y - 1, n2_x + 1] = C['YLW']
                                    frame[n2_y - 1, n2_x + 2] = C['YLW']
                                if n2_y - 2 >= 0 and n2_x + 3 < WIDTH:
                                    frame[n2_y - 2, n2_x + 1 : n2_x + 4] = [C['YLW']] * 3


            # СЦЕНА 10: Преследование Мучи (ИСПРАВЛЕНА)
            elif scene_idx == 10:
                frame[:, 0:4] = frame[:, 28:32] = C['BLK']
                y_pos = int(HEIGHT - t * 20)
                if y_pos < 0: y_pos = 0
                if y_pos + 4 > HEIGHT: y_pos = HEIGHT - 4
                frame[y_pos:y_pos+4, 8:24] = C['RED']
                if y_pos+1 < HEIGHT:
                    frame[y_pos+1, 10:13] = frame[y_pos+1, 19:22] = C['YLW']

            # СЦЕНА 11: Силуэт Арни
            elif scene_idx == 11:
                frame[18:24, 10:22] = C['BLK']
                frame[12:18, 13:19] = C['BLK']
                frame[17:23, 9:23] = C['BLK']
                if f_idx % 10 > 7:
                    frame[14, 15] = frame[14, 16] = C['B_RED']

            # СЦЕНА 12: Camaro
            elif scene_idx == 12:
                frame[:, :12] = C['RED']
                crash_x = int(24 - t * 8)
                if crash_x < 0: crash_x = 0
                frame[:, crash_x:] = C['CHRM']
                for _ in range(3):
                    y = np.random.randint(10, 22)
                    frame[y, crash_x] = C['YLW']

            # СЦЕНА 13: Разбитое стекло
            elif scene_idx == 13:
                frame[:] = C['BLK']
                num_cracks = int(t * 12)
                for i in range(num_cracks):
                    angle = (i * 30) * np.pi / 180
                    for d in range(16):
                        cx = int(16 + np.cos(angle) * d)
                        cy = int(16 + np.sin(angle) * d)
                        if 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
                            frame[cy, cx] = C['WHT']

            # СЦЕНА 14: Бульдозер
            elif scene_idx == 14:
                heavy_y = int(t * 16)
                frame[0:heavy_y, :] = C['YLW']
                if heavy_y+2 <= HEIGHT:
                    frame[heavy_y:heavy_y+2, :] = C['BLK']
                frame[20:, :] = C['RED']

            # СЦЕНА 15: Дым из-под капота
            elif scene_idx == 15:
                frame[16:, 4:28] = C['RED']
                for y in range(0, 16):
                    for x in range(WIDTH):
                        if (x + y + f_idx) % 4 == 0:
                            frame[y, x] = C['CHRM']

            # СЦЕНА 16: Ночное шоссе
            elif scene_idx == 16:
                for y in range(12, HEIGHT):
                    w = int((y - 12) * 0.8)
                    frame[y, 16-w:16+w] = C['BLK']
                    if (y + f_idx) % 8 == 0:
                        frame[y, 16] = C['YLW']
                frame[12:14, 15:18] = C['RED']

            # СЦЕНА 17: Нож мясника
            elif scene_idx == 17:
                for i in range(20):
                    lx = 6 + i
                    ly = int(10 + t * 4 + i * 0.5)
                    if ly < HEIGHT:
                        frame[ly, lx] = C['CHRM']
                if t > 0.5:
                    drop_y = int(15 + (t - 0.5) * 20)
                    if drop_y < HEIGHT:
                        frame[drop_y, 16] = C['B_RED']

            # СЦЕНА 18: Финальная утилизация
            elif scene_idx == 18:
                size = int(14 * (1.0 - t)) + 2
                if size > 2:
                    y1, y2 = max(0, 16-size), min(HEIGHT, 16+size)
                    x1, x2 = max(0, 16-size), min(WIDTH, 16+size)
                    frame[y1:y2, x1:x2] = C['RED']
                    frame[y1, x1:x2] = C['CHRM']
                    if y2-1 >= 0:
                        frame[y2-1, x1:x2] = C['CHRM']
                else:
                    frame[15:17, 15:17] = C['BLK']

            scene_frames.append(frame.tolist())
        all_scenes.append(scene_frames)
    return all_scenes

# ------------------------- ГЕНЕРИРУЕМ СЦЕНЫ -------------------------
ALL_SCENES = generate_scenes()
ACTIVE_SCENE = 9 # можно менять от 0 до 18

# ------------------------- ОСНОВНОЙ КЛАСС ИГРЫ -------------------------
class ChristineComicGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ")
        self.root.geometry("1500x950")            # Большое окно как в JS
        self.root.configure(bg="#2b2b2b")          # Тёмный фон
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Параметры игры
        self.repair = 50
        self.sanity = 80
        self.fuel = 60
        self.reputation = 50
        self.game_active = True

        self.frames = ALL_SCENES[ACTIVE_SCENE]
        self.current_frame = 0
        self.anim_id = None

        self.create_widgets()
        self.start_animation()
        self.update_indicators()
        self.add_initial_dialog()

    def create_widgets(self):
        # Основной контейнер (вертикальное расположение: верхняя часть, затем терминал)
        main_panel = tk.Frame(self.root, bg="#2b2b2b")
        main_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Верхняя часть: слева анимация + индикаторы, справа диалоговое окно
        top_frame = tk.Frame(main_panel, bg="#2b2b2b")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # --- Левая панель (анимация + индикаторы) ---
        left_frame = tk.Frame(top_frame, bg="#2b2b2b")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 20))

        self.canvas = tk.Canvas(left_frame, width=WIDTH*PIXEL_SIZE, height=HEIGHT*PIXEL_SIZE,
                                bg="black", highlightthickness=0, bd=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Motion>", self.mouse_glitch)

        # Панель индикаторов (4 штуки)
        stat_frame = tk.Frame(left_frame, bg="#2b2b2b")
        stat_frame.pack(fill="x", pady=15)
        self.rep_canvas, self.rep_bar, self.rep_lbl = self._indicator(stat_frame, "РЕМ", 150, "#ff5555")
        self.san_canvas, self.san_bar, self.san_lbl = self._indicator(stat_frame, "РАС", 150, "#55ff55")
        self.fuel_canvas, self.fuel_bar, self.fuel_lbl = self._indicator(stat_frame, "ТОП", 100, "#ffff55")
        self.rep2_canvas, self.rep2_bar, self.rep2_lbl = self._indicator(stat_frame, "РЕП", 100, "#ff88ff")

        # --- Правая панель (диалоговое окно в стиле JS) ---
        right_frame = tk.Frame(top_frame, bg="#2b2b2b")
        right_frame.pack(side="right", fill="both", expand=True)

        # Диалоговый контейнер с белым фоном и рамкой как в JS
        dialog_bg = tk.Frame(right_frame, bg="#ffffff", bd=2, relief="solid")
        dialog_bg.pack(fill="both", expand=True)

        self.dialog_text = tk.Text(dialog_bg, bg="#ffffff", fg="#000000", font=("Courier New", 15),
                                   wrap="word", bd=0, relief="flat", padx=12, pady=12)
        self.dialog_text.pack(fill="both", expand=True)
        self.dialog_text.config(state="disabled")

        # --- Три стиля диалогов (имитация JS-стилей 17, 8, 18) ---
        # Стиль 17: Кристина (пиксельная коробка с тенью, жирный шрифт)
        self.dialog_text.tag_configure("christine", foreground="#000000", background="#fefefe",
                                       font=("Courier New", 15, "bold"), lmargin1=15, lmargin2=15,
                                       borderwidth=2, relief="solid", spacing3=8)
        # Стиль 8: Ответ игрока (печатная машинка, серая рамка)
        self.dialog_text.tag_configure("user", foreground="#222222", background="#fefefe",
                                       font=("Courier New", 15), lmargin1=15, lmargin2=15,
                                       borderwidth=1, relief="solid", spacing3=8)
        # Стиль 18: Действие (тёмный фон, подсветка слов)
        self.dialog_text.tag_configure("action", foreground="#dcdcdc", background="#1e1e2e",
                                       font=("Courier New", 14), lmargin1=15, lmargin2=15,
                                       borderwidth=0, relief="flat", spacing3=8)

        # --- Нижний терминал (как в JS: чёрный фон, зелёный текст) ---
        term_frame = tk.Frame(main_panel, bg="#000000", bd=2, relief="sunken")
        term_frame.pack(side="bottom", fill="x", pady=(5, 0))

        tk.Label(term_frame, text="> ТЕРМИНАЛ <", font=("Courier New", 12, "bold"),
                 fg="#00ff00", bg="#000000").pack(anchor="w", padx=12, pady=(8, 0))

        self.term_out = tk.Text(term_frame, bg="#000000", fg="#00ff00", font=("Courier New", 13),
                                height=9, wrap="word", bd=0, relief="flat")
        self.term_out.pack(fill="x", padx=12, pady=5)
        self.term_out.config(state="disabled")

        input_row = tk.Frame(term_frame, bg="#000000")
        input_row.pack(fill="x", padx=12, pady=8)
        tk.Label(input_row, text="$", font=("Courier New", 15, "bold"), fg="#00ff00", bg="#000000").pack(side="left")
        self.input_entry = tk.Entry(input_row, font=("Courier New", 15), bg="#000000", fg="#00ff00",
                                    insertbackground="#00ff00", relief="flat")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=10)
        self.input_entry.bind("<Return>", self.process_command)

        self.append_term("Система готова. Введите 'помощь'.")

    def _indicator(self, parent, label, width, color):
        """Создаёт индикатор (полоску + текст)"""
        cv = tk.Canvas(parent, width=width, height=20, bg="#000000", highlightthickness=1, highlightbackground="#00ff00")
        cv.pack(side="left", padx=8)
        bar = cv.create_rectangle(0, 0, 0, 20, fill=color, outline="")
        lbl = tk.Label(parent, text=f"{label} 50%", font=("Courier New", 12, "bold"),
                       fg="#00ff00", bg="#2b2b2b")
        lbl.pack(side="left", padx=5)
        return cv, bar, lbl

    def update_indicators(self):
        self.rep_canvas.coords(self.rep_bar, 0, 0, int(150 * self.repair / 100), 20)
        self.rep_lbl.config(text=f"РЕМ {self.repair}%")
        self.san_canvas.coords(self.san_bar, 0, 0, int(150 * self.sanity / 100), 20)
        self.san_lbl.config(text=f"РАС {self.sanity}%")
        self.fuel_canvas.coords(self.fuel_bar, 0, 0, int(100 * self.fuel / 100), 20)
        self.fuel_lbl.config(text=f"ТОП {self.fuel}%")
        self.rep2_canvas.coords(self.rep2_bar, 0, 0, int(100 * self.reputation / 100), 20)
        self.rep2_lbl.config(text=f"РЕП {self.reputation}%")

    def add_christine_message(self, text):
        self._add_message(text, "christine")
    def add_user_message(self, text):
        self._add_message(text, "user")
    def add_action_message(self, text):
        self._add_message(text, "action")
    def _add_message(self, text, tag):
        self.dialog_text.config(state="normal")
        if self.dialog_text.get("1.0", tk.END).strip():
            self.dialog_text.insert(tk.END, "\n\n")
        self.dialog_text.insert(tk.END, text, tag)
        self.dialog_text.see(tk.END)
        self.dialog_text.config(state="disabled")

    def append_dialog(self, text):
        self.add_user_message(text)
    def append_term(self, text):
        self.term_out.config(state="normal")
        if self.term_out.get("1.0", tk.END).strip():
            self.term_out.insert(tk.END, "\n")
        self.term_out.insert(tk.END, text)
        self.term_out.see(tk.END)
        self.term_out.config(state="disabled")

    def add_initial_dialog(self):
        self.add_christine_message("=== CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ ===")
        self.add_action_message("Вы за рулём Плимут-Фьюри 1958 года.")
        self.add_christine_message("Кристина жива и жаждет действий.")
        self.add_user_message("Введите 'помощь' в терминале, чтобы увидеть команды.")

    def start_animation(self):
        frame_data = self.frames[self.current_frame]
        img = Image.fromarray(np.array(frame_data, dtype=np.uint8), mode='RGB')
        img = img.resize((WIDTH*PIXEL_SIZE, HEIGHT*PIXEL_SIZE), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.current_frame = (self.current_frame + 1) % TOTAL_FRAMES
        self.anim_id = self.root.after(60, self.start_animation)

    def mouse_glitch(self, event):
        x = event.x // PIXEL_SIZE
        y = event.y // PIXEL_SIZE
        if 0 <= x < WIDTH and 0 <= y < HEIGHT and self.game_active:
            original = self.frames[self.current_frame][y][x].copy()
            self.frames[self.current_frame][y][x] = [255, 0, 255]
            def restore():
                if self.current_frame < len(self.frames):
                    self.frames[self.current_frame][y][x] = original
            self.root.after(150, restore)

    def apply_effect(self, dr, ds, df, drp, desc):
        if not self.game_active:
            return
        self.repair = max(0, min(100, self.repair + dr))
        self.sanity = max(0, min(100, self.sanity + ds))
        self.fuel = max(0, min(100, self.fuel + df))
        self.reputation = max(0, min(100, self.reputation + drp))
        self.update_indicators()
        self.add_action_message(desc)
        self.append_term(f"РЕМ: {dr:+d}% | РАС: {ds:+d}% | ТОП: {df:+d}% | РЕП: {drp:+d}%")
        if self.repair <= 0 or self.sanity <= 0:
            self.game_over()

    def game_over(self):
        self.game_active = False
        self.add_christine_message("\n*** ИГРА ОКОНЧЕНА ***")
        self.append_term("Игра окончена. Перезапустите программу.")

    def show_epilogue(self):
        epilogues = [
            "Бумага пахла бензином и старыми сигаретами. На обратной стороне был номер телефона, который никто не берёт уже двадцать лет.",
            "Она не была просто машиной. Кристина была обещанием. И проклятием.",
            "В зеркале заднего вида я иногда вижу не дорогу, а её улыбку — металлическую, с намёком на ржавчину.",
            "Механик сказал: «Утилизируй». Но я знал: если вставить ключ зажигания, она заведётся с пол-оборота.",
            "Последняя фраза из рации: «...не гони, сынок. Она уже выбрала тебя».",
            "Я выключил двигатель, но мотор всё равно стучал. Где-то в груди.",
            "Полицейский протокол гласил: «водитель не обнаружен». На сиденье остался только след от подушки.",
            "Кристина улыбнулась фарами. Я поклялся, что никогда больше не сяду за руль. На следующее утро ключи сами оказались у меня в кармане.",
            "Старая запись на кассете: «Она любит только тех, кто не боится её любить».",
            "На свалке она стояла три года. А когда я пришёл, фары вспыхнули сами собой.",
            "Чек из автомастерской: «Снять проклятие – 500 баксов. Не помогает».",
            "Запах кожи и перегара. Иногда мне кажется, что я до сих пор еду по тому шоссе.",
            "Ночью радио ловит только одну волну. Оттуда шепчет: «Ты мой, детка».",
            "Кристина не имела двигателя. Она имела душу.",
            "Последняя страница дневника: «Если читаешь это — беги. Машина уже знает, где ты».",
            "В бардачке нашли приглашение на гонку 1978 года. Подпись: «Приз – бессмертие».",
            "После аварии её списали. Но по ночам я слышу, как она заводится в гараже соседа.",
            "Ключ от зажигания до сих пор у меня. И он теплее, чем положено металлу."
        ]
        ep = random.choice(epilogues)
        self.add_action_message(ep)

    def process_command(self, event):
        cmd = self.input_entry.get().strip().lower()
        self.input_entry.delete(0, tk.END)
        self.append_term(f"> {cmd}")
        if not self.game_active:
            self.append_term("Игра окончена, перезапустите.")
            return

        if cmd in ("ремонт", "repair"):
            self.apply_effect(15, -10, -5, 0, "Вы провели ремонт в гараже. Кристина блестит.")
        elif cmd in ("свидание", "date"):
            if random.random() < 0.6:
                self.apply_effect(-5, 20, -5, 10, "Свидание с Ли прошло чудесно. Вы счастливы.")
            else:
                self.apply_effect(5, -15, 0, -5, "Кристина ревнует и мешает свиданию.")
        elif cmd in ("круиз", "cruise"):
            if random.random() < 0.6:
                self.apply_effect(20, -25, -20, -10, "Ночной круиз: вы атаковали банду. Кристина в восторге.")
            else:
                self.apply_effect(5, -10, -15, -5, "Полицейская погоня. Вы едва ушли.")
        elif cmd in ("продать", "sell"):
            self.apply_effect(-30, -40, 0, -20, "Вы попытались продать Кристину. Она в ярости!")
        elif cmd in ("статус", "status"):
            self.add_user_message(f"Ремонт: {self.repair}% | Рассудок: {self.sanity}% | Топливо: {self.fuel}% | Репутация: {self.reputation}%")
        elif cmd in ("эпилог", "epilogue"):
            self.show_epilogue()
        elif cmd in ("помощь", "help"):
            self.add_user_message("Доступные команды: ремонт, свидание, круиз, продать, статус, эпилог, помощь")
        else:
            self.add_user_message(f"Неизвестная команда: {cmd}")

    def on_close(self):
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.root.destroy()

# ------------------------- СИНХРОНИЗАЦИЯ И СЕРВЕР СВЯЗИ -------------------------

class ChristineWebHandler(http.server.SimpleHTTPRequestHandler):
    """Локальный API-сервер для мгновенной передачи матриц и параметров в HTML/JS интерфейс"""
    def do_GET(self):
        if self.path == '/api/matrix':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            # Разрешаем кросс-доменные запросы, чтобы JS из index.html мог забирать данные без блокировок
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Передаем всю сгенерированную попиксельную графику и параметры квеста в JS
            response_data = {
                "scenes": ALL_SCENES,
                "stats": player_stats
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            # Обычная раздача статических файлов (index.html) из текущей папки проекта
            super().do_GET()

def start_server():
    """Запуск TCP-сервера на порту 8000 с автоматическим открытием веб-интерфейса"""
    PORT = 8000
    handler = ChristineWebHandler
    # Позволяет повторно использовать порт без ожидания таймаутов операционной системы
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n[ДВИЖОК КРИСТИНЫ] Локальный сервер связи успешно запущен на http://localhost:{PORT}")
        # Автоматически открываем браузер со стильным окном игры при старте скрипта
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        httpd.serve_forever()

# ------------------------- ТОЧКА ВХОДА (СТАРТ ИГРЫ) -------------------------
if __name__ == "__main__":
    print("[КРИСТИНА] Инициализация графического движка и компиляция кадров...")
    
    # Запускаем трансляцию кадров в веб-интерфейс в отдельном независимом фоновом потоке
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print("[КРИСТИНА] Движок успешно запущен. Для остановки нажмите Ctrl + C.")
    
    # Основной цикл Python остается полностью свободным для обработки игровой логики квеста
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[КРИСТИНА] Игра успешно остановлена.")
