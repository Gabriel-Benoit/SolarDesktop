from solar.math.physic.body import Body
import unittest


class TestBody(unittest.TestCase):
    def setUp(self) -> None:
        self.normal_v = (1, 2, 3)
        self.too_long_v = (1, 2, 3, 4)
        self.normal_mass = 50
        self.b_name = "I am a test"
        self.body = Body(self.normal_mass, self.normal_v,
                         self.normal_v, self.b_name)

    def test_negative_mass(self):
        with self.assertRaises(ValueError):
            Body(-5, self.normal_v, self.normal_v)

    def test_null_mass(self):
        with self.assertRaises(ValueError):
            Body(0, self.normal_v, self.normal_v)

    def test_4d_velocity(self):
        with self.assertRaises(ValueError):
            Body(5, self.normal_v, self.too_long_v)

    def test_4d_position(self):
        with self.assertRaises(ValueError):
            Body(5, self.too_long_v, self.normal_v)

    def test_jsonify(self):
        b = self.body
        self.assertEqual(b.jsonify(), {
                         "name": self.b_name, "position": self.normal_v, "velocity": self.normal_v, "mass": self.normal_mass})

    def test_flatten(self):
        b = self.body
        self.assertEqual(b.flatten(), (self.normal_mass,) + tuple(
            self.normal_v) + tuple(self.normal_v))
    # Getters

    def test_get_mass(self):
        self.assertEqual(self.body.mass, self.normal_mass)

    def test_get_v(self):
        self.assertTrue(all(b == v for b, v in zip(
            self.body.velocity, self.normal_v)))

    def test_get_pos(self):
        self.assertTrue(all(b == v for b, v in zip(
            self.body.position, self.normal_v)))

    # Setters
    def test_set_v(self):
        new = (3, 3, 3)
        self.body.velocity = new
        self.assertTrue(all(b == v for b, v in zip(
            self.body.velocity, new)))

    def test_set_p(self):
        new = (3, 3, 3)
        self.body.position = new
        self.assertTrue(all(b == v for b, v in zip(
            self.body.position, new)))

    def test_set_wrong_v(self):
        new = (3, 3, 3, 3)
        with self.assertRaises(ValueError):
            self.body.velocity = new

    def test_set_wrong_p(self):
        new = (3, 3, 3, 3)
        with self.assertRaises(ValueError):
            self.body.position = new

    def test_repr(self):
        mass = self.body.mass
        position = self.body.position
        velocity = self.body.velocity
        name = self.body.name
        expected = f'<Body: {name= }, {mass= }, {position= }, {velocity= }>'
        self.assertEqual(repr(self.body), expected)

    def tearDown(self) -> None:
        del self.body
        del self.b_name
        del self.normal_v
        del self.too_long_v
        del self.normal_mass
