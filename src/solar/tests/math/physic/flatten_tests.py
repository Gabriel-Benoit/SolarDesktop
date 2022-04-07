from functools import reduce
from solar.math.physic.body import Body, flatten
import unittest

from solar.math.tools.vector import Vector


class TestFlatten(unittest.TestCase):
    def setUp(self) -> None:
        self.masses = tuple(float(i+1) for i in range(15))
        self.vectors = tuple(tuple(float(j)
                             for j in range(i, i+3)) for i in range(15))
        self.bodies = [Body(i+1, list(range(i, i+3)),
                            list(range(i, i+3))) for i in range(15)]
        self.broken = list(self.bodies)
        self.broken[0] = "broken"

    def test_flatten_with_mass(self):
        b = self.bodies
        expected = Vector(*reduce(lambda acc, x: acc + x, tuple((m, x, y, z, x, y, z)
                                                                for m, (x, y, z) in zip(self.masses, self.vectors)), tuple()))
        self.assertEqual(flatten(b, False), expected)

    def test_flatten_with_split_mass(self):
        b = self.bodies
        expected = (Vector(*reduce(lambda acc, x: acc + x, tuple((x, y, z, x, y, z)
                                                                 for (x, y, z) in self.vectors), tuple())),
                    self.masses)
        self.assertEqual(flatten(b, True), expected)

    def test_broken_iter(self):
        b = self.broken
        with self.assertRaises(AssertionError):
            flatten(b)

    def test_empty_iter_without_split(self):
        self.assertEqual(flatten([], False), Vector())

    def test_empty_iter_with_split(self):
        self.assertEqual(flatten([], True), (Vector(), tuple()))

    def tearDown(self) -> None:
        del self.masses
        del self.vectors
        del self.bodies
        del self.broken
