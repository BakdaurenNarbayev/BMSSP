from Block import BNode
from BBLL import BBLL

class BMSSP:
    def __init__(self, N, s):
        self.N = N
        self.s = s
        self.nodes = [BNode(float('inf')) for _ in range(N)]
        self.nodes[s].val = 0


if __name__ == "__main__":
    bmssp = BMSSP(10, 0)

    print("--- Empty BBLL ---")
    ds = BBLL(2, float('inf'), bmssp.nodes)
    ds.traverse()

    print("--- Inserting <1, 5> ---")
    ds.insert(1, 5)
    ds.traverse()

    print("--- Inserting <1, 3> ---")
    ds.insert(1, 3)
    ds.traverse()

    print("--- Inserting <2, 5> ---")
    ds.insert(2, 5)
    ds.traverse()

    print("--- Inserting <4, 1> ---")
    ds.insert(4, 1)
    ds.traverse()

    print("--- Deleting <2, 5> ---")
    ds.delete(2, 5)
    ds.traverse()
