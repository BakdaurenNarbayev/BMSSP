import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from benchmark.utils.config import load_config
from benchmark.utils.sample_runs import (
    demo_run,
    run_scaling_benchmark,
    run_custom_graph,
)


def run_benchmark(force_save: bool = False):
    config, required_force_save = load_config(force_save=force_save)

    if config["demo_run"]:
        demo_conf = config["demo_conf"]
        output_paths = demo_run(**demo_conf)
    if config["custom_dataset_run"]:
        custom_dataset_cfg = config["custom_dataset_conf"]
        output_paths = run_custom_graph(**custom_dataset_cfg)
    elif config["scaling_benchmark_run"]:
        scaling_cfg = config["scaling_benchmark_conf"]
        output_paths = run_scaling_benchmark(**scaling_cfg)

    return output_paths, required_force_save


if __name__ == "__main__":
    run_benchmark()
