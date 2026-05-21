import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos
from coffee_analysis import generate_data, analyze_and_get_figures

FONT_REGULAR = 'fonts/DejaVuSansCondensed.ttf'
FONT_BOLD = 'fonts/DejaVuSansCondensed-Bold.ttf'

if not os.path.exists(FONT_REGULAR) or not os.path.exists(FONT_BOLD):
    print("ОШИБКА: шрифты не найдены в папке fonts/.")
    print("Сначала выполните: make fonts")
    exit(1)

print("Генерируем данные...")
df = generate_data(10000)
print("Строим графики и считаем метрики...")
figures, insights = analyze_and_get_figures(df)

pdf = FPDF()
pdf.add_page()
pdf.add_font('DejaVu', '', FONT_REGULAR)
pdf.add_font('DejaVu', 'B', FONT_BOLD)

# Титульная страница
pdf.set_font('DejaVu', 'B', 24)
pdf.cell(0, 10, 'Отчёт по анализу продаж кофейни "Уютный уголок"', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.set_font('DejaVu', '', 14)
pdf.cell(0, 10, 'Июнь – Август 2024', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.ln(10)
pdf.set_font('DejaVu', '', 12)
pdf.multi_cell(0, 7, 'Данный отчёт содержит ключевые показатели продаж, анализ пиковых часов и рекомендации для оптимизации ассортимента и графика работы персонала.', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# Ключевые выводы
pdf.add_page()
pdf.set_font('DejaVu', 'B', 16)
pdf.cell(0, 10, 'Ключевые выводы', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.ln(5)

pdf.set_font('DejaVu', '', 12)
conclusions = [
    f"- Пиковый час: {insights['peak_hour']}",
    f"- Самый прибыльный день: {insights['best_day']}",
    f"- Лидирующая категория: {insights['top_cat']}",
    f"- Средний чек утром: {insights['avg_check_morning']}, днём: {insights['avg_check_day']}, вечером: {insights['avg_check_evening']}",
    "",
    "Рекомендации:",
    "- Усилить смену бариста в пиковые утренние (8–10) и обеденные (12–13) часы.",
    "- Ввести утренние комбо (кофе + выпечка) для повышения среднего чека.",
    "- Рассмотреть расширение ассортимента сэндвичей (высокий чек, доля всего 15%).",
    "- В выходные снижать активность после 17:00 из-за падения выручки."
]
for line in conclusions:
    pdf.multi_cell(0, 7, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

# Визуализации
pdf.add_page()
pdf.set_font('DejaVu', 'B', 16)
pdf.cell(0, 10, 'Визуализации', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.ln(5)

graphs = [
    (figures['hourly'], 'Выручка по часам'),
    (figures['daily'], 'Выручка по дням недели'),
    (figures['categories'], 'Доля категорий в общей выручке'),
    (figures['avg_check'], 'Средний чек по времени суток'),
    (figures['heatmap'], 'Тепловая карта день × час')
]

for buf, caption in graphs:
    pdf.set_font('DejaVu', 'B', 12)
    pdf.cell(0, 8, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.image(buf, x=10, w=190)
    pdf.ln(5)

pdf.output('coffee_shop_report.pdf')
print("Готово! Отчёт сохранён как coffee_shop_report.pdf")