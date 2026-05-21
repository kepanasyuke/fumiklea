from pathlib import Path

# Корневая директория проекта
ROOT_DIR = Path(__file__).parent.parent

# Директории
REPORTS_DIR = ROOT_DIR / "reports"
FONTS_DIR = ROOT_DIR / "fonts"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Пути к файлам
FONT_PATH = FONTS_DIR / "DejaVuSans.ttf"
PDF_PATH = REPORTS_DIR / "coffee_shop_report.pdf"

# Создаём все необходимые директории
for directory in [REPORTS_DIR, FONTS_DIR, TEMPLATES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
