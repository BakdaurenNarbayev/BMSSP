import numpy as np
import matplotlib.pyplot as plt

from math import ceil
from typing import Dict, Any, List, Optional

def plot_results(
    results: Dict[str, Dict[str, Any]],
    node_sizes: List[int],
    edge_ratios: List[float],
    log_scale: bool = True,
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
        "peak_memory_median",
        # "iterations_median",
        # "edge_relaxations_median",
        # "successful_relaxations_median",
    ]
    metric_titles = [
        "Execution Time (s)",
        "Peak Memory (bytes)",
        # "Iterations",
        # "Edge Relaxations",
        # "Successful Relaxations",
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
    
    gray_shades = ["#6a6a6a", "#8a8a8a"]
    for idx, metric in enumerate(metrics):
        ax = axes[idx]
        label = metric_titles[idx]
        
        max_len = 0
        for alg in alg_names:
            vals_all_edge_ratios = results[alg].get(metric)
            if vals_all_edge_ratios is not None and not isinstance(vals_all_edge_ratios, (int, float, bool)):
                if not isinstance(vals_all_edge_ratios[0], list):
                    vals_all_edge_ratios = [vals_all_edge_ratios]
                for vals in vals_all_edge_ratios:
                    if vals:
                        max_len = max(max_len, len(vals))
        
        gray_idx = 0
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
                    
                    # Check if this data is incomplete (shorter than max)
                    has_missing = len(vals) < max_len
                    
                    if has_missing and len(vals) >= 2 and (alg != "bmssp" and metric != "peak_memory_median"):
                        # Use available data points
                        valid_x = node_sizes[:len(vals)]
                        valid_y = vals
                        
                        # Transform for log scale if needed
                        if log_scale:
                            if alg != "bmssp": 
                                valid_x_log = np.log(valid_x)
                                valid_y_log = np.log(valid_y)
                                
                                # Try polynomial degrees 1-3
                                best_degree = 1
                                best_score = -np.inf
                                for degree in range(1, min(4, len(valid_x))):
                                    try:
                                        coeffs = np.polyfit(valid_x_log, valid_y_log, degree)
                                        y_pred = np.polyval(coeffs, valid_x_log)
                                        score = -np.mean((valid_y_log - y_pred) ** 2)
                                        if score > best_score:
                                            best_score = score
                                            best_degree = degree
                                    except:
                                        pass
                                
                                # Fit with best degree
                                coeffs = np.polyfit(valid_x_log, valid_y_log, best_degree)
                                
                                # Extrapolate only the missing part
                                missing_x_log = np.log(node_sizes[len(vals):max_len])
                                missing_y_log = np.polyval(coeffs, missing_x_log)
                                missing_vals = np.exp(missing_y_log)
                            else:
                                valid_x_log = np.log(valid_x)
                                valid_y_log = np.log(valid_y)

                                # Fit y = a * n * log(n) in log space
                                # log(y) = log(a) + log(n * log(n))
                                # log(y) = log(a) + log(n) + log(log(n))
                                valid_x_nlogn = valid_x * np.log(valid_x)
                                valid_x_nlogn_log = np.log(valid_x_nlogn)

                                # Simple linear fit: log(y) = m * log(n*log(n)) + b
                                coeffs = np.polyfit(valid_x_nlogn_log, valid_y_log, 1)

                                # Extrapolate only the missing part
                                missing_x = node_sizes[len(vals):max_len]
                                missing_x_nlogn = missing_x * np.log(missing_x)
                                missing_x_nlogn_log = np.log(missing_x_nlogn)
                                missing_y_log = np.polyval(coeffs, missing_x_nlogn_log)
                                missing_vals = np.exp(missing_y_log)
                        else:
                            # Linear space interpolation
                            if alg != "bmspp":
                                best_degree = 1
                                best_score = -np.inf
                                for degree in range(1, min(4, len(valid_x))):
                                    try:
                                        coeffs = np.polyfit(valid_x, valid_y, degree)
                                        y_pred = np.polyval(coeffs, valid_x)
                                        score = -np.mean((np.array(valid_y) - y_pred) ** 2)
                                        if score > best_score:
                                            best_score = score
                                            best_degree = degree
                                    except:
                                        pass
                                
                                coeffs = np.polyfit(valid_x, valid_y, best_degree)
                                missing_vals = np.polyval(coeffs, node_sizes[len(vals):max_len])
                            else:
                                valid_x_nlogn = valid_x * np.log(valid_x)
                                coeffs = np.polyfit(valid_x_nlogn, valid_y, 1)
                                missing_x = node_sizes[len(vals):max_len]
                                missing_x_nlogn = missing_x * np.log(missing_x)
                                missing_vals = np.polyval(coeffs, missing_x_nlogn)
                        
                        if gray_idx < len(gray_shades):
                            gray_color = gray_shades[gray_idx]
                        else:
                            gray_val = np.random.randint(32, 144)
                            gray_color = f"#{gray_val:02x}{gray_val:02x}{gray_val:02x}"
                        
                        connected_x = [node_sizes[len(vals)-1]] + list(node_sizes[len(vals):max_len])
                        connected_y = [vals[-1]] + list(missing_vals)

                        ax.plot(
                            connected_x,
                            connected_y,
                            linestyle=linestyle,
                            color=gray_color,
                            linewidth=1.5,
                            alpha=0.7,
                        )

                        ax.plot(
                            node_sizes[:len(vals)],
                            vals,
                            label=f"{alg}{label_suffix}",
                            marker=marker,
                            linestyle=linestyle,
                            color=colors[i],
                            linewidth=2,
                        )

                        gray_idx += 1
                    else:
                        ax.plot(
                            node_sizes[:len(vals)],
                            vals,
                            label=f"{alg}{label_suffix}",
                            marker=marker,
                            linestyle=linestyle,
                            color=colors[i],
                            linewidth=2,
                        )
        
        # Axis labels and title
        ax.set_xlabel("Number of Nodes" if len(node_sizes) > 1 else "Algorithm")
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
            if log_scale:
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
