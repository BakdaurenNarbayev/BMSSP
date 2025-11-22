import os

from typing import List
from collections import deque
from benchmark.datastructures.graph import Graph


def largest_connected_component(g: Graph) -> List[int]:
    visited = set()
    components = []

    for node in range(g.node_count):
        if node in visited:
            continue
        queue = deque([node])
        component = []
        while queue:
            n = queue.popleft()
            if n in visited:
                continue
            visited.add(n)
            component.append(n)
            for neighbor, _ in g.get_neighbors(n):
                if neighbor not in visited:
                    queue.append(neighbor)
        components.append(component)

    # Return nodes in largest component
    largest = max(components, key=len)
    return largest


def load_graph_from_file(filepath: str, directed: bool = False) -> Graph:
    """
    Load a graph from a Matrix Market file into the Graph class.
    Keeps only the largest connected component.

    Args:
        filepath: Path to the .mtx or matrix file
        directed: Whether to treat the graph as directed

    Returns:
        Graph instance
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath} not found")

    edges = []
    max_node_index = 0

    with open(filepath, "r") as f:
        lines = f.readlines()

    # Remove comments and empty lines
    content_lines = [
        line.strip() for line in lines if line.strip() and not line.startswith("%")
    ]

    # First line after comments is the dimensions which is ignored
    for line in content_lines[1:]:
        parts = line.split()
        if not parts:
            continue

        u = int(parts[0]) - 1
        v = int(parts[1]) - 1
        weight = float(parts[2]) if len(parts) == 3 else 1.0
        edges.append((u, v, weight))
        max_node_index = max(max_node_index, u, v)

    graph = Graph(directed=directed)
    for u, v, w in edges:
        graph.add_edge(u, v, w)

    # Remove disconnected nodes: keep largest connected component
    largest_nodes = set(largest_connected_component(graph))

    # Rebuild graph with only largest component
    filtered_graph = Graph(directed=directed)
    for u, v, w in graph.get_all_edges():
        if u in largest_nodes and v in largest_nodes:
            filtered_graph.add_edge(u, v, w)

    print(
        f"Final filtered graph contains: {filtered_graph.node_count} nodes, {filtered_graph.edge_count} edges"
    )

    return filtered_graph
