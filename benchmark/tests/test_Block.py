import unittest
from benchmark.methods.BMSSP_utils.data_structures.Block import Block, BNode
from benchmark.methods.BMSSP_utils.utils.MedianFinder import MedianFinder


# ---------------------------
# Helper functions
# ---------------------------

def collect_vals(block: Block):
    return [node.val for node in block.iterate()] if not block.is_empty() else []


# ---------------------------
# unittest TestCase
# ---------------------------

class TestBlock(unittest.TestCase):

    # ---------------------------
    # Basic insert tests
    # ---------------------------

    def test_insert_single_node(self):
        b = Block()
        n = BNode(1, 10)
        b.insert(n)

        self.assertEqual(b.get_size(), 1)
        self.assertIs(b.head, n)
        self.assertIs(n.next, n)
        self.assertIs(n.prev, n)
        self.assertEqual(b.get_min(), 10)
        self.assertEqual(b.get_max(), 10)

    def test_insert_multiple_nodes(self):
        b = Block()
        nodes = [BNode(i, v) for i, v in enumerate([5, 10, 3])]

        for n in nodes:
            b.insert(n)

        vals = collect_vals(b)
        self.assertEqual(vals, [5, 10, 3])
        self.assertEqual(b.get_size(), 3)
        self.assertEqual(b.get_min(), 3)
        self.assertEqual(b.get_max(), 10)

    def test_circular_structure_preserved(self):
        b = Block()
        nodes = [BNode(i, v) for i, v in enumerate([1, 2, 3])]
        for n in nodes:
            b.insert(n)

        cur = b.head
        seen = []
        for _ in range(5):  # loop more than size
            seen.append(cur.val)
            cur = cur.next

        self.assertEqual(seen[:3], [1, 2, 3])
        self.assertEqual(seen[3:], [1, 2])

    # ---------------------------
    # Delete tests
    # ---------------------------

    def test_delete_only_node(self):
        b = Block()
        n = BNode(1, 50)
        b.insert(n)

        b.delete(n)

        self.assertTrue(b.is_empty())
        self.assertEqual(b.get_size(), 0)
        self.assertEqual(b.get_min(), float("inf"))
        self.assertEqual(b.get_max(), float("-inf"))

    def test_delete_head_node(self):
        b = Block()
        nodes = [BNode(i, v) for i, v in enumerate([7, 3, 9])]
        for n in nodes:
            b.insert(n)

        b.delete(nodes[0])  # delete head

        self.assertEqual(b.get_size(), 2)
        vals = collect_vals(b)
        self.assertEqual(vals, [3, 9])
        self.assertEqual(b.get_min(), 3)
        self.assertEqual(b.get_max(), 9)

    def test_delete_middle_node(self):
        b = Block()
        a, bnode, c = BNode(1, 5), BNode(2, 10), BNode(3, 7)

        for x in [a, bnode, c]:
            b.insert(x)

        b.delete(bnode)

        self.assertEqual(collect_vals(b), [5, 7])
        self.assertEqual(b.get_min(), 5)
        self.assertEqual(b.get_max(), 7)

    def test_delete_tail_node(self):
        b = Block()
        a, bnode, c = BNode(1, 2), BNode(2, 5), BNode(3, 10)
        for n in [a, bnode, c]:
            b.insert(n)

        b.delete(c)  # tail

        self.assertEqual(collect_vals(b), [2, 5])
        self.assertEqual(b.get_max(), 5)

    def test_delete_updates_min_max_correctly(self):
        b = Block()
        n1 = BNode(1, 100)
        n2 = BNode(2, 5)
        n3 = BNode(3, 50)

        for n in [n1, n2, n3]:
            b.insert(n)

        b.delete(n1)  # delete max
        self.assertEqual(b.get_max(), 50)

        b.delete(n2)  # delete min
        self.assertEqual(b.get_min(), 50)

    # ---------------------------
    # Median tests
    # ---------------------------

    def test_median_odd(self):
        b = Block()
        for val in [5, 2, 9]:
            b.insert(BNode(val, val))

        self.assertEqual(b.find_median(), 5)

    def test_median_even(self):
        b = Block()
        for val in [4, 10, 2, 8]:
            b.insert(BNode(val, val))

        self.assertEqual(b.find_median(), (4 + 8) / 2)

    def test_median_single(self):
        b = Block()
        b.insert(BNode(1, 77))
        self.assertEqual(b.find_median(), 77)

    def test_median_empty(self):
        b = Block()
        self.assertIsNone(b.find_median())

    # ---------------------------
    # Iteration tests
    # ---------------------------

    def test_iterate_returns_all_nodes_exactly_once(self):
        b = Block()
        vals = [10, 20, 30, 40]
        for i, v in enumerate(vals):
            b.insert(BNode(i, v))

        self.assertEqual(collect_vals(b), vals)

    # ---------------------------
    # Size and empty tests
    # ---------------------------

    def test_size_tracking(self):
        b = Block()
        nodes = [BNode(i, v) for i, v in enumerate([1, 2, 3])]
        for n in nodes:
            b.insert(n)

        self.assertEqual(b.get_size(), 3)
        b.delete(nodes[1])
        self.assertEqual(b.get_size(), 2)

    def test_empty_block_properties(self):
        b = Block()
        self.assertTrue(b.is_empty())
        self.assertEqual(b.get_min(), float("inf"))
        self.assertEqual(b.get_max(), float("-inf"))


if __name__ == "__main__":
    unittest.main()
