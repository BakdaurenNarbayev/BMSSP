import random

class MedianFinder():
    def find_median(values):
        """Find the median of node values in O(n) expected time using Quickselect."""
        # Quickselect helper
        def quickselect(arr, k):
            if len(arr) == 1:
                return arr[0]
            pivot = random.choice(arr)
            lows = [x for x in arr if x < pivot]
            highs = [x for x in arr if x > pivot]
            pivots = [x for x in arr if x == pivot]

            if k < len(lows):
                return quickselect(lows, k)
            elif k < len(lows) + len(pivots):
                return pivot
            else:
                return quickselect(highs, k - len(lows) - len(pivots))

        # Get median position(s)
        n = len(values)
        if n % 2 == 1:
            return quickselect(values, n // 2)
        else:
            left = quickselect(values, n // 2 - 1)
            right = quickselect(values, n // 2)
            return (left + right) / 2