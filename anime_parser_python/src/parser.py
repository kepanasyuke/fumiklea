import argparse
import csv
import sys
import time
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import subprocess
import shutil

def show_ascii_art():
    if shutil.which('cowsay'):
        subprocess.run(['cowsay', 'Топ-аниме загружен!'])
    elif shutil.which('figlet'):
        subprocess.run(['figlet', 'ANIME TOP'])
    else:
        print("""
        ╔══════════════════════════════════╗
        ║        АНИМЕ ТОП-ЛИСТ            ║
        ╚══════════════════════════════════╝
        """)

GRAPHQL_URL = 'https://graphql.anilist.co'
DELAY = 0.5
DEFAULT_PAGES = 2
DEFAULT_MIN_RATING = 8.0
DEFAULT_OUTPUT_FILE = 'anime_top.csv'
FIELDNAMES = ['title', 'rating_str', 'rating', 'year', 'genres']


def create_session(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=['GET', 'POST'],
        backoff_factor=backoff_factor,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session


def fetch_page(page: int, session: Optional[requests.Session] = None) -> Optional[List[Dict]]:
    animes = None
    session = session or create_session()
    query = """
    query ($page: Int, $perPage: Int) {
      Page(page: $page, perPage: $perPage) {
        media(type: ANIME, sort: SCORE_DESC) {
          title { romaji }
          averageScore
          startDate { year }
          genres
        }
      }
    }
    """
    variables = {
        'page': page,
        'perPage': 50
    }
    try:
        response = session.post(
            GRAPHQL_URL,
            json={'query': query, 'variables': variables},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        media_list = data.get('data', {}).get('Page', {}).get('media', [])
        if media_list:
            animes = media_list
        else:
            print(f"Страница {page}: нет данных")
    except requests.RequestException as error:
        print(f"Ошибка загрузки страницы {page}: {error}")
    except (KeyError, ValueError) as e:
        print(f"Страница {page}: ошибка обработки данных: {e}")
    return animes


def extract_anime_info(anime: Dict) -> Dict[str, object]:
    title = anime.get('title', {}).get('romaji', 'N/A')
    raw_score = anime.get('averageScore')
    if raw_score is not None:
        rating = raw_score / 10.0
        rating_str = f"{rating:.1f}"
    else:
        rating = 0.0
        rating_str = '0'

    year_obj = anime.get('startDate', {})
    year = str(year_obj.get('year')) if year_obj.get('year') else 'N/A'
    genres_list = anime.get('genres', [])
    genres = ', '.join(genres_list)

    result = {
        'title': title,
        'rating_str': rating_str,
        'rating': rating,
        'year': year,
        'genres': genres,
    }
    return result


def parse_anime(pages: int, min_rating: float, output_file: str) -> None:
    result = []
    session = create_session()

    for page in range(1, pages + 1):
        animes = fetch_page(page, session)
        if animes is None:
            continue

        print(f"Страница {page}: получено {len(animes)} аниме.")

        for anime in animes:
            info = extract_anime_info(anime)
            if info['rating'] >= min_rating:
                result.append(info)

        time.sleep(DELAY)

    if not result:
        print(f"\nФильтрация (рейтинг ≥ {min_rating}): осталось 0 аниме.")
        print("Нет данных для отображения.")
        return

    print(f"\nФильтрация (рейтинг ≥ {min_rating}): осталось {len(result)} аниме.")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(result)
    print(f"Результаты сохранены в {output_file}")
    return


def main() -> None:
    parser = argparse.ArgumentParser(description='Парсер топ-аниме с AniList API')
    parser.add_argument('--pages', type=int, default=DEFAULT_PAGES,
                        help=f'Количество страниц (по умолчанию {DEFAULT_PAGES})')
    parser.add_argument('--min-rating', type=float, default=DEFAULT_MIN_RATING,
                        help=f'Минимальный рейтинг (по умолчанию {DEFAULT_MIN_RATING})')
    parser.add_argument('--output-file', type=str, default=DEFAULT_OUTPUT_FILE,
                        help=f'Имя выходного CSV-файла (по умолчанию {DEFAULT_OUTPUT_FILE})')
    args = parser.parse_args()

    parse_anime(args.pages, args.min_rating, args.output_file)
    show_ascii_art()

if __name__ == '__main__':
    main()