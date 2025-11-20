from Block import Block
from RBT import RedBlackTree
from utils.MedianFinder import MedianFinder
import random

# Block-Based Linked List (BBLL)
class BBLL:
    def __init__(self, M, B, nodes):
        # D0: for batch prepends
        self.D0 = {}
        self.D0_bounds = RedBlackTree()

        # D1: maintains elements from insert operations
        self.B = B
        self.D1 = {B: Block()}
        
        # RB tree maintains upper bounds for D1
        self.D1_bounds = RedBlackTree()
        self.D1_bounds.insert(B)

        self.M = M  # maximum block size
        self.nodes = nodes  # reference to BMSSP nodes

    def delete(self, key, val):
        """Delete key/value pair."""
        D0_max_bound_node = self.D0_bounds._find_max(self.D0_bounds.root)
        if D0_max_bound_node is not None and val < D0_max_bound_node.value:
            bound = self.D0_bounds.search_bound(val)
            if bound not in self.D0:
                print(f"[Warning] D0: bound {bound} not found for value {val}.")
                return

            block = self.D0[bound]
            node = self.nodes[key]
            block.delete(node)

            # Delete the block if empty
            if block.is_empty():
                del self.D0[bound]
                self.D0_bounds.delete(bound)
            return

        # pair is in D1
        bound = self.D1_bounds.search_bound(val)
        if bound not in self.D1:
            print(f"[Warning] D1: bound {bound} not found for value {val}.")
            return

        block = self.D1[bound]
        node = self.nodes[key]
        block.delete(node)

        # Only delete the bound if it's not the sentinel
        if block.is_empty() and bound != self.B:
            del self.D1[bound]
            self.D1_bounds.delete(bound)

    def insert(self, key, new_val):
        """Insert or update a key/value pair."""
        node = self.nodes[key]

        if new_val >= node.val:
            return # no need to insert if value not improved

        # Remove from old block if present
        if node.next is not None:
            self.delete(key, node.val)

        bound = self.D1_bounds.search_bound(new_val)
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
        self.D1_bounds.delete(old_bound)

        # Define new bounds for the split blocks
        left_bound = median_value
        right_bound = old_bound

        # Step 4: Insert new bounds and blocks
        self.D1_bounds.insert(left_bound)
        self.D1_bounds.insert(right_bound)
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
        # Each block gets an upper bound equal to min value of the next block
        for i in range(len(blocks) - 1, -1, -1): # in reverse order
            if i == len(blocks) - 1:
                bound = self.find_global_min()
            else:
                bound = blocks[i + 1].get_min()
            
            self.D0[bound] = blocks[i]
            self.D0_bounds.insert(bound)

    def pull(self):
        """
        Pull: Retrieve the smallest M values from D0 ∪ D1.

        Returns:
            S_prime         : list of (key, val) pairs – the smallest M elements
            x : smallest remaining value in D0 ∪ D1 after deletion
        """

        M = self.M

        # -------------------------------
        # Step 1: Collect prefix blocks: S′0 from D0, S′1 from D1
        # -------------------------------
        S0 = self.collect_from_D0(M)
        S1 = self.collect_from_D1(M)

        S_all = S0 + S1       # raw elements
        total = len(S_all)

        # -------------------------------
        # Case 1: If all elements collected ≤ M → return all of them
        # -------------------------------
        if total <= M:
            # delete all collected elements
            for key, val in S_all:
                self.delete(key, val)

            return S_all, self.B

        # -------------------------------
        # Case 2: Need exactly M smallest values from S_all
        # -------------------------------
        # Extract M smallest values in O(M) expected time using Quickselect
        values = [(key, val) for key, val in S_all]

        # quickselect helper
        def quickselect(arr, k, key=lambda x: x[1]):
            if len(arr) == 1:
                return arr[0]
            pivot = random.choice(arr)
            pv = key(pivot)
            lows = [x for x in arr if key(x) < pv]
            highs = [x for x in arr if key(x) > pv]
            pivots = [x for x in arr if key(x) == pv]

            if k < len(lows):
                return quickselect(lows, k, key)
            elif k < len(lows) + len(pivots):
                return pivots[0]
            else:
                return quickselect(highs, k - len(lows) - len(pivots), key)

        # find threshold value (M-th smallest)
        threshold_pair = quickselect(values, M-1, key=lambda x: x[1])
        threshold_val = threshold_pair[1]

        # build S′ = M smallest elements
        # (stable, because each block keeps elements ≤ M)
        S_prime = [pair for pair in values if pair[1] < threshold_val]

        # fill remaining equal-to-threshold if needed
        if len(S_prime) < M:
            needed = M - len(S_prime)
            equal_vals = [pair for pair in values if pair[1] == threshold_val]
            S_prime.extend(equal_vals[:needed])

        # -------------------------------
        # Step 3: Delete S′ from D0 and D1
        # -------------------------------
        for key, val in S_prime:
            self.delete(key, val)
  
        return S_prime, self.find_global_min()
    
    def collect_from_D0(self, M):
        """Collect up to M values from prefix blocks in D0."""
        result = []
        inorder_bounds = self.D0_bounds._inorder_traversal_values(self.D0_bounds.root, [])

        for bound in inorder_bounds:
            block = self.D0[bound]
            for node in block.iterate():
                result.append((node.key, node.val))
                if len(result) >= M:
                    return result
        return result
    
    def collect_from_D1(self, M):
        """Collect up to M values from prefix blocks in D1."""
        result = []
        inorder_bounds = self.D1_bounds._inorder_traversal_values(self.D1_bounds.root, [])

        for bound in inorder_bounds:
            block = self.D1[bound]
            for node in block.iterate():
                result.append((node.key, node.val))
                if len(result) >= M:
                    return result
        return result
    
    def find_global_min(self):
        """Return the smallest value in D0 ∪ D1 in O(M) time."""
        if self.D0_bounds.root == None:
            D1_min_bound = self.D1_bounds._find_min(self.D1_bounds.root).value
            return self.D1[D1_min_bound].get_min()
        else:
            D0_min_bound = self.D0_bounds._find_min(self.D0_bounds.root).value
            if D0_min_bound == self.B and self.D0[D0_min_bound].is_empty():
                return self.B
            return self.D0[D0_min_bound].get_min()

    def traverse(self):
        """Traverse D0 then D1."""
        print("Traversing D0:")
        if not self.D0:
            print("D0 is empty.")
        else:
            bounds = self.D0_bounds._inorder_traversal_values(self.D0_bounds.root, [])
            print(f"Bounds: {bounds}")
            for bound in bounds:
                print(f"Bound {bound}:")
                self.D0[bound].traverse()

        print("\nTraversing D1:")
        if not self.D1:
            print("D1 is empty.")
        else:
            bounds = self.D1_bounds._inorder_traversal_values(self.D1_bounds.root, [])
            print(f"Bounds: {bounds}")
            for bound in bounds:
                print(f"Bound {bound}:")
                self.D1[bound].traverse()
        print()
