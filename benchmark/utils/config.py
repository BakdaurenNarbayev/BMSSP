import yaml
import tempfile

from pathlib import Path


def load_config(
    path: str = "benchmark/config/main.yaml", force_save: bool = False
) -> dict:
    """
    Load a YAML configuration file into a Python dictionary.

    Args:
        path (str, optional): Path to the YAML config file.
        force_save (bool, optional): If True, populate any missing
            `save_result_path` fields with a temp directory.

    Returns:
        dict: Parsed configuration.
        bool: if required force_save

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the YAML content is invalid.
        KeyError: If expected configuration sections are missing.
    """
    required_force_save = False
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    if not force_save:
        return config, required_force_save

    default_save_path = str(Path(tempfile.gettempdir()))
    sections = [
        "demo_conf",
        "custom_dataset_conf",
        "scaling_benchmark_conf",
    ]

    for section in sections:
        if section not in config:
            raise KeyError(f"Missing expected config section: {section}")

        if not config[section.replace("conf", "run")]:
            continue

        if config[section].get("save_result_path") is None:
            config[section]["save_result_path"] = default_save_path

    return config, required_force_save
