import math
import pytest

from BMSSP_algorithm.graph import Graph
from BMSSP_algorithm.data_structures.BMSSP import BMSSP


# ---------------------------------------------------------
# GRAPH HELPERS
# ---------------------------------------------------------

def make_graph(n):
    """Utility: create a directed graph with n isolated nodes."""
    g = Graph(directed=True)
    for i in range(n):
        g.node_count = max(g.node_count, i + 1)
    return g


# ---------------------------------------------------------
# FIND-PIVOTS TESTS
# ---------------------------------------------------------

def test_single_root_becomes_pivot():
    """
    One node in S, its subtree size ≥ k → should be pivot.
    """
    g = make_graph(10)
    bm = BMSSP(g, source=0)
    k = bm.k

    # Build a chain 0→1→2→…→k+1
    for i in range(k + 1):
        g.add_edge(i, i + 1, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    # Because early exit triggers once W > k*|S|
    assert W == {0, 1}
    assert 0 in P


def test_B_threshold_blocks_growth():
    """
    If alt >= B, then the node is not added to W.
    """
    g = make_graph(3)
    bm = BMSSP(g, source=0)
    bm.k = 3

    g.add_edge(0, 1, 20)  # weight exceeds B

    bm.run()
    P, W = bm.find_pivots(B=10, S={0})

    assert W == {0}
    assert P == set() or P == {0}


def test_growth_limit_activates():
    """
    If |W| > k*|S| early, return (S, W).
    """
    g = make_graph(20)
    bm = BMSSP(g, source=0)
    bm.k = 2

    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 1)
    g.add_edge(0, 3, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    assert W >= {0, 1, 2, 3}
    assert P == {0}


def test_multi_step_relaxation_propagates():
    """
    Relaxations propagate up to k rounds.
    """
    g = make_graph(10)
    bm = BMSSP(g, source=0)
    k = bm.k

    for i in range(k + 3):
        g.add_edge(i, i + 1, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0})

    assert 0 in W
    assert len(W) <= k + 1


def test_subtree_computation_and_pivot_selection():
    """
    Explicit subtree structure:
        0→1→2→3→4
    S={0,3}, subtree sizes: size(0)=5, size(3)=2.
    """
    g = make_graph(6)
    bm = BMSSP(g, source=0)
    bm.k = 4

    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 3, 1)
    g.add_edge(3, 4, 1)

    bm.run()
    P, W = bm.find_pivots(B=1000, S={0, 3})

    assert {0, 3}.issubset(W)
    assert P == {0}


# ---------------------------------------------------------
# BASE-CASE TESTS
# ---------------------------------------------------------

class SimpleGraph:
    """Small mock graph reproducing Graph interface."""
    def __init__(self, n):
        self.node_count = n
        self.adj = {i: [] for i in range(n)}

    def add_edge(self, u, v, w):
        self.adj[u].append((v, w))

    def get_neighbors(self, u):
        return self.adj[u]


def make_bmssp(n, source, k_override=None):
    """Construct BMSSP with predictable dist/pred initialization."""
    g = SimpleGraph(n)
    bm = BMSSP(g, source)

    if k_override is not None:
        bm.k = k_override

    bm.dist = [math.inf] * n
    bm.pred = [None] * n
    bm.dist[source] = 0.0
    return bm


def test_base_case_single_node_trivial():
    bm = make_bmssp(1, 0, k_override=3)
    B_out, U = bm.base_case(100.0, {0})
    assert B_out == 100.0
    assert U == {0}


def test_base_case_two_nodes_trivial_when_k_large():
    bm = make_bmssp(2, 0, k_override=5)
    bm.graph.add_edge(0, 1, 1.0)
    B_out, U = bm.base_case(100.0, {0})
    assert U == {0, 1}


def test_base_case_threshold_case_when_k_small():
    bm = make_bmssp(3, 0, k_override=1)
    bm.graph.add_edge(0, 1, 1.0)
    bm.graph.add_edge(1, 2, 1.0)

    Bp, U = bm.base_case(100.0, {0})
    assert pytest.approx(Bp) == 1.0
    assert U == {0}


def test_base_case_B_cuts_expansion():
    bm = make_bmssp(3, 0, k_override=5)
    bm.graph.add_edge(0, 1, 10.0)
    B_out, U = bm.base_case(10.0, {0})
    assert U == {0}


def test_base_case_expands_until_k_plus_1():
    bm = make_bmssp(10, 0, k_override=2)
    for i in range(9):
        bm.graph.add_edge(i, i + 1, 1.0)

    Bp, U = bm.base_case(100.0, {0})
    assert pytest.approx(Bp) == 2.0
    assert U == {0, 1}


def test_base_case_avoids_revisiting_nodes_in_cycle():
    bm = make_bmssp(4, 0, k_override=4)
    bm.graph.add_edge(0, 1, 1.0)
    bm.graph.add_edge(1, 0, 1.0)

    B_out, U = bm.base_case(10.0, {0})
    assert U == {0, 1}


def test_base_case_sets_predecessors_correctly():
    bm = make_bmssp(4, 0, k_override=4)
    bm.graph.add_edge(0, 1, 5.0)
    bm.graph.add_edge(1, 2, 5.0)

    B_out, U = bm.base_case(20.0, {0})
    assert bm.pred[1] == 0
    assert bm.pred[2] == 1
    assert bm.dist[2] == 10.0


def test_base_case_distances_update_correctly():
    bm = make_bmssp(4, 0, k_override=4)
    bm.graph.add_edge(0, 1, 3.0)
    bm.graph.add_edge(1, 2, 4.0)

    B_out, U = bm.base_case(20.0, {0})
    assert bm.dist[2] == 7.0
    assert U == {0, 1, 2}


def test_base_case_zero_weight_edges():
    bm = make_bmssp(3, 0, k_override=5)
    bm.graph.add_edge(0, 1, 0.0)
    bm.graph.add_edge(1, 2, 0.0)

    B_out, U = bm.base_case(10.0, {0})
    assert U == {0, 1, 2}


def test_base_case_large_B_does_not_cut_paths():
    bm = make_bmssp(5, 0, k_override=5)
    bm.graph.add_edge(0, 1, 100.0)
    bm.graph.add_edge(1, 2, 100.0)

    B_out, U = bm.base_case(99999.0, {0})
    assert U == {0, 1, 2}


def test_base_case_returns_correct_B_prime():
    bm = make_bmssp(5, 0, k_override=2)
    bm.graph.add_edge(0, 1, 4.0)
    bm.graph.add_edge(1, 2, 4.0)
    bm.graph.add_edge(2, 3, 4.0)

    Bp, U = bm.base_case(100.0, {0})
    assert pytest.approx(Bp) == 8.0
    assert U == {0, 1}


# ---------------------------------------------------------
# BMSSP END–TO–END TESTS
# ---------------------------------------------------------
'''
@pytest.mark.timeout(5)
def test_bmssp_single_node():
    g = make_graph(1)
    bm = BMSSP(g, source=0)

    l0 = math.ceil(math.log2(g.node_count) / bm.t)
    Bp, U = bm.bmssp(l0, float("inf"), {0})

    assert U == {0}
    assert Bp == float("inf")

@pytest.mark.timeout(5)
def test_bmssp_two_node_chain():
    g = make_graph(2)
    g.add_edge(0, 1, 5)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == {0, 1}
    assert bm.dist[1] == 5

@pytest.mark.timeout(5)
def test_bmssp_long_chain():
    n = 10
    g = make_graph(n)
    for i in range(n - 1):
        g.add_edge(i, i + 1, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == set(range(n))
    assert bm.dist[n - 1] == n - 1

@pytest.mark.timeout(5)
def test_bmssp_tree_structure():
    g = make_graph(6)
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 1)
    g.add_edge(0, 3, 1)
    g.add_edge(1, 4, 1)
    g.add_edge(1, 5, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == {0, 1, 2, 3, 4, 5}
    assert bm.dist[4] == 2
    assert bm.dist[5] == 2

@pytest.mark.timeout(5)
def test_bmssp_cycle_does_not_loop():
    g = make_graph(3)
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 0, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == {0, 1, 2}
    assert bm.dist[2] == 2

@pytest.mark.timeout(5)
def test_bmssp_unreachable_nodes_not_included():
    g = make_graph(3)
    g.add_edge(0, 1, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == {0, 1}
    assert 2 not in U

@pytest.mark.timeout(5)
def test_bmssp_boundary_cutting():
    g = make_graph(4)
    g.add_edge(0, 1, 2)
    g.add_edge(1, 2, 5)
    g.add_edge(2, 3, 10)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, 6, {0})
    assert U == {0, 1, 2}
    assert 3 not in U

@pytest.mark.timeout(5)
def test_bmssp_large_graph_scaling():
    n = 100
    g = make_graph(n)
    for i in range(n - 1):
        g.add_edge(i, i + 1, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == set(range(n))
    assert bm.dist[n - 1] == n - 1

@pytest.mark.timeout(5)
def test_bmssp_multiple_sources_in_recursion():
    g = make_graph(6)
    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(0, 3, 1)
    g.add_edge(3, 4, 1)
    g.add_edge(4, 5, 1)

    bm = BMSSP(g, source=0)
    l0 = math.ceil(math.log2(g.node_count) / bm.t)

    Bp, U = bm.bmssp(l0, float("inf"), {0})
    assert U == {0, 1, 2, 3, 4, 5}
    assert bm.dist[5] == 3
'''