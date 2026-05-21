import base64
import logging
import sys
from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import weasyprint

# Добавляем корневую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from src.analysis import generate_data, analyze_and_get_figures
from src.config import PDF_PATH, TEMPLATES_DIR, FONT_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fig_to_base64(fig: plt.Figure) -> str:
    """Конвертирует объект matplotlib Figure в строку base64 с обработкой ошибок."""
    try:
        if fig is None:
            logger.warning("Попытка конвертировать None объект Figure")
            return ""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=150)
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f"data:image/png;base64,{img_data}"
    except Exception as e:
        logger.error(f"Ошибка конвертации графика в base64: {e}")
        return ""


def generate_pdf_report(df, font_path=None):
    """Генерирует PDF-отчёт с использованием HTML-шаблона, Jinja2 и WeasyPrint."""
    logger.info("Начало формирования PDF-отчёта.")

    try:
        figures, insights = analyze_and_get_figures(df, font_path=font_path)

        if not figures:
            logger.error("Не удалось построить графики. Завершение работы.")
            return None

        figures_b64 = {}
        for name, fig in figures.items():
            img_b64 = fig_to_base64(fig)
            if img_b64:
                figures_b64[name] = img_b64
            else:
                logger.warning(f"График '{name}' не был сконвертирован в base64")

        if not figures_b64:
            logger.error("Не удалось сконвертировать ни один график в base64. Завершение работы.")
            return None

        # Загружаем и рендерим шаблон
        template_loader = FileSystemLoader(searchpath=str(TEMPLATES_DIR))
        template_env = Environment(loader=template_loader)
        template = template_env.get_template("report_template.html")

        html_out = template.render(insights=insights, figures=figures_b64)

        # CSS для печати
        css = CSS(string='@page { size: A4; margin: 2cm; }')

        # Генерируем PDF
        HTML(string=html_out).write_pdf(PDF_PATH, stylesheets=[css])
        logger.info(f"✅ PDF-отчёт успешно сохранён: {PDF_PATH}")

        return PDF_PATH

    except weasyprint.CSS.parsing.ParserError as e:
        logger.error(f"Ошибка парсинга CSS: {e}. Возможно, ошибка в синтаксисе CSS.")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка при генерации отчёта: {e}")
        return None


if __name__ == "__main__":
    # Для тестирования модуля
    df = generate_data()
    generate_pdf_report(df, font_path=FONT_PATH if FONT_PATH.exists() else None)
