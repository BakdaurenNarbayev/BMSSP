from typing import Optional
from benchmark.utils.generate_graphs import GraphTuple, make_random_graph_random_edges

GRAPH_SIZES = {
    "xs": (5, "Extra Small DAG"),
    "s": (10, "Small DAG"),
    "m": (20, "Medium DAG"),
    "l": (30, "Large DAG"),
}


def create_sample_graphs(key, seed: Optional[int] = 42) -> GraphTuple:
    """
    Create and return sample graphs with size based on key.
    """
    if key not in GRAPH_SIZES:
        raise ValueError(f"Unknown graph key: {key}")

    nodes, msg = GRAPH_SIZES[key]
    random_dag, start, end = make_random_graph_random_edges(nodes=nodes, seed=seed)
    return random_dag, start, end, f"{msg} ({nodes} nodes)"
