from benchmark.methods.BMSSP_utils.data_structures.Block import Block, BNode
from benchmark.methods.BMSSP_utils.data_structures.RBT import RedBlackTree
from benchmark.methods.BMSSP_utils.utils.MedianFinder import MedianFinder
import random, math

# Block-Based Linked List (BBLL)
class BBLL:
    def __init__(self, M, B, N):
        # Redefine max bound
        self.B = B

        # D0: for batch prepends
        self.D0 = {}
        self.D0_bounds = RedBlackTree()

        # D1: maintains elements from insert operations
        self.D1 = {self.B: Block()}
        
        # RB tree maintains upper bounds for D1
        self.D1_bounds = RedBlackTree()
        self.D1_bounds.insert(self.B)

        self.M = M  # maximum block size
        self.nodes = [BNode(v, float('inf')) for v in range(N)]

        #print("NEW D")
        #print(B)
        #print(self.B)
        #self.traverse()

    def delete(self, key, val):
        """Delete key/value pair."""
        #print("DELETE FROM D")
        #print(f"key = {key}, val = {val}")
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

        D0_max_bound_node = self.D0_bounds._find_max(self.D0_bounds.root)
        if D0_max_bound_node is not None and val < D0_max_bound_node.value:
            bound = self.D0_bounds.search_bound(val)
            if bound is None:
                bound = D0_max_bound_node.value
                
            if bound is None or bound not in self.D0:
                self.D0_bounds._inorder_traversal_values()
                #self.traverse()
                print(f"[Warning] D0: bound {bound} not found for value {val}.")
                #print(self.D0_bounds._inorder_traversal_values())
                #self.traverse()
                return

            block = self.D0[bound]
            node = self.nodes[key]
            block.delete(node)

            # Delete the block if empty
            if block.is_empty():
                del self.D0[bound]
                self.D0_bounds.delete(bound)

            #print(self.D0_bounds._inorder_traversal_values())
            #self.traverse()
            return

        # pair is in D1
        bound = self.D1_bounds.search_bound(val)
        if bound is None:
            max_node = self.D1_bounds._find_max(self.D1_bounds.root)
            bound = max_node.value if max_node is not None else None

        if bound is None or bound not in self.D1:
            print(f"[Warning] D1: bound {bound} not found for value {val}.")
            #print(self.D0_bounds._inorder_traversal_values())
            #self.traverse()
            return

        block = self.D1[bound]
        node = self.nodes[key]
        block.delete(node)

        # Only delete the bound if it's not the sentinel
        if block.is_empty() and bound != self.B:
            del self.D1[bound]
            self.D1_bounds.delete(bound)

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

    def insert(self, key, new_val):
        """Insert or update a key/value pair."""
        node = self.nodes[key]
        old_val = node.val

        #print("INSERT TO D")
        #print(f"key = {key}, new_val = {new_val}, old_val = {old_val}")
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

        # Only improve
        if new_val >= old_val:
            #print(self.D0_bounds._inorder_traversal_values())
            #self.traverse()
            return

        # Remove from old block if present
        if node.next is not None:
            self.delete(key, old_val)

        # Now update to the new, improved value
        node.val = new_val

        # Find appropriate bound; if no bound > new_val, use the max bound
        bound = self.D1_bounds.search_bound(new_val)
        if bound is None:
            max_node = self.D1_bounds._find_max(self.D1_bounds.root)
            bound = max_node.value if max_node is not None else self.B

        block = self.D1[bound]
        block.insert(node)

        if block.get_size() > self.M:
            self.split(block, bound)

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

    def split(self, block, old_bound):
        """
        Split a block into two when its size exceeds M.
        Uses the Block.find_median() function (O(M) expected time).
        """
        #print("SPLIT IN D")
        #print(f"block = {block}, old_bound = {old_bound}")
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

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
        if old_bound != self.B:
            self.D1_bounds.delete(old_bound)

        # Define new bounds for the split blocks
        left_bound = median_value
        right_bound = old_bound

        # Step 4: Insert new bounds and blocks
        self.D1_bounds.insert(left_bound)
        if old_bound != self.B:
            self.D1_bounds.insert(right_bound)
        self.D1[left_bound] = left_block
        self.D1[right_bound] = right_block

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

    def batch_prepend(self, L):
        """
        BatchPrepend(L):
        If len(L) ≤ M → one new block at the start of D0.
        Else → recursively split L using medians into O(L/M) blocks, 
        each with ≤ ceil(M/2) elements.
        Time: O(L log(L/M)).
        """
        #print("BATCH_PREPEND IN D")
        #print(f"L = {L}")
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()
        
        n = len(L)
        if n == 0:
            #print(self.D0_bounds._inorder_traversal_values())
            #self.traverse()
            return
        
        L_nodes = list()
        for (v, d_v) in L:
            self.nodes[v].val = d_v
            L_nodes.append(self.nodes[v])

        def recursive_partition(nodes):
            """Recursively partition arr into blocks of size ≤ ceil(M/2)."""
            if len(nodes) <= self.M:
                sorted_nodes = sorted(nodes, key=lambda node: node.val)
                block = Block()
                for node in sorted_nodes:
                    block.insert(node)
                return [block]

            # Find median and split around it
            median_value = MedianFinder.find_median([node.val for node in nodes])
            left = [x for x in nodes if x.val < median_value]
            right = [x for x in nodes if x.val >= median_value]

            # Recursively build smaller blocks
            return recursive_partition(left) + recursive_partition(right)

        # Step 1: Split L into multiple blocks
        blocks = recursive_partition(L_nodes)

        # Step 2: Prepend blocks to D0
        # Each block gets an upper bound equal to min value of the next block
        for i in range(len(blocks) - 1, -1, -1): # in reverse order
            if i == len(blocks) - 1:
                bound = self.find_global_min()
            else:
                bound = blocks[i + 1].get_min()
            
            self.D0[bound] = blocks[i]
            self.D0_bounds.insert(bound)

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

    def pull(self):
        """
        Pull: Retrieve the smallest M values from D0 ∪ D1.

        Returns:
            S_prime : set of (key, val) pairs – the smallest M elements
            x       : smallest remaining value in D0 ∪ D1 after deletion
        """
        M = self.M

        #print("PULL FROM D")
        #print(f"M = {M}")
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()

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
        if total < M:
            # delete all collected elements
            for key, val in S_all:
                self.delete(key, val)

            S_set = {key for (key, val) in S_all}
            #print(self.D0_bounds._inorder_traversal_values())
            #self.traverse()
            return S_set, self.B

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

        S_set = {key for (key, val) in S_prime}

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()
  
        return S_set, self.find_global_min()
    
    def collect_from_D0(self, M):
        """Collect up to M values from prefix blocks in D0."""
        result = []
        inorder_bounds = self.D0_bounds._inorder_traversal_values()

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
        inorder_bounds = self.D1_bounds._inorder_traversal_values()

        for bound in inorder_bounds:
            block = self.D1[bound]
            for node in block.iterate():
                result.append((node.key, node.val))
                if len(result) >= M:
                    return result
        return result
    
    def find_global_min(self):
        """Return the smallest value in D0 ∪ D1 in O(M) time."""
        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()
        candidate = self.B

        # Check D0's smallest bound
        if self.D0_bounds.root is not None:
            min_bound_node = self.D0_bounds._find_min(self.D0_bounds.root)
            if min_bound_node is not None:
                #print(self.D0_bounds._inorder_traversal_values())
                #self.traverse()
                block = self.D0[min_bound_node.value]
                if not block.is_empty():
                    potential = block.get_min()
                    if potential < candidate:
                        candidate = potential

        # Check D1's smallest bound
        if self.D1_bounds.root is not None:
            min_bound_node = self.D1_bounds._find_min(self.D1_bounds.root)
            if min_bound_node is not None:
                block = self.D1[min_bound_node.value]
                if not block.is_empty():
                    potential = block.get_min()
                    if potential < candidate:
                        candidate = potential

        #print(self.D0_bounds._inorder_traversal_values())
        #self.traverse()
        return candidate

    def traverse(self):
        """Pretty-#print the structure of D0 and D1 in a clean, readable format."""

        def format_block(block):
            if block is None or block.is_empty():
                return "[]"
            vals = []
            for n in block.iterate():
                vals.append(f"{n.key}:{n.val}")
            return "[" + ", ".join(vals) + "]"

        print("\n=== BBLL Structure ===")

        # ---- D0 ----
        print("D0:")
        print(self.D0_bounds._inorder_traversal_values())
        if self.D0_bounds.is_empty():
            print("  (empty)")
        else:
            bounds = self.D0_bounds._inorder_traversal_values()
            for b in bounds:
                blk = self.D0[b]
                print(f"  bound {b}: {format_block(blk)}")

        # ---- D1 ----
        print("\nD1:")
        print(self.D1_bounds._inorder_traversal_values())
        if self.D1_bounds.is_empty():
            print("  (empty)  <-- SHOULD NOT HAPPEN (sentinel always exists)")
        else:
            bounds = self.D1_bounds._inorder_traversal_values()
            for b in bounds:
                blk = self.D1[b]
                print(f"  bound {b}: {format_block(blk)}")

        print("======================\n")

    def is_empty(self):
        if not self.D0_bounds.is_empty():
            return False

        # D1 should contain exactly 1 bound (sentinel B)
        # If it has more than 1, D is not empty
        if self.D1_bounds.get_size() > 1:
            return False

        # Check sentinel block is empty
        sentinel_block = self.D1[self.B]
        return sentinel_block.is_empty()
    
    def _check_invariants(self):
        # D0: bounds in tree == keys in dict
        d0_tree = set(self.D0_bounds._inorder_traversal_values()) \
                if not self.D0_bounds.is_empty() else set()
        d0_dict = set(self.D0.keys())

        assert d0_tree == d0_dict, f"D0 mismatch: tree={d0_tree}, dict={d0_dict}"

        # D1: tree bounds == dict keys AND sentinel B must exist in both
        d1_tree = set(self.D1_bounds._inorder_traversal_values())
        d1_dict = set(self.D1.keys())

        #print(self.B)
        #print(d1_tree)
        #print(d1_dict)
        assert self.B in d1_tree and self.B in d1_dict, "Sentinel B missing"
        assert d1_tree == d1_dict, f"D1 mismatch: tree={d1_tree}, dict={d1_dict}"

