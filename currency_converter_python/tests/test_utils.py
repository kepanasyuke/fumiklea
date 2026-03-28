import unittest
from currency_converter.src.utils import validate_amount, format_result
from currency_converter.src.exceptions import InvalidAmountError


class TestValidateAmount(unittest.TestCase):
    def test_valid_amount(self):
        # Should not raise
        validate_amount(10.0)
        validate_amount(0.0)
        validate_amount(0.01)

    def test_negative_amount(self):
        with self.assertRaises(InvalidAmountError) as cm:
            validate_amount(-5.0)
        self.assertIn("-5.0", str(cm.exception))

        with self.assertRaises(InvalidAmountError) as cm:
            validate_amount(-0.01)
        self.assertIn("-0.01", str(cm.exception))


class TestFormatResult(unittest.TestCase):
    def test_formatting(self):
        result = format_result(100.0, "USD", 250.0, "EUR", 2.5)
        expected = "100.00 USD = 250.00 EUR (курс: 1 USD = 2.5000 EUR)"
        self.assertEqual(result, expected)

    def test_formatting_fractions(self):
        result = format_result(123.45, "RUB", 152.34, "USD", 1.234)
        expected = "123.45 RUB = 152.34 USD (курс: 1 RUB = 1.2340 USD)"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
