from Block import Block
from RBT import RedBlackTree

# Class for the block-based linked list data structure
class BBLL:
    # constructor for the block-based linked list data structure
    def __init__(self, M, B, nodes):
        # two sequences of blocks
        # blocks are maintained in the sorted order
        self.D0 = {} # only maintains elements from batch prepends, initialize D0 with an empty sequence
        self.D1 = {B : Block(B)} # maintains elements from insert operations, initialize D1 with a single empty block with upper bound B
        self.bounds = RedBlackTree() # dynamically maintains the upper bounds for blocks in D1
        self.bounds.insert(B) # insert the first upper bound
        self.M = M # set the parameter M
        self.nodes = nodes # reference to the BMSSP nodes

    # delete the key/value pair ⟨key, val⟩
    def delete(self, key, val):
        bound = self.bounds.search_bound(key) # identifies bound for to be deleted key
        block = self.D1[bound] # identifies block for the bound
        node = self.nodes[key] # identifies the associated node
        block.delete(node) # deletes the node from the block in O(1)
        if block.is_empty(): # if the block becomes empty after deletion, remove its upper bound from the bounds
            self.bounds.delete(bound)