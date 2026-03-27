from .api_client import get_exchange_rate
from .converter import convert
from .utils import validate_amount, format_result
from .exceptions import APIError, CurrencyNotFoundError, InvalidAmountError


def main() -> None:
    print("Конвертер валют")

    try:
        amount = float(input("Введите сумму: "))
        base = (
            input("Введите код исходной валюты (например, USD): ")
            .strip()
            .upper()  # noqa: E501
        )
        target = (
            input("Введите код целевой валюты (например, RUB): ")
            .strip()
            .upper()  # noqa: E501
        )

        validate_amount(amount)
        rate = get_exchange_rate(base, target)
        converted_amount = convert(amount, rate)

        print(format_result(amount, base, converted_amount, target, rate))

    except ValueError:
        print("Некорректная сумма. Пожалуйста, введите число.")
    except InvalidAmountError as e:
        print(f"Ошибка: {e}")
    except CurrencyNotFoundError as e:
        print(f"Ошибка: {e}")
    except APIError as e:
        print(f"Ошибка при получении курса: {e}")


if __name__ == "__main__":
    main()
