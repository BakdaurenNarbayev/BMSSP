from collections import defaultdict
from typing import Dict, List, Tuple
from benchmark.datastructures.graph import Graph


def transform_to_constant_degree(G: Graph) -> Tuple[Graph, Dict[Tuple[int, str, int], int]]:
    """
    Transform arbitrary directed weighted graph G into G'
    where every node has indegree <= 2 and outdegree <= 2.

    Returns:
        G_prime: transformed graph
        mapping: dictionary mapping (v, "in"/"out", index) -> new_node_id
    """

    # Count in- and out- degrees
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    for u in range(G.node_count):
        for v, _ in G.get_neighbors(u):
            outdeg[u] += 1
            indeg[v] += 1

    # Build mapping for cycle nodes
    mapping = {}
    next_node_id = 0

    # For each original vertex v, allocate cycle nodes
    cycle_nodes = {}
    for v in range(G.node_count):
        d = indeg[v] + outdeg[v]
        if d == 0:
            # isolated vertex → map to single node
            cycle_nodes[v] = [next_node_id]
            mapping[(v, "cycle", 0)] = next_node_id
            next_node_id += 1
        else:
            cycle_nodes[v] = []
            for i in range(d):
                mapping[(v, "cycle", i)] = next_node_id
                cycle_nodes[v].append(next_node_id)
                next_node_id += 1

    # Build transformed graph
    Gp = Graph(directed=True)
    Gp.node_count = next_node_id

    # Create cycles
    for v in cycle_nodes:
        nodes = cycle_nodes[v]
        if len(nodes) == 1:
            continue
        for i in range(len(nodes)):
            a = nodes[i]
            b = nodes[(i + 1) % len(nodes)]
            Gp.add_edge(a, b, 0.0)  # zero-weight cycle

    # We now must assign each incoming and outgoing edge a distinct cycle node
    in_index = defaultdict(int)
    out_index = defaultdict(int)

    # Add transformed edges
    for u in range(G.node_count):
        for v, w_uv in G.get_neighbors(u):

            # original edge u→v becomes:
            #   x_uv → x_vu

            # choose unique cycle slot for u's outgoing edge
            u_slot = out_index[u]
            xu = mapping[(u, "cycle", u_slot)]
            out_index[u] += 1

            # choose unique cycle slot for v's incoming edge
            v_slot = in_index[v]
            xv = mapping[(v, "cycle", v_slot)]
            in_index[v] += 1

            Gp.add_edge(xu, xv, w_uv)

    return Gp, mapping
