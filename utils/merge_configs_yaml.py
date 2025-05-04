import os
from pathlib import Path
from typing import Dict, Any


import yaml


from ._deep_merge_two_dictionaries import deep_merge_two_dictionaries


def merge_configs_yaml(root_dir: str, output_path: str = None) -> Dict[str, Any]:
    """
    Walk through a directory to find all configs.yaml files and merge them,
    with values from deeper directories taking precedence.

    Args:
        root_dir: The root directory to start searching from
        output_path: Optional path to write the merged config to

    Returns:
        The merged configuration dictionary
    """
    root_dir = Path(root_dir).resolve()

    # Start with empty config
    merged_config = {}

    # Keep track of directories by depth to ensure proper precedence
    configs_by_depth = {}

    # Walk through all directories
    for dirpath, _, filenames in os.walk(root_dir):
        path = Path(dirpath)
        if "configs.yaml" in filenames:
            # Calculate depth from root
            depth = len(path.relative_to(root_dir).parts)
            config_path = path / "configs.yaml"

            try:
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)

                if config_data:  # Skip empty configs
                    configs_by_depth[depth] = configs_by_depth.get(depth, []) + [(config_path, config_data)]
            except Exception as e:
                print(f"Error reading {config_path}: {e}")

    # Merge configs in order of depth (shallow to deep)
    for depth in sorted(configs_by_depth.keys()):
        for config_path, config_data in configs_by_depth[depth]:
            merged_config = deep_merge_two_dictionaries(merged_config, config_data)
            print(f"Merged config from {config_path}")

    # Write merged config to output file if specified
    if output_path:
        output_path = output_path if isinstance(output_path, Path) else Path(output_path)
        with open(output_path, 'w') as f:
            yaml.dump(merged_config, f, default_flow_style=False)
        print(f"Wrote merged config to {output_path}")

    return merged_config
