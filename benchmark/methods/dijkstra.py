import math
import heapq
from typing import List, Tuple
from benchmark.methods.base import BaseShortestPath


class Dijkstra(BaseShortestPath):
    def validate(self) -> bool:
        # Dijkstra can't handle negative edge weights
        for _, _, w in self.graph.get_all_edges():
            if w < 0:
                return False
        return True

    def run(self) -> bool:
        if not self.validate():
            return False

        self.reset_state()
        source = self.source

        # initialize distances
        for n in range(self.graph.node_count):
            # ensure every node has an entry even if isolated
            self.dist[n] = math.inf
            self.pred[n] = None

        if source >= self.graph.node_count:
            self.graph.node_count = max(self.graph.node_count, source + 1)
            self.dist[source] = 0.0
        else:
            self.dist[source] = 0.0

        heap: List[Tuple[float, int]] = [(0.0, source)]
        visited = set()

        while heap:
            d_u, u = heapq.heappop(heap)
            if d_u > self.dist.get(u, math.inf):
                continue

            self.iterations += 1
            visited.add(u)

            for v, w in self.graph.get_neighbors(u):
                self.edge_relaxations += 1
                alt = d_u + w
                if alt < self.dist.get(v, math.inf):
                    self.dist[v] = alt
                    self.pred[v] = u
                    self.successful_relaxations += 1
                    heapq.heappush(heap, (alt, v))

        return True
