import math
import heapq
from collections import deque
from typing import List, Tuple
from BMSSP_algorithm.base import BaseShortestPath
from BMSSP_algorithm.graph import Graph
from BMSSP_algorithm.data_structures.BBLL import BBLL

class BMSSP(BaseShortestPath):
    def __init__(self, graph: Graph, source: int):
        super().__init__(graph, source)

        self.reset_state()

        for v in range(self.graph.node_count):
            # ensure every node has an entry even if isolated
            self.dist[v] = float('inf')
            self.pred[v] = None

        if source >= self.graph.node_count:
            self.graph.node_count = max(self.graph.node_count, source + 1)
            self.dist[source] = 0.0
            self.pred[source] = -1
        else:
            self.dist[source] = 0.0
            self.pred[source] = -1

        self.k = math.floor(math.pow(math.log2(self.graph.node_count), 1/3))
        self.t = math.floor(math.pow(math.log2(self.graph.node_count), 2/3))
        self.max_iterations = self.graph.node_count
        self.multiplier = math.pow(10, math.floor(math.log10(self.graph.node_count) + 1))

    def validate(self) -> bool:
        return True

    def run(self) -> bool:
        if not self.validate():
            return False

        l0 = math.ceil(math.log2(self.graph.node_count) / self.t)
        B0 = float('inf')
        S0 = {self.source}

        B_prime, U = self.bmssp(l0, B0, S0)

        return True    

    def find_pivots(self, B, S):
        #print("--- FIND PIVOTS ---")
        W = set(S)
        W_prev = set(S)
        #print(f"W = {W}, W_prev = {W_prev}, k = {self.k}")

        # k relaxations
        for _ in range(1, self.k + 1):
            W_curr = set()
            
            for u in W_prev:
                d_u = self.dist[u]
                for v, w in self.graph.get_neighbors(u):
                    alt = d_u + w
                    alt_multiplied = (alt + 1) * self.multiplier + u + v / self.multiplier
                    if self.dist[v] != float('inf'):
                        d_v_multiplied = (self.dist[v] + 1) * self.multiplier + self.pred[v] + v / self.multiplier
                    else:
                        d_v_multiplied = float('inf')

                    if alt_multiplied <= d_v_multiplied:
                        self.dist[v] = alt
                        self.pred[v] = u

                        if alt_multiplied < B:
                            W_curr.add(v)

            W |= W_curr

            if len(W) > self.k * len(S):
                #print(f"W IS TOO LARGE")
                #print(f"W = {W}")
                return set(S), W

            W_prev = W_curr

            #print(f"W = {W}, W_prev = {W_prev}")

        # Build forest F
        children = {u: [] for u in W}

        for u in W:
            d_u = self.dist[u]
            for v, w in self.graph.get_neighbors(u):
                if v in W and self.dist[v] == d_u + w:
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

        return set(P), W
    
    def base_case(self, B, S):
        # S must be a singleton {x}
        #print(f"BASE CASE: S = {S}")

        assert len(S) == 1
        x = next(iter(S))

        # U0 starts as S
        U0 = set(S)

        # Min-heap for Dijkstra
        heap: List[Tuple[float, int]] = [(self.dist[x], x)]
        visited = set()

        while heap and len(U0) < self.k + 1:
            d_u, u = heapq.heappop(heap)
            if d_u > self.dist[u] or u in visited:
                continue
            
            visited.add(u)
            U0.add(u)

            # relax neighbors
            for v, w in self.graph.get_neighbors(u):
                alt = d_u + w
                alt_multiplied = (alt + 1) * self.multiplier + u + v / self.multiplier
                if self.dist[v] != float('inf'):
                    d_v_multiplied = (self.dist[v] + 1) * self.multiplier + self.pred[v] + v / self.multiplier
                else:
                    d_v_multiplied = float('inf')

                if alt_multiplied <= d_v_multiplied and alt_multiplied < B:
                    self.dist[v] = alt
                    self.pred[v] = u
                    heapq.heappush(heap, (alt, v))

        # If U0 has at most k vertices → trivial case
        if len(U0) <= self.k:
            return B, U0

        # Else choose new boundary B'
        B_prime = max((self.dist[v] + 1) * self.multiplier + self.pred[v] + v / self.multiplier for v in U0) 
        U = {v for v in U0 if (self.dist[v] + 1) * self.multiplier + self.pred[v] + v / self.multiplier < B_prime}
        return B_prime, U

    def bmssp(self, l: int, B: float, S: set[int]) -> tuple[float, set[int]]:
        """
        Recursive BMSSP(l, B, S) implementing Algorithm 3.

        Requirements (from the paper):
          - |S| <= 2^l * t
          - For every incomplete vertex x with d(x) < B, the shortest path
            to x visits some complete vertex y in S.

        Returns:
          B_prime (float): new boundary B' <= B
          U (set[int]): set of vertices discovered/completed in this call
        """

        #print(f"l = {l}")

        # --- Base case ---
        if l == 0:
            B_prime, U = self.base_case(B, S)
            #print(f"Base case: B_prime = {B_prime}, U = {U}")
            return B_prime, U

        # --- Recursive case ---
        P, W = self.find_pivots(B, S)
        M = int(math.pow(2, (l - 1) * self.t))

        #print(f"Recursive case: B = {B}, S = {S}, P = {P}, W = {W}, M = {M}")

        D = BBLL(M, B, self.graph.node_count)
        #print("--- D ---")

        # Insert all pivots
        for x in P:
            D.insert(x, (self.dist[x] + 1) * self.multiplier + self.pred[x] + x / self.multiplier)
            D._check_invariants()

        #D.traverse()

        if P:
            B_prime_agg = min((self.dist[x] + 1) * self.multiplier + self.pred[x] + x / self.multiplier for x in P)
        else:
            B_prime_agg = B

        U: set[int] = set()
        Ui_prev: set[int] = set()
        Si_prev: set[int] = set()
        Bi_prev: float = -1
        Bi_prime_prev: float = -1
        U_threshold = self.k * math.pow(2, l * self.t)

        #print(f"B_prime_agg = {B_prime_agg}, U_threshold = {U_threshold}")

        while len(U) < U_threshold and not D.is_empty():
            print(f"l = {l}")
            D.traverse()
            Si, Bi = D.pull()
            D.traverse()
            D._check_invariants()
            if len(Si) == 0:
                break
            #print(f"k = {self.k}, t = {self.t}, U_threshold = {U_threshold}")
            #print(f"Si = {Si}, Bi = {Bi}")
            Bi_prime, Ui = self.bmssp(l - 1, Bi, Si)
            B_prime_agg = min(B_prime_agg, Bi_prime)
            if Ui == Ui_prev and Si == Si_prev and Bi == Bi_prev and Bi_prime == Bi_prime_prev:
                break
            Ui_prev = Ui
            Si_prev = Si
            Bi_prev = Bi
            Bi_prime_prev = Bi_prime

            U |= Ui
            #print(f"U = {U}, Bi_prime = {Bi_prime}, Ui = {Ui}")
            K: set[tuple[int, float]] = set()

            #print(f"Bi_prime = {Bi_prime}, Ui = {Ui}")
            #print(f"B_prime_agg = {B_prime_agg}, U = {U}")

            for u in Ui:
                d_u = self.dist[u]
                for v, w in self.graph.get_neighbors(u):
                    alt = d_u + w
                    alt_multiplied = (alt + 1) * self.multiplier + u + v / self.multiplier
                    if self.dist[v] != float('inf'):
                        d_v_multiplied = (self.dist[v] + 1) * self.multiplier + self.pred[v] + v / self.multiplier
                    else:
                        d_v_multiplied = float('inf')

                    if alt_multiplied <= d_v_multiplied:
                        self.dist[v] = alt
                        self.pred[v] = u

                        #print(f"v = {v}, alt = {alt}, B = {B}, Bi = {Bi}, Bi_prime = {Bi_prime}")

                        if Bi <= alt_multiplied < B:
                            D.insert(v, alt_multiplied)
                            D._check_invariants()
                            #D.traverse()
                        elif Bi_prime <= alt_multiplied < Bi:
                            K.add((v, alt_multiplied))

            prepend_records: set[tuple[int, float]] = K.copy()
            for x in Si:
                d_x_multiplied = (self.dist[x] + 1) * self.multiplier + self.pred[x] + x / self.multiplier
                if Bi_prime <= d_x_multiplied < Bi:
                    prepend_records.add((x, d_x_multiplied))

            D.batch_prepend(prepend_records)
            D._check_invariants()
            #D.traverse()

        B_prime = min(B_prime_agg, B)
        U_final = set(U)
        for x in W:
            if (self.dist[x] + 1) * self.multiplier + self.pred[x] + x / self.multiplier < B_prime:
                U_final.add(x)

        #print(f"U_final = {U_final}")
        return B_prime, U_final

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def build_chain_graph():
    """
    Graph A:
      0 -> 1 (2)
      1 -== 2 (3)
      2 -> 3 (4)
    """
    g = Graph(directed=True)
    g.node_count = 4
    g.add_edge(0, 1, 2)
    g.add_edge(1, 2, 3)
    g.add_edge(2, 3, 4)
    return g, 0  # graph, source


def build_tree_graph():
    """
    Graph B (tree):
           0
         / | \
        1  2  3
        |
        4
    All weights = 1.
    """
    g = Graph(directed=True)
    g.node_count = 5
    g.add_edge(0, 1, 1)
    g.add_edge(0, 2, 1)
    g.add_edge(0, 3, 1)
    g.add_edge(1, 4, 1)
    return g, 0


def build_cycle_graph():
    """
    Graph C (cycle):
      0 -> 1 -== 2 -> 0
    All weights = 1.
    """
    g = Graph(directed=True)
    g.node_count = 3

    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(2, 0, 1)
    return g, 0


def build_paper_like_graph():
    """
    Graph D: a slightly richer DAG to see pivots / recursion.
      0 -> 1 (1)
      1 -== 2 (1)
      1 -> 3 (2)
      0 -> 4 (3)
      4 -> 5 (1)
    """
    g = Graph(directed=True)
    g.node_count = 6

    g.add_edge(0, 1, 1)
    g.add_edge(1, 2, 1)
    g.add_edge(1, 3, 2)
    g.add_edge(0, 4, 3)
    g.add_edge(4, 5, 1)
    return g, 0


def build_medium_graph(n=20, avg_outdegree=2):
    """
    Builds a sparse directed graph with ~n nodes and outdegree ≈ avg_outdegree.
    Graph is guaranteed source-connected.
    """
    import random
    random.seed(0)

    g = Graph(directed=True)
    g.node_count = n

    # Always connect linearly to ensure connectivity
    for u in range(n - 1):
        g.add_edge(u, u + 1, 1)

    # Add sparse random edges
    extra_edges = int(n * avg_outdegree)

    for _ in range(extra_edges):
        u = random.randint(0, n - 2)
        v = random.randint(u + 1, min(n - 1, u + random.randint(2, 50)))
        w = random.randint(1, 10)
        g.add_edge(u, v, w)

    # Add occasional backward edges — optional (small cycles)
    for _ in range(extra_edges // 10):
        u = random.randint(10, n - 1)
        v = random.randint(0, u - 1)
        g.add_edge(u, v, random.randint(1, 10))

    return g, 0


def print_graph(g: Graph):
    print("Graph edges:")
    for u in range(g.node_count):
        for v, w in g.get_neighbors(u):
            print(f"  {u} -> {v} (w={w})")


def run_bmssp_on_graph(name: str, graph_builder):
    print("\n" + "=" * 60)
    print(f" DEMO: {name}")
    print("=" * 60)

    g, source = graph_builder()
    print(f"Source: {source}")
    print_graph(g)

    # Initialize BMSSP
    bm = BMSSP(g, source)

    # Let run() do whatever initialization it currently does
    bm.run()

    print("\nDistances:")
    for i in range(g.node_count):
        print(f"  dist[{i}] = {bm.dist[i]}")

    print("\nPredecessors:")
    for i in range(g.node_count):
        print(f"  pred[{i}] = {bm.pred[i]}")

    print("=" * 60)
    print()


def main():
    # Run all four demos
    run_bmssp_on_graph("A: Simple Chain 0→1→2→3", build_chain_graph)
    run_bmssp_on_graph("B: Tree 0 with children and a leaf path", build_tree_graph)
    run_bmssp_on_graph("C: Cycle 0→1→2→0", build_cycle_graph)
    run_bmssp_on_graph("D: Paper-like Small DAG", build_paper_like_graph)
    run_bmssp_on_graph("E: Medium Space Graph (2000 nodes)", build_medium_graph)


if __name__ == "__main__":
    main()