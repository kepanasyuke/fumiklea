import csv
import sys
import webbrowser
import tempfile

csv_file = sys.argv[1] if len(sys.argv) > 1 else 'anime_top.csv'

html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Топ-аниме</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .rating-high {{ color: green; font-weight: bold; }}
        .rating-mid {{ color: orange; }}
    </style>
</head>
<body>
    <h1>🏆 Топ-аниме (рейтинг ≥ 8.0)</h1>
    <table>
        <thead>
            <tr>
                {}
            </tr>
        </thead>
        <tbody>
            {}
        </tbody>
    </table>
</body>
</html>
"""

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    headers = reader.fieldnames

# Генерируем таблицу
header_html = ''.join(f'<th>{h}</th>' for h in headers)
rows_html = ''
for row in rows:
    rating = float(row['rating'])
    rating_class = 'rating-high' if rating >= 9.0 else 'rating-mid' if rating >= 8.5 else ''
    row_html = '<tr>'
    for h in headers:
        if h == 'rating':
            row_html += f'<td class="{rating_class}">{row[h]}</td>'
        else:
            row_html += f'<td>{row[h]}</td>'
    row_html += '</tr>'
    rows_html += row_html

full_html = html_template.format(header_html, rows_html)

with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as f:
    f.write(full_html)
    tmp_path = f.name

webbrowser.open('file://' + tmp_path)