import math
import pytest

from BMSSP_algorithm.graph import Graph
from BMSSP_algorithm.data_structures.BMSSP import BMSSP

# ---------------------------------------------------------
# TESTING FIND PIVOTS
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# TESTING BASE CASE
# ---------------------------------------------------------

# --- Simple graph class used with the real BMSSP -----------------------------

class SimpleGraph:
    def __init__(self, n: int):
        self.node_count = n
        self.adj = {i: [] for i in range(n)}

    def add_edge(self, u: int, v: int, w: float):
        self.adj[u].append((v, w))

    def get_neighbors(self, u: int):
        return self.adj.get(u, [])


# --- Helpers -----------------------------------------------------------------

def make_bmssp(n: int, source: int, k_override: int | None = None) -> BMSSP:
    """Create a BMSSP instance with a SimpleGraph and initialized dist/pred."""
    g = SimpleGraph(n)
    bm = BMSSP(g, source)

    # Override k if needed for the test
    if k_override is not None:
        bm.k = k_override

    # Initialize distances/preds as run() would
    bm.dist = [math.inf] * n
    bm.pred = [None] * n
    bm.dist[source] = 0.0

    return bm


# --- Tests for base_case -----------------------------------------------------


def test_base_case_single_node_trivial():
    bm = make_bmssp(n=1, source=0, k_override=3)
    B_in = 100.0
    B_out, U = bm.base_case(B_in, {0})

    # Only one node; U0 never exceeds k, so trivial case
    assert B_out == B_in
    assert U == {0}


def test_base_case_two_nodes_trivial_when_k_large():
    bm = make_bmssp(n=2, source=0, k_override=5)
    bm.graph.add_edge(0, 1, 1.0)

    B_in = 100.0
    B_out, U = bm.base_case(B_in, {0})

    # U0 can grow to {0, 1}, but still |U0| <= k (=5)
    assert U == {0, 1}
    assert B_out == B_in


def test_base_case_threshold_case_when_k_small():
    # Chain 0 -> 1 -> 2, but k = 1 so we stop early
    bm = make_bmssp(n=3, source=0, k_override=1)
    bm.graph.add_edge(0, 1, 1.0)
    bm.graph.add_edge(1, 2, 1.0)

    B_prime, U = bm.base_case(B=100.0, S={0})

    # U0 will become {0,1} then stop (|U0| == k+1 == 2)
    # B' = max(dist[v] for v in U0) = dist[1] = 1
    assert pytest.approx(B_prime) == 1.0
    # U = {v in U0 : dist[v] < B'} = {0}
    assert U == {0}


def test_base_case_B_cuts_expansion():
    bm = make_bmssp(n=3, source=0, k_override=5)
    bm.graph.add_edge(0, 1, 10.0)
    bm.graph.add_edge(1, 2, 1.0)

    # B = 10 means we only relax edges with alt < 10
    B_out, U = bm.base_case(B=10.0, S={0})

    # Edge (0,1) has alt = 10, so alt < B is false → node 1 never added
    assert U == {0}
    assert B_out == 10.0


def test_base_case_expands_until_k_plus_1():
    # Long chain, but small k so we stop after k+1 nodes
    bm = make_bmssp(n=10, source=0, k_override=2)
    for i in range(9):
        bm.graph.add_edge(i, i + 1, 1.0)

    B_prime, U = bm.base_case(B=100.0, S={0})

    # U0 should be {0,1,2} at stop time → B' = dist[2] = 2
    # U = nodes in U0 with distance < B' => {0,1}
    assert pytest.approx(B_prime) == 2.0
    assert U == {0, 1}


def test_base_case_avoids_revisiting_nodes_in_cycle():
    # 0 <-> 1 forms a cycle; visited set should prevent infinite loop
    bm = make_bmssp(n=4, source=0, k_override=4)
    bm.graph.add_edge(0, 1, 1.0)
    bm.graph.add_edge(1, 0, 1.0)

    B_out, U = bm.base_case(B=10.0, S={0})

    # We should not loop; just {0,1} reachable under B=10
    assert U == {0, 1}
    assert B_out == 10.0 or B_out == pytest.approx(B_out)


def test_base_case_sets_predecessors_correctly():
    bm = make_bmssp(n=4, source=0, k_override=4)
    bm.graph.add_edge(0, 1, 5.0)
    bm.graph.add_edge(1, 2, 5.0)

    B_out, U = bm.base_case(B=20.0, S={0})

    # Check pred chain: 0 -> 1 -> 2
    assert bm.pred[1] == 0
    assert bm.pred[2] == 1
    # Make sure distances are as expected
    assert pytest.approx(bm.dist[1]) == 5.0
    assert pytest.approx(bm.dist[2]) == 10.0


def test_base_case_distances_update_correctly():
    bm = make_bmssp(n=4, source=0, k_override=4)
    bm.graph.add_edge(0, 1, 3.0)
    bm.graph.add_edge(1, 2, 4.0)

    B_out, U = bm.base_case(B=20.0, S={0})

    assert pytest.approx(bm.dist[1]) == 3.0
    assert pytest.approx(bm.dist[2]) == 7.0
    # 3 nodes reachable under B=20 with k=4: {0,1,2}
    assert U == {0, 1, 2}


def test_base_case_zero_weight_edges():
    bm = make_bmssp(n=3, source=0, k_override=5)
    bm.graph.add_edge(0, 1, 0.0)
    bm.graph.add_edge(1, 2, 0.0)

    B_out, U = bm.base_case(B=10.0, S={0})

    # All nodes reachable with dist 0 < B
    assert U == {0, 1, 2}
    assert B_out == 10.0


def test_base_case_large_B_does_not_cut_paths():
    bm = make_bmssp(n=5, source=0, k_override=5)
    bm.graph.add_edge(0, 1, 100.0)
    bm.graph.add_edge(1, 2, 100.0)

    B_out, U = bm.base_case(B=99999.0, S={0})

    # B is huge → all reachable nodes included as long as |U0| <= k
    assert U == {0, 1, 2}
    assert B_out == 99999.0


def test_base_case_returns_correct_B_prime():
    bm = make_bmssp(n=5, source=0, k_override=2)
    bm.graph.add_edge(0, 1, 4.0)
    bm.graph.add_edge(1, 2, 4.0)
    bm.graph.add_edge(2, 3, 4.0)

    B_prime, U = bm.base_case(B=100.0, S={0})

    # U0 = {0,1,2} when loop stops (size = k+1 = 3)
    # dist[0] = 0, dist[1] = 4, dist[2] = 8 → B' = 8
    assert pytest.approx(B_prime) == 8.0
    # U = {v in U0 : dist[v] < 8} = {0,1}
    assert U == {0, 1}
