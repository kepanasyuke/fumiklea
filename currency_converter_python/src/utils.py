from .exceptions import InvalidAmountError


def validate_amount(amount: float) -> None:
    """
    Validate that the amount is non-negative.

    Args:
        amount (float): The amount to validate.

    Raises:
        InvalidAmountError: If amount is negative.
    """
    if amount < 0:
        raise InvalidAmountError(amount)


def format_result(
    amount: float, base: str, converted: float, target: str, rate: float
) -> str:
    """
    Format the conversion result into a readable string.

    Args:
        amount (float): Original amount in base currency.
        base (str): Base currency code.
        converted (float): Converted amount in target currency.
        target (str): Target currency code.
        rate (float): Exchange rate used.

    Returns:
        str: Formatted result string.
    """
    return (
        f"{amount:.2f} {base} = {converted:.2f} {target} "
        f"(курс: 1 {base} = {rate:.4f} {target})"
    )
