import pytest

from BMSSP_algorithm.graph import Graph
from BMSSP_algorithm.data_structures.BMSSP import BMSSP


def make_graph(n):
    """Utility: create a directed graph with n isolated nodes."""
    g = Graph(directed=True)
    for i in range(n):
        g.node_count = max(g.node_count, i + 1)
    return g


def test_single_root_becomes_pivot():
    """
    One node in S, its subtree size ≥ k → should be pivot.
    """
    g = make_graph(10)
    # Build a chain: 0→1→2→ ... → k+1   (so subtree_size(0) = k+2)
    bm = BMSSP(g, source=0)
    k = bm.k

    for i in range(0, k + 1):
        g.add_edge(i, i + 1, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    # Because early exit triggers once W > k*|S|
    assert W == {0, 1}
    assert 0 in P      # subtree size ≥ k


def test_B_threshold_blocks_growth():
    """
    If alt >= B then node is not added to W.
    """
    g = make_graph(3)
    bm = BMSSP(g, source=0)
    bm.k = 3  # force small k for deterministic behavior

    # 0 → 1 with a big weight
    g.add_edge(0, 1, 20)

    bm.run()

    # With B = 10, 1 should NEVER enter W
    P, W = bm.find_pivots(B=10, S={0})

    assert W == {0}
    assert P == set() or P == {0}  # subtree_size(0) < k → normally not pivot


def test_growth_limit_activates():
    """
    If |W| > k * |S| early in relaxations → return (S, W).
    """
    g = make_graph(20)
    bm = BMSSP(g, source=0)
    bm.k = 2  # small for easy triggering

    # Create explosive growth:
    # 0 → {1,2,3} all weight 1
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 1)
    g.add_edge(0, 3, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    # Expect early-exit: return (S, W) with W > k*|S| = 2
    assert W >= {0, 1, 2, 3}
    assert P == {0}  # per code early-exit returns S


def test_multi_step_relaxation_propagates():
    """
    Multiple relaxation rounds (k rounds) should propagate through edges.
    """
    g = make_graph(10)
    bm = BMSSP(g, source=0)
    k = bm.k

    # Build a chain long enough to use multiple rounds:
    for i in range(0, k + 3):
        g.add_edge(i, i + 1, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    # W should contain entire chain up to k relaxations
    # W size ≤ k * |S| = k, but the chain should not exceed this.
    assert 0 in W
    assert len(W) <= k + 1


def test_subtree_computation_and_pivot_selection():
    """
    Explicit subtree test:
    Let S={0,3}. Build tree where:
        0 → 1 → 2 → 3 → 4
    Subtree sizes:
        0: 5
        3: 2
    If k ≤ 5 but >2 → only 0 is pivot.
    """
    g = make_graph(6)
    bm = BMSSP(g, source=0)
    bm.k = 4  # require subtree ≥ 4

    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 3, 1)
    g.add_edge(3, 4, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0, 3})

    assert 0 in W and 3 in W
    assert P == {0}     # only subtree rooted at 0 has size ≥ 4
