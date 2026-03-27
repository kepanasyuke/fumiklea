import requests
from .exceptions import APIError, CurrencyNotFoundError


def get_exchange_rate(base_currency: str, target_currency: str) -> float:
    """
    Fetch the exchange rate from base_currency to target_currency using
    exchangerate-api.com API.

    Args:
        base_currency (str): The base currency code (e.g., 'USD').
        target_currency (str): The target currency code (e.g., 'RUB').

    Returns:
        float: The exchange rate.

    Raises:
        APIError: If there's an issue with the API request or response.
        CurrencyNotFoundError: If the target currency is not found in the
        rates.
    """
    if not base_currency or not target_currency:
        raise APIError("Currency codes cannot be empty")

    base_url = "https://api.exchangerate-api.com/v4/latest"  # noqa: E501
    url = f"{base_url}/{base_currency}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise APIError(f"Failed to fetch exchange rate: {e}") from e
    except ValueError as e:
        raise APIError(f"Invalid JSON response from API: {e}") from e

    rates = data.get("rates")
    if not isinstance(rates, dict):
        raise APIError(
            "Unexpected API response format: 'rates' missing or not a dict"
        )  # noqa: E501
    if not rates:
        raise APIError("No exchange rates available")

    if target_currency not in rates:
        raise CurrencyNotFoundError(target_currency)

    return rates[target_currency]
