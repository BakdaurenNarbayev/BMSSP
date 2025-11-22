import time
from typing import Dict, List, Optional, Type
from benchmark.methods.dijkstra import Dijkstra
from benchmark.datastructures.graph import Graph
from benchmark.methods.bellman_ford import BellmanFord


class PathResult:
    """Result of a pathfinding algorithm"""

    def __init__(
        self,
        distances: Dict[int, float],
        previous: Dict[int, Optional[int]],
        execution_time: float,
        operations: int,
        algorithm: str,
    ):
        self.distances = distances
        self.previous = previous
        self.execution_time = execution_time
        self.operations = operations
        self.algorithm = algorithm

    def get_path(self, start: int, end: int) -> Optional[List[int]]:
        """Reconstruct path from start to end"""
        if self.distances.get(end, float("inf")) == float("inf"):
            return None

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = self.previous.get(current)

        path.reverse()
        return path if path[0] == start else None

    def get_distance(self, node: int) -> float:
        """Get distance to a node"""
        return self.distances.get(node, float("inf"))

    def __str__(self):
        return (
            f"{self.algorithm} Result:\n"
            f"  Execution Time: {self.execution_time:.6f} seconds\n"
            f"  Operations: {self.operations:,}\n"
            f"  Nodes Reached: {sum(1 for d in self.distances.values() if d != float('inf'))}"
        )


def run_shortest_path_algo(
    algo_class: Type, graph: Graph, start: int, name: Optional[str] = None
) -> PathResult:
    """
    Runs a shortest-path algorithm and measures execution time and iterations.

    Args:
        algo_class: The class of the algorithm (e.g., Dijkstra or BellmanFord)
        graph: Graph instance
        start: Start node index
        name: Optional name override for the algorithm

    Returns:
        PathResult containing distances, predecessors, execution time, iterations, and name
    """
    algo = algo_class(graph, start)

    start_time = time.perf_counter()
    algo.run()
    end_time = time.perf_counter()

    execution_time = end_time - start_time
    distances = algo.dist
    previous = algo.pred
    operations = algo.iterations
    algo_name = name or algo_class.__name__

    return PathResult(distances, previous, execution_time, operations, algo_name)


def dijkstra(graph: Graph, start: int) -> PathResult:
    return run_shortest_path_algo(Dijkstra, graph, start, "Dijkstra")


def bellman_ford(graph: Graph, start: int) -> PathResult:
    return run_shortest_path_algo(BellmanFord, graph, start, "Bellman-Ford")
