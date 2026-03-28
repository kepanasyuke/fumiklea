from .exceptions import APIError, InvalidAmountError


def convert(amount: float, rate: float) -> float:
    """
    Convert an amount using the given exchange rate.

    Args:
        amount (float): The amount in the base currency. Must be non-negative.
        rate (float): Exchange rate (target per base). Must be positive.

    Returns:
        float: Converted amount in the target currency, rounded to 2 decimal
        places.

    Raises:
        InvalidAmountError: If amount is negative.
        APIError: If rate is not positive.
    """
    if amount < 0:
        raise InvalidAmountError(amount)
    if rate <= 0:
        raise APIError("Exchange rate must be positive")
    return round(amount * rate, 2)
