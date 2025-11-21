import pytest
from BMSSP_algorithm.data_structures.Block import Block, BNode
from BMSSP_algorithm.utils.MedianFinder import MedianFinder


# ---------------------------
# Helper functions
# ---------------------------

def collect_vals(block: Block):
    return [node.val for node in block.iterate()] if not block.is_empty() else []


# ---------------------------
# Basic insert tests
# ---------------------------

def test_insert_single_node():
    b = Block()
    n = BNode(1, 10)
    b.insert(n)

    assert b.get_size() == 1
    assert b.head == n
    assert n.next == n and n.prev == n
    assert b.get_min() == 10
    assert b.get_max() == 10


def test_insert_multiple_nodes():
    b = Block()
    nodes = [BNode(i, v) for i, v in enumerate([5, 10, 3])]

    for n in nodes:
        b.insert(n)

    vals = collect_vals(b)
    assert vals == [5, 10, 3]
    assert b.get_size() == 3
    assert b.get_min() == 3
    assert b.get_max() == 10


def test_circular_structure_preserved():
    b = Block()
    nodes = [BNode(i, v) for i, v in enumerate([1, 2, 3])]
    for n in nodes:
        b.insert(n)

    cur = b.head
    seen = []
    for _ in range(5):  # more than size → should still loop cleanly
        seen.append(cur.val)
        cur = cur.next

    assert seen[:3] == [1, 2, 3]
    assert seen[3:] == [1, 2]


# ---------------------------
# Delete tests
# ---------------------------

def test_delete_only_node():
    b = Block()
    n = BNode(1, 50)
    b.insert(n)

    b.delete(n)

    assert b.is_empty()
    assert b.get_size() == 0
    assert b.get_min() == float("inf")
    assert b.get_max() == float("-inf")


def test_delete_head_node():
    b = Block()
    nodes = [BNode(i, v) for i, v in enumerate([7, 3, 9])]
    for n in nodes:
        b.insert(n)

    b.delete(nodes[0])  # delete head

    assert b.get_size() == 2
    vals = collect_vals(b)
    assert vals == [3, 9]
    assert b.get_min() == 3
    assert b.get_max() == 9


def test_delete_middle_node():
    b = Block()
    a, bnode, c = BNode(1, 5), BNode(2, 10), BNode(3, 7)

    for x in [a, bnode, c]:
        b.insert(x)

    b.delete(bnode)

    assert collect_vals(b) == [5, 7]
    assert b.get_min() == 5
    assert b.get_max() == 7


def test_delete_tail_node():
    b = Block()
    a, bnode, c = BNode(1, 2), BNode(2, 5), BNode(3, 10)
    for n in [a, bnode, c]:
        b.insert(n)

    # tail is c
    b.delete(c)

    assert collect_vals(b) == [2, 5]
    assert b.get_max() == 5  # c was max


def test_delete_updates_min_max_correctly():
    b = Block()
    n1 = BNode(1, 100)
    n2 = BNode(2, 5)
    n3 = BNode(3, 50)

    for n in [n1, n2, n3]:
        b.insert(n)

    b.delete(n1)  # delete max
    assert b.get_max() == 50

    b.delete(n2)  # delete min
    assert b.get_min() == 50


# ---------------------------
# Median tests
# ---------------------------

def test_median_odd():
    b = Block()
    for val in [5, 2, 9]:
        b.insert(BNode(val, val))

    assert b.find_median() == 5  # sorted: [2,5,9]


def test_median_even():
    b = Block()
    for val in [4, 10, 2, 8]:
        b.insert(BNode(val, val))

    assert b.find_median() == (4 + 8) / 2  # sorted: [2,4,8,10]


def test_median_single():
    b = Block()
    b.insert(BNode(1, 77))
    assert b.find_median() == 77


def test_median_empty():
    b = Block()
    assert b.find_median() is None


# ---------------------------
# Iteration tests
# ---------------------------

def test_iterate_returns_all_nodes_exactly_once():
    b = Block()
    vals = [10, 20, 30, 40]
    for i, v in enumerate(vals):
        b.insert(BNode(i, v))

    assert collect_vals(b) == vals


# ---------------------------
# Size and empty tests
# ---------------------------

def test_size_tracking():
    b = Block()
    nodes = [BNode(i, v) for i, v in enumerate([1, 2, 3])]
    for n in nodes:
        b.insert(n)

    assert b.get_size() == 3
    b.delete(nodes[1])
    assert b.get_size() == 2


def test_empty_block_properties():
    b = Block()
    assert b.is_empty()
    assert b.get_min() == float("inf")
    assert b.get_max() == float("-inf")
