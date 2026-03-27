# anime_parser

Парсер топа аниме с сайта [shikimori.one](https://shikimori.one/animes).

## Установка

```bash
cd anime_parser
make install
```

Если `make` недоступен, можно установить вручную:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Запуск

```bash
python3 src/parser.py --pages 2 --min-rating 8.0 --output-file anime_top.csv
```

Аргументы:
- `--pages` — количество страниц для парсинга (по умолчанию `2`)
- `--min-rating` — минимальный рейтинг для фильтрации (по умолчанию `8.0`)
- `--output-file` — имя CSV-файла для сохранения результата (по умолчанию `anime_top.csv`)

## Запуск через Makefile

```bash
make run
```

## Линтинг

```bash
make lint
```

## Тестирование

```bash
make test
```

## Структура проекта

- `src/parser.py` — основной скрипт для парсинга и сохранения данных
- `tests/test_parser.py` — модульные тесты
- `requirements.txt` — зависимости
- `Makefile` — цели `install` и `test`
