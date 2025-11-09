class BNode:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None

# CircularDoublyLinkedList implementation of Block
class Block:
    def __init__(self, B):
        self.head = None
        self.B = B

    def insert(self, node):
        """Insert a node at the end."""
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
            return

        # If deleting the head
        if node == self.head:
            self.head = node.next

        node.prev.next = node.next
        node.next.prev = node.prev

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