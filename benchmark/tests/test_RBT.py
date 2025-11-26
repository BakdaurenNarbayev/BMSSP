import unittest
from benchmark.methods.BMSSP_utils.data_structures.RBT import RedBlackTree, RBNode


# ---------------------------
# Helpers for RB invariants
# ---------------------------

def assert_inorder_sorted(tree):
    """Ensure in-order traversal returns a sorted list."""
    values = tree._inorder_traversal_values()
    assert values == sorted(values)


def assert_red_black_properties(tree):
    """
    Validates standard RBT properties adapted for NIL-sentinel trees:
    - Root is black
    - No red node has a red child
    - All root-to-leaf paths have equal black height
    """

    # Empty tree OK
    if tree.root is tree.NIL:
        assert tree.get_size() == 0
        return

    # Root must be black
    assert tree.root.color == "black"

    NIL = tree.NIL

    # Property 2: No red node has red children
    def check_no_red_red(node):
        if node is NIL:
            return
        if node.color == "red":
            if node.left is not NIL:
                assert node.left.color == "black"
            if node.right is not NIL:
                assert node.right.color == "black"
        check_no_red_red(node.left)
        check_no_red_red(node.right)

    check_no_red_red(tree.root)

    # Property 3: all paths from node to NIL have same black height
    def black_height(node):
        if node is NIL:
            return 1
        lh = black_height(node.left)
        rh = black_height(node.right)
        assert lh == rh
        return lh + (1 if node.color == "black" else 0)

    black_height(tree.root)


# ---------------------------
# unittest TestCase
# ---------------------------

class TestRedBlackTree(unittest.TestCase):

    # ---------------------------
    # Basic operations tests
    # ---------------------------

    def test_insert_basic(self):
        t = RedBlackTree()

        numbers = [10, 20, 5, 15, 1]
        for n in numbers:
            t.insert(n)

        assert_inorder_sorted(t)
        assert_red_black_properties(t)

        for n in numbers:
            self.assertIsNotNone(t.search(n))

    def test_search_not_found(self):
        t = RedBlackTree()
        t.insert(10)
        t.insert(5)
        t.insert(20)

        self.assertIsNone(t.search(7))
        self.assertIsNone(t.search(999))

    def test_search_bound(self):
        t = RedBlackTree()
        for x in [10, 5, 20, 3, 7]:
            t.insert(x)

        self.assertEqual(t.search_bound(6), 7)
        self.assertEqual(t.search_bound(4), 5)
        self.assertEqual(t.search_bound(19), 20)
        self.assertEqual(t.search_bound(20), None)

    def test_insert_maintains_rbt_properties_large(self):
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

    def test_delete_leaf(self):
        t = RedBlackTree()
        for x in [10, 5, 20]:
            t.insert(x)

        t.delete(5)
        self.assertIsNone(t.search(5))
        assert_inorder_sorted(t)
        assert_red_black_properties(t)

    def test_delete_node_with_one_child(self):
        t = RedBlackTree()
        for x in [10, 5, 1]:
            t.insert(x)

        t.delete(5)
        self.assertIsNone(t.search(5))
        assert_inorder_sorted(t)
        assert_red_black_properties(t)

    def test_delete_node_with_two_children(self):
        t = RedBlackTree()
        for x in [10, 5, 20, 15, 25]:
            t.insert(x)

        t.delete(20)
        self.assertIsNone(t.search(20))
        assert_inorder_sorted(t)
        assert_red_black_properties(t)

    def test_delete_root(self):
        t = RedBlackTree()
        for x in [10, 5, 20]:
            t.insert(x)

        t.delete(10)
        self.assertIsNone(t.search(10))
        assert_inorder_sorted(t)
        assert_red_black_properties(t)

    def test_delete_all(self):
        t = RedBlackTree()
        values = [10, 20, 5, 1, 7, 15]

        for v in values:
            t.insert(v)

        for v in values:
            t.delete(v)
            self.assertIsNone(t.search(v))
            assert_inorder_sorted(t)
            assert_red_black_properties(t)

    # ---------------------------
    # Min/Max tests
    # ---------------------------

    def test_find_min_max(self):
        t = RedBlackTree()
        values = [10, 4, 17, 2, 8, 32]
        for v in values:
            t.insert(v)

        self.assertEqual(t._find_min(t.root).value, min(values))
        self.assertEqual(t._find_max(t.root).value, max(values))

    # ---------------------------
    # Duplicate insertion
    # ---------------------------

    def test_duplicate_insert(self):
        t = RedBlackTree()
        t.insert(10)
        t.insert(10)

        values = t._inorder_traversal_values()
        self.assertEqual(values, [10, 10])
        assert_red_black_properties(t)

    # ---------------------------
    # Size / is_empty tests
    # ---------------------------

    def test_empty_tree_size_and_is_empty(self):
        t = RedBlackTree()
        self.assertEqual(t.get_size(), 0)
        self.assertTrue(t.is_empty())

    def test_size_after_single_insert(self):
        t = RedBlackTree()
        t.insert(10)
        self.assertEqual(t.get_size(), 1)
        self.assertFalse(t.is_empty())

    def test_size_after_multiple_inserts(self):
        t = RedBlackTree()
        values = [10, 5, 20, 1, 7, 15]

        for i, v in enumerate(values):
            t.insert(v)
            self.assertEqual(t.get_size(), i + 1)
            self.assertFalse(t.is_empty())

    def test_size_after_deletes(self):
        t = RedBlackTree()
        values = [10, 5, 20, 1, 7, 15]

        for v in values:
            t.insert(v)

        self.assertEqual(t.get_size(), len(values))

        for i, v in enumerate(values):
            t.delete(v)
            self.assertEqual(t.get_size(), len(values) - (i + 1))
            self.assertEqual(t.is_empty(), t.get_size() == 0)

    def test_delete_nonexistent_does_not_change_size(self):
        t = RedBlackTree()
        t.insert(10)
        t.insert(5)

        before = t.get_size()
        t.delete(999)
        self.assertEqual(t.get_size(), before)
        self.assertFalse(t.is_empty())

    def test_duplicate_inserts_increase_size(self):
        t = RedBlackTree()
        t.insert(10)
        t.insert(10)
        t.insert(10)

        self.assertEqual(t.get_size(), 3)
        self.assertFalse(t.is_empty())

        t.delete(10)
        self.assertEqual(t.get_size(), 2)
        t.delete(10)
        self.assertEqual(t.get_size(), 1)

    def test_size_with_random_operations(self):
        import random
        t = RedBlackTree()
        inserted = []

        for _ in range(100):
            op = random.choice(["insert", "delete"])
            x = random.randint(0, 50)

            if op == "insert":
                t.insert(x)
                inserted.append(x)
            else:
                t.delete(x)
                if x in inserted:
                    inserted.remove(x)

            self.assertEqual(t.get_size(), len(inserted))
            self.assertEqual(t.is_empty(), len(inserted) == 0)


if __name__ == "__main__":
    unittest.main()
