# Expected CSV format:
# The CSV file must have a header row with at least the following columns:
# - title (название аниме)
# - rating (числовой рейтинг, например 8.7)
# Other columns are allowed and will be displayed as well.
# Example:
# title,rating,year
# "Naruto",8.2,2002
# "Attack on Titan",9.1,2013

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
                {headers}
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
</body>
</html>
"""

with open(csv_file, 'r', encoding='utf-8') as csv_f:
    reader = csv.DictReader(csv_f)
    rows = list(reader)
    headers = reader.fieldnames

header_html = ''.join(f'<th>{h}</th>' for h in headers)
rows_html = ''
for row in rows:
    if 'rating' not in row or not row['rating']:
        continue  # Skip rows without a 'rating' key or empty rating
    try:
        rating = float(row['rating'])
        if rating >= 9.0:
            rating_class = 'rating-high'
        elif rating >= 8.5:
            rating_class = 'rating-mid'
        else:
            rating_class = ''
    except (ValueError, TypeError):
        continue  # Skip rows with invalid rating
    row_html = '<tr>'
    for h in headers:
        if h == 'rating':
            row_html += f'<td class="{rating_class}">{row[h]}</td>'
        else:
            row_html += f'<td>{row[h]}</td>'
    row_html += '</tr>'
    rows_html += row_html

full_html = html_template.format(headers=header_html, rows=rows_html)

with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False, encoding='utf-8') as html_f:
    html_f.write(full_html)
    tmp_path = html_f.name

webbrowser.open('file://' + tmp_path)