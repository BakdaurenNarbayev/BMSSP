from Block import Block
from RBT import RedBlackTree

# Class for the block-based linked list data structure
class BBLL:
    # constructor for the block-based linked list data structure
    def __init__(self, M, B, nodes):
        # two sequences of blocks
        # blocks are maintained in the sorted order
        self.D0 = {} # only maintains elements from batch prepends, initialize D0 with an empty sequence
        self.D1 = {B : Block(M)} # maintains elements from insert operations, initialize D1 with a single empty block with upper bound B
        self.bounds = RedBlackTree() # dynamically maintains the upper bounds for blocks in D1
        self.bounds.insert(B) # insert the first upper bound
        self.M = M # set the parameter M
        self.nodes = nodes # reference to the BMSSP nodes

    # delete the key/value pair
    def delete(self, key, val):
        bound = self.bounds.search_bound(val) # identifies the bound for to be deleted val
        block = self.D1[bound] # identifies the block for the bound
        node = self.nodes[key] # identifies the associated node
        block.delete(node) # deletes the node from the block in O(1)
        if block.is_empty(): # if the block becomes empty after deletion, remove its upper bound from the bounds
            self.bounds.delete(bound)
    
    # insert a key/value pair
    def insert(self, key, val):
        node = self.nodes[key] # identifies the associated node
        if val < node.val: # checks if the key/value pair has been added to the BBLL and new value is less than the current value
            self.delete(key, val) # deletes the key/value pair from its current block
            bound = self.bounds.search_bound(val) # identifies the bound for to be inserted val
            block = self.D1[bound] # identifies the block for the bound
            node.val = val # update the value of the node
            block.insert(node) # inserts the node to the block in O(1)
            if block.get_size() > self.M: # split the block if its size exceeds the size limit M 
                self.split(block)

    def split(self, block):
        return