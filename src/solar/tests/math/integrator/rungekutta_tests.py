from typing import Type
import unittest
import numpy as np
from solar.math.integrator.rungekutta import ARK, ERK4
from solar.math.tools.vector import Vector


class TestERK4(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.f = lambda t, s: Vector(t+s[0])
        cls.y = Vector(0)
        cls.TestRK = type("TestRK", (ARK,), dict())

    @classmethod
    def tearDownClass(cls) -> None:
        del cls

    def test_zero_steps(self):
        with self.assertRaises(ValueError):
            ERK4(self.f, self.y, 5, 10, 0)

    def test_negative_steps(self):
        with self.assertRaises(ValueError):
            ERK4(self.f, self.y, 5, 10, -5)

    def test_same_start_and_end(self):
        with self.assertRaises(ValueError):
            ERK4(self.f, self.y, 5, 5, 3)

    def test_wrong_A(self):
        self.TestRK.A = np.array([
            [1, 2], [3, 4]
        ])
        self.TestRK.b = [1, 2, 4]
        self.TestRK.c = [1, 2, 3]
        with self.assertRaises(ValueError):
            t = self.TestRK(self.f, self.y, 5, 10, 3)
            list(t.run_simulation())

    def test_malformed_A(self):
        self.TestRK.A = np.array([
            [1, 2], [3, 4, 3]
        ])
        self.TestRK.b = [1, 2]
        self.TestRK.c = [1, 2]
        with self.assertRaises(ValueError):
            t = self.TestRK(self.f, self.y, 5, 10, 3)
            list(t.run_simulation())
