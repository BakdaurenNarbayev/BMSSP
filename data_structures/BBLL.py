from Block import Block
from RBT import RedBlackTree

# Block-Based Linked List (BBLL)
class BBLL:
    def __init__(self, M, B, nodes):
        # D0: for batch prepends
        self.D0 = {}

        # D1: maintains elements from insert operations
        self.D1 = {B: Block()}

        # RB tree maintains upper bounds for D1
        self.bounds = RedBlackTree()
        self.bounds.insert(B)

        self.M = M  # maximum block size
        self.nodes = nodes  # reference to BMSSP nodes

    def delete(self, key, val):
        """Delete key/value pair."""
        bound = self.bounds.search_bound(val)
        if bound not in self.D1:
            print(f"[Warning] Bound {bound} not found for value {val}.")
            return

        block = self.D1[bound]
        node = self.nodes[key]
        block.delete(node)

        # Only delete the bound if it's not the sentinel
        if block.is_empty() and bound != float('inf'):
            del self.D1[bound]
            self.bounds.delete(bound)

    def insert(self, key, new_val):
        """Insert or update a key/value pair."""
        node = self.nodes[key]

        if new_val >= node.val and node.val != float('inf'):
            return # no need to insert if value not improved
        
        if new_val == float('inf') and node.val == float('inf') and node.next is not None: # if both are 'inf', and node is in a block
            return # no need to insert if value not improved

        # Remove from old block if present
        if node.next is not None:
            self.delete(key, node.val)

        bound = self.bounds.search_bound(new_val)
        block = self.D1[bound]
        block.insert(node)
        node.val = new_val

        if block.get_size() > self.M:
            self.split(block, bound)

    def split(self, block, bound):
        """Splits block into two when size > M."""
        print(f"Splitting block with bound {bound} (size={block.get_size()})")
        # Placeholder — implement balancing strategy later

    def traverse(self):
        """Traverse D0 then D1."""
        print("Traversing D0:")
        if not self.D0:
            print("D0 is empty.")
        else:
            for bound in self.D0:
                self.D0[bound].traverse()

        print("\nTraversing D1:")
        if not self.D1:
            print("D1 is empty.")
        else:
            bounds = self.bounds._inorder_traversal_values(self.bounds.root, [])
            print(f"Bounds: {bounds}")
            for bound in bounds:
                print(f"Bound {bound}:")
                self.D1[bound].traverse()
        print()
