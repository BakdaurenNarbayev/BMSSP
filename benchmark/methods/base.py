import math
from abc import ABC, abstractmethod
from benchmark.datastructures.graph import Graph
from typing import Dict, List, Optional


class BaseShortestPath(ABC):
    """
    Minimal abstract base for single-source shortest path algorithms using `Graph`.

    Subclasses must implement:
      - run(source: int) -> bool
      - validate() -> bool
    """

    def __init__(self, graph: Graph, source: int):
        self.graph = graph
        self.source = source
        self.dist: Dict[int, float] = {}  # node -> distance
        self.pred: Dict[int, Optional[int]] = {}  # node -> predecessor or None

        self.edge_relaxations: int = 0
        self.successful_relaxations: int = 0
        self.iterations: int = 0

    def reset_state(self) -> None:
        self.dist.clear()
        self.pred.clear()
        self.edge_relaxations = 0
        self.successful_relaxations = 0
        self.iterations = 0

    def distance(self, node: int) -> float:
        return self.dist.get(node, math.inf)

    def path(self, node: int) -> List[int]:
        """Reconstruct path from last run()'s source to `node`. Empty if unreachable."""
        if self.source is None or node not in self.dist:
            return []
        if math.isinf(self.dist[node]):
            return []

        rev = []
        cur = node
        while cur is not None:
            rev.append(cur)
            cur = self.pred.get(cur)
        rev.reverse()
        if not rev or rev[0] != self.source:
            return []
        return rev

    @abstractmethod
    def run(self) -> bool:
        """Compute shortest paths from source. Return True on success (False if algo can't run / detects negative cycle)."""
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        """Return True if graph satisfies preconditions for algorithm (e.g., Dijkstra: no negative weights)."""
        raise NotImplementedError
