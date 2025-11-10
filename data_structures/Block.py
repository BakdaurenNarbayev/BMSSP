import random

class BNode:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None


# Circular Doubly Linked List implementation of Block
class Block:
    def __init__(self):
        self.head = None
        self.size = 0

    def insert(self, node):
        """Insert a node at the end."""
        if node is None:
            return

        self.size += 1

        if self.head is None:
            node.next = node.prev = node
            self.head = node
            return

        tail = self.head.prev
        tail.next = node
        node.prev = tail
        node.next = self.head
        self.head.prev = node

    def delete(self, node):
        """Delete a node by reference."""
        if self.head is None or node is None:
            return

        # If only one node
        if node == self.head and node.next == self.head:
            self.head = None
            self.size = 0
            return

        # If deleting the head
        if node == self.head:
            self.head = node.next

        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def find_median(self):
        """Find the median of node values in O(n) expected time using Quickselect."""
        if self.is_empty():
            return None

        # Step 1: Gather all values from the circular linked list
        values = []
        current = self.head
        while True:
            values.append(current.val)
            current = current.next
            if current == self.head:
                break

        # Step 2: Quickselect helper
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

        # Step 3: Get median position(s)
        n = len(values)
        if n % 2 == 1:
            return quickselect(values, n // 2)
        else:
            left = quickselect(values, n // 2 - 1)
            right = quickselect(values, n // 2)
            return (left + right) / 2

    def traverse(self):
        """Traverse the block forward."""
        if not self.head:
            print("Block is empty.")
            return

        current = self.head
        while True:
            print(f"({current.val})", end=" → ")
            current = current.next
            if current == self.head:
                break
        print("(head)")

    def is_empty(self):
        return self.head is None

    def get_size(self):
        return self.size
    