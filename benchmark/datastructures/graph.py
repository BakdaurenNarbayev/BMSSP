from collections import defaultdict
from typing import Dict, List, Tuple


class Graph:
    """Graph data structure with adjacency list representation"""

    def __init__(self, directed: bool = True):
        self.adjacency_list: Dict[int, List[Tuple[int, float]]] = defaultdict(list)
        self.directed = directed
        self.node_count = 0
        self.edge_count = 0

    def add_edge(self, from_node: int, to_node: int, weight: float):
        """
        Add an edge to the graph. If edge already exists, update its weight.

        Args:
            from_node: Source node
            to_node: Destination node
            weight: Edge weight
        """

        edge_exists = False
        for i, (node, _) in enumerate(self.adjacency_list[from_node]):
            if node == to_node:
                self.adjacency_list[from_node][i] = (to_node, weight)
                edge_exists = True
                break

        if not edge_exists:
            self.adjacency_list[from_node].append((to_node, weight))
            self.edge_count += 1

        if not self.directed:
            reverse_exists = False
            for i, (node, _) in enumerate(self.adjacency_list[to_node]):
                if node == from_node:
                    self.adjacency_list[to_node][i] = (from_node, weight)
                    reverse_exists = True
                    break

            if not reverse_exists:
                self.adjacency_list[to_node].append((from_node, weight))

        self.node_count = max(self.node_count, from_node + 1, to_node + 1)

    def get_neighbors(self, node: int) -> List[Tuple[int, float]]:
        """Get all neighbors of a node"""
        return self.adjacency_list.get(node, [])

    def get_all_edges(self) -> List[Tuple[int, int, float]]:
        """Get all edges in the graph"""
        edges = []
        seen = set()
        for from_node, neighbors in self.adjacency_list.items():
            for to_node, weight in neighbors:
                if self.directed or (from_node, to_node) not in seen:
                    edges.append((from_node, to_node, weight))
                    if not self.directed:
                        seen.add((to_node, from_node))
        return edges

    def __str__(self):
        return f"Graph(nodes={self.node_count}, edges={self.edge_count}, directed={self.directed})"
