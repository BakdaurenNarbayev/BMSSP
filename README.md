# Graph Algorithm Benchmark

A comprehensive benchmark suite for evaluating shortest path algorithms: Dijkstra's algorithm, Bellman-Ford algorithm, and BMSSP (Bounded Multi-Source Shortest Path algorithm from the `Breaking the Sorting Barrier for Directed Single-Source Shortest Paths` paper). The project supports a demo run, custom dataset benchmarking, and a multi-size scaling benchmark that measures performance across various graph configurations. Results and plots are saved to timestamped directories.

## Features

* Demo run for quick algorithm validation on small graphs
* Custom dataset benchmarking using the following format: `source_node_idx dest_node_idx optional_weight`
* Scaling benchmark across logarithmically spaced graph sizes
* Interactive GUI for algorithm visualization and configuration
* Configurable experiment parameters and seeds
* Saves JSON results and PDF plots to timestamped directories

## Requirements

* Python 3.13 (recommended)

While the project is expected to run with newer versions of Python, it was only tested with Python version 3.13.

## Recommended Environment

Create and activate the recommended `conda` environment:

```bash
conda create -n graph_benchmark python=3.13 -y
conda activate graph_benchmark
```

## Install Dependencies

### Minimal Setup

This allows the usage of all the repository's functionality:

```bash
pip install -r requirements.txt
```

## Running

### Benchmark Modes

Configure the desired mode in the config file (`config/main.yaml`):

**Demo mode example:**
```yaml
demo_run: true
custom_dataset_run: false
scaling_benchmark_run: false
```

**Custom dataset mode example:**
```yaml
demo_run: false
custom_dataset_run: true
scaling_benchmark_run: false
```

**Scaling benchmark example:**
```yaml
demo_run: false
custom_dataset_run: false
scaling_benchmark_run: true
```

Run the main benchmark program:

```bash
python benchmark/main.py
```

Note: If multiple run modes are set to `true`, all of them will be ran. The priority is given in the order: demo_run > custom_dataset_run > scaling_benchmark_run.

### GUI Mode

Launch the interactive GUI for algorithm visualization:

```bash
python gui/run.py
```

The GUI provides:
* Random graph generation with configurable node count
* Algorithm execution (Dijkstra, Bellman-Ford, BMSSP)
* Graph visualization before and after solving shortest paths
* Benchmark configuration and execution
* Results viewing interface

## Unit Tests

Run unit tests with:

```bash
python -m unittest discover
```

## Configuration

The configuration is read from `config/main.yaml`. The following sections describe the available configuration options.

### Demo Configuration

```yaml
demo_run: false
demo_conf:
  algos_to_test:
    - dijkstra
    - bellmanford
  save_result_path: results
```

**algos_to_test:**
List of algorithms to benchmark in demo mode. Available options:
- `dijkstra`: Dijkstra's shortest path algorithm
- `bellmanford`: Bellman-Ford algorithm
- `bmssp`: Bounded Multi-Source Shortest Path algorithm from the `Breaking the Sorting Barrier for Directed Single-Source Shortest Paths` paper

**save_result_path:**
Directory where benchmark outputs are stored. Results are saved into a timestamped subdirectory (e.g., `results/20251125_143210/`) containing JSON results and PDF plots.

### Custom Dataset Configuration

```yaml
custom_dataset_run: false
custom_dataset_conf:
  graph_path: benchmark/datasets/road-minnesota.mtx
  directed_graph: false
  algos_to_test:
    - dijkstra
    - bellmanford
  save_result_path: results
```

**graph_path:**
Path to a graph file in Matrix Market (.mtx) format. The benchmark will load and test algorithms on this specific graph.

**directed_graph:**
Boolean flag indicating whether the input graph should be treated as directed (`true`) or undirected (`false`).

**algos_to_test:**
List of algorithms to benchmark on the custom dataset.

**save_result_path:**
Directory for saving benchmark results and plots.

### Scaling Benchmark Configuration

```yaml
scaling_benchmark_run: true
scaling_benchmark_conf:
  min_nodes: 10
  max_nodes: 1e5
  max_in_degree: 2
  max_out_degree: 2
  num_steps: 5
  edge_ratios:
    - 1.2
    - 1.5
    - 1.8
  algos_to_test:
    - dijkstra
    - bellmanford
  exclude_algos_above:
    - ["bellmanford", 1e3]
  seed: 42
  num_trials: 3
  save_result_path: results
```

**Graph Generation:**
The benchmark generates random graphs with varying sizes between `min_nodes` and `max_nodes`, spaced logarithmically according to `num_steps`. For example, with `min_nodes=10`, `max_nodes=100000`, and `num_steps=5`, the system generates graphs at 5 size points between 10 and 100,000 nodes.

**min_nodes / max_nodes:**
The range of graph sizes to test. Sizes are distributed logarithmically.

**max_in_degree / max_out_degree:**
Maximum number of incoming and outgoing edges per node. These parameters control graph density and connectivity.

**num_steps:**
Number of different graph sizes to test between `min_nodes` and `max_nodes`.

**edge_ratios:**
List of edge-to-node ratios to test. Each ratio creates a different graph density. For example, `edge_ratios: [1.2, 1.5]` will test graphs where the number of edges is 1.2× and 1.5× the number of nodes.

**algos_to_test:**
List of algorithms to benchmark. Available options:
- `dijkstra`
- `bellmanford`
- `bmssp`

**exclude_algos_above:**
Some algorithms become impractical at large graph sizes due to computational complexity. This setting allows disabling algorithms when the graph size exceeds a threshold.

* Each entry is a pair `[algorithm_name, max_allowed_nodes]`
* For example, `["bellmanford", 1e3]` means Bellman-Ford is only tested on graphs up to and including 1,000 nodes
* Plotting note: When an algorithm is excluded for larger sizes, its performance curve is linearly extrapolated from its last valid measurement. Extrapolated segments appear as dashed lines.

**num_trials:**
Number of times each benchmark is repeated for a given graph configuration. The median value across trials is reported for each metric to smooth out system noise.

**seed:**
Random seed for reproducible graph generation across runs.

**save_result_path:**
Directory where benchmark outputs are stored. Results are saved into timestamped subdirectories containing:
* JSON file with raw benchmark results
* PDF plot showing performance trends

If unset (`null`), results are not saved to disk; only interactive plots are shown.

## Graph Generation

Graphs are randomly generated with the following characteristics:

1. **Node count**: Determined by the scaling parameters (`min_nodes`, `max_nodes`, `num_steps`)

2. **Edge generation**: Edges are added randomly while respecting `max_in_degree` and `max_out_degree` constraints, with the total number of edges controlled by `edge_ratios`

3. **Edge weights**: Randomly assigned positive weights

4. **Reproducibility**: A random seed ensures consistent graph generation across runs

5. **Connectivity**: The generation process attempts to create connected graphs suitable for shortest path algorithms

## Docstring

This project uses *NumPy-style docstrings*. Comments and docstrings in the codebase were generated with assistance from AI tools.