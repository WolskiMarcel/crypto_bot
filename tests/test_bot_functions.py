import unittest
from src.app import parse_chart_args

class TestBotFunctions(unittest.TestCase):
    def test_parse_chart_args_single_argument(self):
        """
        Test of the parse_chart_args function with a single argument.
        We expect the symbol to be converted to uppercase, and the remaining parameters
        to take their default values.
        """
        args = ["btc"]
        expected = {
            "symbol": "BTC",
            "target": "USDT",
            "days": 30,
            "interval": "1d",
            "kolor": "royalblue"
        }
        result = parse_chart_args(args)
        self.assertEqual(result, expected)

    def test_parse_chart_args_two_arguments_days(self):
        """
        Test of the parse_chart_args function when providing two arguments,
        where the second one ends with "d" and is treated as the number of days.
        """
        args = ["eth", "7d"]
        expected = {
            "symbol": "ETH",
            "target": "USDT",
            "days": 7,
            "interval": "1d",
            "kolor": "royalblue"
        }
        result = parse_chart_args(args)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
