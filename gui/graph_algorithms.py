import time
import heapq
from typing import Dict, List, Optional
from benchmark.datastructures.graph import Graph


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


def dijkstra(graph: Graph, start: int, end: Optional[int] = None) -> PathResult:
    """
    Dijkstra's algorithm for finding shortest paths.

    Time Complexity: O((V + E) log V) with binary heap
    Space Complexity: O(V)

    Args:
        graph: The graph to search
        start: Starting node
        end: Optional ending node (for early termination)

    Returns:
        PathResult containing distances, previous nodes, and metrics
    """
    start_time = time.perf_counter()

    # Initialize distances and previous nodes
    distances = {start: 0}
    previous = {start: None}
    visited = set()

    # Priority queue: (distance, node)
    pq = [(0, start)]
    operations = 0

    while pq:
        current_dist, current = heapq.heappop(pq)
        operations += 1

        # Skip if already visited
        if current in visited:
            continue

        visited.add(current)

        # Early termination if we reached the end
        if end is not None and current == end:
            break

        # Explore neighbors
        for neighbor, weight in graph.get_neighbors(current):
            if neighbor not in visited:
                distance = current_dist + weight

                # Update if we found a shorter path
                if distance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = distance
                    previous[neighbor] = current
                    heapq.heappush(pq, (distance, neighbor))
                    operations += 1

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    return PathResult(distances, previous, execution_time, operations, "Dijkstra")
