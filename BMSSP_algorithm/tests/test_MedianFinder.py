import pytest
from BMSSP_algorithm.utils.MedianFinder import MedianFinder

def test_single_element():
    assert MedianFinder.find_median([5]) == 5

def test_two_elements():
    assert MedianFinder.find_median([1, 3]) == 2  # average of 1 and 3

def test_odd_number_of_elements():
    values = [7, 1, 3]
    assert MedianFinder.find_median(values) == 3

def test_even_number_of_elements():
    values = [4, 2, 9, 6]
    # sorted: [2, 4, 6, 9] → median = (4 + 6) / 2 = 5
    assert MedianFinder.find_median(values) == 5

def test_unsorted_random_values():
    values = [10, 1, 7, 3, 8, 5, 2]
    assert MedianFinder.find_median(values) == 5  # sorted median

def test_negative_numbers():
    values = [-5, -1, -3]
    assert MedianFinder.find_median(values) == -3

def test_duplicates():
    values = [5, 5, 5, 5]
    assert MedianFinder.find_median(values) == 5

def test_large_random_list():
    import statistics, random
    values = [random.randint(-1000, 1000) for _ in range(5001)]
    assert MedianFinder.find_median(values) == statistics.median(values)

def test_even_large_random_list():
    import statistics, random
    values = [random.randint(-1000, 1000) for _ in range(5000)]
    assert MedianFinder.find_median(values) == statistics.median(values)
