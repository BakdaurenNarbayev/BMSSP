#!/usr/bin/env python3

import json
import argparse
from pathlib import Path
from utils.plot import plot_results

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Plot scaling results from JSON")
parser.add_argument(
    "json_path",
    type=str,
    help="Path to the results.json file",
)
parser.add_argument(
    "--save_path",
    type=str,
    help="Path to save the PDF plot. If not provided will simply show the plot without saving it.",
)
parser.add_argument(
    '--disable_log_scale', 
    action='store_true',
    help="Enable verbose output"
)

args = parser.parse_args()

file_path = Path(args.json_path)
save_path = Path(args.save_path) if args.save_path else None

# Load JSON data
with open(file_path, "r") as f:
    data = json.load(f)

results = data["results"]
node_sizes = data["node_sizes"]
edge_ratios = data["edge_ratios"]

# Plot results
plot_results(
    results,
    node_sizes,
    edge_ratios,
    save_path=save_path,
    log_scale=not args.disable_log_scale,
)