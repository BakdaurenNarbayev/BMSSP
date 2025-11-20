import pytest
from data_structures.Block import Block, BNode

@pytest.fixture
def empty_block():
    return Block()

@pytest.fixture
def filled_block():
    b = Block()
    nodes = [BNode(i) for i in range(1, 4)]
    for node in nodes:
        b.insert(node)
    return b, nodes

def traverse_nodes(block):
    """Helper to collect all nodes in the circular list."""
    if block.is_empty():
        return []
    nodes = []
    current = block.head
    while True:
        nodes.append(current)
        current = current.next
        if current == block.head:
            break
    return nodes

# --- Insertion tests ---
def test_insert_single_node(empty_block):
    node = BNode(10)
    empty_block.insert(node)
    assert empty_block.head == node
    assert node.next == node.prev == node
    assert empty_block.get_size() == 1

def test_insert_multiple_nodes(filled_block):
    b, nodes = filled_block
    assert b.get_size() == 3
    # Check circular links
    assert nodes[0].prev == nodes[-1]
    assert nodes[-1].next == nodes[0]
    # Sequential links
    assert nodes[0].next == nodes[1]
    assert nodes[1].next == nodes[2]
    assert nodes[2].prev == nodes[1]

# --- Deletion tests ---
def test_delete_middle_node(filled_block):
    b, nodes = filled_block
    middle = nodes[1]
    b.delete(middle)
    remaining = traverse_nodes(b)
    assert middle not in remaining
    assert b.get_size() == 2
    # Circularity after deletion
    assert nodes[0].next == nodes[2]
    assert nodes[2].prev == nodes[0]

def test_delete_head_node(filled_block):
    b, nodes = filled_block
    old_head = nodes[0]
    b.delete(old_head)
    assert b.head == nodes[1]
    remaining = [n.val for n in traverse_nodes(b)]
    assert remaining == [2, 3]
    assert b.get_size() == 2
    # Circularity
    assert nodes[1].prev == nodes[2]
    assert nodes[2].next == nodes[1]

def test_delete_tail_node(filled_block):
    b, nodes = filled_block
    tail = nodes[-1]
    b.delete(tail)
    remaining = [n.val for n in traverse_nodes(b)]
    assert remaining == [1, 2]
    assert b.get_size() == 2
    # Circularity
    assert nodes[0].next == nodes[1]
    assert nodes[1].prev == nodes[0]

def test_delete_only_node(empty_block):
    node = BNode(99)
    empty_block.insert(node)
    empty_block.delete(node)
    assert empty_block.is_empty()
    assert empty_block.get_size() == 0

def test_delete_none(empty_block):
    empty_block.delete(None)
    assert empty_block.is_empty()
    assert empty_block.get_size() == 0

# --- Traversal tests ---
def test_traverse_prints(capsys, filled_block):
    b, _ = filled_block
    b.traverse()
    output = capsys.readouterr().out
    assert "(1)" in output
    assert "(2)" in output
    assert "(3)" in output
    assert "(head)" in output
