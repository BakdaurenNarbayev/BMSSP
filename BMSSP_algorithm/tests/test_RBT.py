import pytest
from BMSSP_algorithm.data_structures.RBT import RedBlackTree, RBNode


# ---------------------------
# Helpers for RB invariants
# ---------------------------

def assert_inorder_sorted(tree):
    """Ensure in-order traversal returns a sorted list."""
    values = tree._inorder_traversal_values(tree.root, [])
    assert values == sorted(values)


def assert_red_black_properties(tree):
    """
    Validates standard RBT properties adapted for NIL-sentinel trees:
    - Root is black
    - No red node has a red child
    - All root-to-leaf paths have equal black height
    """

    # Property 0: Empty tree → OK
    if tree.root is tree.NIL:
        assert tree.get_size() == 0
        return

    # Property 1: root is black
    assert tree.root.color == "black"

    NIL = tree.NIL

    # Property 2: red node cannot have red children
    def check_no_red_red(node):
        if node is NIL:
            return

        if node.color == "red":
            # both children must be black if not NIL
            if node.left != NIL:
                assert node.left.color == "black"
            if node.right != NIL:
                assert node.right.color == "black"

        check_no_red_red(node.left)
        check_no_red_red(node.right)

    check_no_red_red(tree.root)

    # Property 3: all paths from a node to NIL leaves have same black-height
    def black_height(node):
        if node is NIL:
            return 1  # NIL counts as one black node

        left_h = black_height(node.left)
        right_h = black_height(node.right)
        assert left_h == right_h  # must match

        # Add this node's black contribution
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

# ---------------------------
# Size / is_empty tests
# ---------------------------

def test_empty_tree_size_and_is_empty():
    t = RedBlackTree()
    assert t.get_size() == 0
    assert t.is_empty() is True


def test_size_after_single_insert():
    t = RedBlackTree()
    t.insert(10)
    assert t.get_size() == 1
    assert t.is_empty() is False


def test_size_after_multiple_inserts():
    t = RedBlackTree()
    values = [10, 5, 20, 1, 7, 15]

    for i, v in enumerate(values):
        t.insert(v)
        assert t.get_size() == (i + 1)
        assert t.is_empty() is False


def test_size_after_deletes():
    t = RedBlackTree()
    values = [10, 5, 20, 1, 7, 15]

    # insert all
    for v in values:
        t.insert(v)

    assert t.get_size() == len(values)

    # delete all one by one
    for i, v in enumerate(values):
        t.delete(v)
        assert t.get_size() == len(values) - (i + 1)
        assert t.is_empty() == (t.get_size() == 0)


def test_delete_nonexistent_does_not_change_size():
    t = RedBlackTree()
    t.insert(10)
    t.insert(5)

    before = t.get_size()
    t.delete(999)  # does nothing
    assert t.get_size() == before
    assert t.is_empty() is False


def test_duplicate_inserts_increase_size():
    t = RedBlackTree()
    t.insert(10)
    t.insert(10)  # allowed → inserts duplicate
    t.insert(10)  # another duplicate
    assert t.get_size() == 3
    assert t.is_empty() is False

    # delete two of them
    t.delete(10)
    assert t.get_size() == 2
    t.delete(10)
    assert t.get_size() == 1


def test_size_with_random_operations():
    import random
    t = RedBlackTree()
    ops = []
    inserted = []

    for _ in range(100):
        op = random.choice(["insert", "delete"])
        x = random.randint(0, 50)
        ops.append((op, x))

        if op == "insert":
            t.insert(x)
            inserted.append(x)
        else:
            t.delete(x)
            if x in inserted:
                inserted.remove(x)

        # Check consistency
        assert t.get_size() == len(inserted)
        assert t.is_empty() == (len(inserted) == 0)
