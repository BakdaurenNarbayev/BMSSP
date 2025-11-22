import random

from typing import Optional, Tuple
from benchmark.datastructures.graph import Graph

GraphTuple = Tuple[Graph, int, int, str]


def make_random_graph_random_edges(
    nodes: int, seed: Optional[int] = 42, directed: Optional[bool] = True
) -> GraphTuple:
    """
    Create a random graph with the given number of nodes.
    The random seed controls node position jitter and random extra edges.
    """
    if seed is not None:
        random.seed(seed)

    random_dag = Graph(directed)
    for i in range(nodes - 1):
        random_dag.add_edge(i, i + 1, random.randint(1, 5))
        if i < nodes - 2 and random.random() > 0.5:
            target = random.randint(i + 2, min(i + 5, nodes - 1))
            random_dag.add_edge(i, target, random.randint(1, 8))

    return random_dag, 0, nodes - 1


def generate_grid_graph(rows: int, cols: int, directed: bool = True) -> Graph:
    """Generate a grid graph with random edge weights"""
    graph = Graph(directed=directed)

    for i in range(rows * cols):
        row = i // cols
        col = i % cols

        # Connect to right neighbor
        if col < cols - 1:
            weight = random.uniform(1, 10)
            graph.add_edge(i, i + 1, weight)

        # Connect to bottom neighbor
        if row < rows - 1:
            weight = random.uniform(1, 10)
            graph.add_edge(i, i + cols, weight)

    return graph


def generate_random_graph(
    num_nodes: int,
    num_edges: int,
    directed: bool = True,
    min_weight: float = 1,
    max_weight: float = 10,
    seed: Optional[int] = None,
) -> Graph:
    """Generate a random graph with specified nodes and edges"""
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random

    graph = Graph(directed=directed)

    # Ensure connectivity with a spanning tree first
    for i in range(1, num_nodes):
        parent = rng.randint(0, i - 1)
        weight = rng.uniform(min_weight, max_weight)
        graph.add_edge(parent, i, weight)

    # Add remaining random edges
    edges_added = num_nodes - 1
    attempts = 0
    max_attempts = num_edges * 10

    while edges_added < num_edges and attempts < max_attempts:
        from_node = rng.randint(0, num_nodes - 1)
        to_node = rng.randint(0, num_nodes - 1)

        if from_node != to_node:
            # Check if edge already exists
            if not any(n == to_node for n, _ in graph.get_neighbors(from_node)):
                weight = rng.uniform(min_weight, max_weight)
                graph.add_edge(from_node, to_node, weight)
                edges_added += 1

        attempts += 1

    return graph


def generate_complete_graph(num_nodes: int, directed: bool = True) -> Graph:
    """Generate a complete graph where every node is connected to every other node"""
    graph = Graph(directed=directed)
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            weight = random.uniform(1, 10)
            graph.add_edge(i, j, weight)
    return graph
