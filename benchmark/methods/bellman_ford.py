import math
from methods.base import BaseShortestPath


class BellmanFord(BaseShortestPath):
    def validate(self) -> bool:
        # Bellman-Ford accepts negative weights; always valid
        return True

    def run(self) -> bool:
        self.reset_state()
        source = self.source

        # initialize distances
        for n in range(self.graph.node_count):
            self.dist[n] = math.inf
            self.pred[n] = None

        if source >= self.graph.node_count:
            self.graph.node_count = max(self.graph.node_count, source + 1)
            self.dist[source] = 0.0
        else:
            self.dist[source] = 0.0

        edges = self.graph.get_all_edges()
        n = self.graph.node_count

        # Relax edges up to n-1 times
        for _ in range(max(0, n - 1)):
            self.iterations += 1
            any_relaxed = False
            for u, v, w in edges:
                self.edge_relaxations += 1
                du = self.dist.get(u, math.inf)
                if math.isinf(du):
                    continue
                if du + w < self.dist.get(v, math.inf):
                    self.dist[v] = du + w
                    self.pred[v] = u
                    self.successful_relaxations += 1
                    any_relaxed = True
            if not any_relaxed:
                break

        # final pass to detect negative cycles reachable from source
        self.iterations += 1
        for u, v, w in edges:
            self.edge_relaxations += 1
            du = self.dist.get(u, math.inf)
            if math.isinf(du):
                continue
            if du + w < self.dist.get(v, math.inf):
                # negative cycle detected
                return False

        return True
