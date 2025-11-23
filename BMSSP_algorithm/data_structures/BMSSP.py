import math
from collections import deque
from BMSSP_algorithm.data_structures.Block import BNode
from BMSSP_algorithm.data_structures.BBLL import BBLL

class BMSSP:
    def __init__(self, N, s):
        self.N = N
        self.k = math.floor(math.pow(math.log2(N), 1/3))
        self.t = math.floor(math.pow(math.log2(N), 2/3))
        self.s = s
        self.BNodes = [BNode(_, float('inf')) for _ in range(N)]
        self.BNodes[s].val = 0
        self.edges = [list() for _ in range(self.N)] # list of tuples

    def find_pivots(self, B, S):
        W = set(S)
        W_prev = set(S)

        # k relaxations
        for i in range(1, self.k + 1):
            W_curr = set()
            
            for u in W_prev:
                for v, w in self.edges[u]:
                    if self.BNodes[u].val + w <= self.BNodes[v].val:
                        self.BNodes[v].val = self.BNodes[u].val + w

                    if self.BNodes[u].val + w < B:
                        W_curr.add(v)

            W |= W_curr

            if len(W) > self.k * len(S):
                return set(S), W

            W_prev = W_curr

        # Build forest F
        children = {u: [] for u in W}

        for u in W:
            for v, w in self.edges[u]:
                if v in W and self.BNodes[v].val == self.BNodes[u].val + w:
                    children[u].append(v)

        # Roots = nodes with no parent
        has_parent = set()
        for u in children:
            for v in children[u]:
                has_parent.add(v)

        roots = [u for u in W if u not in has_parent]

        # Compute subtree sizes
        subtree_size = {}

        for r in roots:
            size = 0
            q = deque([r])
            while q:
                x = q.popleft()
                size += 1
                for ch in children[x]:
                    q.append(ch)
            subtree_size[r] = size

        # P = roots in S that have subtree ≥ k
        P = {u for u in S if u in subtree_size and subtree_size[u] >= self.k}

        return P, W

if __name__ == "__main__":
    bmssp = BMSSP(10, 0)

    print("-" * 25 + " Empty BBLL " + "-" * 25)
    ds = BBLL(3, float('inf'), bmssp.BNodes)
    ds.traverse()

    print("-" * 25 + " Inserting <1, 5> " + "-" * 25)
    ds.insert(1, 5)
    ds.traverse()

    print("-" * 25 + " Inserting <1, 3> " + "-" * 25)
    ds.insert(1, 3)
    ds.traverse()

    print("-" * 25 + " Inserting <2, 5> " + "-" * 25)
    ds.insert(2, 5)
    ds.traverse()

    print("-" * 25 + " Inserting <4, 1> " + "-" * 25)
    ds.insert(4, 1)
    ds.traverse()

    print("-" * 25 + " Inserting <5, 5> " + "-" * 25)
    ds.insert(5, 5)
    ds.traverse()

    print("-" * 25 + " Deleting <2, 5> " + "-" * 25)
    ds.delete(2, 5)
    ds.traverse()

    print("-" * 25 + " Batch Prepending <3, 3>, <6, 6>, <7, 7>, <8, 8>, <9, 9> " + "-" * 25)
    bmssp.BNodes[3].val = -5
    bmssp.BNodes[6].val = -4
    bmssp.BNodes[7].val = -3
    bmssp.BNodes[8].val = -2
    bmssp.BNodes[9].val = -1
    L = [bmssp.BNodes[9]]
    ds.batch_prepend(L)
    ds.traverse()
    L = [bmssp.BNodes[7], bmssp.BNodes[8], bmssp.BNodes[3], bmssp.BNodes[6]]
    ds.batch_prepend(L)
    ds.traverse()

    print("-" * 25 + " Pulling " + "-" * 25)
    S, x = ds.pull()
    print(f"S: {S}")
    print(f"x: {x}")

    ds.traverse()

    bmssp = BMSSP(6, 0)

    # Build small graph
    bmssp.edges[0] = [(1,1), (2,2)]
    bmssp.edges[1] = [(3,1)]
    bmssp.edges[2] = [(3,1)]
    bmssp.edges[3] = [(4,1)]
    bmssp.edges[4] = [(5,1)]

    # Reset distances
    for node in bmssp.BNodes:
        node.val = float('inf')
    bmssp.BNodes[0].val = 0

    S = {0}
    B = 10

    P, W = bmssp.find_pivots(B, S)
    print("Pivots:", P)
    print("W:", W)