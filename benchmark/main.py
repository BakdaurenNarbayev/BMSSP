import os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from benchmark.utils.config import load_config
from benchmark.sample_runs import demo_run, run_scaling_benchmark


def main():
    config = load_config()

    if config["demo_run"]:
        demo_run()
    elif config["scaling_benchmark_run"]:
        scaling_cfg = config["scaling_benchmark_conf"]
        run_scaling_benchmark(**scaling_cfg)


if __name__ == "__main__":
    main()
