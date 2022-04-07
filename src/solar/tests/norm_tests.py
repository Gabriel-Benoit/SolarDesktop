import unittest
from solar import norm
from solar.math.tools.vector import Vector


class TestNorm(unittest.TestCase):
    def setUp(self) -> None:
        self.v1 = Vector(1, 2, 3, 4)
        self.v2 = Vector(5, 6, 7, 8)
        self.v3 = Vector(-1, -2, -3, -4)

    def tearDown(self) -> None:
        del self.v1
        del self.v2
        del self.v3

    def testNorm2(self):
        self.assertEqual(norm(self.v1, 2), (30)**(1/2))

    def testOppositeVectorNorm(self):
        self.assertEqual(norm(self.v1, 2), norm(self.v3, 2))

    def testNegativeDeg(self):
        with self.assertRaises(ValueError):
            norm(self.v1, -5)
