import unittest
from currency_converter.src.converter import convert
from currency_converter.src.exceptions import InvalidAmountError, APIError


class TestConverter(unittest.TestCase):
    def test_convert_positive(self):
        self.assertAlmostEqual(convert(100, 2.5), 250.0)
        self.assertAlmostEqual(convert(50, 0.5), 25.0)
        self.assertAlmostEqual(convert(123.45, 1.234), 152.34)  # Test rounding

    def test_convert_zero(self):
        self.assertAlmostEqual(convert(0, 2.5), 0.0)

    def test_convert_negative_amount(self):
        with self.assertRaises(InvalidAmountError):
            convert(-100, 2.5)

    def test_convert_zero_rate(self):
        with self.assertRaises(APIError):
            convert(100, 0)

    def test_convert_negative_rate(self):
        with self.assertRaises(APIError):
            convert(100, -2)


if __name__ == "__main__":
    unittest.main()
