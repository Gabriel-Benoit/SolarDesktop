import unittest
from solar import exclude


class TestExclude(unittest.TestCase):
    def setUp(self) -> None:
        self.lst1 = tuple(str(i) for i in range(10))
        self.in_lst1 = "5"
        self.lst2 = tuple(str(i) for i in range(15, 25))

    def tearDown(self) -> None:
        del self.lst1
        del self.in_lst1
        del self.lst2

    def testExcludePresentElement(self):
        tmp = list(self.lst1)
        tmp.remove(self.in_lst1)
        excpected = tuple(tmp)
        result = tuple(exclude(self.lst1, self.in_lst1))
        self.assertEqual(result, excpected)

    def testExcludeAbsentElement(self):
        excpected = self.lst2
        result = tuple(exclude(self.lst2, self.in_lst1))
        self.assertEqual(result, excpected)
