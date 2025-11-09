from Block import BNode

# Class for a list of BNodes
class SSP:
    # constructor for the dictionary
    # N is the number of nodes
    # s is the index of the source node
    def __init__(self, N, s):
        self.N = N
        self.s = s
        self.nodes = [BNode(float('inf'))] * N
        self.nodes[s].val = 0