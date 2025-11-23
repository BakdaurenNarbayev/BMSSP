from BMSSP_algorithm.data_structures.BMSSP import BMSSP

def connect(bm, u, v, w):
    bm.edges[u].append((v, w))


def test_single_node_graph():
    bm = BMSSP(1, 0)
    P, W = bm.find_pivots(B=10, S={0})
    assert P == {0}
    assert W == {0}


def test_two_nodes_simple_path():
    bm = BMSSP(2, 0)
    bm.k = 2   # force deeper relaxation
    connect(bm, 0, 1, 1)
    P, W = bm.find_pivots(B=10, S={0})
    assert W == {0, 1}
    assert P == {0}


def test_unreachable_node_not_in_W():
    bm = BMSSP(3, 0)
    bm.k = 3
    connect(bm, 0, 1, 5)
    P, W = bm.find_pivots(B=10, S={0})
    assert W == {0, 1}
    assert 2 not in W


def test_B_threshold_excludes_node():
    bm = BMSSP(3, 0)
    bm.k = 3
    connect(bm, 0, 1, 20)
    P, W = bm.find_pivots(B=10, S={0})

    assert W == {0}       # 1 excluded due to cost >= B
    assert P == set()     # subtree size(0)=1 < k so root is NOT a pivot


def test_multi_step_relaxation():
    bm = BMSSP(5, 0)
    bm.k = 5   # override k so full chain is explored
    connect(bm, 0, 1, 1)
    connect(bm, 1, 2, 1)
    connect(bm, 2, 3, 1)
    connect(bm, 3, 4, 1)

    P, W = bm.find_pivots(B=10, S={0})
    assert set(W) == {0, 1, 2, 3, 4}
    assert 0 in P


def test_early_termination_trigger():
    bm = BMSSP(10, 0)
    bm.k = 1   # early termination easiest when k=1

    for i in range(1, 7):
        connect(bm, 0, i, 1)

    P, W = bm.find_pivots(B=10, S={0})
    assert P == {0}    # early termination returns P=S


def test_subtree_of_size_less_than_k():
    bm = BMSSP(6, 0)
    bm.k = 3           # subtree must have size >= 3
    connect(bm, 0, 1, 1)  # only 1 child

    P, W = bm.find_pivots(B=10, S={0})
    assert P == set()      # root subtree too small


def test_subtree_large_enough_to_be_pivot():
    bm = BMSSP(8, 0)
    bm.k = 4   # require subtree of size ≥ 4

    prev = 0
    for i in range(1, 6):
        connect(bm, prev, i, 1)
        prev = i

    P, W = bm.find_pivots(B=100, S={0})
    assert 0 in P
    assert len(W) >= 5


def test_multiple_roots_pivots():
    bm = BMSSP(10, 0)
    bm.k = 3

    S = {0, 5}

    connect(bm, 0, 1, 1)
    connect(bm, 1, 2, 1)

    connect(bm, 5, 6, 1)
    connect(bm, 6, 7, 1)

    P, W = bm.find_pivots(B=20, S=S)
    assert S.issubset(W)


def test_random_graph_small_seeded():
    import random
    random.seed(1337)

    bm = BMSSP(7, 0)
    bm.k = 3

    for _ in range(10):
        u = random.randint(0, 6)
        v = random.randint(0, 6)
        if u != v:
            connect(bm, u, v, random.randint(1, 5))

    P, W = bm.find_pivots(B=15, S={0})

    assert 0 in W
    assert P.issubset({0})


def test_k_equals_1_case_still_works():
    bm = BMSSP(2, 0)
    bm.k = 1
    connect(bm, 0, 1, 1)

    P, W = bm.find_pivots(B=10, S={0})
    assert W == {0, 1}
    assert P == {0}


def test_cost_update_distances():
    bm = BMSSP(4, 0)
    bm.k = 4
    connect(bm, 0, 1, 3)
    connect(bm, 1, 2, 3)
    connect(bm, 2, 3, 3)

    P, W = bm.find_pivots(B=100, S={0})
    assert bm.BNodes[1].val == 3
    assert bm.BNodes[2].val == 6
    assert bm.BNodes[3].val == 9