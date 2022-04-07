import unittest

from solar.types import SingletonMeta


class TestSingletonMeta(unittest.TestCase):
    def setUp(self) -> None:
        # Creating a new class type singleton
        self.c1_type = SingletonMeta("singleton", (),
                                     {
            "__init__": lambda self: None,
            '__metaclass__': SingletonMeta
        })
        # instatiating first time
        self.c1 = self.c1_type()

    def tearDown(self) -> None:
        del self.c1_type
        del self.c1

    def testSingleton(self):
        c2 = self.c1_type()
        self.assertEqual(self.c1, c2)
