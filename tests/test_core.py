import math
import unittest

from sparse_table import SparseTable


class TestSparseTable(unittest.TestCase):
    def test_range_minimum(self):
        st = SparseTable([3, 1, 4, 1, 5, 9, 2, 6], min)
        self.assertEqual(st.query(0, 8), 1)
        self.assertEqual(st.query(0, 1), 3)
        self.assertEqual(st.query(2, 5), 1)
        self.assertEqual(st.query(4, 8), 2)
        self.assertEqual(st.query(5, 6), 9)

    def test_range_maximum(self):
        st = SparseTable([3, 1, 4, 1, 5, 9, 2, 6], max)
        self.assertEqual(st.query(0, 8), 9)
        self.assertEqual(st.query(0, 2), 3)
        self.assertEqual(st.query(2, 4), 4)
        self.assertEqual(st.query(5, 8), 9)

    def test_single_element(self):
        st = SparseTable([42], min)
        self.assertEqual(st.query(0, 1), 42)

    def test_two_elements(self):
        st = SparseTable([7, 3], min)
        self.assertEqual(st.query(0, 2), 3)
        self.assertEqual(st.query(0, 1), 7)
        self.assertEqual(st.query(1, 2), 3)

    def test_all_equal(self):
        st = SparseTable([5, 5, 5, 5], max)
        self.assertEqual(st.query(1, 3), 5)
        self.assertEqual(st.query(0, 4), 5)

    def test_gcd_idempotent(self):
        from math import gcd
        data = [12, 18, 24, 9, 15]
        st = SparseTable(data, gcd)
        self.assertEqual(st.query(0, 3), 6)
        self.assertEqual(st.query(0, 5), 3)
        self.assertEqual(st.query(2, 4), 3)

    def test_full_range(self):
        st = SparseTable([5, 3, 7, 1, 9], min)
        self.assertEqual(st.query(0, 5), 1)

    def test_value_projection(self):
        people = [("alice", 30), ("bob", 25), ("carol", 35)]
        st = SparseTable(people, lambda a, b: a if a[1] < b[1] else b, value=lambda p: p[1])
        youngest = st.query(0, 3)
        self.assertEqual(youngest[0], "bob")
        self.assertEqual(youngest[1], 25)

    def test_value_projection_max(self):
        people = [("alice", 30), ("bob", 25), ("carol", 35)]
        st = SparseTable(people, lambda a, b: a if a[1] > b[1] else b, value=lambda p: p[1])
        oldest = st.query(0, 3)
        self.assertEqual(oldest[0], "carol")

    def test_power_of_two_length(self):
        st = SparseTable([8, 2, 6, 4], min)
        self.assertEqual(st.query(0, 4), 2)
        self.assertEqual(st.query(1, 3), 2)
        self.assertEqual(st.query(2, 4), 4)

    def test_invalid_range_empty(self):
        st = SparseTable([1, 2, 3], min)
        with self.assertRaises(IndexError):
            st.query(1, 1)

    def test_invalid_range_out_of_bounds(self):
        st = SparseTable([1, 2, 3], min)
        with self.assertRaises(IndexError):
            st.query(-1, 2)
        with self.assertRaises(IndexError):
            st.query(0, 4)

    def test_invalid_range_reversed(self):
        st = SparseTable([1, 2, 3], min)
        with self.assertRaises(IndexError):
            st.query(2, 1)

    def test_n_property(self):
        st = SparseTable([1, 2, 3], min)
        self.assertEqual(st.n, 3)

    def test_strings(self):
        st = SparseTable(["banana", "apple", "cherry"], min)
        self.assertEqual(st.query(0, 3), "apple")
        self.assertEqual(st.query(1, 2), "apple")

    def test_op_not_callable(self):
        with self.assertRaises(TypeError):
            SparseTable([1, 2, 3], "min")  # type: ignore[arg-type]

    def test_value_not_callable(self):
        with self.assertRaises(TypeError):
            SparseTable([1, 2, 3], min, value=5)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
