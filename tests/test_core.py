# python -m unittest discover -s tests

import unittest
from bot.utils import format_datetime

class TestUtils(unittest.TestCase):
    def test_format_datetime(self):
        dt = "2024-09-01T12:34:56Z"
        formatted = format_datetime(dt)
        self.assertEqual(formatted, "2024-09-01 12:34 UTC")

if __name__ == "__main__":
    unittest.main()
