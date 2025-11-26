import unittest
from benchmark.methods.BMSSP_utils.utils.MedianFinder import MedianFinder
import random
import statistics


class TestMedianFinder(unittest.TestCase):

    def test_single_element(self):
        self.assertEqual(MedianFinder.find_median([5]), 5)

    def test_two_elements(self):
        self.assertEqual(MedianFinder.find_median([1, 3]), 2)

    def test_odd_number_of_elements(self):
        values = [7, 1, 3]
        self.assertEqual(MedianFinder.find_median(values), 3)

    def test_even_number_of_elements(self):
        values = [4, 2, 9, 6]
        # sorted: [2, 4, 6, 9] → median = (4 + 6) / 2 = 5
        self.assertEqual(MedianFinder.find_median(values), 5)

    def test_unsorted_random_values(self):
        values = [10, 1, 7, 3, 8, 5, 2]
        self.assertEqual(MedianFinder.find_median(values), 5)

    def test_negative_numbers(self):
        values = [-5, -1, -3]
        self.assertEqual(MedianFinder.find_median(values), -3)

    def test_duplicates(self):
        values = [5, 5, 5, 5]
        self.assertEqual(MedianFinder.find_median(values), 5)

    def test_large_random_list(self):
        values = [random.randint(-1000, 1000) for _ in range(5001)]
        self.assertEqual(MedianFinder.find_median(values), statistics.median(values))

    def test_even_large_random_list(self):
        values = [random.randint(-1000, 1000) for _ in range(5000)]
        self.assertEqual(MedianFinder.find_median(values), statistics.median(values))


if __name__ == "__main__":
    unittest.main()
