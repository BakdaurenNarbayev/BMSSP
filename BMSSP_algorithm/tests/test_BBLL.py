import pytest
from BMSSP_algorithm.data_structures.Block import Block
from BMSSP_algorithm.data_structures.RBT import RedBlackTree
from BMSSP_algorithm.utils.MedianFinder import MedianFinder
from BMSSP_algorithm.data_structures.BBLL import BBLL


# ---------------------------------------------------------
# Helper mock node class — matches BNode structure exactly
# ---------------------------------------------------------
class MockNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None


# ---------------------------------------------------------
# BBLL creation helper
# ---------------------------------------------------------
def make_bbll(M=4, B=10, initial_vals=None):
    """Helper to create a BBLL with a nodes dict of MockNodes."""
    nodes = {}
    if initial_vals:
        for k, v in initial_vals.items():
            nodes[k] = MockNode(k, v)
    else:
        nodes = {i: MockNode(i, float("inf")) for i in range(20)}  # large default pool

    bb = BBLL(M=M, B=B, nodes=nodes)
    return bb, nodes


# ---------------------------------------------------------
# Basic INSERT and DELETE tests
# ---------------------------------------------------------
def test_insert_basic():
    bbll, nodes = make_bbll(M=3, B=999, initial_vals={1: 50, 2: 30, 3: 40})

    bbll.insert(1, 20)  # improves from 50 -> 20
    bbll.insert(2, 10)  # improves from 30 -> 10

    # Check D1 block structure
    min_val = bbll.find_global_min()
    assert min_val == 10

    # Collect all values
    collected = []
    for bound, block in bbll.D1.items():
        for n in block.iterate():
            collected.append(n.val)

    assert sorted(collected) == [10, 20]


def test_delete_basic():
    bbll, nodes = make_bbll(M=3, B=999, initial_vals={1: 20, 2: 40, 3: 10})
    bbll.insert(1, 5)   # improve val
    bbll.insert(2, 30)  # improve val

    bbll.delete(1, 5)
    bbll.delete(3, 10)

    # Remaining should be only key=2
    remaining = []
    for bound, block in bbll.D1.items():
        for n in block.iterate():
            remaining.append((n.key, n.val))

    assert remaining == [(2, 30)]


# ---------------------------------------------------------
# SPLIT TESTS
# ---------------------------------------------------------
def test_split_triggering():
    # M = 3 so insertions of 4 improved values triggers split
    bbll, nodes = make_bbll(M=3, B=100,
                            initial_vals={i: 1000 for i in range(6)})

    # Insert 6 decreasing values => they land in D1[B]
    for i in range(6):
        bbll.insert(i, 100 - i)

    # After inserts the initial block should have been split at least once
    assert len(bbll.D1) >= 2

    # All values still must exist
    vals = []
    for bound, block in bbll.D1.items():
        for n in block.iterate():
            vals.append(n.val)

    assert sorted(vals) == sorted([100 - i for i in range(6)])


# ---------------------------------------------------------
# BATCH PREPEND TESTS
# ---------------------------------------------------------
def test_batch_prepend_small():
    bbll, nodes = make_bbll(M=3, B=50,
                            initial_vals={1: 10, 2: 20, 3: 30})

    block_nodes = [nodes[1], nodes[2]]
    block_nodes[0].val = 5
    block_nodes[1].val = 15

    bbll.batch_prepend(block_nodes)

    # Should create 1 new D0 block
    assert len(bbll.D0) == 1
    block = next(iter(bbll.D0.values()))
    vals = [n.val for n in block.iterate()]
    assert sorted(vals) == [5, 15]


def test_batch_prepend_large():
    # Large batch that forces recursive split
    bbll, nodes = make_bbll(M=3, B=50,
                            initial_vals={i: float("inf") for i in range(10)})

    L = []
    for i in range(10):
        nodes[i].val = i
        L.append(nodes[i])

    bbll.batch_prepend(L)

    # Should create multiple D0 blocks
    assert len(bbll.D0) > 1

    all_values = []
    for block in bbll.D0.values():
        for n in block.iterate():
            all_values.append(n.val)

    assert sorted(all_values) == list(range(10))


# ---------------------------------------------------------
# PULL TESTS
# ---------------------------------------------------------
def test_pull_basic():
    bbll, nodes = make_bbll(M=3, B=100,
                            initial_vals={1: 50, 2: 40, 3: 30, 4: 20, 5: 10})

    # Improve several values
    bbll.insert(1, 25)
    bbll.insert(2, 10)
    bbll.insert(3, 5)

    S, x = bbll.pull()

    # Pull should return exactly 3 smallest values
    pulled_vals = sorted([v for (k, v) in S])
    assert pulled_vals == sorted([5, 10, 25])[:3]

    # x should be remaining minimum
    assert x == bbll.find_global_min()


def test_pull_all_values_small():
    bbll, nodes = make_bbll(M=5, B=100,
                            initial_vals={1: 30, 2: 20, 3: 10})

    bbll.insert(1, 5)
    bbll.insert(2, 3)

    S, x = bbll.pull()

    # All three values are <= M so should all be returned
    pulled = sorted([v for (k, v) in S])
    assert pulled == [3, 5]

    # After deletion, everything is removed → next min is B
    assert x == 100


# ---------------------------------------------------------
# GLOBAL MIN TEST
# ---------------------------------------------------------
def test_find_global_min():
    bbll, nodes = make_bbll(M=3, B=99,
                            initial_vals={1: 50, 2: 40, 3: 30})

    bbll.insert(3, 5)  # smallest
    bbll.insert(2, 10)

    assert bbll.find_global_min() == 5


# ---------------------------------------------------------
# ITERATION / STRUCTURE SANITY
# ---------------------------------------------------------
def test_structure_integrity_after_multiple_ops():
    bbll, nodes = make_bbll(M=3, B=200)

    # Insert many updates
    for i in range(10):
        nodes[i].val = 1000
        bbll.insert(i, 100 - i)

    # Delete a few
    for i in [0, 2, 4]:
        bbll.delete(i, 100 - i)

    # Ensure values match expected
    remaining = []
    for bound, block in bbll.D1.items():
        for n in block.iterate():
            remaining.append((n.key, n.val))

    expected = [(i, 100 - i) for i in range(10) if i not in {0, 2, 4}]
    assert sorted(remaining) == sorted(expected)
