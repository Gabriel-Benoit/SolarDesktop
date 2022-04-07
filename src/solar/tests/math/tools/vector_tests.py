import unittest
from solar.math.tools.vector import EMPTY, Vector, Vector3D


class TestVector(unittest.TestCase):
    def setUp(self):
        self.null_vector = Vector()
        self.vector_1 = Vector(1, 2, 3, 4)
        self.vector_2 = Vector(4, 3, 2, 1)
        self.different_dim_vector = Vector(5, 4, 3, 2, 1)

    def tearDown(self):
        del self.null_vector
        del self.vector_1
        del self.vector_2
        del self.different_dim_vector

    #-----------------------------------------------#
    #       Operations over vectors test suite      #
    #-----------------------------------------------#
    def test_add_same_dim(self):
        self.assertEqual(self.vector_1 + self.vector_2, Vector(5, 5, 5, 5))

    def test_add_different_dim(self):
        with self.assertRaises(ValueError):
            self.vector_1 + self.different_dim_vector

    def test_add_null(self):
        self.assertEqual(self.vector_1 + self.null_vector, self.vector_1)

    def test_minus_same_dim(self):
        self.assertEqual(self.vector_1 - self.vector_2, Vector(-3, -1, 1, 3))

    def test_minus_different_dim(self):
        with self.assertRaises(ValueError):
            self.vector_1 - self.different_dim_vector

    def test_minus_null(self):
        self.assertEqual(self.vector_1 - self.null_vector, self.vector_1)

    def test_scalar_product_same_dim(self):
        self.assertEqual(self.vector_1 @ self.vector_2, 20)

    def test_scalar_product_different_dim(self):
        with self.assertRaises(ValueError):
            self.vector_1 @ self.different_dim_vector

    def test_scalar_product_null(self):
        self.assertEqual(self.vector_1 @ self.null_vector, 0)

    def test_product(self):
        self.assertEqual(self.vector_1 * 2, Vector(2, 4, 6, 8))

    def test_product_null(self):
        self.assertEqual(self.null_vector * 5, EMPTY)

    # --------------------------------------#
    #       Other methods test suite        #
    #---------------------------------------#

    def test_concat_normal(self):
        res = Vector.concat(self.vector_1, self.vector_2,
                            self.different_dim_vector)
        expectation = Vector(*(tuple(self.vector_1) + tuple(self.vector_2) +
                               tuple(self.different_dim_vector)))
        self.assertEqual(res, expectation)

    def test_concat_with_null(self):
        res = Vector.concat(self.vector_1, self.null_vector)
        expectation = Vector(*(tuple(self.vector_1) + tuple(self.null_vector)))
        self.assertEqual(res, expectation)

    def test_sum_same_dim(self):
        ls = [self.vector_1, self.vector_1, self.vector_2, self.vector_2]
        self.assertEqual(Vector.sum(ls), Vector(10, 10, 10, 10))

    def test_sum_different_dim(self):
        with self.assertRaises(ValueError):
            Vector.sum(
                (self.vector_1, self.different_dim_vector))

    def test_sum_null(self):
        self.assertEqual(Vector.sum(
            (self.null_vector, self.null_vector)), EMPTY)

    def test_sum_empty(self):
        self.assertEqual(Vector.sum([]), EMPTY)

    def test_equal_with_other_type(self):
        self.assertFalse(self.vector_1 == (1, 2, 3, 4))

    def test_repr(self):
        expected = f"<Vector: (1, 2, 3, 4)>"
        self.assertEqual(repr(self.vector_1), expected)

    def test_get_bracket_out_of_range(self):
        with self.assertRaises(IndexError):
            self.vector_1[10]

    def test_get_slice_negative(self):
        with self.assertRaises(IndexError):
            self.vector_1[-3:2]

    def test_get_slice_out_of_range(self):
        with self.assertRaises(IndexError):
            self.vector_1[0:10]


class TestVector3D(unittest.TestCase):
    def setUp(self) -> None:
        self.v = Vector3D(1, 2, 3)

    def tearDown(self) -> None:
        return super().tearDown()

    def test_get_x(self):
        self.assertEqual(self.v.x, 1)

    def test_get_y(self):
        self.assertEqual(self.v.y, 2)

    def test_get_z(self):
        self.assertEqual(self.v.z, 3)

    def test_repr(self):
        expected = "<Vector3D: (1, 2, 3)>"
        self.assertEqual(repr(self.v), expected)
