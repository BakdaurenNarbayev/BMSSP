from Block import Block
from RBT import RedBlackTree

# Class for the block-based linked list data structure
class BBLL:
    # constructor for the block-based linked list data structure
    def __init__(self, M, B):
        # two sequences of blocks
        # blocks are maintained in the sorted order
        self.D0 = {} # only maintains elements from batch prepends, initialize D0 with an empty sequence
        self.D1 = {Block(B)} # maintains elements from insert operations, initialize D1 with a single empty block with upper bound B
        self.bounds = RedBlackTree() # dynamically maintains the upper bounds for blocks in D1
        self.bounds.insert(B) # insert the first upper bound
        self.M = M # set the parameter M