#!/usr/bin/env python3
import csv
import sys
from rich.console import Console
from rich.table import Table
from rich.text import Text

def main():
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'anime_top.csv'
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"Файл {csv_file} не найден.")
        sys.exit(1)

    if not rows:
        print("Нет данных для отображения.")
        return

    console = Console()
    table = Table(title="🏆 Топ-аниме", title_style="bold magenta")
    for field in reader.fieldnames:
        table.add_column(field.capitalize(), style="cyan")

    for row in rows[:50]:  # ограничим 50 строками
        # Сделаем рейтинг цветным
        rating = float(row['rating'])
        rating_style = "green" if rating >= 9.0 else "yellow" if rating >= 8.5 else "white"
        table.add_row(
            row['title'],
            Text(row['rating_str'], style=rating_style),
            row['rating'],
            row['year'],
            row['genres']
        )

    console.print(table)

if __name__ == "__main__":
    main()
    