import gc
import time
import statistics

import tracemalloc
from benchmark.methods.BMSSP import BMSSP
from typing import Dict, Any, List, Optional
from benchmark.methods.dijkstra import Dijkstra
from benchmark.datastructures.graph import Graph
from benchmark.methods.bellman_ford import BellmanFord


class ShortestPathBenchmark:
    """
    Benchmark for shortest-path algorithms (Dijkstra, Bellman-Ford).

    It receives:
      - a Graph object (already constructed)
      - a start node (int)
      - algorithms = ["dijkstra", "bellmanford", "bmssp"]

    Metrics tracked:
      - run_ns / run_sec
      - iterations
      - edge_relaxations
      - successful_relaxations
      - has_negative_cycle
      - peak_memory_bytes (peak memory usage during execution)
    """

    def __init__(
        self,
        graph,
        start: int,
        trials: int = 3,
        algorithms: Optional[list[str]] = None,
    ):
        self.graph = graph
        self.start = start
        self.trials = trials

        available_algos = {
            "dijkstra": Dijkstra,
            "bellmanford": BellmanFord,
            "bmssp": BMSSP,
        }

        if algorithms is None:
            self.algorithms = available_algos
        else:
            self.algorithms = {
                name: available_algos[name.lower()]
                for name in algorithms
                if name.lower() in available_algos
            }

        if not self.algorithms:
            raise ValueError("No valid algorithms provided")

    def _run_single_trial(self, alg_cls: type) -> Dict[str, Any]:
        """
        Executes one timed run of a shortest-path algorithm.
        """

        gc.collect()

        # Create a fresh copy of the graph so algorithms don't modify the original
        G = Graph(self.graph.directed)
        for u, nbrs in self.graph.adjacency_list.items():
            for v, w in nbrs:
                G.add_edge(u, v, w)

        algo = alg_cls(G, self.start)
        ok = algo.validate()
        algo.setup()

        if ok:
            t0 = time.perf_counter_ns()
            tracemalloc.start()
            ok = algo.run()
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            run_ns = time.perf_counter_ns() - t0
            peak_memory_bytes = peak
        else: 
            run_ns = -1
            peak_memory_bytes = -1

        return {
            "run_ns": run_ns,
            "run_ok": bool(ok),
            "iterations": getattr(algo, "iterations", None),
            "edge_relaxations": getattr(algo, "edge_relaxations", None),
            "successful_relaxations": getattr(algo, "successful_relaxations", None),
            "has_negative_cycle": getattr(algo, "has_negative_cycle", False),
            "peak_memory_bytes": peak_memory_bytes,
        }

    def _aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Take median of numeric metrics across all trials."""

        run_ns = [r["run_ns"] for r in results]
        iterations = [r["iterations"] for r in results if r["iterations"] is not None]
        relax = [
            r["edge_relaxations"] for r in results if r["edge_relaxations"] is not None
        ]
        success_relax = [
            r["successful_relaxations"]
            for r in results
            if r["successful_relaxations"] is not None
        ]
        memory = [r["peak_memory_bytes"] for r in results]
        has_neg = any(r["has_negative_cycle"] for r in results)

        return {
            "run_sec_median": statistics.median(run_ns) / 1e9,
            "run_ns_median": statistics.median(run_ns),
            "iterations_median": statistics.median(iterations) if iterations else None,
            "edge_relaxations_median": statistics.median(relax) if relax else None,
            "successful_relaxations_median": (
                statistics.median(success_relax) if success_relax else None
            ),
            "negative_cycle_detected": has_neg,
            "peak_memory_median": statistics.median(memory)
        }

    def run(self) -> Dict[str, Dict[str, Any]]:
        """
        Run benchmark for every algorithm.
        """
        summary: Dict[str, Dict[str, Any]] = {}

        for name, alg_cls in self.algorithms.items():
            trials = [self._run_single_trial(alg_cls) for _ in range(self.trials)]
            summary[name] = self._aggregate(trials)

        return summary
