import unittest
from unittest.mock import patch, Mock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import parser  

class TestFetchPage(unittest.TestCase):
    @patch('parser.requests.Session.post')
    def test_successful_response(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'data': {
                'Page': {
                    'media': [{'id': 1, 'title': {'romaji': 'Test Anime'}}]
                }
            }
        }
        mock_post.return_value = mock_response

        result = parser.fetch_page(1)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title']['romaji'], 'Test Anime')

    @patch('parser.requests.Session.post')
    def test_network_error(self, mock_post):
        mock_post.side_effect = parser.requests.RequestException('Network error')
        with patch('builtins.print'):
            result = parser.fetch_page(1)
        self.assertIsNone(result)

    @patch('parser.requests.Session.post')
    def test_malformed_json(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError('Invalid JSON')
        mock_post.return_value = mock_response

        with patch('builtins.print'):
            result = parser.fetch_page(1)
        self.assertIsNone(result)


class TestExtractAnimeInfo(unittest.TestCase):
    def test_full_data(self):
        anime = {
            'title': {'romaji': 'Shingeki no Kyojin'},
            'averageScore': 87,
            'startDate': {'year': 2013},
            'genres': ['Action', 'Drama']
        }
        result = parser.extract_anime_info(anime)
        self.assertEqual(result['title'], 'Shingeki no Kyojin')
        self.assertEqual(result['rating'], 8.7)
        self.assertEqual(result['rating_str'], '8.7')
        self.assertEqual(result['year'], '2013')
        self.assertEqual(result['genres'], 'Action, Drama')

    def test_missing_fields(self):
        anime = {}
        result = parser.extract_anime_info(anime)
        self.assertEqual(result['title'], 'N/A')
        self.assertEqual(result['rating'], 0.0)
        self.assertEqual(result['rating_str'], '0')
        self.assertEqual(result['year'], 'N/A')
        self.assertEqual(result['genres'], '')

    def test_no_score(self):
        anime = {'title': {'romaji': 'Test'}, 'averageScore': None}
        result = parser.extract_anime_info(anime)
        self.assertEqual(result['rating'], 0.0)
        self.assertEqual(result['rating_str'], '0')

    def test_no_year(self):
        anime = {'title': {'romaji': 'Test'}, 'startDate': {}}
        result = parser.extract_anime_info(anime)
        self.assertEqual(result['year'], 'N/A')


if __name__ == '__main__':
    unittest.main()