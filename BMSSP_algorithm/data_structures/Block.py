from BMSSP_algorithm.utils.MedianFinder import MedianFinder

class BNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


# Circular Doubly Linked List implementation of Block
class Block:
    def __init__(self):
        self.head = None
        self.size = 0
        self.max_val = float('-inf')
        self.min_val = float('inf')

    def insert(self, node):
        """Insert a node at the end."""
        if node is None:
            return

        # Update size and extreme vals
        self.size += 1
        if node.val > self.max_val:
            self.max_val = node.val
        if node.val < self.min_val:
            self.min_val = node.val

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
        
        # If node is not currently linked into this block, ignore it
        # (e.g., node never inserted or already removed)
        if node.next is None or node.prev is None:
            return

        # If only one node
        if node == self.head and node.next == self.head:
            self.head = None
            self.size = 0
            self.max_val = float('-inf')
            self.min_val = float('inf')
            return

        # If deleting the head
        if node == self.head:
            self.head = node.next

        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

        # Recompute extreme values only if needed
        if node.val == self.max_val:
            self.recompute_max()

        if node.val == self.min_val:
            self.recompute_min()

    def recompute_max(self):
        """Recompute max_val by traversing all nodes (O(n))."""
        if self.is_empty():
            self.max_val = float('-inf')
            return

        current = self.head
        new_max = current.val
        while True:
            if current.val > new_max:
                new_max = current.val
            current = current.next
            if current == self.head:
                break
        self.max_val = new_max

    def recompute_min(self):
        """Recompute min_val by traversing all nodes (O(n))."""
        if self.is_empty():
            self.min_val = float('inf')
            return

        current = self.head
        new_min = current.val
        while True:
            if current.val < new_min:
                new_min = current.val
            current = current.next
            if current == self.head:
                break
        self.min_val = new_min

    def get_max(self):
        """Return the maximum value in the block."""
        return self.max_val
    
    def get_min(self):
        """Return the minimum value in the block."""
        return self.min_val
    
    def find_median(self):
        if self.is_empty():
            return None

        # Gather all values from the circular linked list
        values = []
        current = self.head
        while True:
            values.append(current.val)
            current = current.next
            if current == self.head:
                break

        return MedianFinder.find_median(values)
    
    def find_median_index(self):
        if self.is_empty():
            return None

        # Gather all values from the circular linked list
        values = []
        current = self.head
        while True:
            values.append(current.key)
            current = current.next
            if current == self.head:
                break

        return MedianFinder.find_median(values)
    
    def find_candidate_index(self):
        if self.is_empty():
            return None
        
        candidate = self.get_min()

        # Gather all values from the circular linked list
        values = []
        current = self.head
        while True:
            if current.val == candidate:
                values.append(current.key)
            current = current.next
            if current == self.head:
                break

        return min(values)
    
    def iterate(self):
        """Iterate through all nodes in a circular block."""
        if self.head is None:
            return
        current = self.head
        while True:
            yield current
            current = current.next
            if current == self.head:
                break

    def traverse(self):
        """Traverse the block forward."""
        if not self.head:
            print("Block is empty.")
            return

        current = self.head
        while True:
            print(f"({current.key}, {current.val})", end=" → ")
            current = current.next
            if current == self.head:
                break
        print("(head)")

    def is_empty(self):
        return self.head is None

    def get_size(self):
        return self.size
    