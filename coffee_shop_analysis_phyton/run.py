#!/usr/bin/env python3
"""
Точка входа для генерации отчёта о продажах кофейни.
Запуск: 
  python run.py                    # Использовать синтетические данные (10k записей)
  python run.py --csv data.csv     # Загрузить данные из CSV файла
"""

import sys
import argparse
from pathlib import Path

# Добавляем src в путь для импорта
sys.path.append(str(Path(__file__).parent))

from src.analysis import generate_data, load_data_from_csv
from src.report_generator import generate_pdf_report
from src.config import FONT_PATH


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(description='Генерация отчёта о продажах кофейни')
    parser.add_argument('--csv', type=str, help='Путь к CSV файлу с реальными данными (опционально)')
    parser.add_argument('--records', type=int, default=10000, help='Количество синтетических записей (по умолчанию 10000)')
    args = parser.parse_args()
    
    print("🚀 Запуск генерации отчёта о продажах кофейни...")
    
    # Загрузка данных
    if args.csv:
        print(f"📂 Загрузка данных из CSV: {args.csv}")
        df = load_data_from_csv(args.csv)
        if df is None:
            print("❌ Ошибка при загрузке CSV файла.")
            return
    else:
        print(f"🔄 Генерация {args.records} синтетических записей...")
        df = generate_data(n_transactions=args.records)
    
    if df is None or df.empty:
        print("❌ Не удалось загрузить или сгенерировать данные.")
        return
    
    print(f"✅ Загружено {len(df)} записей")
    print(f"   Период: {df['date'].min().date()} — {df['date'].max().date()}")
    print(f"   Категории: {', '.join(df['category'].unique())}")

    # Генерация отчёта
    font_path = FONT_PATH if FONT_PATH.exists() else None
    pdf_path = generate_pdf_report(df, font_path=font_path)

    if pdf_path:
        print(f"\n✅ Отчёт успешно создан!")
        print(f"📄 Путь: {pdf_path}")
        print("🎉 Вы можете открыть его в любом PDF-просмотрщике.")
    else:
        print("\n❌ Не удалось создать отчёт. Проверьте логи ошибок.")


if __name__ == "__main__":
    main()
