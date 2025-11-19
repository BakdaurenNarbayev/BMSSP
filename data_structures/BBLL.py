from Block import Block
from RBT import RedBlackTree
from utils.MedianFinder import MedianFinder

# Block-Based Linked List (BBLL)
class BBLL:
    def __init__(self, M, B, nodes):
        # D0: for batch prepends
        self.D0 = {}
        self.D0_bounds = list()

        # D1: maintains elements from insert operations
        self.B = B
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
        if block.is_empty() and bound != self.B:
            del self.D1[bound]
            self.bounds.delete(bound)

    def insert(self, key, new_val):
        """Insert or update a key/value pair."""
        node = self.nodes[key]

        if new_val >= node.val:
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

    def split(self, block, old_bound):
        """
        Split a block into two when its size exceeds M.
        Uses the Block.find_median() function (O(M) expected time).
        """
        if block.is_empty():
            return

        # Step 1: Find median value using Block's O(M) method
        median_value = block.find_median()

        # Step 2: Partition all nodes into two new blocks
        left_block = Block()
        right_block = Block()

        current_node = block.head
        while current_node:
            next_node = current_node.next  # Save next pointer before reassignment

            if current_node.val < median_value:
                left_block.insert(current_node)
            else:
                right_block.insert(current_node)

            current_node = next_node
            if current_node == block.head:
                break

        # Step 3: Update D1 and bounds
        # Remove old bound from D1 and RedBlackTree
        del self.D1[old_bound]
        self.bounds.delete(old_bound)

        # Define new bounds for the split blocks
        left_bound = median_value
        right_bound = old_bound

        # Step 4: Insert new bounds and blocks
        self.bounds.insert(left_bound)
        self.bounds.insert(right_bound)
        self.D1[left_bound] = left_block
        self.D1[right_bound] = right_block

    def batch_prepend(self, L):
        """
        BatchPrepend(L):
        If len(L) ≤ M → one new block at the start of D0.
        Else → recursively split L using medians into O(L/M) blocks, 
        each with ≤ ceil(M/2) elements.
        Time: O(L log(L/M)).
        """
        n = len(L)
        if n == 0:
            return

        def recursive_partition(nodes):
            """Recursively partition arr into blocks of size ≤ ceil(M/2)."""
            if len(nodes) <= self.M:
                block = Block()
                for node in nodes:
                    block.insert(node)
                return [block]

            # Find median and split around it
            median_value = MedianFinder.find_median([node.val for node in nodes])
            left = [x for x in nodes if x.val < median_value]
            right = [x for x in nodes if x.val >= median_value]

            # Recursively build smaller blocks
            return recursive_partition(left) + recursive_partition(right)

        # Step 1: Split L into multiple blocks
        blocks = recursive_partition(L)

        # Step 2: Prepend blocks to D0
        # Each block gets an upper bound equal to its max value
        for block in blocks[::-1]: # in reverse order
            max_val = block.get_max()
            self.D0[max_val] = block
            self.D0_bounds.append(max_val)

    def traverse(self):
        """Traverse D0 then D1."""
        print("Traversing D0:")
        if not self.D0:
            print("D0 is empty.")
        else:
            for bound in self.D0_bounds[::-1]:
                print(f"Bound {bound}:")
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
