from copy import deepcopy
from solar.exceptions import BodyError
import unittest
from solar.solar_simulator import SOLARSimulator
import logging
logging.disable(logging.CRITICAL)


class TestSOLARSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        from solar import presets  # nopep8
        cls.system = presets.convert_bodylikes([
            presets.sun,
            presets.mercury,
            presets.venus,
            presets.earth,
            presets.mars,
            presets.jupiter,
            presets.saturn,
            presets.uranus,
            presets.neptune,
            presets.pluto
        ])

    @classmethod
    def tearDownClass(cls) -> None:
        del cls.system

    def test_nagative_duration(self):
        with self.assertRaises(ValueError):
            SOLARSimulator(self.system, -50, 10)

    def test_too_big_step(self):
        with self.assertRaises(ValueError):
            SOLARSimulator(self.system, 50, 100)

    def test_same_bodies(self):
        sys = tuple(deepcopy(self.system[0]) for _ in range(5))
        with self.assertRaises(BodyError):
            SOLARSimulator(sys, 50, 10)

    def test_wrong_callback_arg_match(self):
        with self.assertRaises(TypeError):
            sim = SOLARSimulator(self.system, 500, 100)
            sim.run_simulation(lambda: None, lambda: None)

    def test_show_results_without_run_sim(self):
        with self.assertRaises(RuntimeError):
            sim = SOLARSimulator(self.system, 500, 100)
            sim.show_results()
