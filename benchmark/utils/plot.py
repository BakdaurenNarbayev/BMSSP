import numpy as np
import matplotlib.pyplot as plt

from math import ceil
from typing import Dict, Any, List, Optional


def plot_results(
    results: Dict[str, Dict[str, Any]],
    node_sizes: List[int],
    edge_ratios: List[float],
    save_path: Optional[str] = None,
    title: Optional[str] = None,
):
    if not results:
        raise ValueError("results must not be empty")

    alg_names = list(results.keys())
    if len(alg_names) > 3:
        colors = plt.cm.tab20(np.linspace(0, 1, len(alg_names)))
    else:
        colors = ["#4c72b0", "#dd8452", "#55a868"]

    metric_keys_order = [
        "run_sec_median",
        "iterations_median",
        "edge_relaxations_median",
        "successful_relaxations_median",
    ]

    metric_titles = [
        "Execution Time (s)",
        "Iterations",
        "Edge Relaxations",
        "Successful Relaxations",
    ]

    metrics = [m for m in metric_keys_order if any(m in results[a] for a in alg_names)]
    metric_titles = [
        metric_titles[i] for i, m in enumerate(metric_keys_order) if m in metrics
    ]
    n_metrics = len(metrics)

    n_rows = 1
    n_cols = ceil(n_metrics / n_rows)

    fig, axes = plt.subplots(
        n_rows, n_cols, figsize=(6 * n_cols, 5 * n_rows), constrained_layout=True
    )
    if title:
        fig.suptitle(title, fontsize=16)
    axes = np.array(axes).reshape(-1)

    markers = ["o", "s", "^", "D", "v", "P", "*", "X", "h", "8"]
    linestyles = ["-", "--", ":"]
    edge_styles = [(m, ls) for m in markers for ls in linestyles]

    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        label = metric_titles[idx]

        for i, alg in enumerate(alg_names):
            vals_all_edge_ratios = results[alg].get(metric)

            if vals_all_edge_ratios is None:
                continue

            if isinstance(vals_all_edge_ratios, (int, float, bool)):
                ax.bar(alg, vals_all_edge_ratios, color=colors[i])
            else:
                if not isinstance(vals_all_edge_ratios[0], list):
                    vals_all_edge_ratios = [vals_all_edge_ratios]

                for er_idx, vals in enumerate(vals_all_edge_ratios):
                    if not vals:
                        continue
                    marker, linestyle = edge_styles[er_idx % len(edge_styles)]
                    label_suffix = (
                        f" (ER={edge_ratios[er_idx]})" if len(edge_ratios) > 1 else ""
                    )

                    ax.plot(
                        node_sizes[: len(vals)],
                        vals,
                        label=f"{alg}{label_suffix}",
                        marker=marker,
                        linestyle=linestyle,
                        color=colors[i],
                        linewidth=2,
                    )

        # Axis labels and title
        ax.set_xlabel("Node Size" if len(node_sizes) > 1 else "Algorithm")
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.grid(True, alpha=0.3)

        scale_run = any(
            isinstance(results[alg].get(metric, None), list)
            and (not isinstance(results[alg][metric], bool))
            for alg in alg_names
        )

        if scale_run:
            ax.legend()
            ax.set_yscale("log")
            ax.set_xscale("log")

    for k in range(n_metrics, len(axes)):
        axes[k].axis("off")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")
    else:
        plt.show()


if __name__ == "__main__":
    example_results = {
        "dijkstra": {
            "run_sec_median": 0.0012,
            "iterations_median": 5,
            "edge_relaxations_median": 8,
            "successful_relaxations_median": 5,
            "negative_cycle_detected": False,
        },
        "bellmanford": {
            "run_sec_median": 0.0034,
            "iterations_median": 4,
            "edge_relaxations_median": 12,
            "successful_relaxations_median": 5,
            "negative_cycle_detected": False,
        },
    }
    plot_results(example_results, node_sizes=[100], edge_ratios=[1])

    example_scaling = {
        "dijkstra": {
            "run_sec_median": [
                [0.0002, 0.0004, 0.0009, 0.002],
                [0.0005, 0.0007, 0.0015, 0.003],
            ],
            "iterations_median": [[2, 3, 4, 6], [3, 4, 6, 9]],
            "edge_relaxations_median": [[4, 6, 9, 13], [6, 7, 8, 15]],
            "successful_relaxations_median": [[2, 3, 4, 6], [3, 4, 5, 13]],
            "negative_cycle_detected": [
                [False, False, False, False],
                [False, False, False, False],
            ],
        },
        "bellmanford": {
            "run_sec_median": [
                [0.0005, 0.0014, 0.0039, 0.009],
                [0.0007, 0.0019, 0.0049, 0.012],
            ],
            "iterations_median": [[2, 3, 4, 6], [4, 6, 10, 12]],
            "edge_relaxations_median": [[6, 12, 24, 48], [10, 16, 34, 58]],
            "successful_relaxations_median": [[2, 5, 8, 12], [3, 4, 10, 22]],
            "negative_cycle_detected": [
                [False, False, False, False],
                [False, False, False, False],
            ],
        },
    }

    plot_results(
        example_scaling, node_sizes=[100, 500, 1_000, 5_000], edge_ratios=[1, 1.2]
    )
