"""
Unit Test Suite for Calculator Application.
"""

import math
import os
import unittest
from calculator_engine import CalculatorEngine
from history_manager import HistoryManager
from settings_manager import SettingsManager


class TestCalculatorEngine(unittest.TestCase):
    def setUp(self):
        self.engine = CalculatorEngine()

    def test_basic_arithmetic(self):
        self.assertEqual(self.engine.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.engine.evaluate("(10 - 2) / 4"), 2)
        self.assertEqual(self.engine.evaluate("5 − 2 × 3"), -1)
        self.assertEqual(self.engine.evaluate("10 ÷ 2"), 5)

    def test_trigonometry(self):
        # DEG mode
        self.engine.set_angle_unit("DEG")
        self.assertAlmostEqual(self.engine.evaluate("sin(90)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("cos(0)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("tan(45)"), 1.0)

        # RAD mode
        self.engine.set_angle_unit("RAD")
        self.assertAlmostEqual(self.engine.evaluate("sin(pi/2)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("cos(pi)"), -1.0)

        # GRAD mode
        self.engine.set_angle_unit("GRAD")
        self.assertAlmostEqual(self.engine.evaluate("sin(100)"), 1.0)

    def test_scientific_functions(self):
        self.assertEqual(self.engine.evaluate("sqrt(16)"), 4)
        self.assertEqual(self.engine.evaluate("2^3"), 8)
        self.assertEqual(self.engine.evaluate("5!"), 120)
        self.assertEqual(self.engine.evaluate("log(100)"), 2)
        self.assertAlmostEqual(self.engine.evaluate("ln(e)"), 1.0)

    def test_logic_operations(self):
        self.assertEqual(self.engine.evaluate("12 AND 10"), 8)
        self.assertEqual(self.engine.evaluate("12 OR 10"), 14)
        self.assertEqual(self.engine.evaluate("12 XOR 10"), 6)
        self.assertEqual(self.engine.evaluate("10 MOD 3"), 1)
        self.assertEqual(self.engine.evaluate("1 LSH 3"), 8)
        self.assertEqual(self.engine.evaluate("16 RSH 2"), 4)

    def test_number_bases(self):
        self.assertEqual(CalculatorEngine.to_hex(255), "0xFF")
        self.assertEqual(CalculatorEngine.to_bin(10), "0b1010")
        self.assertEqual(CalculatorEngine.to_oct(8), "0o10")

    def test_errors(self):
        with self.assertRaises(ValueError):
            self.engine.evaluate("1 / 0")
        with self.assertRaises(ValueError):
            self.engine.evaluate("sqrt(-5)")


class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.filename = "test_hist_temp.json"
        self.history = HistoryManager(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_add_and_clear_history(self):
        self.history.add_entry("5 + 5", "10", "Standard")
        self.assertEqual(len(self.history.get_history()), 1)
        self.assertEqual(self.history.get_history()[0]["expression"], "5 + 5")

        self.history.clear_history()
        self.assertEqual(len(self.history.get_history()), 0)


class TestSettingsManager(unittest.TestCase):
    def setUp(self):
        self.filename = "test_sett_temp.json"
        self.settings = SettingsManager(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_settings_save_and_load(self):
        self.settings.set("precision", 8)
        self.assertEqual(self.settings.get("precision"), 8)

        # Reload from disk
        new_settings = SettingsManager(self.filename)
        self.assertEqual(new_settings.get("precision"), 8)


if __name__ == "__main__":
    unittest.main()
