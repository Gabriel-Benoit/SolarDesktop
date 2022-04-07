import unittest
from solar import get_magnitude
from solar.math.tools.vector import Vector


class TestGetMagnitude(unittest.TestCase):
    def setUp(self) -> None:
        self.v1 = Vector(1, 2, 3, 4)
        self.v2 = Vector(5, 6, 7, 8)
        self.v3 = Vector(5, 6, 7, 8, 9)

    def tearDown(self) -> None:
        del self.v1
        del self.v2
        del self.v3

    def testSameVectorMagnitude(self):
        self.assertEqual(get_magnitude(self.v1, self.v1), 0)

    def testNormalDiffVectorMagnitude(self):
        self.assertEqual(get_magnitude(self.v1, self.v2), 8)

    def testDiffLenVectorMagnitude(self):
        with self.assertRaises(ValueError):
            get_magnitude(self.v1, self.v3)
