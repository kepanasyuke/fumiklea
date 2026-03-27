class APIError(Exception):

    def __init__(
        self,
        message: str = "An error occurred while communicating "
        "with the external API.",
    ):
        super().__init__(message)


class CurrencyNotFoundError(APIError):

    def __init__(self, currency: str = "", message: str = None):
        if message is None:
            message = f"The requested currency '{currency}' is not found in the API response."  # noqa: E501
        super().__init__(message)
        self.currency = currency


class InvalidAmountError(Exception):

    def __init__(
        self,
        amount=None,
        message: str = "The amount is invalid " "(must be positive number).",
    ):
        if amount is not None:
            message = (
                f"The amount {amount} is invalid " "(must be positive number)."
            )  # noqa: E501
            super().__init__(message)
            self.amount = amount
