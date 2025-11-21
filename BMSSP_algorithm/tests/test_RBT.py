import pytest
from  BMSSP_algorithm.data_structures.RBT import RedBlackTree, RBNode


# ---------------------------
# Helpers for RB invariants
# ---------------------------

def assert_inorder_sorted(tree):
    """Ensure in-order traversal returns a sorted list."""
    values = tree._inorder_traversal_values(tree.root, [])
    assert values == sorted(values)


def assert_red_black_properties(tree):
    if tree.root is None:
        return

    # Property 1: root is black
    assert tree.root.color == "black"

    # Property 2: red node cannot have red children
    def check_no_red_red(node):
        if node is None:
            return True
        if node.color == "red":
            if node.left:
                assert node.left.color == "black"
            if node.right:
                assert node.right.color == "black"
        check_no_red_red(node.left)
        check_no_red_red(node.right)

    check_no_red_red(tree.root)

    # Property 3: all paths have same black-height
    def black_height(node):
        if node is None:
            return 1
        left_h = black_height(node.left)
        right_h = black_height(node.right)
        assert left_h == right_h  # must match
        return left_h + (1 if node.color == "black" else 0)

    black_height(tree.root)


# ---------------------------
# Basic operations tests
# ---------------------------

def test_insert_basic():
    t = RedBlackTree()

    numbers = [10, 20, 5, 15, 1]
    for n in numbers:
        t.insert(n)

    assert_inorder_sorted(t)
    assert_red_black_properties(t)

    # Ensure all nodes can be found
    for n in numbers:
        assert t.search(n) is not None


def test_search_not_found():
    t = RedBlackTree()
    t.insert(10)
    t.insert(5)
    t.insert(20)

    assert t.search(7) is None
    assert t.search(999) is None


def test_search_bound():
    t = RedBlackTree()
    for x in [10, 5, 20, 3, 7]:
        t.insert(x)

    assert t.search_bound(6) == 7
    assert t.search_bound(4) == 5
    assert t.search_bound(19) == 20
    assert t.search_bound(20) == float("inf")  # no value strictly above


def test_insert_maintains_rbt_properties_large():
    t = RedBlackTree()
    import random
    data = random.sample(range(1000), 200)

    for v in data:
        t.insert(v)

    assert_inorder_sorted(t)
    assert_red_black_properties(t)


# ---------------------------
# Deletion tests
# ---------------------------

def test_delete_leaf():
    t = RedBlackTree()
    for x in [10, 5, 20]:
        t.insert(x)

    t.delete(5)

    assert t.search(5) is None
    assert_inorder_sorted(t)
    assert_red_black_properties(t)


def test_delete_node_with_one_child():
    t = RedBlackTree()
    # Creates a situation where 5 has one child
    for x in [10, 5, 1]:
        t.insert(x)

    t.delete(5)

    assert t.search(5) is None
    assert_inorder_sorted(t)
    assert_red_black_properties(t)


def test_delete_node_with_two_children():
    t = RedBlackTree()

    for x in [10, 5, 20, 15, 25]:
        t.insert(x)

    t.delete(20)
    assert t.search(20) is None
    assert_inorder_sorted(t)
    assert_red_black_properties(t)


def test_delete_root():
    t = RedBlackTree()
    for x in [10, 5, 20]:
        t.insert(x)

    t.delete(10)  # root deletion

    assert t.search(10) is None
    assert_inorder_sorted(t)
    assert_red_black_properties(t)


def test_delete_all():
    t = RedBlackTree()
    values = [10, 20, 5, 1, 7, 15]

    for v in values:
        t.insert(v)

    for v in values:
        t.delete(v)
        assert t.search(v) is None
        assert_inorder_sorted(t)
        # tree may become empty; properties still hold
        assert_red_black_properties(t)


# ---------------------------
# Min/Max tests
# ---------------------------

def test_find_min_max():
    t = RedBlackTree()
    vals = [10, 4, 17, 2, 8, 32]
    for v in vals:
        t.insert(v)

    assert t._find_min(t.root).value == min(vals)
    assert t._find_max(t.root).value == max(vals)


# ---------------------------
# Duplicate insertion behavior
# ---------------------------

def test_duplicate_insert():
    t = RedBlackTree()
    t.insert(10)
    t.insert(10)  # should insert as right child (BST rule used)

    values = t._inorder_traversal_values(t.root, [])
    assert values == [10, 10]

    assert_red_black_properties(t)
