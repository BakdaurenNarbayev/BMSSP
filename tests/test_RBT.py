import pytest
from data_structures.RBT import RedBlackTree, RBNode


@pytest.fixture
def rbt():
    tree = RedBlackTree()
    for v in [10, 20, 30, 15, 25, 5]:
        tree.insert(v)
    return tree


def test_insert_and_search(rbt):
    # Check that inserted values are found
    for v in [10, 20, 30, 15, 25, 5]:
        assert rbt.search(v) is not None

    # Check a value that should not exist
    assert rbt.search(99) is None


def test_root_is_black_after_insertion(rbt):
    assert rbt.root.color == "black"


def test_parent_child_order_property(rbt):
    # Ensure BST property holds: left < parent < right
    def is_bst(node):
        if node is None:
            return True
        if node.left and node.left.value >= node.value:
            return False
        if node.right and node.right.value <= node.value:
            return False
        return is_bst(node.left) and is_bst(node.right)
    assert is_bst(rbt.root)


def test_search_bound(rbt):
    # Find the node whose value is just above 16 -> should be 20
    bound = rbt.search_bound(16)
    assert bound is not None
    assert bound.value == 20


def test_delete_leaf(rbt):
    rbt.delete(5)
    assert rbt.search(5) is None
    # Ensure tree still satisfies root black rule
    assert rbt.root.color == "black"


def test_delete_with_children(rbt):
    rbt.delete(20)
    assert rbt.search(20) is None
    # Ensure remaining values still valid
    for v in [10, 30, 15, 25, 5]:
        assert rbt.search(v) is not None


def test_inorder_traversal_output(capsys):
    rbt = RedBlackTree()
    for v in [7, 3, 18, 10, 22, 8, 11, 26]:
        rbt.insert(v)
    rbt._inorder_traversal(rbt.root)
    captured = capsys.readouterr()
    assert captured.out.strip() == "3 7 8 10 11 18 22 26"
