#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ (КОМИКС-СТИЛЬ)
- 19 анимированных сцен (дождь, бампер, спидометр, погоня, взрыв...)
- Диалоги справа (белое облачко)
- Терминал внизу с вводом команд (видимый)
- Глитч при наведении на пиксели
"""

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import random

# ------------------------- ПАРАМЕТРЫ -------------------------
WIDTH, HEIGHT = 32, 32
PIXEL_SIZE = 14
TOTAL_FRAMES = 50
TOTAL_SCENES = 19

# ------------------------- ЦВЕТА -------------------------
C = {
    'BLK': [0, 0, 0],       'RED': [200, 0, 0],     'B_RED': [255, 30, 30],
    'YLW': [255, 215, 0],   'ORG': [255, 100, 0],   'CHRM': [192, 192, 192],
    'WHT': [255, 255, 255], 'BLU': [0, 100, 200],   'GRN': [0, 150, 50],
    'PNK': [230, 0, 120]
}

# ------------------------- ГЕНЕРАЦИЯ СЦЕН (С ИСПРАВЛЕНИЕМ ГРАНИЦ) -------------------------
def generate_scenes():
    all_scenes = []
    for scene_idx in range(TOTAL_SCENES):
        scene_frames = []
        for f_idx in range(TOTAL_FRAMES):
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            t = f_idx / TOTAL_FRAMES

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
                
                # 2. Отрисовка кузова 
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

                        # --- СЦЕНА 2: Спидометр (Вид из салона, Луна и Летучая мышь) ---
            elif scene_idx == 2:
                # 1. НОЧНОЕ НЕБО И ЛУНА (За лобовым стеклом в верхней части, y от 0 до 12)
                # Огромная круглая луна в верхнем правом углу
                for y in range(0, 8):
                    for x in range(18, 28):
                        if np.hypot(x - 22, y - 4) < 4:
                            frame[y, x] = [230, 230, 250] # Мягкий лунный свет

                # Анимированная летучая мышь (летит справа налево перед луной)
                # Ее координата x зависит от кадра f_idx
                bat_x = int(32 - (f_idx * 0.8))
                bat_y = 3 + int(np.sin(f_idx * 0.5) * 1) # Слегка колышется вверх-вниз
                
                if 0 <= bat_x < WIDTH:
                    # Тело летучей мыши
                    frame[bat_y, bat_x] = C['BLK']
                    # Анимация крыльев (взмахи в зависимости от кадра)
                    if f_idx % 4 < 2:
                        # Крылья подняты вверх
                        if bat_y - 1 >= 0 and bat_x - 1 >= 0 and bat_x + 1 < WIDTH:
                            frame[bat_y - 1, bat_x - 1] = C['BLK']
                            frame[bat_y - 1, bat_x + 1] = C['BLK']
                    else:
                        # Крылья опущены вниз
                        if bat_y + 1 < 12 and bat_x - 1 >= 0 and bat_x + 1 < WIDTH:
                            frame[bat_y + 1, bat_x - 1] = C['BLK']
                            frame[bat_y + 1, bat_x + 1] = C['BLK']

                # 2. ДОРОГА И СВЕТ ФАР (Вырывается из-под капота в средней части)
                # Мощный дальний свет фар освещает летящую навстречу дорогу (y от 10 до 15)
                frame[10:14, 4:28] = [60, 60, 40] # Желтоватый конус света фар на асфальте
                
                # Летящая навстречу разметка (бешеные белые пиксели скорости)
                line_y = int(10 + (f_idx * 2) % 4)
                if 10 <= line_y < 14:
                    frame[line_y, 15:17] = C['WHT']

                # 3. ПРИБОРНАЯ ПАНЕЛЬ (Нижняя часть экрана, y от 14 до 32)
                # Корпус торпеды отделяет салон от лобового стекла
                frame[14:32, 2:30] = [20, 20, 20] # Темный салон

                # Отрисовка круглой шкалы спидометра (Зеленый неон Chrysler 1958 года)
                for a in range(6, 26):
                    # Параболическая арка щитка приборов
                    y_gauge = 25 - int(np.sin((a - 6) / 19 * np.pi) * 9)
                    if 0 <= y_gauge < HEIGHT:
                        frame[y_gauge, a] = C['WHT']
                        if y_gauge + 1 < HEIGHT:
                            frame[y_gauge + 1, a] = C['GRN'] # Подсветка шкал

                # Ограничительные желтые деления на спидометре
                frame[24, 7] = frame[16, 15] = frame[24, 24] = C['YLW']

                # 4. ДИВИЖЕНИЕ КРАСНОЙ СТРЕЛКИ (Ложится до упора вправо)
                # t идет от 0.0 до 1.0. Угол поворота: от 180 до 0 градусов (полная скорость!)
                angle = np.pi - (t * np.pi)
                sx = int(15 + np.cos(angle) * 7)
                sy = int(25 - np.sin(angle) * 7)
                
                # Ступица стрелки
                frame[25, 15] = C['B_RED']
                
                # Прорисовываем саму стрелку скорости от центра к шкале
                for i in range(8):
                    y_str = int(25 + (sy - 25) * i / 7)
                    x_str = int(15 + (sx - 15) * i / 7)
                    if 0 <= y_str < HEIGHT and 0 <= x_str < WIDTH:
                        frame[y_str, x_str] = C['B_RED']


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


            # СЦЕНА 4: Преследование Бадди
            elif scene_idx == 4:
                size = int(1 + t * 4)
                for y in range(16-size, 16+size):
                    for x in range(6-size, 6+size):
                        if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                            frame[y, x] = C['YLW']
                for y in range(16-size, 16+size):
                    for x in range(26-size, 26+size):
                        if 0 <= y < HEIGHT and 0 <= x < WIDTH:
                            frame[y, x] = C['YLW']
                hx = int(20 - t * 4)
                if 0 <= hx < WIDTH:
                    frame[18:22, hx] = C['WHT']
                    frame[17, hx] = C['CHRM']
                    if hx-1 >= 0: frame[22, hx-1] = C['WHT']
                    if hx+1 < WIDTH: frame[22, hx+1] = C['WHT']

            # СЦЕНА 5: Вывеска автомастерской
            elif scene_idx == 5:
                neon = C['PNK'] if (f_idx % 12 > 2) else C['BLK']
                frame[10, 4:28] = neon
                frame[11:15, 6] = neon
                frame[11:15, 14] = neon
                frame[20:25, 2:30] = C['BLK']

            # СЦЕНА 6: Взрыв и пожар на заправке
            elif scene_idx == 6:
                fire_radius = int(t * 18)
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        if np.hypot(x - 16, y - 32) < fire_radius:
                            frame[y, x] = C['YLW'] if (y + f_idx) % 3 == 0 else C['ORG']
                if t < 0.6:
                    frame[14:28, 13:19] = C['BLK']

            # СЦЕНА 7: Ослепление дальним светом
            elif scene_idx == 7:
                frame[:] = [int(t * 40)] * 3
                glow = int(4 + t * 12)
                for y in range(HEIGHT):
                    for x in range(WIDTH):
                        if np.hypot(x - 8, y - 16) < glow or np.hypot(x - 24, y - 16) < glow:
                            frame[y, x] = C['WHT']

            # СЦЕНА 8: Дождь и дворники
            elif scene_idx == 8:
                for i in range(15):
                    rx = (i * 7 + f_idx * 2) % WIDTH
                    ry = (i * 11 + f_idx * 3) % HEIGHT
                    frame[ry, rx] = C['BLU']
                w_pos = int(16 + np.sin(t * np.pi * 2) * 14)
                for y in range(10, 25):
                    if 0 <= w_pos < WIDTH:
                        frame[y, w_pos] = C['BLK']

            # СЦЕНА 9: Магнитола
            elif scene_idx == 9:
                frame[14:18, 4:28] = C['BLK']
                freq_x = int(10 + np.sin(t * np.pi * 6) * 8)
                frame[15:17, 6:26] = C['GRN'] if f_idx % 2 == 0 else C['BLK']
                if 0 <= freq_x < WIDTH:
                    frame[15:17, freq_x] = C['YLW']

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
ACTIVE_SCENE = 0   # можно менять от 0 до 18

# ------------------------- ОСНОВНОЙ КЛАСС ИГРЫ -------------------------
class ChristineComicGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ")
        self.root.geometry("1000x760")
        self.root.configure(bg="#2b2b2b")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

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
        left_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief="flat")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(left_frame, width=WIDTH*PIXEL_SIZE, height=HEIGHT*PIXEL_SIZE,
                                bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Motion>", self.mouse_glitch)

        stat_frame = tk.Frame(left_frame, bg="#1a1a1a")
        stat_frame.pack(fill="x", pady=5)
        self.rep_canvas, self.rep_bar, self.rep_lbl = self._indicator(stat_frame, "РЕМ", 120, "#ff5555")
        self.san_canvas, self.san_bar, self.san_lbl = self._indicator(stat_frame, "РАС", 120, "#55ff55")
        self.fuel_canvas, self.fuel_bar, self.fuel_lbl = self._indicator(stat_frame, "ТОП", 80, "#ffff55")
        self.rep2_canvas, self.rep2_bar, self.rep2_lbl = self._indicator(stat_frame, "РЕП", 80, "#ff88ff")

        right_frame = tk.Frame(self.root, bg="#2b2b2b")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        dialog_bg = tk.Frame(right_frame, bg="#ffffff", bd=2, relief="ridge")
        dialog_bg.pack(fill="both", expand=True, pady=(0, 10))
        self.dialog_text = tk.Text(dialog_bg, bg="#ffffff", fg="#000000", font=("Comic Sans MS", 12),
                                   wrap="word", bd=0, relief="flat", padx=10, pady=10)
        self.dialog_text.pack(fill="both", expand=True)
        self.dialog_text.config(state="disabled")

        term_frame = tk.Frame(self.root, bg="#000000", bd=2, relief="sunken")
        term_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        tk.Label(term_frame, text="> ТЕРМИНАЛ <", font=("Courier New", 8, "bold"),
                 fg="#00ff00", bg="#000000").pack(anchor="w", padx=5, pady=(5,0))
        self.term_out = tk.Text(term_frame, bg="#000000", fg="#00ff00", font=("Courier New", 10),
                                height=5, wrap="word", bd=0, relief="flat")
        self.term_out.pack(fill="x", padx=5, pady=2)
        self.term_out.config(state="disabled")

        input_row = tk.Frame(term_frame, bg="#000000")
        input_row.pack(fill="x", padx=5, pady=5)
        tk.Label(input_row, text="$", font=("Courier New", 12, "bold"), fg="#00ff00", bg="#000000").pack(side="left")
        self.input_entry = tk.Entry(input_row, font=("Courier New", 12), bg="#000000", fg="#00ff00",
                                    insertbackground="#00ff00", relief="flat")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.input_entry.bind("<Return>", self.process_command)

        self.append_term("Система готова. Введите 'помощь'.")

    def _indicator(self, parent, label, width, color):
        cv = tk.Canvas(parent, width=width, height=12, bg="#000000", highlightthickness=1, highlightbackground="#00ff00")
        cv.pack(side="left", padx=5)
        bar = cv.create_rectangle(0,0,0,12, fill=color, outline="")
        lbl = tk.Label(parent, text=f"{label} 50%", font=("Courier New",9,"bold"), fg="#00ff00", bg="#1a1a1a")
        lbl.pack(side="left", padx=2)
        return cv, bar, lbl

    def update_indicators(self):
        self.rep_canvas.coords(self.rep_bar, 0, 0, int(120 * self.repair / 100), 12)
        self.rep_lbl.config(text=f"РЕМ {self.repair}%")
        self.san_canvas.coords(self.san_bar, 0, 0, int(120 * self.sanity / 100), 12)
        self.san_lbl.config(text=f"РАС {self.sanity}%")
        self.fuel_canvas.coords(self.fuel_bar, 0, 0, int(80 * self.fuel / 100), 12)
        self.fuel_lbl.config(text=f"ТОП {self.fuel}%")
        self.rep2_canvas.coords(self.rep2_bar, 0, 0, int(80 * self.reputation / 100), 12)
        self.rep2_lbl.config(text=f"РЕП {self.reputation}%")

    def append_dialog(self, text):
        self.dialog_text.config(state="normal")
        if self.dialog_text.get("1.0", tk.END).strip():
            self.dialog_text.insert(tk.END, "\n\n")
        self.dialog_text.insert(tk.END, text)
        self.dialog_text.see(tk.END)
        self.dialog_text.config(state="disabled")

    def append_term(self, text):
        self.term_out.config(state="normal")
        if self.term_out.get("1.0", tk.END).strip():
            self.term_out.insert(tk.END, "\n")
        self.term_out.insert(tk.END, text)
        self.term_out.see(tk.END)
        self.term_out.config(state="disabled")

    def add_initial_dialog(self):
        self.append_dialog("=== CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ ===")
        self.append_dialog("Вы за рулём Плимут-Фьюри 1958 года.")
        self.append_dialog("Кристина жива и жаждет действий.")
        self.append_dialog("Введите 'помощь' в терминале, чтобы увидеть команды.")

    def start_animation(self):
        frame_data = self.frames[self.current_frame]
        img = Image.fromarray(np.array(frame_data, dtype=np.uint8), mode='RGB')
        img = img.resize((WIDTH*PIXEL_SIZE, HEIGHT*PIXEL_SIZE), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.current_frame = (self.current_frame + 1) % TOTAL_FRAMES
        self.anim_id = self.root.after(50, self.start_animation)

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
        self.append_dialog(desc)
        self.append_term(f"РЕМ: {dr:+d}% | РАС: {ds:+d}% | ТОП: {df:+d}% | РЕП: {drp:+d}%")
        if self.repair <= 0 or self.sanity <= 0:
            self.game_over()

    def game_over(self):
        self.game_active = False
        self.append_dialog("\n*** ИГРА ОКОНЧЕНА ***")
        self.append_term("Игра окончена. Перезапустите программу.")

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
            self.append_dialog(f"Ремонт: {self.repair}% | Рассудок: {self.sanity}% | Топливо: {self.fuel}% | Репутация: {self.reputation}%")
        elif cmd in ("помощь", "help"):
            self.append_dialog("Доступные команды: ремонт, свидание, круиз, продать, статус, помощь")
        else:
            self.append_dialog(f"Неизвестная команда: {cmd}")

    def on_close(self):
        if self.anim_id:
            self.root.after_cancel(self.anim_id)
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChristineComicGame(root)
    root.mainloop()
