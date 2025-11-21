import random
from graph_algorithms import Graph
from typing import Tuple, Optional

GraphTuple = Tuple[Graph, int, int, str]
GRAPH_SIZES = {
    "xs": (5, "Extra Small DAG"),
    "s": (10, "Small DAG"),
    "m": (20, "Medium DAG"),
    "l": (30, "Large DAG"),
}


def make_random_dag(nodes: int, seed: Optional[int] = 42) -> GraphTuple:
    """
    Create a random DAG with the given number of nodes.
    The random seed controls node position jitter and random extra edges.
    """
    if seed is not None:
        random.seed(seed)

    random_dag = Graph()
    for i in range(nodes - 1):
        random_dag.add_edge(i, i + 1, random.randint(1, 5))
        if i < nodes - 2 and random.random() > 0.5:
            target = random.randint(i + 2, min(i + 5, nodes - 1))
            random_dag.add_edge(i, target, random.randint(1, 8))

    return random_dag, 0, nodes - 1


def create_sample_graphs(key, seed: Optional[int] = 42) -> GraphTuple:
    """
    Create and return sample graphs with size based on key.
    """
    if key not in GRAPH_SIZES:
        raise ValueError(f"Unknown graph key: {key}")

    nodes, msg = GRAPH_SIZES[key]
    random_dag, start, end = make_random_dag(nodes=nodes, seed=seed)
    return random_dag, start, end, f"{msg} ({nodes} nodes)"
