from Block import BNode
from BBLL import BBLL

class BMSSP:
    def __init__(self, N, s):
        self.N = N
        self.s = s
        self.nodes = [BNode(_, float('inf')) for _ in range(N)]
        self.nodes[s].val = 0


if __name__ == "__main__":
    bmssp = BMSSP(10, 0)

    print("--- Empty BBLL ---")
    ds = BBLL(3, float('inf'), bmssp.nodes)
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

    print("--- Inserting <5, 5> ---")
    ds.insert(5, 5)
    ds.traverse()

    print("--- Deleting <2, 5> ---")
    ds.delete(2, 5)
    ds.traverse()

    print("--- Batch Prepending <3, 3>, <6, 6>, <7, 7>, <8, 8>, <9, 9> ---")
    bmssp.nodes[3].val = -5
    bmssp.nodes[6].val = -4
    bmssp.nodes[7].val = -3
    bmssp.nodes[8].val = -2
    bmssp.nodes[9].val = -1
    L = [bmssp.nodes[9]]
    ds.batch_prepend(L)
    ds.traverse()
    L = [bmssp.nodes[7], bmssp.nodes[8], bmssp.nodes[3], bmssp.nodes[6]]
    ds.batch_prepend(L)
    ds.traverse()

    print("--- Pulling ---")
    S, x = ds.pull()
    print(f"S: {S}")
    print(f"x: {x}")

    ds.traverse()