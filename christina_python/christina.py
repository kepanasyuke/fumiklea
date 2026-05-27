#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ (КОМИКС-СТИЛЬ)
- Анимация: 19 ваших сцен (дождь, бампер, спидометр, плавники, погоня, вывеска...)
- Диалоги справа (белое облако)
- Терминал внизу с вводом команд
- Глитч при наведении на пиксели
"""

import tkinter as tk
import numpy as np
from PIL import Image, ImageTk
import random

# ------------------------- ПАРАМЕТРЫ -------------------------
WIDTH, HEIGHT = 32, 32
PIXEL_SIZE = 14          # 32*14 = 448px
TOTAL_FRAMES = 50
TOTAL_SCENES = 19

# ------------------------- ЦВЕТА (ВАШИ) -------------------------
C = {
    'BLK': [0, 0, 0],       'RED': [200, 0, 0],     'B_RED': [255, 30, 30],
    'YLW': [255, 215, 0],   'ORG': [255, 100, 0],   'CHRM': [192, 192, 192],
    'WHT': [255, 255, 255], 'BLU': [0, 100, 200],   'GRN': [0, 150, 50],
    'PNK': [230, 0, 120]
}

# ------------------------- ГЕНЕРАЦИЯ СЦЕН (ИЗ ВАШЕГО КОДА) -------------------------
def generate_scenes():
    all_scenes = []
    for scene_idx in range(TOTAL_SCENES):
        scene_frames = []
        for f_idx in range(TOTAL_FRAMES):
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            t = f_idx / TOTAL_FRAMES

            if scene_idx == 0:   # базовая + огонь
                bright = 255 if f_idx >= 15 else int((f_idx/15)*255)
                frame[14:16, 5:8] = frame[14:16, 24:27] = [bright, int(bright*0.8), 0]
                frame[12:14, 4:28] = C['RED']
                frame[16:18, 4:28] = C['CHRM']
                if f_idx > 10:
                    for x in range(WIDTH):
                        h = int((np.sin(x + f_idx) + 1.2) * 5 * ((f_idx-10)/40))
                        for y in range(h):
                            frame[HEIGHT-1-y, x] = C['YLW'] if y < h-3 else C['ORG']
            elif scene_idx == 1:  # регенерация бампера
                frame[12:15, 4:28] = C['RED']
                dent = int((1.0 - t) * 6)
                frame[16, 4:28] = C['CHRM']
                if dent > 0:
                    frame[16, 12:20] = C['BLK']
                    frame[16+dent, 12:20] = C['CHRM']
            elif scene_idx == 2:  # спидометр
                for a in range(5, 27):
                    frame[22 - int(np.sin((a-5)/22*np.pi)*10), a] = C['WHT']
                angle = t * np.pi
                sx = int(16 + np.cos(angle) * 8)
                sy = int(22 - np.sin(angle) * 8)
                frame[22, 16] = C['B_RED']
                for i in range(9):
                    frame[int(22 + (sy-22)*i/8), int(16 + (sx-16)*i/8)] = C['B_RED']
            elif scene_idx == 3:  # задние плавники
                frame[10:22, 6:10] = C['RED']
                frame[10:22, 22:26] = C['RED']
                g_b = int(150 + np.sin(t * np.pi * 4) * 105)
                frame[11:14, 7:9] = [g_b, 0, 0]
                frame[11:14, 23:25] = [g_b, 0, 0]
            elif scene_idx == 4:  # преследование Бадди
                size = int(1 + t * 4)
                frame[16-size:16+size, 6-size:6+size] = C['YLW']
                frame[16-size:16+size, 26-size:26+size] = C['YLW']
                hx = int(20 - t * 4)
                frame[18:22, hx] = C['WHT']
                frame[17, hx] = C['CHRM']
                frame[22, hx - (f_idx%2)] = C['WHT']
                frame[22, hx + (f_idx%2)] = C['WHT']
            elif scene_idx == 5:  # вывеска автомастерской
                neon = C['PNK'] if (f_idx % 12 > 2) else C['BLK']
                frame[10, 4:28] = neon
                frame[11:15, 6] = neon
                frame[11:15, 14] = neon
                frame[20:25, 2:30] = [30, 30, 40]
            else:                 # сцены 6-18: ночное шоссе, дождь, свет фар
                shift = (f_idx * 2) % 32
                for y in range(HEIGHT):
                    if (y + shift) % 16 < 6 and 14 <= (y * WIDTH // HEIGHT) <= 18:
                        frame[y, 15:17] = C['YLW']
                    if scene_idx % 2 == 0:
                        if (y + f_idx) % 10 == 0:
                            frame[y, :, 0] = 50
                    else:
                        frame[int(t*31), int((np.sin(y)+1)*15)] = C['BLU']
            scene_frames.append(frame.tolist())
        all_scenes.append(scene_frames)
    return all_scenes

ALL_SCENES = generate_scenes()
ACTIVE_SCENE = 6   # можно менять от 0 до 18

# ------------------------- ОСНОВНОЙ КЛАСС -------------------------
class ChristineComicGame:
    def __init__(self, root):
        self.root = root
        self.root.title("CHRISTINE: ПИКСЕЛЬНЫЙ КВЕСТ")
        self.root.geometry("1000x720")
        self.root.configure(bg="#2b2b2b")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Игровые параметры
        self.repair = 50
        self.sanity = 80
        self.fuel = 60
        self.reputation = 50
        self.game_active = True

        # Анимация
        self.frames = ALL_SCENES[ACTIVE_SCENE]
        self.current_frame = 0
        self.anim_id = None

        # Создание интерфейса
        self.create_widgets()
        self.start_animation()
        self.update_indicators()
        self.add_initial_dialog()

    def create_widgets(self):
        # Левая панель: холст с анимацией
        left_frame = tk.Frame(self.root, bg="#1a1a1a", bd=2, relief="flat")
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(left_frame, width=WIDTH*PIXEL_SIZE, height=HEIGHT*PIXEL_SIZE,
                                bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.bind("<Motion>", self.mouse_glitch)

        # Индикаторы (под холстом)
        stat_frame = tk.Frame(left_frame, bg="#1a1a1a")
        stat_frame.pack(fill="x", pady=5)
        self.rep_canvas, self.rep_bar, self.rep_lbl = self._indicator(stat_frame, "РЕМ", 120, "#ff5555")
        self.san_canvas, self.san_bar, self.san_lbl = self._indicator(stat_frame, "РАС", 120, "#55ff55")
        self.fuel_canvas, self.fuel_bar, self.fuel_lbl = self._indicator(stat_frame, "ТОП", 80, "#ffff55")
        self.rep2_canvas, self.rep2_bar, self.rep2_lbl = self._indicator(stat_frame, "РЕП", 80, "#ff88ff")

        # Правая панель: диалоги в стиле комиксов (облачко)
        right_frame = tk.Frame(self.root, bg="#2b2b2b")
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Облачко диалога (белый прямоугольник с тенью)
        dialog_bg = tk.Frame(right_frame, bg="#ffffff", bd=2, relief="ridge")
        dialog_bg.pack(fill="both", expand=True, pady=(0, 10))
        # Имитация хвостика облачка (упрощённо)
        self.dialog_text = tk.Text(dialog_bg, bg="#ffffff", fg="#000000", font=("Comic Sans MS", 12),
                                   wrap="word", bd=0, relief="flat", padx=10, pady=10)
        self.dialog_text.pack(fill="both", expand=True)
        self.dialog_text.config(state="disabled")

        # Нижняя панель: терминал (видимый)
        term_frame = tk.Frame(self.root, bg="#000000", bd=2, relief="sunken")
        term_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        tk.Label(term_frame, text="> ТЕРМИНАЛ <", font=("Courier New", 8, "bold"),
                 fg="#00ff00", bg="#000000").pack(anchor="w", padx=5, pady=(5,0))

        # Область вывода терминала
        self.term_out = tk.Text(term_frame, bg="#000000", fg="#00ff00", font=("Courier New", 10),
                                height=4, wrap="word", bd=0, relief="flat")
        self.term_out.pack(fill="x", padx=5, pady=2)
        self.term_out.config(state="disabled")

        # Строка ввода
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

    # ------------------------- АНИМАЦИЯ И ГЛИТЧ -------------------------
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
            # Сохраняем исходный пиксель
            original = self.frames[self.current_frame][y][x].copy()
            # Меняем на розовый
            self.frames[self.current_frame][y][x] = [255, 0, 255]
            # Возврат через 150 мс
            def restore():
                if self.current_frame < len(self.frames):
                    self.frames[self.current_frame][y][x] = original
            self.root.after(150, restore)

    # ------------------------- ИГРОВАЯ ЛОГИКА -------------------------
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
            self.apply_effect(15, -10, -5, 0, "Вы провели ремонт в гараже. Кристина блестит на солнце.")
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
