import unittest
from unittest.mock import patch, Mock
import requests
from currency_converter.src.api_client import get_exchange_rate
from currency_converter.src.exceptions import APIError, CurrencyNotFoundError


class TestApiClient(unittest.TestCase):
    @patch("currency_converter.src.api_client.requests.get")
    def test_successful_response(self, mock_get):
        # Mock the response
        mock_response = Mock()
        mock_response.json.return_value = {
            "rates": {"USD": 1.0, "EUR": 0.85, "RUB": 91.5}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        rate = get_exchange_rate("USD", "EUR")
        self.assertAlmostEqual(rate, 0.85)

    @patch("currency_converter.src.api_client.requests.get")
    def test_currency_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"rates": {"USD": 1.0, "EUR": 0.85}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(CurrencyNotFoundError) as cm:
            get_exchange_rate("USD", "RUB")
        self.assertIn("RUB", str(cm.exception))

    @patch("currency_converter.src.api_client.requests.get")
    def test_empty_currency(self, mock_get):
        with self.assertRaises(APIError):
            get_exchange_rate("", "EUR")

    @patch("currency_converter.src.api_client.requests.get")
    def test_empty_rates(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"rates": {}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(APIError):
            get_exchange_rate("USD", "EUR")

    @patch("currency_converter.src.api_client.requests.get")
    def test_invalid_rates_format(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"rates": "invalid"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(APIError):
            get_exchange_rate("USD", "EUR")

    @patch("currency_converter.src.api_client.requests.get")
    def test_api_request_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException(
            "Network error"
        )  # noqa: E501

        with self.assertRaises(APIError):
            get_exchange_rate("USD", "EUR")

    @patch("currency_converter.src.api_client.requests.get")
    def test_invalid_json(self, mock_get):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with self.assertRaises(APIError):
            get_exchange_rate("USD", "EUR")


if __name__ == "__main__":
    unittest.main()
