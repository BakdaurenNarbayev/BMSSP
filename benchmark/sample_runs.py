import sys
import numpy as np
from benchmark.utils.plot import plot_results
from typing import Any, Dict, List, Optional, Tuple
from benchmark.utils.benchmark import ShortestPathBenchmark
from benchmark.utils.generate_graphs import generate_random_graph
from benchmark.utils.misc import save_benchmark_results_json, get_file_paths_to_save


def print_benchmark_results(
    results: Dict[str, Dict[str, Any]],
    title: Optional[str] = None,
) -> None:
    """
    Print benchmark results in a formatted ASCII table for shortest-path algorithms.
    Handles both numeric and boolean metrics, including scaling (list) and non-scaling (single value).
    """
    if not results:
        print("No benchmark results to display.")
        return

    alg_names = list(results.keys())
    metric_order = [
        "run_sec_median",
        "iterations_median",
        "edge_relaxations_median",
        "successful_relaxations_median",
        "negative_cycle_detected",
    ]

    metric_units = {
        "run_sec_median": "s",
        "iterations_median": "it",
        "edge_relaxations_median": "relax",
        "successful_relaxations_median": "relax",
    }

    rows = []
    for alg in alg_names:
        metrics = results[alg]
        row = {"Algorithm": alg}
        for metric in metric_order:
            val = metrics.get(metric, None)
            if isinstance(val, bool):
                row[metric] = "True" if val else "False"
            else:
                row[metric] = f"{val:.4f}" if val is not None else "N/A"

        rows.append(row)

    headers = ["Algorithm"]
    metric_key_map = {}

    for metric in metric_order:
        unit = metric_units.get(metric, "").strip()
        if unit:
            header = f"{metric.replace('_', ' ').title()} ({unit})"
        else:
            header = metric.replace("_", " ").title()
        headers.append(header)
        metric_key_map[header] = metric

    widths = {}
    for h in headers:
        vals = [str(r.get(metric_key_map.get(h, h), "")) for r in rows]
        widths[h] = max(len(h), max(len(v) for v in vals))

    border = "+" + "+".join("-" * (widths[h] + 2) for h in headers) + "+"
    header_line = " | ".join(f"{h:^{widths[h]}}" for h in headers)

    print()
    if title:
        print(title.center(len(border)))
    print(border)
    print("| " + header_line + " |")
    print(border.replace("-", "="))
    for r in rows:
        line = " | ".join(
            (
                str(r.get(metric_key_map.get(h, h), "")).rjust(widths[h])
                if h != "Algorithm"
                else str(r.get(metric_key_map.get(h, h), "").title()).ljust(widths[h])
            )
            for h in headers
        )
        print("| " + line + " |")
    print(border)


def demo_run() -> None:
    """
    Run a small demo benchmark for graph-based shortest path checker and print results.

    This demo generates a modest graph of 50,000 nodes and 100,000 edges,
    runs the benchmark using default parameters, and prints results using
    `print_benchmark_results`.

    Notes:
        - Plotting is skipped because plotting requires results across multiple dataset sizes.
        - This demo uses a small-scale dataset for quick testing.
    """
    print(
        "Demo: generate a small-scale dataset and run the benchmark logic \n"
        "Note: plotting skipped — plotting requires results across multiple dataset sizes.\n"
        "To enable plotting, use a scaling benchmark run and disable demo_run."
    )
    print("=" * 90 + "\n")

    seed = 42
    start_node_idx = 0

    num_nodes = 50_000
    num_edges = 100_000

    print(f"Generating a graph with {num_nodes:,} nodes and {num_edges:,}...")
    graph = generate_random_graph(num_nodes, num_edges, seed=seed)

    print("Running benchmark...")
    results = ShortestPathBenchmark(graph, start_node_idx).run()

    print_benchmark_results(results)


def scaling_benchmark(
    min_nodes: int = 1_000,
    max_nodes: int = 200_000,
    num_steps: int = 8,
    edge_ratios: List[float] = [1.0],
    algos_to_test: Optional[List[str]] = None,
    exclude_algos_above: Optional[List[Tuple[str, int]]] = None,
    num_trials: int = 3,
    seed: int = 42,
) -> Dict[str, Dict[str, List[float]]]:

    # Generate logarithmically spaced dataset sizes
    nodes_sizes = np.logspace(
        np.log10(min_nodes), np.log10(max_nodes), num_steps, dtype=int
    )

    # Remove duplicates that may be caused by rounding
    nodes_sizes = sorted(set(nodes_sizes))
    print(
        f"Running scaling benchmark with node sizes: {' | '.join(f'{x:,}' for x in nodes_sizes)}"
    )

    start_node_index = 0

    # Initialize results structure
    all_results = {}
    metrics_to_track = [
        "run_sec_median",
        "iterations_median",
        "edge_relaxations_median",
        "successful_relaxations_median",
        "negative_cycle_detected",
    ]

    for edge_ratio in edge_ratios:
        print(f"Benchmarking edge ratio: {edge_ratio}")

        edge_ratio_results = {}
        for node_size in nodes_sizes:
            print(f"\tBenchmarking node size: {node_size:,}")
            graph = generate_random_graph(node_size, int(node_size * edge_ratio), seed)

            current_algos_to_test = algos_to_test.copy() if algos_to_test else None
            for structure_name, max_allowed_size in exclude_algos_above or []:
                max_allowed_size = int(float(max_allowed_size))
                if current_algos_to_test and node_size > max_allowed_size:
                    current_algos_to_test.remove(structure_name)

            try:
                benchmark = ShortestPathBenchmark(
                    graph,
                    start_node_index,
                    num_trials,
                    current_algos_to_test,
                )

                results = benchmark.run()

                for structure_name, metrics in results.items():
                    if structure_name not in edge_ratio_results:
                        edge_ratio_results[structure_name] = {
                            metric: [] for metric in metrics_to_track
                        }

                    for metric in metrics_to_track:
                        if metric in metrics:
                            edge_ratio_results[structure_name][metric].append(
                                metrics[metric]
                            )

            except Exception as e:
                sys.exit(
                    f"Error benchmarking with number of nodes: {node_size} and edge ratio: {edge_ratio}: {e}"
                )

        # Merge edge_ratio results into all_results
        for structure_name, metrics_dict in edge_ratio_results.items():
            if structure_name not in all_results:
                all_results[structure_name] = {
                    metric: [] for metric in metrics_to_track
                }

            for metric, values in metrics_dict.items():
                all_results[structure_name][metric].append(values)

    return all_results, nodes_sizes


def run_scaling_benchmark(
    min_nodes: int = 1_000,
    max_nodes: int = 200_000,
    num_steps: int = 8,
    edge_ratios: List[float] = [1.0],
    algos_to_test: Optional[List[str]] = None,
    exclude_algos_above: Optional[List[Tuple[str, int]]] = None,
    num_trials: int = 3,
    seed: int = 42,
    save_result_path: str = None,
) -> None:
    print("Scaling Benchmark Run: Performance vs Graph Size")
    print("=" * 50)

    # This is to allow scientific notations in yaml e.g. 1e9
    min_nodes = int(float(min_nodes))
    max_nodes = int(float(max_nodes))

    results, node_sizes = scaling_benchmark(
        min_nodes=min_nodes,
        max_nodes=max_nodes,
        num_steps=num_steps,
        edge_ratios=edge_ratios,
        algos_to_test=algos_to_test,
        exclude_algos_above=exclude_algos_above,
        num_trials=num_trials,
        seed=seed,
    )

    per_size_results = {}
    for struct_name, metrics in results.items():
        per_size_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, list) and all(isinstance(inner, list) for inner in v):
                last_edge_ratio_values = v[-1]
                per_size_metrics[k] = (
                    last_edge_ratio_values[-1] if last_edge_ratio_values else None
                )
            else:
                per_size_metrics[k] = v
        per_size_results[struct_name] = per_size_metrics

    print_benchmark_results(
        per_size_results,
        title=f"Results for the Graph with {node_sizes[-1]:,} Node and {int(node_sizes[-1] * edge_ratios[-1]):,} Edges",
    )

    print("\nGenerating plots...")
    if save_result_path is not None:
        plot_results(results, node_sizes, edge_ratios, file_path_pdf)
        file_path_json, file_path_pdf = get_file_paths_to_save(save_result_path)
        save_benchmark_results_json(file_path_json, results, node_sizes, edge_ratios)
    else:
        plot_results(results, node_sizes, edge_ratios)
