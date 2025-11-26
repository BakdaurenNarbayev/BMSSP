import pytest
from benchmark.methods.BMSSP_utils.data_structures.BBLL import BBLL

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def collect_all_pairs(bdll: BBLL):
    """Collect all (key, val) pairs from D0 and D1."""
    out = []
    for bound in bdll.D0_bounds._inorder_traversal_values(bdll.D0_bounds.root, []):
        blk = bdll.D0[bound]
        for n in blk.iterate():
            out.append((n.key, n.val))

    for bound in bdll.D1_bounds._inorder_traversal_values(bdll.D1_bounds.root, []):
        blk = bdll.D1[bound]
        for n in blk.iterate():
            out.append((n.key, n.val))

    return sorted(out, key=lambda x: (x[1], x[0]))


# ----------------------------------------------------------------------
# Basic construction
# ----------------------------------------------------------------------

def test_init_empty():
    bd = BBLL(M=4, B=10**9, N=5)
    assert bd.is_empty()  # sentinel block empty
    assert bd.D0_bounds.is_empty()


# ----------------------------------------------------------------------
# Insert / delete
# ----------------------------------------------------------------------

def test_insert_basic():
    bd = BBLL(M=4, B=10**9, N=5)

    bd.insert(0, 7)
    bd.insert(1, 3)
    bd.insert(2, 9)

    all_pairs = collect_all_pairs(bd)
    assert all_pairs == [(1, 3), (0, 7), (2, 9)]


def test_improvement_rule():
    """Insert should only improve values."""
    bd = BBLL(M=4, B=10**9, N=3)

    bd.insert(0, 10)
    bd.insert(0, 20)   # Should NOT worsen
    assert collect_all_pairs(bd) == [(0, 10)]

    bd.insert(0, 5)    # Should improve
    assert collect_all_pairs(bd) == [(0, 5)]


def test_delete_basic():
    bd = BBLL(M=4, B=10**9, N=4)

    bd.insert(0, 10)
    bd.insert(1, 5)

    bd.delete(1, 5)
    all_pairs = collect_all_pairs(bd)
    assert all_pairs == [(0, 10)]

    bd.delete(0, 10)
    assert bd.is_empty()


# ----------------------------------------------------------------------
# Block splitting
# ----------------------------------------------------------------------

def test_block_split():
    """Force Block split by exceeding M."""
    bd = BBLL(M=3, B=10**9, N=10)

    # Insert 4 decreasing values → forces >M in same block → split
    bd.insert(0, 40)
    bd.insert(1, 30)
    bd.insert(2, 20)
    bd.insert(3, 10)

    all_pairs = collect_all_pairs(bd)
    vals = [v for _, v in all_pairs]

    assert sorted(vals) == [10, 20, 30, 40]
    # Should now have at least 2 blocks (split)
    assert bd.D1_bounds.get_size() >= 2


# ----------------------------------------------------------------------
# Pull operation
# ----------------------------------------------------------------------

def test_pull_basic():
    bd = BBLL(M=3, B=10**9, N=10)

    bd.insert(0, 9)
    bd.insert(1, 2)
    bd.insert(2, 5)
    bd.insert(3, 1)
    bd.insert(4, 3)

    S, nxt = bd.pull()
    assert S == {3, 1, 4}  # smallest 3 values: 1,2,3 → keys 3,1,4
    assert nxt == 5        # next smallest value after deletion

    # After pulling those, remaining are values 5,9
    remaining = collect_all_pairs(bd)
    vals = [v for _, v in remaining]
    assert sorted(vals) == [5, 9]


# ----------------------------------------------------------------------
# Batch prepend
# ----------------------------------------------------------------------

def test_batch_prepend_small():
    bd = BBLL(M=4, B=10**9, N=10)

    bd.batch_prepend([(0, 50), (1, 20), (2, 70)])
    all_pairs = collect_all_pairs(bd)
    assert sorted(all_pairs) == [(0, 50), (1, 20), (2, 70)]


def test_batch_prepend_large_split():
    """Large batch → recursive median splits."""
    bd = BBLL(M=3, B=10**9, N=20)
    L = [(i, 100 - i) for i in range(10)]  # values decreasing

    bd.batch_prepend(L)
    bd.traverse()
    pairs = collect_all_pairs(bd)

    assert len(pairs) == 10
    vals = [v for _, v in pairs]
    assert sorted(vals) == sorted([100 - i for i in range(10)])

    # Should produce multiple D0 blocks
    assert bd.D0_bounds.get_size() > 1


# ----------------------------------------------------------------------
# find_global_min
# ----------------------------------------------------------------------

def test_find_global_min():
    bd = BBLL(M=4, B=10**9, N=5)
    assert bd.find_global_min() == 10**9  # sentinel only

    bd.insert(0, 7)
    bd.insert(1, 3)
    assert bd.find_global_min() == 3


# ----------------------------------------------------------------------
# is_empty
# ----------------------------------------------------------------------

def test_is_empty_logic():
    bd = BBLL(M=4, B=10**9, N=5)
    assert bd.is_empty()

    bd.insert(0, 10)
    assert not bd.is_empty()

    bd.delete(0, 10)
    assert bd.is_empty()
