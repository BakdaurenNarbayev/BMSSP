import math
from collections import deque
from BMSSP_algorithm.base import BaseShortestPath
from BMSSP_algorithm.graph import Graph
from BMSSP_algorithm.data_structures.Block import BNode
from BMSSP_algorithm.data_structures.BBLL import BBLL

class BMSSP(BaseShortestPath):
    def __init__(self, graph: Graph, source: int):
        super().__init__(graph, source)
        N = self.graph.node_count
        self.k = math.floor(math.pow(math.log2(N), 1/3))
        self.t = math.floor(math.pow(math.log2(N), 2/3))

    def validate(self) -> bool:
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

        '''
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
        '''

        return True    

    def find_pivots(self, B, S):
        W = set(S)
        W_prev = set(S)

        # k relaxations
        for _ in range(1, self.k + 1):
            W_curr = set()
            
            for u in W_prev:
                d_u = self.dist.get(u, math.inf)
                for v, w in self.graph.get_neighbors(u):
                    alt = d_u + w
                    if alt <= self.dist.get(v, math.inf):
                        self.dist[v] = alt
                        self.pred[v] = u

                        if alt < B:
                            W_curr.add(v)

            W |= W_curr

            if len(W) > self.k * len(S):
                return set(S), W

            W_prev = W_curr

        # Build forest F
        children = {u: [] for u in W}

        for u in W:
            d_u = self.dist.get(u, math.inf)
            for v, w in self.graph.get_neighbors(u):
                if v in W and self.dist.get(v, math.inf) == d_u + w:
                    children[u].append(v)

        # Roots = nodes with no parent
        has_parent = set()
        for u in children:
            for v in children[u]:
                has_parent.add(v)

        roots = [u for u in W if u not in has_parent]

        # Compute subtree sizes
        subtree_size = {}

        for r in roots:
            size = 0
            q = deque([r])
            while q:
                x = q.popleft()
                size += 1
                for ch in children[x]:
                    q.append(ch)
            subtree_size[r] = size

        # P = roots in S that have subtree ≥ k
        P = {u for u in S if u in subtree_size and subtree_size[u] >= self.k}

        return P, W
    